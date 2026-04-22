"""MQTT gateway service.

This component forwards messages between backend and tag topics.
"""
import os
import time
import sys
import json
import re
import paho.mqtt.client as mqtt
from ble_adapter import BleTagAdapter, TAG1
import asyncio

BROKER = os.getenv("MQTT_BROKER", "mosquitto")
PORT = int(os.getenv("MQTT_PORT", "1883"))
PAYLOAD_TOPIC_PATTERN = re.compile(r"^tag(?P<tag_id>\d+)/payload$")

is_connected = False

async def main():
    # mqtt_init()
    adapter = BleTagAdapter(TAG1)
    await adapter.connect()
    await asyncio.sleep(5)
    await adapter.disconnect()

def mqtt_init():
    global is_connected
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_start()

    while not is_connected:
        time.sleep(0.1)

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
    _handle_incoming_message(msg.topic, payload_text)
    
def _handle_incoming_message(topic: str, payload_text: str) -> None:
    if topic.startswith("tag/") and topic.endswith("/payload"):
        _handle_tag_payload(topic, payload_text)

def _handle_tag_payload(topic: str, payload_text: str) -> None:
    payload = json.loads(payload_text)
    print(f"Parsed payload: {payload}")
    sys.stdout.flush()
    pass

if __name__ == "__main__":
    asyncio.run(main())
