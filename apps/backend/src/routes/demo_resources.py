"""Temporary demo-backed routes for resources not moved to the database yet."""

from __future__ import annotations

from flask import jsonify

from . import api
from .shared import dashboard_data


@api.route("/api/stores")
def stores():
    return jsonify(dashboard_data()["stores"])


@api.route("/api/gateways")
def gateways():
    return jsonify(dashboard_data()["gateways"])


@api.route("/api/shelf-locations")
def shelf_locations():
    return jsonify(dashboard_data()["shelfLocations"])


@api.route("/api/tag-payloads")
def tag_payloads():
    return jsonify(dashboard_data()["tagPayloads"])


@api.route("/api/promotions")
def promotions():
    return jsonify(dashboard_data()["promotions"])
