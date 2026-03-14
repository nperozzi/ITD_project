"""MQTT integration for backend service.

Responsibilities:
- publish price updates to tag path
- subscribe to battery updates from tag path
- store battery in DB and emit Socket.IO events
"""

import json
import random
import sys
import paho.mqtt.client as mqtt
from db.crud.crud_tag import get_tag, update_tag

BROKER = "mosquitto"
PORT = 1883

db = None
app = None
socketio = None

# Single MQTT client instance reused by this module.
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

def set_app(flask_app):
    # Save Flask app instance for later app-context operations.
    global app
    app = flask_app

def set_socketio(sio):
    # Save Socket.IO instance used to push updates to browser clients.
    global socketio
    socketio = sio

def mqtt_client_connect():
    # Register callbacks and open broker connection.
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_start()

def set_db(db_instance):
    # Save database adapter used for persistence.
    global db
    db = db_instance

def set_db(db_instance):
    # Duplicate definition kept for behavior compatibility with existing code.
    global db
    db = db_instance

def publish_price(price):
    # Publish price update to backend->gateway topic namespace.
    payload = json.dumps({"price": price})
    topic = f"b-g/tag1/price"
    client.publish(topic, payload, retain=True)


def publish_tag_payload(tag_id: int, payload_data: dict):
    # Publish a generated tag payload snapshot to the tag topic namespace.
    payload = json.dumps(payload_data)
    topic = f"b-g/tag{tag_id}/payload"
    client.publish(topic, payload, retain=True)

def on_connect(client, userdata, flags, rc, properties=None):
    # Called by paho-mqtt after broker connection succeeds.
    print("Backend connected to broker")
    sys.stdout.flush()
    
    # Listen for battery values coming back from gateway/tag.
    client.subscribe("b-g/tag1/battery")

def on_message(client, userdata, message):
    # Called whenever a subscribed MQTT message arrives.

    payload = message.payload.decode()

    # Parse payload, persist battery level, and push to web clients.
    try:
        data = json.loads(payload)

        if "battery" in data and db:
            # Randomize on backend so UI always depends on backend-provided battery.
            battery = random.randint(1, 100)
            with db.SessionLocal() as session:
                update_tag(session, 1, product_id=1, battery_pct=battery)

                # Read persisted value and emit event through Socket.IO.
                tag = get_tag(session, 1)
                battery = tag.battery_pct if tag else None

            if app and socketio:
                with app.app_context():
                    socketio.emit("battery_update", {"battery": battery})
                    
    except (json.JSONDecodeError, KeyError):
        pass
