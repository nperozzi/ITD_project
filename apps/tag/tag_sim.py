"""Tag simulator service.

Simulates an electronic shelf label device by:
- receiving price updates
- printing displayed price
- publishing a battery level message
"""

import time
import json
import sys
import time

import paho.mqtt.client as mqtt

# MQTT broker connection settings
BROKER = os.getenv("BROKER", "mosquitto")
PORT = int(os.getenv("PORT", "1883"))

# Topic used to publish simulated tags packets
PACKET_TOPIC = os.getenv("PACKET_TOPIC", "tags/packets")

class TagSim:
    def __init__(self, tag_id, battery, product_id, reliability):
        self.tag_id = tag_id
        self.battery = battery
        self.product_id = product_id
        self.reliability = reliability
        self.status = "OK"

    def update_status(self):
        # Update status based on current battery level.
        if self.battery <= 20:
            self.status = "LOW_BATTERY"
        else:
            self.status = "OK"

    def build_packet(self):
        # Stop sending packet if the battery is empty
        if self.battery <= 0:
            return None

        self.update_status()

        return {
            "tag_id": self.tag_id,
            "battery": self.battery,
            "status": self.status,
            "product_id": self.product_id,
            "reliability": self.reliability
        }

    def drain_battery(self, amount=1):
        # Reduce battery after each publish cycle.
        if self.battery > 0:
            self.battery = max(0, self.battery - amount)


def main():
    # Create one simulated tag instance.
    tag = TagSim(
        tag_id=TAG_ID,
        battery=BATTERY,
        product_id=PRODUCT_ID,
        reliability=RELIABILITY,
    )

    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.connect(BROKER, PORT, 60)
    client.loop_start()

    print(
        f"TagSim started | tag_id={TAG_ID} | product_id={PRODUCT_ID} | "
        f"battery={BATTERY} | publish_topic={PACKET_TOPIC}"
    )
    sys.stdout.flush()

    try:
        while True:
            # Build current tag packet
            packet = tag.build_packet()

            if packet is None:
                print(f"TagSim {tag.tag_id}: battery is 0, no packet published")
                sys.stdout.flush()
                time.sleep(PUBLISH_INTERVAL)
                continue
            
            # Convert packet to JSON and publish it
            payload = json.dumps(packet)
            client.publish(PACKET_TOPIC, payload)

            print(f"TagSim published -> topic={PACKET_TOPIC} payload={payload}")
            sys.stdout.flush()

            # Simulate battery drain after each transmission.
            tag.drain_battery()
            time.sleep(PUBLISH_INTERVAL)

    except KeyboardInterrupt:
        print("TagSim stopped")
        sys.stdout.flush()
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()