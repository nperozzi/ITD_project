import json
import sys
import paho.mqtt.client as mqtt

BROKER = "mosquitto"
PORT = 1883

db = None
app = None
socketio = None

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

def set_app(flask_app): # App instances (will be set by backend.py with this function)
    global app
    app = flask_app

def set_socketio(sio): # SocketIO instances (will be set by backend.py with this function)
    global socketio
    socketio = sio

def mqtt_client_connect():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_start()

def set_db(db_instance):
    global db
    db = db_instance

def set_db(db_instance):
    global db
    db = db_instance

def publish_price(price):
    payload = json.dumps({"price": price})
    topic = f"b-g/tag1/price"
    client.publish(topic, payload, retain=True)

def on_connect(client, userdata, flags, rc, properties=None): # MQTT_client on_connect callback:
    print("Backend connected to broker")
    sys.stdout.flush()
    
    client.subscribe("b-g/tag1/battery")

def on_message(client, userdata, message):  # MQTT_client on_message callback:

    payload = message.payload.decode()

    # Store battery level in database and emit update from database
    try:
        data = json.loads(payload)

        if "battery" in data and db:
            db.set_tag(1, 1, data["battery"])

            # Fetch battery from database and emit update
            tag = db.get_tag(1)
            battery = tag["battery_level"] if tag else None

            if app and socketio:
                with app.app_context():
                    socketio.emit("battery_update", {"battery": battery})
                    
    except (json.JSONDecodeError, KeyError):
        pass
