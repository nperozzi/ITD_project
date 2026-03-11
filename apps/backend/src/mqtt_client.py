import json
import sys
import paho.mqtt.client as mqtt
from db.crud.crud_tag import update_tag

# MQTT broker connection settings.
BROKER = "mosquitto"
PORT = 1883

db = None
app = None
socketio = None

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)


def set_app(flask_app):
    # Save Flask app instance for later app-context operations.
    global app
    app = flask_app


def set_socketio(sio):
    # Save Socket.IO instance used to push updates to browser clients.
    global socketio
    socketio = sio


def set_db(db_instance):
    # Save database/session provider used for persistence.
    global db
    db = db_instance


def mqtt_client_connect():
    # Register callbacks and open broker connection.
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_start()


# Keep only if team still needs backend-originated price update.
def publish_price(price):
    # Publish price update to backend command topic.
    payload = json.dumps({"price": price})
    topic = "backend/commands/price"
    client.publish(topic, payload, retain=True)


def on_connect(client, userdata, flags, reason_code, properties=None):
    # Called by paho-mqtt after broker connection succeeds.
    print("Backend connected to broker")
    sys.stdout.flush()

    # Subscribe to gateway event topics.
    client.subscribe("gateway/events/tag/+/heard")
    client.subscribe("gateway/events/tag/+/low_battery")
    client.subscribe("gateway/events/tag/+/offline")


def on_message(client, userdata, message):
    # Called whenever a subscribed MQTT message arrives.
    payload = message.payload.decode()
    topic = message.topic

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        print(f"Backend ignored invalid JSON on topic {topic}")
        sys.stdout.flush()
        return

    # Expected topic format:
    # gateway / events / tag / <tag_id> / <event_type>
    parts = topic.split("/")

    if len(parts) != 5:
        return

    if parts[0] != "gateway" or parts[1] != "events" or parts[2] != "tag":
        return

    try:
        tag_id = int(parts[3])
    except ValueError:
        return

    event_type = parts[4]

    if event_type == "heard":
        battery = data.get("battery")
        product_id = data.get("product_id")
        status = data.get("status", "online")

        # Persist latest known tag state using ORM CRUD.
        if db:
            updates = {}

            if battery is not None:
                updates["battery_pct"] = battery
            if product_id is not None:
                updates["product_id"] = product_id
            if status is not None:
                updates["status"] = status

            if updates:
                with db.SessionLocal() as session:
                    update_tag(session, tag_id, **updates)

        # Notify connected frontend clients.
        if app and socketio:
            with app.app_context():
                socketio.emit(
                    "tag_update",
                    {
                        "tag_id": tag_id,
                        "battery": battery,
                        "product_id": product_id,
                        "status": status,
                        "event": "heard",
                    },
                )

    elif event_type == "low_battery":
        battery = data.get("battery")

        # Persist low-battery state.
        if db and battery is not None:
            with db.SessionLocal() as session:
                update_tag(session, tag_id, battery_pct=battery)
            
        # Forward low battery event to the frontend.
        if app and socketio:
            with app.app_context():
                socketio.emit(
                    "tag_update",
                    {
                        "tag_id": tag_id,
                        "battery": battery,
                        "event": "low_battery",
                    },
                )

    elif event_type == "offline":
        # Persist offline state.
        if db:
            with db.SessionLocal() as session:
                update_tag(session, tag_id, status="offline")

        # Forward offline event to the frontend.
        if app and socketio:
            with app.app_context():
                socketio.emit(
                    "tag_update",
                    {
                        "tag_id": tag_id,
                        "event": "offline",
                    },
                )