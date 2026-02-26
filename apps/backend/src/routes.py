"""HTTP routes for browser UI and API endpoints."""

from flask import Blueprint, request, jsonify, render_template, current_app
from mqtt_client import publish_price

# Blueprint keeps route registration organized.
api = Blueprint("api", __name__)

@api.route("/")
def index():
    # Serve simple HTML control page.
    return render_template("index.html")

@api.route("/set_price", methods=["POST"])
def set_price():
    # Receive new price from form submission.
    price = request.form["price"]

    # Persist current product price.
    db = current_app.config.get('db')
    if db:
        db.set_product_price(1, price)

    # Broadcast price update through MQTT.
    publish_price(price)
    return "OK"

@api.route("/battery")
def battery():
    # Return latest known battery as JSON.
    db = current_app.config.get('db')
    tag = db.get_tag(1) if db else None
    battery = tag["battery_level"] if tag else None
    return jsonify({"battery": battery})
