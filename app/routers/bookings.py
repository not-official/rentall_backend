from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Booking, User
from ..schemas import BookingCreate, BookingResponse
from ..dependencies import get_current_user

router = APIRouter(prefix="/bookings", tags=["Bookings"])


def clean_prefixed_id(value: str | None, prefix: str) -> int | None:
    if not value:
        return None

    value = str(value)

    if value.startswith(prefix):
        return int(value.replace(prefix, ""))

    if value.isdigit():
        return int(value)

    return None


def clean_booking_id(booking_id: str) -> int:
    value = str(booking_id)

    if value.startswith("b"):
        return int(value.replace("b", ""))

    if value.isdigit():
        return int(value)

    raise HTTPException(status_code=400, detail="Invalid booking ID.")


def format_booking(booking: Booking) -> dict:
    return {
        "_id": f"b{booking.id}",
        "userId": f"u{booking.user_id}",
        "ownerId": f"u{booking.owner_id}" if booking.owner_id else "",
        "itemId": booking.item_id,
        "itemName": booking.item_name,
        "itemImage": booking.item_image or "",
        "pricePerDay": booking.price_per_day,
        "days": booking.days,
        "totalPrice": booking.total_price,
        "status": booking.status,
        "createdAt": booking.created_at.isoformat(),
    }


@router.post("")
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.days < 1:
        raise HTTPException(status_code=400, detail="Rental days must be at least 1.")

    owner_id = clean_prefixed_id(payload.ownerId, "u")

    if not owner_id:
        raise HTTPException(
            status_code=400,
            detail="This item does not have an owner. Request cannot be sent.",
        )

    if owner_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot rent your own item.",
        )

    expected_total = payload.pricePerDay * payload.days

    booking = Booking(
        user_id=current_user.id,
        owner_id=owner_id,
        item_id=payload.itemId,
        item_name=payload.itemName,
        item_image=payload.itemImage or "",
        price_per_day=payload.pricePerDay,
        days=payload.days,
        total_price=payload.totalPrice or expected_total,
        status="pending",
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return format_booking(booking)


@router.get("/my")
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookings = (
        db.query(Booking)
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )

    return [format_booking(booking) for booking in bookings]


@router.get("/owner")
def get_owner_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookings = (
        db.query(Booking)
        .filter(Booking.owner_id == current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )

    return [format_booking(booking) for booking in bookings]


@router.get("")
def get_all_bookings(db: Session = Depends(get_db)):
    bookings = db.query(Booking).order_by(Booking.created_at.desc()).all()
    return [format_booking(booking) for booking in bookings]


@router.put("/{booking_id}/accept")
def accept_booking(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    clean_id = clean_booking_id(booking_id)

    booking = db.query(Booking).filter(Booking.id == clean_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    if booking.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only the owner can accept this request.")

    if booking.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending requests can be accepted.")

    booking.status = "confirmed"

    db.commit()
    db.refresh(booking)

    return format_booking(booking)


@router.put("/{booking_id}/reject")
def reject_booking(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    clean_id = clean_booking_id(booking_id)

    booking = db.query(Booking).filter(Booking.id == clean_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    if booking.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only the owner can reject this request.")

    if booking.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending requests can be rejected.")

    booking.status = "rejected"

    db.commit()
    db.refresh(booking)

    return format_booking(booking)


@router.put("/{booking_id}/cancel")
def cancel_booking(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    clean_id = clean_booking_id(booking_id)

    booking = db.query(Booking).filter(Booking.id == clean_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    if booking.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="You cannot cancel this booking.")

    if booking.status == "confirmed":
        raise HTTPException(
            status_code=400,
            detail="Confirmed bookings cannot be cancelled from renter side.",
        )

    booking.status = "cancelled"

    db.commit()
    db.refresh(booking)

    return format_booking(booking)