from flask import Blueprint, request, jsonify, render_template
import state
from mqtt_client import publish_price

api = Blueprint("api", __name__)

@api.route("/")
def index():
    return render_template("index.html")

@api.route("/set_price", methods=["POST"])
def set_price():
    price = request.form["price"]
    publish_price(price)
    return "OK"

@api.route("/battery")
def battery():
    return jsonify({"battery": state.latest_battery})
