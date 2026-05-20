from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import SignupRequest, LoginRequest, AuthUserResponse
from ..security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


def format_user_response(user: User, token: str) -> dict:
    return {
        "_id": f"u{user.id}",
        "name": user.name,
        "email": user.email,
        "phone": user.phone or "",
        "address": user.address or "",
        "profilePic": user.profile_pic or "",
        "isAdmin": user.is_admin,
        "token": token
    }


@router.post("/signup", response_model=AuthUserResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    if payload.confirm is not None and payload.password != payload.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match."
        )

    new_user = User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone or "",
        address=payload.address or "",
        hashed_password=hash_password(payload.password),
        is_admin=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(new_user.id, new_user.email)

    return format_user_response(new_user, token)


@router.post("/login", response_model=AuthUserResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been blocked."
        )

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    token = create_access_token(user.id, user.email)

    return format_user_response(user, token)