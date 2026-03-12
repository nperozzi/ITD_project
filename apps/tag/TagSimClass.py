

class TagSim:
    def __init__(self, tag_id, battery, product_id, reliability):
        self.tag_id = tag_id
        self.battery = battery
        self.product_id = product_id
        self.reliability = reliability
        self.status = "online"

    def update_status(self):
        if self.battery > 0:
            self.status = "online"
    

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