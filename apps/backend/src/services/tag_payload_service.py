from __future__ import annotations

from datetime import datetime, UTC
from typing import Any

from sqlalchemy.orm import Session

from db.crud.crud_product import get_product
from db.crud.crud_promotion import get_all_promotions
from db.crud.crud_tag import get_tag
from db.crud.crud_tagpayload import create_tagpayload, get_latest_tagpayload_for_tag
from db.models.promotion import Promotion
from mqtt_client import publish_tag_payload
from services.tag_service import tag_to_dictionary


class TagPayloadError(ValueError):
    """Raised when a tag payload cannot be generated or published."""


def get_debug_payload_for_tag(db: Session, tag_id: int) -> dict[str, Any]:
    tag = get_tag(db, tag_id)
    if tag is None:
        raise TagPayloadError("Tag not found.")

    payload = build_payload_for_tag(db, tag_id)
    stored_payload = get_latest_tagpayload_for_tag(db, tag_id)

    return {
        "tagId": tag_id,
        "payload": payload,
        "storedPayloadId": stored_payload.id if stored_payload else None,
        "storedPayload": stored_payload.payload_json if stored_payload else None,
    }


def publish_payload_for_tag(db: Session, tag_id: int) -> dict[str, Any]:
    tag = get_tag(db, tag_id)
    if tag is None:
        raise TagPayloadError("Tag not found.")

    payload = build_payload_for_tag(db, tag_id)
    stored_payload = create_tagpayload(db, tag_id=tag_id, payload_json=payload)
    publish_tag_payload(tag_id, payload)

    return {
        "status": "published",
        "tagId": tag_id,
        "tagPayloadId": stored_payload.id,
        "payload": payload,
    }


def build_payload_for_tag(db: Session, tag_id: int) -> dict[str, Any]:
    tag = get_tag(db, tag_id)
    if tag is None:
        raise TagPayloadError("Tag not found.")
    if tag.product_id is None:
        raise TagPayloadError("Tag is not assigned to a product.")

    product = get_product(db, tag.product_id)
    if product is None:
        raise TagPayloadError("Product for tag was not found.")

    active_promotion = _get_active_promotion_for_product(db, product.id)
    base_price = float(product.price)
    final_price = _apply_percentage_discount(base_price, active_promotion.discount_percentage) if active_promotion else base_price
    tag_summary = tag_to_dictionary(tag)

    return {
        "tagId": tag.id,
        "productId": product.id,
        "title": product.name,
        "sku": product.sku,
        "basePrice": round(base_price, 2),
        "finalPrice": round(final_price, 2),
        "currency": "EUR",
        "promotion": (
            {
                "type": "percentage",
                "value": active_promotion.discount_percentage,
                "startAt": _convert_datetime_to_str(active_promotion.start_at),
                "endAt": _convert_datetime_to_str(active_promotion.end_at),
            }
            if active_promotion
            else None
        ),
        "tagStatus": tag_summary["status"],
        "batteryPct": tag_summary["batteryPct"],
        "shelfLocationId": tag.shelf_location_id,
        "generatedAt": _convert_datetime_to_str(datetime.now(UTC)),
    }


def _get_active_promotion_for_product(db: Session, product_id: int) -> Promotion | None:
    now = datetime.now(UTC).replace(tzinfo=None)
    promotions = [
        promotion
        for promotion in get_all_promotions(db)
        if promotion.product_id == product_id and promotion.start_at <= now <= promotion.end_at
    ]
    if not promotions:
        return None
    return max(promotions, key=lambda promotion: (promotion.discount_percentage, promotion.id))


def _apply_percentage_discount(price: float, discount_percentage: int) -> float:
    return price * (1 - (discount_percentage / 100))


def _convert_datetime_to_str(value: datetime) -> str:
    if value.tzinfo is not None:
        value = value.astimezone(UTC).replace(tzinfo=None)
    return value.isoformat() + "Z"
