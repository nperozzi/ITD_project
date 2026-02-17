import json
import sys
import paho.mqtt.client as mqtt
from state import latest_battery

BROKER = "mosquitto"
PORT = 1883

client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

# App and SocketIO instances (will be set by backend.py)
app = None
socketio = None

def set_app_and_socketio(flask_app, sio):
    global app, socketio
    app = flask_app
    socketio = sio

def mqtt_client_connect():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_start()

def publish_price(price):
    payload = json.dumps({"price": price})
    topic = f"b-g/tag1/price"
    client.publish(topic, payload, retain=True)

def on_connect(client, userdata, flags, rc, properties=None): # MQTT_client on_connect callback:
    print("Backend connected to broker")
    sys.stdout.flush()
    client.subscribe("b-g/tag1/battery")

def on_message(client, userdata, message):
    global latest_battery

    payload = message.payload.decode()
    print(f"Received: {message.topic} {payload}")
    sys.stdout.flush()

    # Write to the state file and emit via WebSocket.
    try:
        data = json.loads(payload)
        if "battery" in data:
            import state
            state.latest_battery = data["battery"]
            # Emit battery update to all connected clients
            if app and socketio:
                with app.app_context():
                    socketio.emit("battery_update", {"battery": data["battery"]})
    except (json.JSONDecodeError, KeyError):
        pass
