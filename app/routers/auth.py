from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import os
import shutil
from uuid import uuid4

from ..database import get_db
from ..models import User
from ..schemas import SignupRequest, LoginRequest, AuthUserResponse
from ..security import hash_password, verify_password, create_access_token
from ..dependencies import get_current_user

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
        "token": token,
    }


def format_user_without_token(user: User) -> dict:
    return {
        "_id": f"u{user.id}",
        "name": user.name,
        "email": user.email,
        "phone": user.phone or "",
        "address": user.address or "",
        "profilePic": user.profile_pic or "",
        "isAdmin": user.is_admin,
    }


@router.post("/signup", response_model=AuthUserResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )

    if payload.confirm is not None and payload.password != payload.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match.",
        )

    new_user = User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone or "",
        address=payload.address or "",
        hashed_password=hash_password(payload.password),
        is_admin=False,
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
            detail="Invalid email or password.",
        )

    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been blocked.",
        )

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token(user.id, user.email)

    return format_user_response(user, token)


@router.post("/profile-image")
def upload_profile_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG, PNG, and WEBP images are allowed.",
        )

    upload_dir = "uploads/profile"
    os.makedirs(upload_dir, exist_ok=True)

    extension = file.filename.split(".")[-1].lower()
    filename = f"profile-{current_user.id}-{uuid4()}.{extension}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image_url = f"http://127.0.0.1:8000/uploads/profile/{filename}"

    current_user.profile_pic = image_url

    db.commit()
    db.refresh(current_user)

    return format_user_without_token(current_user)