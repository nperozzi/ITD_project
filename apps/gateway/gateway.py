import asyncio
import json
import os
import re
import sys
import threading
import time

import paho.mqtt.client as mqtt
from ble_adapter import BleTagAdapter, TAG1, TAG2

BROKER = os.getenv("MQTT_BROKER", "mosquitto")
PORT = int(os.getenv("MQTT_PORT", "1883"))
GATEWAY_MODE = os.getenv("GATEWAY_MODE", "mqtt")

PAYLOAD_TOPIC_PATTERN = re.compile(r"^tag/(?P<tag_id>\d+)/payload$")
TAG_CONTRACTS = {
    1: TAG1,
    2: TAG2,
}

is_connected = False
mqtt_client = None
event_loop = None

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
    is_connected = True
    print("- Gateway connected to Backend")

    mqtt_client.subscribe("tag/+/payload")
    time.sleep(0.5)

def on_message(mqtt_client, userdata, msg):
    print("- Payload from Backend received")
    payload_text = msg.payload.decode()
    asyncio.run_coroutine_threadsafe(
        _handle_incoming_message(msg.topic, payload_text),
        event_loop,
    )
    
async def _handle_incoming_message(topic: str, payload_text: str) -> None:
    match = PAYLOAD_TOPIC_PATTERN.match(topic)
    if match is None:
        return

    await _handle_tag_payload(int(match.group("tag_id")), payload_text)

async def _handle_tag_payload(topic_tag_id: int, payload_text: str) -> None:
    payload = json.loads(payload_text)
    tag_id = int(payload["tagId"])
    if tag_id != topic_tag_id:
        print(f"- Skipping payload mismatch for topic tag {topic_tag_id} and payload tag {tag_id}")
        return

    contract = _get_tag_contract(tag_id)
    if contract is None:
        print(f"- Skipping payload for unsupported tag {tag_id}")
        return

    if not contract.mac_address:
        print(f"- Skipping payload for {contract.name}; MAC address is not configured")
        return

    ble_adapter = BleTagAdapter(contract)
    await ble_adapter.connect()

    try:
        await ble_adapter.send_payload(payload_text)
        await asyncio.sleep(0.1)
        print(f"- Parsed payload for {contract.name}: {payload}")

        ack = await ble_adapter.wait_for_ack()
        print(f"- Payload ACK received from {contract.name}: {ack}")
    finally:
        await ble_adapter.disconnect()

    ack_topic = f"tag/{tag_id}/ack"
    ack_json_payload = _convert_to_ack_payload(tag_id, ack, contract)

    mqtt_client.publish(ack_topic, ack_json_payload)
    print("- ACK sent to backend")

def _convert_to_ack_payload(tag_id: int, ack: str, contract) -> str:
    ack_payload = {
        "tagId": int(tag_id),
        "ack": ack == contract.expected_ack
    }
    return json.dumps(ack_payload)

async def run_ble_test():
    tag_id = int(os.getenv("BLE_TEST_TAG_ID", "1"))
    contract = _get_tag_contract(tag_id)
    if contract is None:
        print(f"Unsupported BLE test tag: {tag_id}")
        return
    if not contract.mac_address:
        print(f"{contract.name} is not configured with a MAC address")
        return

    ble_adapter = BleTagAdapter(contract)
    await ble_adapter.connect()

    try:
        test_payload = json.dumps({"tagId": tag_id, "title": "Bread", "finalPrice": "10.0"})
        await ble_adapter.send_payload(test_payload)

        ack = await ble_adapter.wait_for_ack()
        if ack == contract.expected_ack:
            print(f"{contract.name} acknowledged successfully")
        else:
            print(f"Unexpected ack from {contract.name}: {ack}")
    finally:
        await ble_adapter.disconnect()

async def run_mqtt_gateway():
    mqtt_thread = threading.Thread(target=mqtt_init, daemon=True)
    mqtt_thread.start()

    while True:
        await asyncio.sleep(1)

def _get_tag_contract(tag_id: int):
    return TAG_CONTRACTS.get(tag_id)

if __name__ == "__main__":
    asyncio.run(main())
