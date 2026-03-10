from typing import Any, Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.promotion import Promotion

def create_promotion(
    db: Session,
    product_id: Optional[int],
    discount_percentage: int,
    start_at: datetime,
    end_at: datetime,
) -> Promotion:
    promotion = Promotion(
        product_id=product_id,
        discount_percentage=discount_percentage,
        start_at=start_at,
        end_at=end_at,
    )

    db.add(promotion)
    db.commit()
    db.refresh(promotion)
    return promotion

def get_promotion (db: Session, promotion_id: int) -> Promotion | None:
    return db.get(Promotion, promotion_id)

def get_all_promotions(db: Session) -> list[Promotion]:
    stmt = select(Promotion)
    return db.scalars(stmt).all()

def update_promotion(db: Session, promotion_id: int, **kwargs: Any) -> Promotion | None:
    promotion = db.get(Promotion, promotion_id)
    if not promotion:
        return None
    
    for key, value in kwargs.items():
        if hasattr(promotion, key):
            setattr(promotion, key, value)

    db.commit()
    db.refresh(promotion)
    return promotion

def delete_promotion(db: Session, promotion_id: int) -> bool:
    promotion = db.get(Promotion, promotion_id)
    if not promotion:
        return False
    
    db.delete(promotion)
    db.commit()
    return True