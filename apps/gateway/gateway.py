import asyncio
import json
import os
import re
import sys
import threading
import time

import paho.mqtt.client as mqtt
from ble_adapter import BleTagAdapter, TAG1

BROKER = os.getenv("MQTT_BROKER", "mosquitto")
PORT = int(os.getenv("MQTT_PORT", "1883"))
GATEWAY_MODE = os.getenv("GATEWAY_MODE", "mqtt")

PAYLOAD_TOPIC_PATTERN = re.compile(r"^tag(?P<tag_id>\d+)/payload$")

is_connected = False
mqtt_client = None
event_loop = None
ble_adapter = BleTagAdapter(TAG1)

async def main():
    global event_loop
    event_loop = asyncio.get_running_loop()

    if GATEWAY_MODE == "ble-test":
        await run_ble_test()
    else:
        await run_mqtt_gateway()

def mqtt_init():
    global is_connected, mqtt_client
    mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(BROKER, PORT, 60)
    mqtt_client.loop_start()

    while not is_connected:
        time.sleep(0.1)

    while True:
        time.sleep(1)

def on_connect(mqtt_client, userdata, flags, rc, properties=None):
    global is_connected
    print("Gateway connected")
    is_connected = True
    mqtt_client.subscribe("tag/+/payload")
    time.sleep(0.5)

def on_message(mqtt_client, userdata, msg):
    payload_text = msg.payload.decode()
    asyncio.run_coroutine_threadsafe(
        _handle_incoming_message(msg.topic, payload_text),
        event_loop,
    )
    
async def _handle_incoming_message(topic: str, payload_text: str) -> None:
    if topic.startswith("tag/") and topic.endswith("/payload"):
        await _handle_tag_payload(topic, payload_text)

async def _handle_tag_payload(topic: str, payload_text: str) -> None:
    payload = json.loads(payload_text)
    await ble_adapter.send_payload(payload_text)
    await asyncio.sleep(0.1)
    print(f"- Parsed payload: {payload}")

    ack = await ble_adapter.wait_for_ack()
    print(f"- Payload ACK received: {ack}")

    tag_id = int(payload["tagId"])
    ack_topic = f"tag/{tag_id}/ack"
    ack_json_payload = _convert_to_ack_payload(tag_id, ack)

    mqtt_client.publish(ack_topic, ack_json_payload)
    print("- ACK sent to backend")

def _convert_to_ack_payload(tag_id: int, ack: str) -> str:
    ack_payload = {
        "tagId": int(tag_id),
        "ack": ack == TAG1.expected_ack
    }
    return json.dumps(ack_payload)

async def run_ble_test():
    await ble_adapter.connect()

    test_payload = '{"tagId": "1", "title": "Bread", "finalPrice": "10.0"}'
    await ble_adapter.send_payload(test_payload)

    ack = await ble_adapter.wait_for_ack()
    if ack == TAG1.expected_ack:
        print("Tag acknowledged successfully")
    else:
        print(f"Unexpected ack: {ack}")

    await ble_adapter.disconnect()

async def run_mqtt_gateway():
    await ble_adapter.connect()
    mqtt_thread = threading.Thread(target=mqtt_init, daemon=True)
    mqtt_thread.start()

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
