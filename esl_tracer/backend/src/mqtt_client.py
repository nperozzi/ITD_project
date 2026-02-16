import json
import sys
import paho.mqtt.client as mqtt
from state import latest_battery

BROKER = "mosquitto"
PORT = 1883

client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

def on_connect(client, userdata, flags, rc, properties=None):
    print("Backend connected to broker")
    sys.stdout.flush()
    client.subscribe("b-g/tag1/battery")

def on_message(client, userdata, message):
    global latest_battery

    payload = message.payload.decode()
    print(f"Received: {message.topic} {payload}")
    sys.stdout.flush()

    # Write to the state file.
    try:
        data = json.loads(payload)
        if "battery" in data:
            import state
            state.latest_battery = data["battery"]
    except (json.JSONDecodeError, KeyError):
        pass

def start():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_start()

def publish_price(price):
    payload = json.dumps({"price": price})
    topic = f"b-g/tag1/price"
    client.publish(topic, payload, retain=True)
