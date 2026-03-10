
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import select
from db.models.store import Store

def create_store(db: Session, name: str) -> Store:
    store = Store(name = name)
    
    db.add(store)
    db.commit()
    db.refresh(store)

    return store

def get_store(db: Session, store_id: int) -> Store | None:
    return db.get(Store, store_id)

def get_all_stores(db: Session):
    stores = select(Store)
    return db.scalars(stores).all()

def update_store(db: Session, store_id: int, **kwargs: Any) -> Store | None:
    store = db.get(Store, store_id)

    if not store:
        return None
    
    for key, value in kwargs.items():
        if hasattr(store, key):
            setattr(store, key, value)
    
    db.commit()
    db.refresh(store)

    return store

def delete_store(db: Session, store_id: int) -> bool:
    store = db.get(Store, store_id)

    if not store:
        return False

    db.delete(store)
    db.commit()

    return True
