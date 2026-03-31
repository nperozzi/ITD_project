from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.base import Base
from db.crud.shelflocation import (
    create_shelflocation,
    delete_shelflocation,
    get_all_shelflocations,
    get_shelflocation,
    update_shelflocation,
)
from db.crud.store import create_store
from db.models.gateway import Gateway  # noqa: F401
from db.models.shelfLocation import ShelfLocation  # noqa: F401
from db.models.store import Store  # noqa: F401


def make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return Session()


def test_create_and_get_shelflocation():
    db = make_session()
    store = create_store(db, "Downtown")
    shelflocation = create_shelflocation(db, store_id=store.id, aisle=1, level=2)

    assert shelflocation.id is not None
    fetched = get_shelflocation(db, shelflocation.id)
    assert fetched is not None
    assert fetched.store_id == store.id
    assert fetched.aisle == 1
    assert fetched.level == 2


def test_get_all_shelflocations():
    db = make_session()
    store = create_store(db, "Downtown")
    create_shelflocation(db, store_id=store.id, aisle=1, level=1)
    create_shelflocation(db, store_id=store.id, aisle=2, level=3)

    shelflocations = get_all_shelflocations(db)
    assert len(shelflocations) == 2
    assert {(s.aisle, s.level) for s in shelflocations} == {(1, 1), (2, 3)}


def test_update_shelflocation():
    db = make_session()
    store = create_store(db, "Downtown")
    shelflocation = create_shelflocation(db, store_id=store.id, aisle=1, level=1)

    updated = update_shelflocation(db, shelflocation.id, aisle=5, level=4)
    assert updated is not None
    assert updated.aisle == 5
    assert updated.level == 4


def test_update_shelflocation_ignores_unknown_fields():
    db = make_session()
    store = create_store(db, "Downtown")
    shelflocation = create_shelflocation(db, store_id=store.id, aisle=3, level=2)

    updated = update_shelflocation(db, shelflocation.id, not_a_field="ignored")
    assert updated is not None
    assert updated.aisle == 3
    assert updated.level == 2
    assert not hasattr(updated, "not_a_field")


def test_update_unknown_shelflocation_returns_none():
    db = make_session()
    assert update_shelflocation(db, 999, aisle=8) is None


def test_delete_shelflocation():
    db = make_session()
    store = create_store(db, "Downtown")
    shelflocation = create_shelflocation(db, store_id=store.id, aisle=6, level=1)

    assert delete_shelflocation(db, shelflocation.id) is True
    assert get_shelflocation(db, shelflocation.id) is None


def test_delete_unknown_shelflocation_returns_false():
    db = make_session()
    assert delete_shelflocation(db, 999) is False
