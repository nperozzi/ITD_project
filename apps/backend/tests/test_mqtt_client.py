from __future__ import annotations

import json
from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import mqtt_client
from db.base import Base
from db.crud.tag import create_tag
from db.crud.tagpayload import create_tagpayload, get_tagpayload
from db.models.shelfLocation import ShelfLocation  # noqa: F401
from db.models.tag import Status


class DummyDB:
    def __init__(self) -> None:
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        self.SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def test_ack_message_marks_latest_payload_as_acknowledged():
    db = DummyDB()
    mqtt_client.set_db(db)

    with db.SessionLocal() as session:
        tag = create_tag(session, status=Status.ONLINE, battery_pct=80)
        stored_payload = create_tagpayload(session, tag_id=tag.id, payload_json={"price": 10.0})

    message = SimpleNamespace(
        topic=f"g-b/tag{tag.id}/ack",
        payload=json.dumps({"ack": True}).encode(),
    )

    mqtt_client.on_message(None, None, message)

    with db.SessionLocal() as session:
        refreshed_payload = get_tagpayload(session, stored_payload.id)

    assert refreshed_payload is not None
    assert refreshed_payload.acknowledged is True
