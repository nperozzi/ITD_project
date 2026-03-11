from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.base import Base
from db.crud.crud_store import create_store
from db.crud.crud_gateway import (
    create_gateway,
    get_gateway,
    get_all_gateways,
    update_gateway,
    delete_gateway,
)
from db.models.gateway import Status
from db.models.shelfLocation import ShelfLocation  # noqa: F401


def make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return Session()


def test_create_and_get_gateway():
    db = make_session()
    store = create_store(db, "Downtown")
    heartbeat = datetime.now()
    gateway = create_gateway(
        db,
        status=Status.ONLINE,
        store_id=store.id,
        last_heartbeat_at=heartbeat,
    )
    assert gateway.id is not None
    fetched = get_gateway(db, gateway.id)
    assert fetched is not None
    assert fetched.status == Status.ONLINE
    assert fetched.store_id == store.id
    assert fetched.last_heartbeat_at == heartbeat


def test_get_all_gateways():
    db = make_session()
    create_gateway(db, status=Status.ONLINE)
    create_gateway(db, status=Status.OFFLINE)
    gateways = get_all_gateways(db)
    assert len(gateways) == 2
    assert {g.status for g in gateways} == {Status.ONLINE, Status.OFFLINE}


def test_update_gateway():
    db = make_session()
    gateway = create_gateway(db, status=Status.OFFLINE)
    heartbeat = datetime.now()
    updated = update_gateway(
        db,
        gateway.id,
        status=Status.DISABLED,
        last_heartbeat_at=heartbeat,
    )
    assert updated is not None
    assert updated.status == Status.DISABLED
    assert updated.last_heartbeat_at == heartbeat


def test_update_gateway_ignores_unknown_fields():
    db = make_session()
    gateway = create_gateway(db, status=Status.ONLINE)
    updated = update_gateway(db, gateway.id, not_a_field="ignored")
    assert updated is not None
    assert updated.status == Status.ONLINE
    assert not hasattr(updated, "not_a_field")


def test_update_unknown_gateway_returns_none():
    db = make_session()
    assert update_gateway(db, 999, status=Status.ONLINE) is None


def test_delete_gateway():
    db = make_session()
    gateway = create_gateway(db, status=Status.ONLINE)
    assert delete_gateway(db, gateway.id) is True
    assert get_gateway(db, gateway.id) is None


def test_delete_unknown_gateway_returns_false():
    db = make_session()
    assert delete_gateway(db, 999) is False
