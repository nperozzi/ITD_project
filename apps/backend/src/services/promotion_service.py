from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from db.crud.promotion import (
    create_promotion,
    delete_promotion,
    get_all_promotions,
    get_promotion,
    update_promotion,
)
from db.models.promotion import Promotion


class PromotionValidationError(ValueError):
    """Raised when incoming promotion payloads are invalid."""


DEFAULT_PRIORITY = 1


def promotion_to_dictionary(promotion: Promotion) -> dict[str, Any]:
    return {
        "id": promotion.id,
        "productId": promotion.product_id,
        "promoType": "percentage",
        "value": promotion.discount_percentage,
        "startAt": _serialize_datetime(promotion.start_at),
        "endAt": _serialize_datetime(promotion.end_at),
        "priority": DEFAULT_PRIORITY,
    }


def list_all_promotions(db: Session) -> list[dict[str, Any]]:
    return [promotion_to_dictionary(promotion) for promotion in get_all_promotions(db)]


def get_promotion_details(db: Session, promotion_id: int) -> dict[str, Any] | None:
    promotion = get_promotion(db, promotion_id)
    if promotion is None:
        return None
    return promotion_to_dictionary(promotion)


def create_promotion_from_payload(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    promotion_data = _validated_promotion_fields(payload, partial=False)
    promotion = create_promotion(db=db, **promotion_data)
    return promotion_to_dictionary(promotion)


def update_promotion_from_payload(db: Session, promotion_id: int, payload: dict[str, Any]) -> dict[str, Any] | None:
    promotion_data = _validated_promotion_fields(payload, partial=True)
    if not promotion_data:
        raise PromotionValidationError("At least one updatable field is required.")

    promotion = update_promotion(db, promotion_id, **promotion_data)
    if promotion is None:
        return None
    return promotion_to_dictionary(promotion)


def delete_promotion_by_id(db: Session, promotion_id: int) -> bool:
    return delete_promotion(db, promotion_id)


def _validated_promotion_fields(payload: dict[str, Any], *, partial: bool) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PromotionValidationError("JSON object payload is required.")

    allowed_fields = {"productId", "promoType", "value", "startAt", "endAt", "priority"}
    unknown_fields = sorted(set(payload) - allowed_fields)
    if unknown_fields:
        raise PromotionValidationError(f"Unknown field(s): {', '.join(unknown_fields)}")

    data: dict[str, Any] = {}

    if "productId" in payload:
        data["product_id"] = _validate_optional_int(payload["productId"], "productId")

    if "promoType" in payload:
        promo_type = payload["promoType"]
        if not isinstance(promo_type, str) or promo_type.strip().lower() != "percentage":
            raise PromotionValidationError("Field 'promoType' currently supports only: percentage.")
    elif not partial:
        raise PromotionValidationError("Field 'promoType' is required.")

    if "value" in payload:
        data["discount_percentage"] = _validate_discount_percentage(payload["value"])
    elif not partial:
        raise PromotionValidationError("Field 'value' is required.")

    if "startAt" in payload:
        data["start_at"] = _validate_datetime(payload["startAt"], "startAt")
    elif not partial:
        raise PromotionValidationError("Field 'startAt' is required.")

    if "endAt" in payload:
        data["end_at"] = _validate_datetime(payload["endAt"], "endAt")
    elif not partial:
        raise PromotionValidationError("Field 'endAt' is required.")

    if "priority" in payload:
        priority = payload["priority"]
        if priority != DEFAULT_PRIORITY:
            raise PromotionValidationError("Field 'priority' is not stored yet and must be 1 for now.")

    if "start_at" in data and "end_at" in data and data["end_at"] < data["start_at"]:
        raise PromotionValidationError("Field 'endAt' must be after or equal to 'startAt'.")

    return data


def _validate_optional_int(value: Any, field_name: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise PromotionValidationError(f"Field '{field_name}' must be an integer or null.")
    if value <= 0:
        raise PromotionValidationError(f"Field '{field_name}' must be greater than 0.")
    return value


def _validate_discount_percentage(value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise PromotionValidationError("Field 'value' must be an integer percentage.")
    if not 0 <= value <= 100:
        raise PromotionValidationError("Field 'value' must be between 0 and 100.")
    return value


def _validate_datetime(value: Any, field_name: str) -> datetime:
    if not isinstance(value, str):
        raise PromotionValidationError(f"Field '{field_name}' must be an ISO 8601 string.")
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1]
    try:
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise PromotionValidationError(f"Field '{field_name}' must be an ISO 8601 string.") from exc


def _serialize_datetime(value: datetime) -> str:
    return value.isoformat() + "Z"
