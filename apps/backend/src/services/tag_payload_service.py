from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from db.crud.product import get_product, get_tags_for_product
from db.crud.promotion import get_all_promotions
from db.crud.tag import get_tag
from db.crud.tagpayload import (
    create_tagpayload,
    get_all_tagpayloads,
    get_latest_unacknowledged_tagpayload_for_tag,
    update_tagpayload,
)
from db.models.promotion import Promotion
from db.models.tagpayload import TagPayload
from mqtt_client import publish_tag_payload


class TagPayloadError(ValueError):
    """Raised when a tag payload cannot be generated or published."""


def list_all_tagpayloads(db: Session) -> list[dict[str, Any]]:
    return [_convert_tagpayload_to_dict(tagpayload) for tagpayload in get_all_tagpayloads(db)]


def publish_payload_for_tag(db: Session, tag_id: int) -> dict[str, Any]:
    tag = get_tag(db, tag_id)
    if tag is None:
        raise TagPayloadError("Tag not found.")

    payload = build_payload_for_tag(db, tag_id)
    stored_payload = create_tagpayload(db, tag_id=tag_id, payload_json=payload, acknowledged=False)
    publish_tag_payload(tag_id, payload)

    return {
        "status": "published",
        "tagId": tag_id,
        "tagPayloadId": stored_payload.id,
        "payload": payload,
    }


def publish_payloads_for_product(db: Session, product_id: int) -> list[dict[str, Any]]:
    product = get_product(db, product_id)
    if product is None:
        raise TagPayloadError("Product not found.")

    published_payloads: list[dict[str, Any]] = []
    for tag in get_tags_for_product(db, product_id):
        published_payloads.append(publish_payload_for_tag(db, tag.id))

    return published_payloads


def acknowledge_latest_payload_for_tag(db: Session, tag_id: int) -> bool:
    tag = get_tag(db, tag_id)
    if tag is None:
        raise TagPayloadError("Tag not found.")

    tagpayload = get_latest_unacknowledged_tagpayload_for_tag(db, tag_id)
    if tagpayload is None:
        return False

    update_tagpayload(db, tagpayload.id, acknowledged=True)
    return True


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

    return {
        "tagId": tag.id,
        "title": product.name,
        "finalPrice": round(final_price, 2),
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
def _convert_tagpayload_to_dict(tagpayload: TagPayload) -> dict[str, Any]:
    return {
        "id": tagpayload.id,
        "payloadJson": tagpayload.payload_json,
        "acknowledged": tagpayload.acknowledged,
    }
