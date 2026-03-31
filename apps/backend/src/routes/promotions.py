"""Promotion API routes."""

from __future__ import annotations

from flask import jsonify, request

from services.promotion_service import (
    PromotionValidationError,
    create_promotion_from_payload,
    delete_promotion_by_id,
    get_promotion_details,
    list_all_promotions,
    update_promotion_from_payload,
)

from . import api
from .shared import session_scope


@api.route("/api/promotions")
def get_all_promotions_route():
    with session_scope() as session:
        return jsonify(list_all_promotions(session))


@api.route("/api/promotions/<int:promotion_id>")
def get_promotion_route(promotion_id: int):
    with session_scope() as session:
        promotion = get_promotion_details(session, promotion_id)

    if promotion is None:
        return jsonify({"error": "Promotion not found."}), 404

    return jsonify(promotion)


@api.route("/api/promotions", methods=["POST"])
def create_promotion_route():
    payload = request.get_json(silent=True)
    try:
        with session_scope() as session:
            promotion = create_promotion_from_payload(session, payload or {})
    except PromotionValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(promotion), 201


@api.route("/api/promotions/<int:promotion_id>", methods=["PATCH"])
def update_promotion_route(promotion_id: int):
    payload = request.get_json(silent=True)
    try:
        with session_scope() as session:
            promotion = update_promotion_from_payload(session, promotion_id, payload or {})
    except PromotionValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    if promotion is None:
        return jsonify({"error": "Promotion not found."}), 404

    return jsonify(promotion)


@api.route("/api/promotions/<int:promotion_id>", methods=["DELETE"])
def delete_promotion_route(promotion_id: int):
    with session_scope() as session:
        is_deleted = delete_promotion_by_id(session, promotion_id)

    if not is_deleted:
        return jsonify({"error": "Promotion not found."}), 404

    return jsonify({"status": "deleted", "id": promotion_id})
