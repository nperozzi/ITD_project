from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.shelflocation import ShelfLocation

def create_shelflocation(
        db: Session,
        store_id: int, 
        aisle: int,
        level: int,
) -> ShelfLocation:
    shelflocation = ShelfLocation(
        store_id=store_id,
        aisle=aisle,
        level=level
    )

    db.add(shelflocation)
    db.commit()
    db.refresh(shelflocation)
    return shelflocation

def get_shelflocation(db: Session, shelflocation_id: int) -> ShelfLocation | None:
    return db.get(ShelfLocation, shelflocation_id)

def get_all_shelflocations(db: Session, shelflocation_id: int, **kwargs: Any) -> ShelfLocation | None:
    shelflocation = db.get(ShelfLocation, shelflocation_id)
    if not shelflocation:
        return None
    
    for key, value in kwargs.items():
        if hasattr(shelflocation, key):
            setattr(shelflocation, key, value)

    db.commit()
    db.refresh(shelflocation)
    return shelflocation

def delete_shelflocation(db: Session, shelflocation_id: int) -> bool:
    shelflocation = db.get(ShelfLocation, shelflocation_id)
    if not shelflocation:
        return False

    db.delete(shelflocation)
    db.commit()
    return True