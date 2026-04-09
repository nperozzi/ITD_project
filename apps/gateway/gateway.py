"""MQTT gateway service.

This component forwards messages between two topic namespaces:
- b-g/* (backend-facing)
- g-t/* (tag-facing)
"""

import time
import sys
import paho.mqtt.client as mqtt

BROKER = "mosquitto"
PORT = 1883

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
    client.subscribe("b-g/tag1/price")
    time.sleep(0.5)
    client.subscribe("g-t/tag1/battery")
    time.sleep(0.5)

def on_message(client, userdata, msg):
    # Translate topic prefixes and republish payload unchanged.
    topic = msg.topic

    if topic.startswith("b-g/tag1/"):
        forward_topic = topic.replace("b-g/", "g-t/", 1)

    elif topic.startswith("g-t/tag1/"):
        forward_topic = topic.replace("g-t/", "b-g/", 1)

    else:
        return  # Ignore unrelated topics.

    print(f"Gateway forwarding: {topic} -> {forward_topic}")
    sys.stdout.flush()
    client.publish(forward_topic, msg.payload)


if __name__ == "__main__":
    main()