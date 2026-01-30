"""
BLE Scanner for Arduino Labels

Scans for Arduino UNO R4 WiFi devices advertising as ESL labels.
Each label advertises with name format: "ESL-{serial_number_short}"
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

logger = logging.getLogger(__name__)

# Arduino labels advertise with this name prefix
LABEL_NAME_PREFIX = "ESL-"


@dataclass
class DiscoveredLabel:
    """A discovered label device."""
    serial_number: str
    address: str
    name: str
    rssi: int
    
    def __repr__(self) -> str:
        return f"Label({self.serial_number}, rssi={self.rssi})"


def extract_serial_from_name(name: str) -> Optional[str]:
    """
    Extract serial number from device name.
    
    Expected format: "ESL-{short_serial}" where short_serial is first 8 chars
    The full serial will be looked up from the server.
    """
    if name and name.startswith(LABEL_NAME_PREFIX):
        return name[len(LABEL_NAME_PREFIX):]
    return None


async def scan_for_labels(timeout: float = 10.0) -> list[DiscoveredLabel]:
    """
    Scan for ESL label devices via BLE.
    
    Args:
        timeout: How long to scan in seconds
        
    Returns:
        List of discovered labels
    """
    logger.info(f"Scanning for labels (timeout={timeout}s)...")
    
    discovered: dict[str, DiscoveredLabel] = {}
    
    def callback(device: BLEDevice, adv_data: AdvertisementData):
        name = device.name or adv_data.local_name
        if not name:
            return
            
        serial = extract_serial_from_name(name)
        if serial:
            label = DiscoveredLabel(
                serial_number=serial,
                address=device.address,
                name=name,
                rssi=adv_data.rssi or -100,
            )
            discovered[device.address] = label
            logger.debug(f"Found label: {label}")
    
    scanner = BleakScanner(detection_callback=callback)
    
    await scanner.start()
    await asyncio.sleep(timeout)
    await scanner.stop()
    
    labels = list(discovered.values())
    logger.info(f"Scan complete. Found {len(labels)} labels.")
    
    return labels


async def scan_for_label_by_serial(
    serial_prefix: str,
    timeout: float = 10.0
) -> Optional[DiscoveredLabel]:
    """
    Scan for a specific label by serial number prefix.
    
    Args:
        serial_prefix: First 8 characters of the serial number
        timeout: How long to scan in seconds
        
    Returns:
        The discovered label or None
    """
    labels = await scan_for_labels(timeout)
    
    for label in labels:
        if label.serial_number.lower() == serial_prefix.lower():
            return label
    
    return None


# For testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    async def main():
        labels = await scan_for_labels(timeout=5.0)
        print(f"\nDiscovered {len(labels)} labels:")
        for label in labels:
            print(f"  - {label.name} ({label.address}) RSSI: {label.rssi}")
    
    asyncio.run(main())
