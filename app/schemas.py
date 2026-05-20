from pydantic import BaseModel, EmailStr, Field
from typing import Optional


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