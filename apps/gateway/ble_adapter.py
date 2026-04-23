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
    mac_address="74:4D:BD:63:C3:26",
    service_uuid="B8E4F533-E530-4D1D-B54C-0D5D5A9A5A4B",
    payload_char_uuid="99CFD161-DCD8-4BEB-86B2-48673AEAE284",
    ack_char_uuid="53B04C05-A5E1-475B-BC9E-61C00112ACDE",
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

    async def send_payload(self, payload_text: str) -> None:
        data = payload_text.encode(self.contract.encoding)
        await self.client.write_gatt_char(
            self.contract.payload_char_uuid,
            data
        )
        print(f"Sent to {self.contract.name}: {payload_text}")


    async def wait_for_ack(self) -> str | None:
        data = await self.client.read_gatt_char(self.contract.ack_char_uuid)
        ack = data.decode(self.contract.encoding)
        print(f"Ack from {self.contract.name}: {ack}")
        return ack
