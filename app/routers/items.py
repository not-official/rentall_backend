import json
import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..database import get_db
from ..models import Item, User
from ..schemas import ItemCreate, ItemUpdate
from ..dependencies import get_current_user

router = APIRouter(prefix="/items", tags=["Items"])


def clean_item_id(value: str | None) -> int | None:
    if not value:
        return None

    value = str(value)

    if value.startswith("bi"):
        return int(value.replace("bi", ""))

    if value.isdigit():
        return int(value)

    raise HTTPException(status_code=400, detail="Invalid backend item ID.")


def clean_prefixed_id(value: str | None, prefix: str) -> int | None:
    if not value:
        return None

    value = str(value)

    if value.startswith(prefix):
        return int(value.replace(prefix, ""))

    if value.isdigit():
        return int(value)

    return None


def format_item(item: Item, db: Session | None = None) -> dict:
    try:
        images = json.loads(item.images) if item.images else []
    except Exception:
        images = []

    owner = None

    if db and item.user_id:
        owner = db.query(User).filter(User.id == item.user_id).first()

    return {
        "_id": f"bi{item.id}",
        "name": item.name,
        "price": item.price,
        "stock": item.stock,
        "featured": item.featured,
        "availableDate": item.available_date or "",
        "description": item.description or "",
        "category": f"cat{item.category_id}" if item.category_id else "",
        "userId": f"u{item.user_id}" if item.user_id else "",
        "image": item.image or "",
        "images": images,
        "source": "backend",
        "ownerName": owner.name if owner else "RentAll Owner",
        "ownerEmail": owner.email if owner else "",
        "ownerProfilePic": owner.profile_pic if owner else "",
    }


@router.get("")
def get_items(
    search: str | None = Query(default=None),
    category: str | None = Query(default=None),
    featured: bool | None = Query(default=None),
    min_price: float | None = Query(default=None),
    max_price: float | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Item)

    if search:
        query = query.filter(
            or_(
                Item.name.ilike(f"%{search}%"),
                Item.description.ilike(f"%{search}%"),
            )
        )

    if category:
        category_id = clean_prefixed_id(category, "cat")
        query = query.filter(Item.category_id == category_id)

    if featured is not None:
        query = query.filter(Item.featured == featured)

    if min_price is not None:
        query = query.filter(Item.price >= min_price)

    if max_price is not None:
        query = query.filter(Item.price <= max_price)

    items = query.order_by(Item.id.desc()).all()

    return [format_item(item, db) for item in items]


@router.get("/featured")
def get_featured_items(db: Session = Depends(get_db)):
    items = (
        db.query(Item)
        .filter(Item.featured == True)
        .order_by(Item.id.desc())
        .all()
    )

    return [format_item(item, db) for item in items]


@router.post("/upload-image")
def upload_item_image(file: UploadFile = File(...)):
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG, and WEBP images are allowed.",
        )

    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    extension = file.filename.split(".")[-1].lower()
    filename = f"{uuid4()}.{extension}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "imageUrl": f"http://127.0.0.1:8000/uploads/{filename}",
    }


@router.get("/{item_id}")
def get_item(item_id: str, db: Session = Depends(get_db)):
    clean_id = clean_item_id(item_id)

    item = db.query(Item).filter(Item.id == clean_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found.")

    return format_item(item, db)


@router.post("")
def create_item(
    payload: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = Item(
        name=payload.name,
        price=payload.price,
        stock=payload.stock,
        featured=payload.featured,
        available_date=payload.availableDate or "",
        description=payload.description or "",
        category_id=clean_prefixed_id(payload.category, "cat"),
        user_id=current_user.id,
        image=payload.image or "",
        images=json.dumps(payload.images or []),
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return format_item(item, db)


@router.put("/{item_id}")
def update_item(
    item_id: str,
    payload: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    clean_id = clean_item_id(item_id)

    item = db.query(Item).filter(Item.id == clean_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found.")

    if item.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Only the owner can update this item.",
        )

    if payload.name is not None:
        item.name = payload.name

    if payload.price is not None:
        item.price = payload.price

    if payload.stock is not None:
        item.stock = payload.stock

    if payload.featured is not None:
        item.featured = payload.featured

    if payload.availableDate is not None:
        item.available_date = payload.availableDate

    if payload.description is not None:
        item.description = payload.description

    if payload.category is not None:
        item.category_id = clean_prefixed_id(payload.category, "cat")

    if payload.image is not None:
        item.image = payload.image

    if payload.images is not None:
        item.images = json.dumps(payload.images)

    db.commit()
    db.refresh(item)

    return format_item(item, db)


@router.delete("/{item_id}")
def delete_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    clean_id = clean_item_id(item_id)

    item = db.query(Item).filter(Item.id == clean_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found.")

    if item.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Only the owner can delete this item.",
        )

    db.delete(item)
    db.commit()

    return {"message": "Item deleted successfully."}