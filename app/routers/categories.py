from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Category
from ..schemas import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["Categories"])


def format_category(category: Category) -> dict:
    return {
        "_id": f"cat{category.id}",
        "name": category.name,
        "image": category.image or "",
    }


@router.get("", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return [format_category(category) for category in categories]


@router.post("", response_model=CategoryResponse)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    category = Category(
        name=payload.name,
        image=payload.image or "",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return format_category(category)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: str, db: Session = Depends(get_db)):
    clean_id = int(category_id.replace("cat", ""))

    category = db.query(Category).filter(Category.id == clean_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")

    return format_category(category)