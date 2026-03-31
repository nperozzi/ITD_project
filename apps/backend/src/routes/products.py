"""Product API routes."""

from __future__ import annotations

from flask import jsonify, request
from services.product_service import (
    ProductValidationError,
    create_product_from_payload,
    delete_product_by_id,
    get_product_details,
    list_all_products,
    update_product_from_payload,
)
from . import api
from .shared import session_scope


@api.route("/api/products")
def get_all_products_route():
    with session_scope() as session:
        return jsonify(list_all_products(session))


@api.route("/api/products/<int:product_id>")
def get_product_route(product_id: int):
    with session_scope() as session:
        product = get_product_details(session, product_id)

    if product is None:
        return jsonify({"error": "Product not found."}), 404

    return jsonify(product)


@api.route("/api/products", methods=["POST"])
def create_product_route():
    payload = request.get_json(silent=True)
    try:
        with session_scope() as session:
            product = create_product_from_payload(session, payload or {})
    except ProductValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(product), 201


@api.route("/api/products/<int:product_id>", methods=["PATCH"])
def update_product_route(product_id: int):
    payload = request.get_json(silent=True)
    try:
        with session_scope() as session:
            product = update_product_from_payload(session, product_id, payload or {})
    except ProductValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    if product is None:
        return jsonify({"error": "Product not found."}), 404

    return jsonify(product)


@api.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product_route(product_id: int):
    with session_scope() as session:
        is_deleted = delete_product_by_id(session, product_id)

    if not is_deleted:
        return jsonify({"error": "Product not found."}), 404

    return jsonify({"status": "deleted", "id": product_id})
