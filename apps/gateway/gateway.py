import json
import os
#import random
import sys
import threading
import time

import paho.mqtt.client as mqtt

#Our classes imported here.
from gatewaycore import GatewayCore
from mqttpublisher import MQTTPublisher


# MQTT broker host and port.
# These come from environment variables if provided, otherwise defaults are used.
BROKER = os.getenv("BROKER", "mosquitto")
PORT = int(os.getenv("PORT", "1883"))

# Topic where simulated tag packets arrive.
INPUT_TOPIC = os.getenv("INPUT_TOPIC", "tags/packets")

# How often the gateway checks for offline/low battery alerts.
CHECK_INTERVAL = float(os.getenv("CHECK_INTERVAL", "2.0"))

# Battery level at or below this value triggers a low battery alert.
LOW_BATTERY_THRESHOLD = int(os.getenv("LOW_BATTERY_THRESHOLD", "20"))

# Time in seconds before a tag is considered offline.
OFFLINE_TIMEOUT_SECONDS = float(os.getenv("OFFLINE_TIMEOUT_SECONDS", "5.0"))

# Known tag IDs, read from environment like "1,2,3".
KNOWN_TAGS_ENV = os.getenv("KNOWN_TAGS", "1,2,3")
KNOWN_TAGS = [int(value.strip()) for value in KNOWN_TAGS_ENV.split(",") if value.strip()]


# Create the main gateway core object.
gateway_core = GatewayCore(known_tags=KNOWN_TAGS)

# A shared round counter used to label events over time.
current_round = 0

# Lock protects current_round because it is accessed from different threads.
current_round_lock = threading.Lock()

# Will later hold an MQTTPublisher instance.
publisher = None


def on_connect(client, userdata, flags, reason_code, properties=None):
    """
    MQTT callback fired when gateway connects to broker.
    """
    print("Gateway connected")
    print(f"Gateway subscribing to: {INPUT_TOPIC}")
    sys.stdout.flush()
    client.subscribe(INPUT_TOPIC)


def on_message(client, userdata, msg):
    """
    MQTT callback fired whenever a packet arrives on the subscribed topic.
    """
    global current_round

    try:
        packet = json.loads(msg.payload.decode("utf-8"))
    except json.JSONDecodeError:
        print(f"Gateway rejected payload: invalid JSON on topic {msg.topic}")
        sys.stdout.flush()
        return

    # Read the current round safely.
    with current_round_lock:
        round_number = current_round

    # Let GatewayCore process the packet.
    events = gateway_core.process_packet(packet, round_number)

    # Publish any resulting events.
    for event in events:
        gateway_core.handle_event(event, publisher)


def alert_loop():
    """
    Background loop that periodically checks for:
    - offline tags
    - low battery tags
    """
    global current_round

    while True:
        time.sleep(CHECK_INTERVAL)

        # Increase the round number safely.
        with current_round_lock:
            current_round += 1
            round_number = current_round

        # Check for alerts.
        alert_events = gateway_core.check_alerts(
            current_round=round_number,
            offline_timeout_seconds=OFFLINE_TIMEOUT_SECONDS,
            low_battery_threshold=LOW_BATTERY_THRESHOLD
        )

        # Publish generated alert events.
        for event in alert_events:
            gateway_core.handle_event(event, publisher)


def main():
    """
    Program entry point.
    Sets up MQTT client, starts background alert loop,
    and keeps the process alive.
    """
    global publisher

    # Create MQTT client using callback API version 2.
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

    # Register MQTT callback functions.
    client.on_connect = on_connect
    client.on_message = on_message

    # Create publisher helper.
    publisher = MQTTPublisher(client)

    # Connect to MQTT broker.
    client.connect(BROKER, PORT, 60)

    # Start MQTT networking loop in background.
    client.loop_start()

    # Start background thread for periodic alert checks.
    thread = threading.Thread(target=alert_loop, daemon=True)
    thread.start()

    try:
        # Keep main thread alive.
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Gateway stopped")
        sys.stdout.flush()
    finally:
        # Clean shutdown of MQTT client.
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()