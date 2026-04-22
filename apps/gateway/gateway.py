"""MQTT gateway service.

This component forwards messages between backend and tag topics.
"""
import os
import time
import sys
import json
import re
import paho.mqtt.client as mqtt

BROKER = os.getenv("MQTT_BROKER", "mosquitto")
PORT = int(os.getenv("MQTT_PORT", "1883"))
PAYLOAD_TOPIC_PATTERN = re.compile(r"^tag(?P<tag_id>\d+)/payload$")

is_connected = False

def main():
    # Create MQTT client and register callbacks.
    global is_connected
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, 60)
    
    client.loop_start()

    # Wait for broker connection before entering idle loop.
    while not is_connected:
        time.sleep(0.1)

    # Keep process alive while callbacks do the work.
    while True:
        time.sleep(1)


def on_connect(client, userdata, flags, rc, properties=None):
    # Subscribe to both directions that this gateway forwards.
    global is_connected
    print("Gateway connected")
    sys.stdout.flush()
    is_connected = True
    client.subscribe("tag/+/payload")
    time.sleep(0.5)

def on_message(client, userdata, msg):
    payload_text = msg.payload.decode()
    print(f"Topic: {msg.topic}")
    print(f"Payload: {payload_text}")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
