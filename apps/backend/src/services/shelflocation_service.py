from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from db.crud.crud_shelflocation import (
    create_shelflocation,
    delete_shelflocation,
    get_all_shelflocations,
    get_shelflocation,
    update_shelflocation,
)
from db.models.shelfLocation import ShelfLocation


class ShelfLocationValidationError(ValueError):
    """Raised when incoming shelf-location payloads are invalid."""


def shelflocation_to_dictionary(shelflocation: ShelfLocation) -> dict[str, Any]:
    return {
        "id": shelflocation.id,
        "storeId": shelflocation.store_id,
        "aisle": shelflocation.aisle,
        "level": shelflocation.level,
    }


def list_all_shelflocations(db: Session) -> list[dict[str, Any]]:
    return [shelflocation_to_dictionary(item) for item in get_all_shelflocations(db)]


def get_shelflocation_details(db: Session, shelflocation_id: int) -> dict[str, Any] | None:
    shelflocation = get_shelflocation(db, shelflocation_id)
    if shelflocation is None:
        return None
    return shelflocation_to_dictionary(shelflocation)


def create_shelflocation_from_payload(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    shelflocation_data = _validated_shelflocation_fields(payload, partial=False)
    shelflocation = create_shelflocation(db=db, **shelflocation_data)
    return shelflocation_to_dictionary(shelflocation)


def update_shelflocation_from_payload(
    db: Session,
    shelflocation_id: int,
    payload: dict[str, Any],
) -> dict[str, Any] | None:
    shelflocation_data = _validated_shelflocation_fields(payload, partial=True)
    if not shelflocation_data:
        raise ShelfLocationValidationError("At least one updatable field is required.")

    shelflocation = update_shelflocation(db, shelflocation_id, **shelflocation_data)
    if shelflocation is None:
        return None
    return shelflocation_to_dictionary(shelflocation)


def delete_shelflocation_by_id(db: Session, shelflocation_id: int) -> bool:
    return delete_shelflocation(db, shelflocation_id)


def _validated_shelflocation_fields(payload: dict[str, Any], *, partial: bool) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ShelfLocationValidationError("JSON object payload is required.")

    allowed_fields = {"storeId", "aisle", "level"}
    unknown_fields = sorted(set(payload) - allowed_fields)
    if unknown_fields:
        raise ShelfLocationValidationError(f"Unknown field(s): {', '.join(unknown_fields)}")

    data: dict[str, Any] = {}

    if "storeId" in payload:
        data["store_id"] = _validate_positive_int(payload["storeId"], "storeId")
    elif not partial:
        raise ShelfLocationValidationError("Field 'storeId' is required.")

    if "aisle" in payload:
        data["aisle"] = _validate_positive_int(payload["aisle"], "aisle")
    elif not partial:
        raise ShelfLocationValidationError("Field 'aisle' is required.")

    if "level" in payload:
        data["level"] = _validate_positive_int(payload["level"], "level")
    elif not partial:
        raise ShelfLocationValidationError("Field 'level' is required.")

    return data


def _validate_positive_int(value: Any, field_name: str) -> int:
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped.isdigit():
            raise ShelfLocationValidationError(f"Field '{field_name}' must be a positive integer.")
        value = int(stripped)

    if not isinstance(value, int) or isinstance(value, bool):
        raise ShelfLocationValidationError(f"Field '{field_name}' must be a positive integer.")
    if value <= 0:
        raise ShelfLocationValidationError(f"Field '{field_name}' must be a positive integer.")
    return value
