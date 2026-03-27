"""Health and system-level backend routes."""

from __future__ import annotations

from flask import current_app, jsonify, request

from db.crud.tag import get_tag

from . import api


@api.route("/")
def index():
    return jsonify({"service": "backend", "status": "ok"})


@api.route("/battery")
def battery():
    tag_id = request.args.get("tagId", type=int)
    if tag_id is None or tag_id <= 0:
        return jsonify({"error": "Query parameter 'tagId' must be a positive integer."}), 400

    db = current_app.config.get("db")
    if db is None:
        raise RuntimeError("Database is not configured for this app.")

    with db.SessionLocal() as session:
        tag = get_tag(session, tag_id)

    if tag is None:
        return jsonify({"error": "Tag not found."}), 404

    return jsonify({"battery": tag.battery_pct})
