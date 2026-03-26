from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session
from db.crud.product import (
    create_product,
    delete_product,
    get_all_products,
    get_product,
    update_product,
)
from db.models.product import Product


class ProductValidationError(ValueError):
    """Raised when incoming product payloads are invalid."""


def convert_product_obj_to_dict(product: Product) -> dict[str, Any]:
    return {
        "id": product.id,
        "sku": product.sku,
        "name": product.name,
        "attributesJson": product.attributes_json,
        "price": product.price,
    }


def list_all_products(db: Session) -> list[dict[str, Any]]:
    return [convert_product_obj_to_dict(product) for product in get_all_products(db)]


def get_product_details(db: Session, product_id: int) -> dict[str, Any] | None:
    product = get_product(db, product_id)
    if product is None:
        return None
    return convert_product_obj_to_dict(product)


def create_product_from_payload(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    product_data = _validated_product_fields(payload, partial=False)
    product = create_product(db=db, **product_data)
    return convert_product_obj_to_dict(product)


def update_product_from_payload(db: Session, product_id: int, payload: dict[str, Any]) -> dict[str, Any] | None:
    product_data = _validated_product_fields(payload, partial=True)
    if not product_data:
        raise ProductValidationError("At least one updatable field is required.")

    product = update_product(db, product_id, **product_data)
    if product is None:
        return None
    return convert_product_obj_to_dict(product)


def delete_product_by_id(db: Session, product_id: int) -> bool:
    return delete_product(db, product_id)


def _validated_product_fields(payload: dict[str, Any], *, partial: bool) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ProductValidationError("JSON object payload is required.")

    allowed_fields = {"sku", "name", "attributesJson", "price"}
    unknown_fields = sorted(set(payload) - allowed_fields)
    if unknown_fields:
        raise ProductValidationError(f"Unknown field(s): {', '.join(unknown_fields)}")

    data: dict[str, Any] = {}

    if "sku" in payload:
        sku = payload["sku"]
        if not isinstance(sku, str) or not sku.strip():
            raise ProductValidationError("Field 'sku' must be a non-empty string.")
        data["sku"] = sku.strip()
    elif not partial:
        raise ProductValidationError("Field 'sku' is required.")

    if "name" in payload:
        name = payload["name"]
        if not isinstance(name, str) or not name.strip():
            raise ProductValidationError("Field 'name' must be a non-empty string.")
        data["name"] = name.strip()
    elif not partial:
        raise ProductValidationError("Field 'name' is required.")

    if "attributesJson" in payload:
        attributes_json = payload["attributesJson"]
        if not isinstance(attributes_json, dict):
            raise ProductValidationError("Field 'attributesJson' must be an object.")
        data["attributes_json"] = attributes_json
    elif not partial:
        data["attributes_json"] = {}

    if "price" in payload:
        price = payload["price"]
        if not isinstance(price, (int, float)) or isinstance(price, bool):
            raise ProductValidationError("Field 'price' must be a number.")
        if price < 0:
            raise ProductValidationError("Field 'price' must be zero or greater.")
        data["price"] = float(price)
    elif not partial:
        raise ProductValidationError("Field 'price' is required.")

    return data
