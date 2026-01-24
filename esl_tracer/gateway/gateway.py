import time
import sys
import paho.mqtt.client as mqtt

BROKER = "mosquitto"
PORT = 1883

is_connected = False

def main():
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
    global is_connected
    print("Gateway connected")
    sys.stdout.flush()
    is_connected = True
    client.subscribe("b-g/tag/+/update")
    time.sleep(0.5)
    client.subscribe("g-t/tag/+/status")
    time.sleep(0.5)

def on_message(client, userdata, msg):
    topic = msg.topic

    if topic.startswith("b-g/tag/") and topic.endswith("/update"):
        forward_topic = topic.replace("b-g/", "g-t/", 1)

    elif topic.startswith("g-t/tag/") and topic.endswith("/status"):
        forward_topic = topic.replace("g-t/", "b-g/", 1)

    else:
        return  # ignore anything else

    print(f"Gateway forwarding: {topic} -> {forward_topic}")
    sys.stdout.flush()
    client.publish(forward_topic, msg.payload)




if __name__ == "__main__":
    main()