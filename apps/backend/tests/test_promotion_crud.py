from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.base import Base
from db.crud.product import create_product
from db.crud.promotion import (
    create_promotion,
    delete_promotion,
    get_all_promotions,
    get_promotion,
    update_promotion,
)
from db.models.shelfLocation import ShelfLocation  # noqa: F401
from db.models.tag import Tag  # noqa: F401


def make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return Session()


def test_create_and_get_promotion():
    db = make_session()
    product = create_product(db, "SKU-001", "Coffee", {}, 10.0)
    promotion = create_promotion(
        db,
        product_id=product.id,
        discount_percentage=20,
        start_at=datetime(2026, 3, 1, 10, 0, 0),
        end_at=datetime(2026, 3, 10, 10, 0, 0),
    )
    assert promotion.id is not None
    fetched = get_promotion(db, promotion.id)
    assert fetched is not None
    assert fetched.product_id == product.id
    assert fetched.discount_percentage == 20


def test_get_all_promotions():
    db = make_session()
    create_promotion(db, None, 10, datetime(2026, 3, 1), datetime(2026, 3, 2))
    create_promotion(db, None, 15, datetime(2026, 3, 3), datetime(2026, 3, 4))
    promotions = get_all_promotions(db)
    assert len(promotions) == 2
    assert {promotion.discount_percentage for promotion in promotions} == {10, 15}


def test_update_promotion():
    db = make_session()
    promotion = create_promotion(db, None, 10, datetime(2026, 3, 1), datetime(2026, 3, 2))
    updated = update_promotion(
        db,
        promotion.id,
        discount_percentage=25,
        end_at=datetime(2026, 3, 5),
    )
    assert updated is not None
    assert updated.discount_percentage == 25
    assert updated.end_at == datetime(2026, 3, 5)


def test_update_unknown_promotion_returns_none():
    db = make_session()
    assert update_promotion(db, 999, discount_percentage=50) is None


def test_delete_promotion():
    db = make_session()
    promotion = create_promotion(db, None, 5, datetime(2026, 3, 1), datetime(2026, 3, 2))
    assert delete_promotion(db, promotion.id) is True
    assert get_promotion(db, promotion.id) is None


def test_delete_unknown_promotion_returns_false():
    db = make_session()
    assert delete_promotion(db, 999) is False
