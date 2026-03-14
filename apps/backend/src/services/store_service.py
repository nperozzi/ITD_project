from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from db.crud.crud_store import create_store, delete_store, get_all_stores, get_store, update_store
from db.models.store import Store


class StoreValidationError(ValueError):
    """Raised when incoming store payloads are invalid."""


def store_to_dictionary(store: Store) -> dict[str, Any]:
    return {
        "id": store.id,
        "name": store.name,
    }


def list_all_stores(db: Session) -> list[dict[str, Any]]:
    return [store_to_dictionary(store) for store in get_all_stores(db)]


def get_store_details(db: Session, store_id: int) -> dict[str, Any] | None:
    store = get_store(db, store_id)
    if store is None:
        return None
    return store_to_dictionary(store)


def create_store_from_payload(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    store_data = _validated_store_fields(payload, partial=False)
    store = create_store(db=db, **store_data)
    return store_to_dictionary(store)


def update_store_from_payload(db: Session, store_id: int, payload: dict[str, Any]) -> dict[str, Any] | None:
    store_data = _validated_store_fields(payload, partial=True)
    if not store_data:
        raise StoreValidationError("At least one updatable field is required.")

    store = update_store(db, store_id, **store_data)
    if store is None:
        return None
    return store_to_dictionary(store)


def delete_store_by_id(db: Session, store_id: int) -> bool:
    return delete_store(db, store_id)


def _validated_store_fields(payload: dict[str, Any], *, partial: bool) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise StoreValidationError("JSON object payload is required.")

    allowed_fields = {"name"}
    unknown_fields = sorted(set(payload) - allowed_fields)
    if unknown_fields:
        raise StoreValidationError(f"Unknown field(s): {', '.join(unknown_fields)}")

    data: dict[str, Any] = {}

    if "name" in payload:
        name = payload["name"]
        if not isinstance(name, str) or not name.strip():
            raise StoreValidationError("Field 'name' must be a non-empty string.")
        data["name"] = name.strip()
    elif not partial:
        raise StoreValidationError("Field 'name' is required.")

    return data
