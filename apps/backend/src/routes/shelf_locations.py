"""Shelf-location API routes."""

from __future__ import annotations

from flask import jsonify, request

from services.shelflocation_service import (
    ShelfLocationValidationError,
    create_shelflocation_from_payload,
    delete_shelflocation_by_id,
    get_shelflocation_details,
    list_all_shelflocations,
    update_shelflocation_from_payload,
)

from . import api
from .shared import session_scope


@api.route("/api/shelf-locations")
def get_all_shelflocations_route():
    with session_scope() as session:
        return jsonify(list_all_shelflocations(session))


@api.route("/api/shelf-locations/<int:shelflocation_id>")
def get_shelflocation_route(shelflocation_id: int):
    with session_scope() as session:
        shelflocation = get_shelflocation_details(session, shelflocation_id)

    if shelflocation is None:
        return jsonify({"error": "Shelf location not found."}), 404

    return jsonify(shelflocation)


@api.route("/api/shelf-locations", methods=["POST"])
def create_shelflocation_route():
    payload = request.get_json(silent=True)
    try:
        with session_scope() as session:
            shelflocation = create_shelflocation_from_payload(session, payload or {})
    except ShelfLocationValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(shelflocation), 201


@api.route("/api/shelf-locations/<int:shelflocation_id>", methods=["PATCH"])
def update_shelflocation_route(shelflocation_id: int):
    payload = request.get_json(silent=True)
    try:
        with session_scope() as session:
            shelflocation = update_shelflocation_from_payload(session, shelflocation_id, payload or {})
    except ShelfLocationValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    if shelflocation is None:
        return jsonify({"error": "Shelf location not found."}), 404

    return jsonify(shelflocation)


@api.route("/api/shelf-locations/<int:shelflocation_id>", methods=["DELETE"])
def delete_shelflocation_route(shelflocation_id: int):
    with session_scope() as session:
        is_deleted = delete_shelflocation_by_id(session, shelflocation_id)

    if not is_deleted:
        return jsonify({"error": "Shelf location not found."}), 404

    return jsonify({"status": "deleted", "id": shelflocation_id})
