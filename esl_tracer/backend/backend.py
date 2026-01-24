import time
import json
import sys
import paho.mqtt.client as mqtt

BROKER = "mosquitto"
PORT = 1883

is_connected = False

def main():
    global is_connected

    # Create the MQTT client and assigne callbacks
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    # Start the connection
    client.connect(BROKER, PORT, 60)
    client.loop_start()             # Starts the background thread for the network
    
    while not is_connected:
        time.sleep(0.1)
    time.sleep(0.5)

    # Repeatedly publish so the message reaches gateway/tag
    while True:
        payload = json.dumps({"price": "19.90"})
        print("Backend publishing update")
        sys.stdout.flush()
        client.publish("b-g/tag/123/update", payload, retain=True)    # Arg1: MQTT topic, Arg3: Just to hold the message until
                                                                    # the other containers are established.
        time.sleep(5)


# Callback on connect
def on_connect(client, userdata, flags, rc, properties=None):
    global is_connected
    print("Backend connected")
    sys.stdout.flush()
    is_connected = True
    client.subscribe("b-g/+/+/status")        # Subscribes to all topics that follow this pattern. '+' is a wildcard.

# Calledback whenever a message arrives on a subscribed topic
def on_message(client, userdata, message):
    print(f"Backend received status: {message.topic} {message.payload.decode()}")
    sys.stdout.flush()


if __name__ == "__main__":
    main()