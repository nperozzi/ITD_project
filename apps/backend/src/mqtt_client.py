"""MQTT integration for backend service.

Responsibilities:
- publish price updates to tag path
- subscribe to battery updates from tag path
- store battery in DB and emit Socket.IO events
"""

import json
import random
import re
import sys
import paho.mqtt.client as mqtt
from db.crud.tag import get_tag, update_tag
from db.crud.tagpayload import get_latest_unacknowledged_tagpayload_for_tag, update_tagpayload

BROKER = "mosquitto"
PORT = 1883
ACK_TOPIC_PATTERN = re.compile(r"^g-b/tag(?P<tag_id>\d+)/ack$")

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
    client.subscribe("g-b/+/ack")

def on_message(client, userdata, message):
    # Called whenever a subscribed MQTT message arrives.

    payload = message.payload.decode()

    # Parse payload, persist battery level, and push to web clients.
    try:
        data = json.loads(payload)

        if _is_ack_message(message.topic, data) and db:
            tag_id = _extract_tag_id_from_ack(message.topic, data)
            if tag_id is not None:
                with db.SessionLocal() as session:
                    _acknowledge_latest_payload_for_tag(session, tag_id)
            return

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


def _is_ack_message(topic: str, data: dict) -> bool:
    return bool(ACK_TOPIC_PATTERN.match(topic)) and data.get("ack") is True


def _extract_tag_id_from_ack(topic: str, data: dict) -> int | None:
    payload_tag_id = data.get("tagId")
    if isinstance(payload_tag_id, int) and payload_tag_id > 0:
        return payload_tag_id

    match = ACK_TOPIC_PATTERN.match(topic)
    if not match:
        return None

    return int(match.group("tag_id"))


def _acknowledge_latest_payload_for_tag(session, tag_id: int) -> bool:
    tagpayload = get_latest_unacknowledged_tagpayload_for_tag(session, tag_id)
    if tagpayload is None:
        return False

    update_tagpayload(session, tagpayload.id, acknowledged=True)
    return True
