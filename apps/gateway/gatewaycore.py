import random
import sys
import time

class GatewayCore:
    """
    Core gateway logic:
    - validates incoming packets
    - decides whether a tag was "heard"
    - tracks last seen state
    - creates alert events
    """

    def __init__(self, known_tags):
        # List of tag IDs this gateway expects to track.
        self.known_tags = known_tags
        self.last_seen = {}

        # Tags that have already triggered a low battery alert.
        # This prevents publishing the same alert repeatedly every cycle.
        self.low_battery_alerted = set()

        # Tags that have already triggered an offline alert.
        # This prevents repeated offline messages until the tag is heard again.
        self.offline_alerted = set()

    def validate_packet(self, packet):
        """
        Check whether an incoming packet has the required structure and value types.
        Returns:
            (True, "Valid packet") if valid
            (False, "reason") if invalid
        """
        if packet is None:
            return False, "No packet"

        required_fields = ["tag_id", "battery", "status", "product_id", "reliability"]

        for field in required_fields:
            if field not in packet:
                return False, f"Missing field: {field}"

        if not isinstance(packet["tag_id"], int):
            return False, "tag_id must be int"

        if not isinstance(packet["battery"], int):
            return False, "battery must be int"

        if not (0 <= packet["battery"] <= 100):
            return False, "battery must be between 0 and 100"

        if  not isinstance(packet["status"], str):
            return False, "status must be string"
        
        if packet["status"] != "online":
            return False, "status must be online"

        if not isinstance(packet["product_id"], int):
            return False, "product_id must be int"

        if not isinstance(packet["reliability"], (int, float)):
            return False, "reliability must be a number"

        if not (0.0 <= packet["reliability"] <= 1.0):
            return False, "reliability must be between 0.0 and 1.0"

        return True, "Valid packet"

    def process_packet(self, packet, round_number):
        """
        Process one incoming tag packet.

        Steps:
        1. Validate packet fields
        2. Simulate radio reliability using the 'reliability' value
        3. If the packet is heard, update the tag's last known state
        4. Return a TAG_HEARD event if successful
        """
        valid, reason = self.validate_packet(packet)

        if not valid:
            print(f"Gateway rejected packet: {reason}")
            sys.stdout.flush()
            return []

        # Simulate BLE/radio packet loss.
        # If reliability is 0.9, then roughly 90% of packets are heard.
        heard = random.random() < packet["reliability"]

        if not heard:
            print(f"Gateway missed tag {packet['tag_id']}")
            sys.stdout.flush()
            return []

        tag_id = packet["tag_id"]

        # Save latest known state for the tag.
        self.last_seen[tag_id] = {
            "battery": packet["battery"],
            "status": packet["status"],
            "product_id": packet["product_id"],
            "last_seen_time": time.time()
        }

        # If the tag was previously marked offline and is heard again,
        # remove it from offline_alerted.
        if tag_id in self.offline_alerted:
            self.offline_alerted.remove(tag_id)

        print(
            f"Gateway heard tag {tag_id} | "
            f"battery={packet['battery']} | "
            f"status={packet['status']} | "
            f"product_id={packet['product_id']}"
        )
        sys.stdout.flush()

        # Return one event describing what happened.
        return [{
            "type": "TAG_HEARD",
            "tag_id": tag_id,
            "round": round_number,
            "battery": packet["battery"],
            "status": packet["status"],
            "product_id": packet["product_id"]
        }]

    def check_alerts(self, current_round, offline_timeout_seconds=5.0, low_battery_threshold=20):
        """
        Check all known tags for:
        - offline condition
        - low battery condition

        This function returns a list of alert events.
        """
        events = []

        # Current time used to measure how long ago each tag was last heard.
        now = time.time()

        for tag_id in self.known_tags:
            # If a tag has never been heard yet, skip it.
            if tag_id not in self.last_seen:
                continue

            data = self.last_seen[tag_id]
            seconds_missing = now - data["last_seen_time"]

            # If the tag has not been heard for too long, mark it offline.
            if seconds_missing >= offline_timeout_seconds:
                if tag_id not in self.offline_alerted:
                    events.append({
                        "type": "TAG_OFFLINE",
                        "tag_id": tag_id,
                        "round": current_round
                    })
                    self.offline_alerted.add(tag_id)

                # Once tag is offline, skip low battery check for this round.
                continue

            # If battery is low and alert not already sent, create alert event.
            if data["battery"] <= low_battery_threshold:
                if tag_id not in self.low_battery_alerted:
                    events.append({
                        "type": "LOW_BATTERY",
                        "tag_id": tag_id,
                        "round": current_round,
                        "battery": data["battery"]
                    })
                    self.low_battery_alerted.add(tag_id)
            else:
                # If battery recovered above threshold, allow future low battery alerts again.
                if tag_id in self.low_battery_alerted:
                    self.low_battery_alerted.remove(tag_id)

        return events

    def event_to_message(self, event):
        """
        Convert an internal event dictionary into:
        - MQTT topic
        - MQTT payload
        """
        tag_id = event["tag_id"]

        if event["type"] == "TAG_HEARD":
            return {
                "topic": f"gateway/events/tag/{tag_id}/heard",
                "payload": {
                    "tag_id": tag_id,
                    "round": event["round"],
                    "battery": event["battery"],
                    "status": event["status"],
                    "product_id": event["product_id"]
                }
            }

        if event["type"] == "LOW_BATTERY":
            return {
                "topic": f"gateway/events/tag/{tag_id}/low_battery",
                "payload": {
                    "tag_id": tag_id,
                    "round": event["round"],
                    "battery": event["battery"]
                }
            }

        if event["type"] == "TAG_OFFLINE":
            return {
                "topic": f"gateway/events/tag/{tag_id}/offline",
                "payload": {
                    "tag_id": tag_id,
                    "round": event["round"]
                }
            }

        return None

    def handle_event(self, event, publisher):
        """
        Convert an event to an MQTT message and publish it.
        """
        message = self.event_to_message(event)
        if message is None:
            return

        publisher.publish(message["topic"], message["payload"])
