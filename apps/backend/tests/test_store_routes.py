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


def test_get_stores_returns_database_rows():
    client = make_client()

    create_response = client.post("/api/stores", json={"name": "Downtown Market"})
    assert create_response.status_code == 201

    response = client.get("/api/stores")

    assert response.status_code == 200
    assert response.get_json() == [{"id": 1, "name": "Downtown Market"}]


def test_get_single_store_returns_404_when_missing():
    client = make_client()

    response = client.get("/api/stores/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Store not found."}


def test_create_store_validates_payload():
    client = make_client()

    response = client.post("/api/stores", json={"name": ""})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Field 'name' must be a non-empty string."}


def test_patch_store_updates_existing_row():
    client = make_client()
    create_response = client.post("/api/stores", json={"name": "Old Name"})
    store_id = create_response.get_json()["id"]

    response = client.patch(f"/api/stores/{store_id}", json={"name": "New Name"})

    assert response.status_code == 200
    assert response.get_json() == {"id": store_id, "name": "New Name"}


def test_delete_store_removes_existing_row():
    client = make_client()
    create_response = client.post("/api/stores", json={"name": "To Delete"})
    store_id = create_response.get_json()["id"]

    delete_response = client.delete(f"/api/stores/{store_id}")
    get_response = client.get(f"/api/stores/{store_id}")

    assert delete_response.status_code == 200
    assert delete_response.get_json() == {"status": "deleted", "id": store_id}
    assert get_response.status_code == 404
