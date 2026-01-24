import time
import json
import sys
import paho.mqtt.client as mqtt

BROKER = "mosquitto"
PORT = 1883


def main():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, 1883, 60)
    client.loop_forever()



def on_connect(client, userdata, flags, rc, properties=None):
    print("Tag connected")
    sys.stdout.flush()
    client.subscribe("g-t/tag/123/update")
    time.sleep(0.5)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    print(f"Tag display updated: {data['price']}")
    sys.stdout.flush()
    client.publish("g-t/tag/123/status", json.dumps({"battery": 95}), retain=True)


if __name__ == "__main__":
    main()