"""Tag API routes."""

from __future__ import annotations

from flask import jsonify, request

from services.tag_service import (
    TagValidationError,
    create_tag_from_payload,
    delete_tag_by_id,
    get_tag_details,
    list_all_tags,
    update_tag_from_payload,
)

from . import api
from .shared import session_scope


@api.route("/api/tags")
def get_all_tags_route():
    with session_scope() as session:
        return jsonify(list_all_tags(session))


@api.route("/api/tags/<int:tag_id>")
def get_tag_route(tag_id: int):
    with session_scope() as session:
        tag = get_tag_details(session, tag_id)

    if tag is None:
        return jsonify({"error": "Tag not found."}), 404

    return jsonify(tag)


@api.route("/api/tags", methods=["POST"])
def create_tag_route():
    payload = request.get_json(silent=True)
    try:
        with session_scope() as session:
            tag = create_tag_from_payload(session, payload or {})
    except TagValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(tag), 201


@api.route("/api/tags/<int:tag_id>", methods=["PATCH"])
def update_tag_route(tag_id: int):
    payload = request.get_json(silent=True)
    try:
        with session_scope() as session:
            tag = update_tag_from_payload(session, tag_id, payload or {})
    except TagValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    if tag is None:
        return jsonify({"error": "Tag not found."}), 404

    return jsonify(tag)


@api.route("/api/tags/<int:tag_id>", methods=["DELETE"])
def delete_tag_route(tag_id: int):
    with session_scope() as session:
        is_deleted = delete_tag_by_id(session, tag_id)

    if not is_deleted:
        return jsonify({"error": "Tag not found."}), 404

    return jsonify({"status": "deleted", "id": tag_id})
