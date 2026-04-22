from __future__ import annotations

import json
from types import SimpleNamespace

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import mqtt_client
from db.base import Base
from db.crud.tag import create_tag, get_tag
from db.crud.tagpayload import create_tagpayload, get_tagpayload
from db.models.shelfLocation import ShelfLocation  # noqa: F401
from db.models.tag import Status


class DummyDB:
    def __init__(self) -> None:
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        self.SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class SocketRecorder:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def emit(self, event: str, payload: dict) -> None:
        self.events.append((event, payload))


def test_ack_message_marks_latest_payload_as_acknowledged():
    db = DummyDB()
    mqtt_client.set_db(db)

    with db.SessionLocal() as session:
        tag = create_tag(session, status=Status.ONLINE, battery_pct=80)
        stored_payload = create_tagpayload(session, tag_id=tag.id, payload_json={"price": 10.0})

    message = SimpleNamespace(
        topic=f"tag/{tag.id}/ack",
        payload=json.dumps({"tagId": tag.id, "ack": True}).encode(),
    )

    mqtt_client.on_message(None, None, message)

    with db.SessionLocal() as session:
        refreshed_payload = get_tagpayload(session, stored_payload.id)

    assert refreshed_payload is not None
    assert refreshed_payload.acknowledged is True


def test_battery_message_updates_specific_tag_and_emits_socket_event():
    db = DummyDB()
    socket = SocketRecorder()
    app = Flask(__name__)
    mqtt_client.set_db(db)
    mqtt_client.set_app(app)
    mqtt_client.set_socketio(socket)

    with db.SessionLocal() as session:
        tag = create_tag(session, status=Status.ONLINE, battery_pct=80)

    message = SimpleNamespace(
        topic=f"tag/{tag.id}/advertisement",
        payload=json.dumps({"battery": 42, "rssi": -62}).encode(),
    )

    mqtt_client.on_message(None, None, message)

    with db.SessionLocal() as session:
        refreshed_tag = get_tag(session, tag.id)

    assert refreshed_tag is not None
    assert refreshed_tag.battery_pct == 42
    assert socket.events == [
        ("battery_update", {"tagId": tag.id, "batteryPct": 42, "status": "active"})
    ]
