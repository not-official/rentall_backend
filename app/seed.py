import json

from .database import SessionLocal, Base, engine
from .models import Category, Item, User
from .security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()


def seed_users():
    if db.query(User).count() > 0:
        return

    demo_users = [
        {
            "name": "Admin User",
            "email": "admin@rentall.com",
            "phone": "0400000000",
            "address": "Sydney, Australia",
            "is_admin": True,
        },
        {
            "name": "Owner User",
            "email": "owner@rentall.com",
            "phone": "0411111111",
            "address": "Canberra, Australia",
            "is_admin": False,
        },
        {
            "name": "Renter User",
            "email": "renter@rentall.com",
            "phone": "0422222222",
            "address": "Melbourne, Australia",
            "is_admin": False,
        },
    ]

    for user in demo_users:
        db.add(
            User(
                name=user["name"],
                email=user["email"],
                phone=user["phone"],
                address=user["address"],
                profile_pic="",
                is_admin=user["is_admin"],
                hashed_password=hash_password("password123"),
            )
        )

    db.commit()


def seed_categories():
    if db.query(Category).count() > 0:
        return

    categories = [
        {
            "name": "Men",
            "image": "https://images.pexels.com/photos/1183266/pexels-photo-1183266.jpeg?auto=compress&cs=tinysrgb&w=600",
        },
        {
            "name": "Women",
            "image": "https://images.pexels.com/photos/1536619/pexels-photo-1536619.jpeg?auto=compress&cs=tinysrgb&w=600",
        },
        {
            "name": "Kids",
            "image": "https://images.pexels.com/photos/35537/child-children-girl-happy.jpg?auto=compress&cs=tinysrgb&w=600",
        },
        {
            "name": "Accessories",
            "image": "https://images.pexels.com/photos/1152077/pexels-photo-1152077.jpeg?auto=compress&cs=tinysrgb&w=600",
        },
        {
            "name": "Outerwear",
            "image": "https://images.pexels.com/photos/1040945/pexels-photo-1040945.jpeg?auto=compress&cs=tinysrgb&w=600",
        },
        {
            "name": "Footwear",
            "image": "https://images.pexels.com/photos/267301/pexels-photo-267301.jpeg?auto=compress&cs=tinysrgb&w=600",
        },
    ]

    for category in categories:
        db.add(Category(name=category["name"], image=category["image"]))

    db.commit()


def seed_items():
    if db.query(Item).count() > 0:
        return

    backend_items = [
        {
            "name": "Owner Added Denim Jacket",
            "price": 19,
            "stock": 2,
            "featured": True,
            "available_date": "2026-06-15",
            "description": "This is a backend item added by an owner. It proves that new owner listings can appear beside local frontend products.",
            "category_id": 5,
            "user_id": 2,
            "image": "https://images.pexels.com/photos/7679720/pexels-photo-7679720.jpeg?auto=compress&cs=tinysrgb&w=600",
            "images": [
                "https://images.pexels.com/photos/7679720/pexels-photo-7679720.jpeg?auto=compress&cs=tinysrgb&w=600"
            ],
        },
        {
            "name": "Owner Added Travel Backpack",
            "price": 14,
            "stock": 4,
            "featured": False,
            "available_date": "2026-06-18",
            "description": "A backend-created backpack listing. This item is stored in SQLite and merged with frontend local products.",
            "category_id": 4,
            "user_id": 2,
            "image": "https://images.pexels.com/photos/1546003/pexels-photo-1546003.jpeg?auto=compress&cs=tinysrgb&w=600",
            "images": [
                "https://images.pexels.com/photos/1546003/pexels-photo-1546003.jpeg?auto=compress&cs=tinysrgb&w=600"
            ],
        },
    ]

    for item in backend_items:
        db.add(
            Item(
                name=item["name"],
                price=item["price"],
                stock=item["stock"],
                featured=item["featured"],
                available_date=item["available_date"],
                description=item["description"],
                category_id=item["category_id"],
                user_id=item["user_id"],
                image=item["image"],
                images=json.dumps(item["images"]),
            )
        )

    db.commit()


try:
    seed_users()
    seed_categories()
    seed_items()

    print("Database seeded successfully.")
    print("Demo accounts:")
    print("Admin : admin@rentall.com / password123")
    print("Owner : owner@rentall.com / password123")
    print("Renter: renter@rentall.com / password123")
finally:
    db.close()