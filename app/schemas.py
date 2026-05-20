from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


# =========================
# AUTH SCHEMAS
# =========================

class SignupRequest(BaseModel):
    name: str = Field(min_length=2)
    email: EmailStr
    phone: Optional[str] = ""
    address: Optional[str] = ""
    password: str = Field(min_length=6)
    confirm: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthUserResponse(BaseModel):
    _id: str
    name: str
    email: EmailStr
    phone: str
    address: str
    profilePic: str
    isAdmin: bool
    token: str


# =========================
# CATEGORY SCHEMAS
# =========================

class CategoryCreate(BaseModel):
    name: str
    image: Optional[str] = ""


class CategoryResponse(BaseModel):
    _id: str
    name: str
    image: str


# =========================
# ITEM SCHEMAS
# =========================

class ItemCreate(BaseModel):
    name: str
    price: float
    stock: int = 1
    featured: bool = False
    availableDate: Optional[str] = ""
    description: Optional[str] = ""
    category: Optional[str] = None
    userId: Optional[str] = None
    image: Optional[str] = ""
    images: Optional[List[str]] = []


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    featured: Optional[bool] = None
    availableDate: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    userId: Optional[str] = None
    image: Optional[str] = None
    images: Optional[List[str]] = None


class ItemResponse(BaseModel):
    _id: str
    name: str
    price: float
    stock: int
    featured: bool
    availableDate: str
    description: str
    category: str
    userId: str
    image: str
    images: List[str]
    source: Optional[str] = "backend"

    # Real owner details from backend
    ownerName: str = ""
    ownerEmail: str = ""
    ownerProfilePic: str = ""


# =========================
# BOOKING / RENTAL SCHEMAS
# =========================

class BookingCreate(BaseModel):
    itemId: str
    ownerId: Optional[str] = ""
    itemName: str
    itemImage: Optional[str] = ""
    pricePerDay: float
    days: int = 1
    totalPrice: float


class BookingResponse(BaseModel):
    _id: str
    userId: str
    ownerId: str
    itemId: str
    itemName: str
    itemImage: str
    pricePerDay: float
    days: int
    totalPrice: float
    status: str
    createdAt: str