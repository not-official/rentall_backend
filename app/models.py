from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text
from datetime import datetime

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, default="")
    address = Column(String, default="")
    profile_pic = Column(String, default="")

    hashed_password = Column(String, nullable=False)

    is_admin = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    image = Column(String, default="")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=1)
    featured = Column(Boolean, default=False)
    available_date = Column(String, default="")
    description = Column(Text, default="")

    category_id = Column(Integer, nullable=True)
    user_id = Column(Integer, nullable=True)

    image = Column(Text, default="")
    images = Column(Text, default="")

    created_at = Column(DateTime, default=datetime.utcnow)

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False)      # renter
    owner_id = Column(Integer, nullable=True)      # owner

    item_id = Column(String, nullable=False)
    item_name = Column(String, nullable=False)
    item_image = Column(String, default="")

    price_per_day = Column(Float, nullable=False)
    days = Column(Integer, default=1)
    total_price = Column(Float, nullable=False)

    status = Column(String, default="pending")
    # pending, confirmed, rejected, cancelled

    created_at = Column(DateTime, default=datetime.utcnow)