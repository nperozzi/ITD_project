import asyncio
from bleak import BleakClient
from dataclasses import dataclass

@dataclass(frozen=True)
class BleTagContract:
    name: str
    mac_address: str
    service_uuid: str
    payload_char_uuid: str
    ack_char_uuid: str
    expected_ack: str
    encoding: str = "utf-8"


TAG1 = BleTagContract(
    name="TAG1",
    mac_address="A8:42:E3:CA:AA:A2",
    service_uuid="12345678-1234-1234-1234-1234567890ab",
    payload_char_uuid="abcd1234-5678-90ab-cdef-1234567890ab",
    ack_char_uuid="abcd1234-5678-90ab-cdef-1234567890ac",
    expected_ack="OK",
)

class BleTagAdapter:
    def __init__(self, contract: BleTagContract) -> None:
        self.contract = contract
        self.client = None

    async def connect(self) -> None:
        self.client = BleakClient(self.contract.mac_address)
        await self.client.connect()
        print(f"Connected: {self.client.is_connected}")

    async def disconnect(self) -> None:
        if self.client is not None:
            await self.client.disconnect()
            self.client = None

    def send_payload(self, payload_text: str) -> None:
        # Next step: connect and write with Bleak.
        print(f"Would send to {self.contract.name}: {payload_text}")

    def wait_for_ack(self) -> str | None:
        # Next step: read notifications or ack characteristic.
        return None
