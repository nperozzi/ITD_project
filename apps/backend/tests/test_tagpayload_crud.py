from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.base import Base
from db.crud.tag import create_tag
from db.crud.tagpayload import (
    create_tagpayload,
    delete_tagpayload,
    get_all_tagpayloads,
    get_tagpayload,
    update_tagpayload,
)
from db.models.gateway import Gateway  # noqa: F401
from db.models.product import Product  # noqa: F401
from db.models.promotion import Promotion  # noqa: F401
from db.models.shelfLocation import ShelfLocation  # noqa: F401
from db.models.store import Store  # noqa: F401
from db.models.tag import Status
from db.models.tagpayload import TagPayload  # noqa: F401


def make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return Session()


def test_create_and_get_tagpayload():
    db = make_session()
    tag = create_tag(db, status=Status.ONLINE, battery_pct=90)
    tagpayload = create_tagpayload(
        db,
        tag_id=tag.id,
        payload_json={"title": "Coffee", "price": 22.9},
    )

    assert tagpayload.id is not None
    fetched = get_tagpayload(db, tagpayload.id)
    assert fetched is not None
    assert fetched.tag_id == tag.id
    assert fetched.payload_json == {"title": "Coffee", "price": 22.9}


def test_get_all_tagpayloads():
    db = make_session()
    tag = create_tag(db, status=Status.ONLINE)
    create_tagpayload(db, tag_id=tag.id, payload_json={"sku": "A"})
    create_tagpayload(db, tag_id=tag.id, payload_json={"sku": "B"})

    payloads = get_all_tagpayloads(db)
    assert len(payloads) == 2
    assert {p.payload_json["sku"] for p in payloads} == {"A", "B"}


def test_update_tagpayload():
    db = make_session()
    tag = create_tag(db, status=Status.ONLINE)
    tagpayload = create_tagpayload(db, tag_id=tag.id, payload_json={"price": 5.0})

    updated = update_tagpayload(db, tagpayload.id, payload_json={"price": 6.5})
    assert updated is not None
    assert updated.payload_json == {"price": 6.5}


def test_update_tagpayload_ignores_unknown_fields():
    db = make_session()
    tag = create_tag(db, status=Status.ONLINE)
    tagpayload = create_tagpayload(db, tag_id=tag.id, payload_json={"x": 1})

    updated = update_tagpayload(db, tagpayload.id, not_a_field="ignored")
    assert updated is not None
    assert updated.payload_json == {"x": 1}
    assert not hasattr(updated, "not_a_field")


def test_update_unknown_tagpayload_returns_none():
    db = make_session()
    assert update_tagpayload(db, 999, payload_json={"x": 2}) is None


def test_delete_tagpayload():
    db = make_session()
    tag = create_tag(db, status=Status.ONLINE)
    tagpayload = create_tagpayload(db, tag_id=tag.id, payload_json={"x": 1})

    assert delete_tagpayload(db, tagpayload.id) is True
    assert get_tagpayload(db, tagpayload.id) is None


def test_delete_unknown_tagpayload_returns_false():
    db = make_session()
    assert delete_tagpayload(db, 999) is False
