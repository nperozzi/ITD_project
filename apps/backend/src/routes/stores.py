"""Store API routes."""

from __future__ import annotations

from flask import jsonify, request

from services.store_service import (
    StoreValidationError,
    create_store_from_payload,
    delete_store_by_id,
    get_store_details,
    list_all_stores,
    update_store_from_payload,
)

from . import api
from .shared import session_scope


@api.route("/api/stores")
def get_all_stores_route():
    with session_scope() as session:
        return jsonify(list_all_stores(session))


@api.route("/api/stores/<int:store_id>")
def get_store_route(store_id: int):
    with session_scope() as session:
        store = get_store_details(session, store_id)

    if store is None:
        return jsonify({"error": "Store not found."}), 404

    return jsonify(store)


@api.route("/api/stores", methods=["POST"])
def create_store_route():
    payload = request.get_json(silent=True)
    try:
        with session_scope() as session:
            store = create_store_from_payload(session, payload or {})
    except StoreValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(store), 201


@api.route("/api/stores/<int:store_id>", methods=["PATCH"])
def update_store_route(store_id: int):
    payload = request.get_json(silent=True)
    try:
        with session_scope() as session:
            store = update_store_from_payload(session, store_id, payload or {})
    except StoreValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    if store is None:
        return jsonify({"error": "Store not found."}), 404

    return jsonify(store)


@api.route("/api/stores/<int:store_id>", methods=["DELETE"])
def delete_store_route(store_id: int):
    with session_scope() as session:
        is_deleted = delete_store_by_id(session, store_id)

    if not is_deleted:
        return jsonify({"error": "Store not found."}), 404

    return jsonify({"status": "deleted", "id": store_id})
