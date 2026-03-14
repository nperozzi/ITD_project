from __future__ import annotations

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.base import Base
from db.models.shelfLocation import ShelfLocation  # noqa: F401
from db.models.tag import Tag  # noqa: F401
from routes import api
from seeds.demo_data import seed_demo_data


class DummyDB:
    def __init__(self) -> None:
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        self.SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
        with self.SessionLocal() as session:
            seed_demo_data(session)


def make_client():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["db"] = DummyDB()
    app.register_blueprint(api)
    return app.test_client()


def test_get_tagpayloads_returns_seeded_rows():
    client = make_client()

    response = client.get("/api/tag-payloads")

    assert response.status_code == 200
    assert response.get_json() == [
        {
            "id": 1,
            "payloadJson": {"tagId": 1, "title": "Arabica Coffee Beans", "basePrice": 22.9, "finalPrice": 20.61},
        },
        {
            "id": 2,
            "payloadJson": {"tagId": 2, "title": "Organic Oat Milk", "basePrice": 4.5, "finalPrice": 4.5},
        },
    ]
