import sys
import json

class MQTTPublisher:
    """
    Small helper class used to publish JSON messages to MQTT.
    """

    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client

    def publish(self, topic, payload_dict):
        """
        Convert a Python dictionary to JSON and publish it.
        """
        payload_json = json.dumps(payload_dict)
        self.mqtt_client.publish(topic, payload_json)
        print(f"Gateway published -> topic={topic} payload={payload_json}")
        sys.stdout.flush()