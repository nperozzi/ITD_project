"""MQTT integration for backend service.

Responsibilities:
- subscribe to advertisement updates from tag path
- store battery in DB and emit Socket.IO events
"""

import json
import re
import sys
import paho.mqtt.client as mqtt
from db.crud.tag import update_tag
from db.crud.tagpayload import get_latest_unacknowledged_tagpayload_for_tag, update_tagpayload

BROKER = "mosquitto"
PORT = 1883
ACK_TOPIC_PATTERN = re.compile(r"^tag/(?P<tag_id>\d+)/ack$")
ADVERTISEMENT_TOPIC_PATTERN = re.compile(r"^tag/(?P<tag_id>\d+)/advertisement$")

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

def publish_tag_payload(tag_id: int, payload_data: dict):
    # Publish a generated tag payload snapshot to the tag topic namespace.
    payload = json.dumps(payload_data)
    topic = f"tag/{tag_id}/payload"
    client.publish(topic, payload, retain=True)

def on_connect(client, userdata, flags, rc, properties=None):
    # Called by paho-mqtt after broker connection succeeds.
    print("Backend connected to broker")
    sys.stdout.flush()
    
    # Listen for advertisement payloads coming back from gateway/tag.
    client.subscribe("tag/+/advertisement")
    client.subscribe("tag/+/ack")

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

        if _is_advertisement_message(message.topic, data) and db:
            tag_id = _extract_tag_id_from_advertisement_topic(message.topic)
            battery = _extract_battery_value(data)
            if tag_id is None or battery is None:
                return

            with db.SessionLocal() as session:
                tag = update_tag(session, tag_id, battery_pct=battery)
                if tag is None:
                    return
                from services.tag_service import tag_to_dictionary

                tag_summary = tag_to_dictionary(tag)

            if app and socketio:
                with app.app_context():
                    socketio.emit(
                        "battery_update",
                        {
                            "tagId": tag_summary["id"],
                            "batteryPct": tag_summary["batteryPct"],
                            "status": tag_summary["status"],
                        },
                    )
                    
    except (json.JSONDecodeError, KeyError):
        pass


def _is_ack_message(topic: str, data: dict) -> bool:
    return bool(ACK_TOPIC_PATTERN.match(topic)) and data.get("ack") is True


def _is_advertisement_message(topic: str, data: dict) -> bool:
    return bool(ADVERTISEMENT_TOPIC_PATTERN.match(topic)) and "battery" in data


def _extract_tag_id_from_ack(topic: str, data: dict) -> int | None:
    payload_tag_id = data.get("tagId")
    if isinstance(payload_tag_id, int) and payload_tag_id > 0:
        return payload_tag_id
    return None


def _extract_tag_id_from_advertisement_topic(topic: str) -> int | None:
    match = ADVERTISEMENT_TOPIC_PATTERN.match(topic)
    if not match:
        return None
    return int(match.group("tag_id"))


def _extract_battery_value(data: dict) -> int | None:
    raw_battery = data.get("battery")
    if isinstance(raw_battery, bool):
        return None
    if isinstance(raw_battery, int):
        battery = raw_battery
    elif isinstance(raw_battery, float) and raw_battery.is_integer():
        battery = int(raw_battery)
    else:
        return None

    if not 0 <= battery <= 100:
        return None

    return battery


def _acknowledge_latest_payload_for_tag(session, tag_id: int) -> bool:
    tagpayload = get_latest_unacknowledged_tagpayload_for_tag(session, tag_id)
    if tagpayload is None:
        return False

    update_tagpayload(session, tagpayload.id, acknowledged=True)
    return True
