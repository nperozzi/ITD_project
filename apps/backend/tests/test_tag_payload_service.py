from __future__ import annotations

from datetime import datetime, timedelta, UTC

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.base import Base
from db.crud.product import create_product
from db.crud.promotion import create_promotion
from db.crud.tag import create_tag
from db.models.shelfLocation import ShelfLocation  # noqa: F401
from db.models.tag import Status
from services.tag_payload_service import build_payload_for_tag


def make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return Session()


def test_build_payload_for_tag_applies_active_percentage_promotion():
    db = make_session()
    product = create_product(db, "SKU-1", "Coffee", {}, 20.0)
    tag = create_tag(db, status=Status.ONLINE, battery_pct=88, product_id=product.id)
    now = datetime.now(UTC).replace(tzinfo=None)
    create_promotion(
        db,
        product_id=product.id,
        discount_percentage=25,
        start_at=now - timedelta(days=1),
        end_at=now + timedelta(days=1),
    )

    payload = build_payload_for_tag(db, tag.id)

    assert payload["tagId"] == tag.id
    assert payload["title"] == "Coffee"
    assert payload["finalPrice"] == 15.0
    assert payload == {"tagId": tag.id, "title": "Coffee", "finalPrice": 15.0}
