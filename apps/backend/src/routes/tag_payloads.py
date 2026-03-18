"""Tag-payload read routes for debugging and compatibility."""

from __future__ import annotations

from flask import jsonify

from services.tag_payload_service import list_all_tagpayloads

from . import api
from .shared import session_scope


@api.route("/api/tag-payloads")
def get_all_tagpayloads_route():
    with session_scope() as session:
        return jsonify(list_all_tagpayloads(session))
