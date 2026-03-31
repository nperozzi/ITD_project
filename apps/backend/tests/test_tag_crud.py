import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.base import Base
from db.models.tag import Status
from db.crud.tag import (
    create_tag,
    get_tag,
    get_all_tags,
    update_tag,
    delete_tag,
)



def make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return Session()


def test_create_and_get_tag():
    db = make_session()
    tag = create_tag(db, status=Status.ONLINE, battery_pct=80)
    assert tag.id is not None
    fetched = get_tag(db, tag.id)
    assert fetched is not None
    assert fetched.status == Status.ONLINE
    assert fetched.battery_pct == 80


def test_create_tag_with_string_status():
    db = make_session()
    tag = create_tag(db, status="offline", battery_pct=20)
    assert tag.status == Status.OFFLINE
    assert tag.battery_pct == 20


def test_get_all_tags():
    db = make_session()
    create_tag(db, status=Status.ONLINE)
    create_tag(db, status=Status.DISABLED)
    tags = get_all_tags(db)
    assert len(tags) == 2
    assert {t.status for t in tags} == {Status.ONLINE, Status.DISABLED}


def test_update_tag():
    db = make_session()
    tag = create_tag(db, status=Status.OFFLINE, battery_pct=10)
    updated = update_tag(db, tag.id, status="online", battery_pct=65)
    assert updated is not None
    assert updated.status == Status.ONLINE
    assert updated.battery_pct == 65


def test_update_tag_ignores_unknown_fields():
    db = make_session()
    tag = create_tag(db, status=Status.ONLINE)
    updated = update_tag(db, tag.id, not_a_field="ignored")
    assert updated is not None
    assert updated.status == Status.ONLINE
    assert not hasattr(updated, "not_a_field")


def test_update_unknown_tag_returns_none():
    db = make_session()
    assert update_tag(db, 999, status=Status.ONLINE) is None


def test_delete_tag():
    db = make_session()
    tag = create_tag(db, status=Status.ONLINE)
    assert delete_tag(db, tag.id) is True
    assert get_tag(db, tag.id) is None


def test_delete_unknown_tag_returns_false():
    db = make_session()
    assert delete_tag(db, 999) is False


def test_create_tag_invalid_status_raises_value_error():
    db = make_session()
    with pytest.raises(ValueError, match="Invalid status"):
        create_tag(db, status="bad-status")


def test_create_tag_out_of_range_battery_raises_value_error():
    db = make_session()
    with pytest.raises(ValueError, match="battery_pct must be between 0 and 100"):
        create_tag(db, status=Status.ONLINE, battery_pct=101)


def test_update_tag_out_of_range_battery_raises_value_error():
    db = make_session()
    tag = create_tag(db, status=Status.ONLINE, battery_pct=50)
    with pytest.raises(ValueError, match="battery_pct must be between 0 and 100"):
        update_tag(db, tag.id, battery_pct=-1)
