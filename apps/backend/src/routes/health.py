"""Health and system-level backend routes."""

from __future__ import annotations

import random

from flask import current_app, jsonify, request

from db.crud.crud_product import update_product
from db.crud.crud_tag import update_tag
from mqtt_client import publish_price

from . import api


@api.route("/")
def index():
    return jsonify({"service": "backend", "status": "ok"})


@api.route("/set_price", methods=["POST"])
def set_price():
    price = request.form["price"]

    db = current_app.config.get("db")
    if db:
        with db.SessionLocal() as session:
            update_product(session, 1, price=float(price))

    publish_price(price)
    return "OK"


@api.route("/battery")
def battery():
    battery_value = random.randint(1, 100)

    db = current_app.config.get("db")
    if db:
        with db.SessionLocal() as session:
            update_tag(session, 1, product_id=1, battery_pct=battery_value)

    return jsonify({"battery": battery_value})
