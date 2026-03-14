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


def test_get_shelflocations_returns_database_rows():
    client = make_client()
    store_response = client.post("/api/stores", json={"name": "Downtown Market"})
    store_id = store_response.get_json()["id"]

    create_response = client.post(
        "/api/shelf-locations",
        json={"storeId": store_id, "aisle": 1, "level": "2"},
    )
    assert create_response.status_code == 201

    response = client.get("/api/shelf-locations")

    assert response.status_code == 200
    assert response.get_json() == [
        {"id": 1, "storeId": store_id, "aisle": 1, "level": 2}
    ]


def test_get_single_shelflocation_returns_404_when_missing():
    client = make_client()

    response = client.get("/api/shelf-locations/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Shelf location not found."}


def test_create_shelflocation_validates_payload():
    client = make_client()

    response = client.post("/api/shelf-locations", json={"storeId": 1, "aisle": "A1", "level": 2})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Field 'aisle' must be a positive integer."}


def test_patch_shelflocation_updates_existing_row():
    client = make_client()
    store_response = client.post("/api/stores", json={"name": "Downtown Market"})
    store_id = store_response.get_json()["id"]
    create_response = client.post(
        "/api/shelf-locations",
        json={"storeId": store_id, "aisle": 1, "level": 1},
    )
    shelflocation_id = create_response.get_json()["id"]

    response = client.patch(
        f"/api/shelf-locations/{shelflocation_id}",
        json={"aisle": "5", "level": 4},
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "id": shelflocation_id,
        "storeId": store_id,
        "aisle": 5,
        "level": 4,
    }


def test_delete_shelflocation_removes_existing_row():
    client = make_client()
    store_response = client.post("/api/stores", json={"name": "Downtown Market"})
    store_id = store_response.get_json()["id"]
    create_response = client.post(
        "/api/shelf-locations",
        json={"storeId": store_id, "aisle": 3, "level": 2},
    )
    shelflocation_id = create_response.get_json()["id"]

    delete_response = client.delete(f"/api/shelf-locations/{shelflocation_id}")
    get_response = client.get(f"/api/shelf-locations/{shelflocation_id}")

    assert delete_response.status_code == 200
    assert delete_response.get_json() == {"status": "deleted", "id": shelflocation_id}
    assert get_response.status_code == 404
