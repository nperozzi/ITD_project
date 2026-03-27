from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from db.crud.product import get_product
from db.crud.tag import create_tag, delete_tag, get_all_tags, get_tag, update_tag
from db.models.tag import Status, Tag
from services.tag_payload_service import publish_payload_for_tag


class TagValidationError(ValueError):
    """Raised when incoming tag payloads are invalid."""


LOW_BATTERY_THRESHOLD = 25


def tag_to_dictionary(tag: Tag) -> dict[str, Any]:
    battery_pct = 0 if tag.battery_pct is None else tag.battery_pct
    return {
        "id": tag.id,
        "batteryPct": battery_pct,
        "status": _convert_status_obj_to_str(tag.status, battery_pct),
        "productId": tag.product_id,
        "shelfLocationId": tag.shelf_location_id,
    }


def list_all_tags(db: Session) -> list[dict[str, Any]]:
    return [tag_to_dictionary(tag) for tag in get_all_tags(db)]


def get_tag_details(db: Session, tag_id: int) -> dict[str, Any] | None:
    tag = get_tag(db, tag_id)
    if tag is None:
        return None
    return tag_to_dictionary(tag)


def create_tag_from_payload(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    tag_data = _validated_tag_fields(payload, partial=False)
    tag = create_tag(db=db, **tag_data)
    _publish_tag_after_assignment(db, previous_product_id=None, tag=tag)
    return tag_to_dictionary(tag)


def update_tag_from_payload(db: Session, tag_id: int, payload: dict[str, Any]) -> dict[str, Any] | None:
    tag_data = _validated_tag_fields(payload, partial=True)
    if not tag_data:
        raise TagValidationError("At least one updatable field is required.")

    existing_tag = get_tag(db, tag_id)
    if existing_tag is None:
        return None
    previous_product_id = existing_tag.product_id

    tag = update_tag(db, tag_id, **tag_data)
    if tag is None:
        return None
    _publish_tag_after_assignment(db, previous_product_id=previous_product_id, tag=tag)
    return tag_to_dictionary(tag)


def delete_tag_by_id(db: Session, tag_id: int) -> bool:
    return delete_tag(db, tag_id)


def _validated_tag_fields(payload: dict[str, Any], *, partial: bool) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise TagValidationError("JSON object payload is required.")

    allowed_fields = {"batteryPct", "status", "productId", "shelfLocationId"}
    unknown_fields = sorted(set(payload) - allowed_fields)
    if unknown_fields:
        raise TagValidationError(f"Unknown field(s): {', '.join(unknown_fields)}")

    data: dict[str, Any] = {}

    if "batteryPct" in payload:
        battery_pct = payload["batteryPct"]
        if battery_pct is not None:
            if not isinstance(battery_pct, int) or isinstance(battery_pct, bool):
                raise TagValidationError("Field 'batteryPct' must be an integer or null.")
            if not 0 <= battery_pct <= 100:
                raise TagValidationError("Field 'batteryPct' must be between 0 and 100.")
        data["battery_pct"] = battery_pct

    if "status" in payload:
        data["status"] = _convert_status_str_to_obj(payload["status"])
    elif not partial:
        raise TagValidationError("Field 'status' is required.")

    if "productId" in payload:
        data["product_id"] = _validate_optional_int(payload["productId"], "productId")

    if "shelfLocationId" in payload:
        data["shelf_location_id"] = _validate_optional_int(payload["shelfLocationId"], "shelfLocationId")

    return data


def _validate_optional_int(value: Any, field_name: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise TagValidationError(f"Field '{field_name}' must be an integer or null.")
    if value <= 0:
        raise TagValidationError(f"Field '{field_name}' must be greater than 0.")
    return value


def _convert_status_str_to_obj(value: Any) -> Status:
    if not isinstance(value, str):
        raise TagValidationError("Field 'status' must be a string.")

    normalized = value.strip().lower()
    if normalized in {"active", "online", "low-battery"}:
        return Status.ONLINE
    if normalized == "offline":
        return Status.OFFLINE
    if normalized == "disabled":
        return Status.DISABLED

    raise TagValidationError("Field 'status' must be one of: active, low-battery, offline, disabled.")


def _convert_status_obj_to_str(status: Status, battery_pct: int) -> str:
    if status in {Status.OFFLINE, Status.DISABLED}:
        return "offline"
    if battery_pct < LOW_BATTERY_THRESHOLD:
        return "low-battery"
    return "active"


def _publish_tag_after_assignment(db: Session, *, previous_product_id: int | None, tag: Tag) -> None:
    if tag.product_id is None:
        return
    if tag.product_id == previous_product_id:
        return
    if get_product(db, tag.product_id) is None:
        return
    publish_payload_for_tag(db, tag.id)
