"""Gateway API routes."""

from __future__ import annotations

from flask import jsonify, request

from services.gateway_service import (
    GatewayValidationError,
    create_gateway_from_payload,
    delete_gateway_by_id,
    get_gateway_details,
    list_all_gateways,
    update_gateway_from_payload,
)

from . import api
from .shared import session_scope


@api.route("/api/gateways")
def get_all_gateways_route():
    with session_scope() as session:
        return jsonify(list_all_gateways(session))


@api.route("/api/gateways/<int:gateway_id>")
def get_gateway_route(gateway_id: int):
    with session_scope() as session:
        gateway = get_gateway_details(session, gateway_id)

    if gateway is None:
        return jsonify({"error": "Gateway not found."}), 404

    return jsonify(gateway)


@api.route("/api/gateways", methods=["POST"])
def create_gateway_route():
    payload = request.get_json(silent=True)
    try:
        with session_scope() as session:
            gateway = create_gateway_from_payload(session, payload or {})
    except GatewayValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(gateway), 201


@api.route("/api/gateways/<int:gateway_id>", methods=["PATCH"])
def update_gateway_route(gateway_id: int):
    payload = request.get_json(silent=True)
    try:
        with session_scope() as session:
            gateway = update_gateway_from_payload(session, gateway_id, payload or {})
    except GatewayValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    if gateway is None:
        return jsonify({"error": "Gateway not found."}), 404

    return jsonify(gateway)


@api.route("/api/gateways/<int:gateway_id>", methods=["DELETE"])
def delete_gateway_route(gateway_id: int):
    with session_scope() as session:
        is_deleted = delete_gateway_by_id(session, gateway_id)

    if not is_deleted:
        return jsonify({"error": "Gateway not found."}), 404

    return jsonify({"status": "deleted", "id": gateway_id})
