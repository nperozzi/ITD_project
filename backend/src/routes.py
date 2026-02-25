from flask import Blueprint, request, jsonify, render_template, current_app
from mqtt_client import publish_price

api = Blueprint("api", __name__)

@api.route("/")
def index():
    return render_template("index.html")

@api.route("/set_price", methods=["POST"])
def set_price():
    price = request.form["price"]
    db = current_app.config.get('db')
    if db:
        db.set_product_price(1, price)
    publish_price(price)
    return "OK"

@api.route("/battery")
def battery():
    db = current_app.config.get('db')
    tag = db.get_tag(1) if db else None
    battery = tag["battery_level"] if tag else None
    return jsonify({"battery": battery})
