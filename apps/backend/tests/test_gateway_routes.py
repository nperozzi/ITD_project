from __future__ import annotations

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.base import Base
from db.models.shelfLocation import ShelfLocation  # noqa: F401
from db.models.tag import Tag  # noqa: F401
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


def test_get_gateways_returns_database_rows():
    client = make_client()

    create_response = client.post(
        "/api/gateways",
        json={"storeId": None, "status": "degraded", "lastHeartbeatAt": "2026-03-14T10:30:00Z"},
    )
    assert create_response.status_code == 201

    response = client.get("/api/gateways")

    assert response.status_code == 200
    assert response.get_json() == [
        {
            "id": 1,
            "storeId": None,
            "status": "degraded",
            "lastHeartbeatAt": "2026-03-14T10:30:00Z",
        }
    ]


def test_get_single_gateway_returns_404_when_missing():
    client = make_client()

    response = client.get("/api/gateways/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Gateway not found."}


def test_create_gateway_validates_payload():
    client = make_client()

    response = client.post("/api/gateways", json={"status": "unknown"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Field 'status' must be one of: online, offline, degraded."}


def test_patch_gateway_updates_existing_row():
    client = make_client()
    create_response = client.post(
        "/api/gateways",
        json={"storeId": None, "status": "online", "lastHeartbeatAt": "2026-03-14T10:30:00Z"},
    )
    gateway_id = create_response.get_json()["id"]

    response = client.patch(
        f"/api/gateways/{gateway_id}",
        json={"status": "offline", "lastHeartbeatAt": "2026-03-15T08:00:00Z"},
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "id": gateway_id,
        "storeId": None,
        "status": "offline",
        "lastHeartbeatAt": "2026-03-15T08:00:00Z",
    }


def test_delete_gateway_removes_existing_row():
    client = make_client()
    create_response = client.post(
        "/api/gateways",
        json={"storeId": None, "status": "online", "lastHeartbeatAt": ""},
    )
    gateway_id = create_response.get_json()["id"]

    delete_response = client.delete(f"/api/gateways/{gateway_id}")
    get_response = client.get(f"/api/gateways/{gateway_id}")

    assert delete_response.status_code == 200
    assert delete_response.get_json() == {"status": "deleted", "id": gateway_id}
    assert get_response.status_code == 404
