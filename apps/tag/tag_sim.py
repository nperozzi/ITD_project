"""Tag simulator service.

Simulates an electronic shelf label device by:
- receiving price updates
- printing displayed price
- publishing a battery level message
"""

import time
import json
import sys
import paho.mqtt.client as mqtt

BROKER = "mosquitto"
PORT = 1883


def main():
    # Connect client and run forever to handle MQTT callbacks.
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, 1883, 60)
    client.loop_forever()



def on_connect(client, userdata, flags, rc, properties=None):
    # Subscribe for incoming price updates from gateway.
    print("Tag connected")
    sys.stdout.flush()
    client.subscribe("g-t/tag1/price")
    time.sleep(0.5)

def on_message(client, userdata, msg):
    # Decode incoming price payload and display it.
    data = json.loads(msg.payload.decode())
    print(f"Tag display updated: {data['price']}")
    sys.stdout.flush()

    # Publish a fixed battery value to simulate telemetry.
    client.publish("g-t/tag1/battery", json.dumps({"battery": 95}), retain=True)


if __name__ == "__main__":
    main()