"""Temporary demo-backed routes for resources not moved to the database yet."""

from __future__ import annotations

from flask import jsonify

from . import api
from .shared import dashboard_data


@api.route("/api/tag-payloads")
def tag_payloads():
    return jsonify(dashboard_data()["tagPayloads"])


@api.route("/api/promotions")
def promotions():
    return jsonify(dashboard_data()["promotions"])
