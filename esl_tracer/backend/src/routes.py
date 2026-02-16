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

# SocketIO event handlers
from flask_socketio import emit
from backend import socketio

@socketio.on("connect")
def handle_connect():
    print(f"Client connected")
    # Send current battery value to the newly connected client
    emit("battery_update", {"battery": state.latest_battery})

@socketio.on("disconnect")
def handle_disconnect():
    print(f"Client disconnected")
