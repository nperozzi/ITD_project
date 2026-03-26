from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.base import Base


from db.crud.store import (
    create_store,
    get_store,
    get_all_stores,
    update_store,
    delete_store,
)

def make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return Session()

def test_create_and_get_store():
    db = make_session()
    store = create_store(db, "Downtown")
    assert store.id is not None
    fetched = get_store(db, store.id)
    assert fetched is not None
    assert fetched.name == "Downtown"

def test_get_all_stores():
    db = make_session()
    create_store(db, "A")
    create_store(db, "B")
    stores = get_all_stores(db)
    assert len(stores) == 2
    assert {s.name for s in stores} == {"A", "B"}

def test_update_store():
    db = make_session()
    store = create_store(db, "Old")
    updated = update_store(db, store.id, name="New")
    assert updated is not None
    assert updated.name == "New"

def test_update_unknown_store_returns_none():
    db = make_session()
    assert update_store(db, 999, name="X") is None

def test_delete_store():
    db = make_session()
    store = create_store(db, "ToDelete")
    assert delete_store(db, store.id) is True
    assert get_store(db, store.id) is None

def test_delete_unknown_store_returns_false():
    db = make_session()
    assert delete_store(db, 999) is False
