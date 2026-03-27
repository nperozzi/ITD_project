from __future__ import annotations

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.base import Base
from db.crud.tag import create_tag
from db.models.shelfLocation import ShelfLocation  # noqa: F401
from db.models.tag import Status, Tag  # noqa: F401
from routes import api


class DummyDB:
    def __init__(self) -> None:
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        self.SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def make_client():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["db"] = DummyDB()
    app.register_blueprint(api)
    return app.test_client()


def test_get_battery_reads_last_stored_value_for_default_tag():
    client = make_client()

    with client.application.app_context():
        db = client.application.config["db"]
        with db.SessionLocal() as session:
            create_tag(session, status=Status.ONLINE, battery_pct=73)

    response = client.get("/battery")

    assert response.status_code == 200
    assert response.get_json() == {"battery": 73}


def test_get_battery_reads_specific_tag_from_query_param():
    client = make_client()

    with client.application.app_context():
        db = client.application.config["db"]
        with db.SessionLocal() as session:
            create_tag(session, status=Status.ONLINE, battery_pct=12)
            second_tag = create_tag(session, status=Status.ONLINE, battery_pct=88)

    response = client.get(f"/battery?tagId={second_tag.id}")

    assert response.status_code == 200
    assert response.get_json() == {"battery": 88}


def test_get_battery_rejects_invalid_tag_id():
    client = make_client()

    response = client.get("/battery?tagId=0")

    assert response.status_code == 400
    assert response.get_json() == {"error": "Query parameter 'tagId' must be a positive integer."}


def test_get_battery_returns_404_when_tag_is_missing():
    client = make_client()

    response = client.get("/battery?tagId=999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Tag not found."}
