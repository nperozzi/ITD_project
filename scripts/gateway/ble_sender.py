"""
BLE Sender for Arduino Labels

Sends LED matrix frames to Arduino UNO R4 WiFi labels via BLE.
"""

import asyncio
import logging
from typing import Optional

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

logger = logging.getLogger(__name__)

# BLE UUIDs (must match Arduino code)
SERVICE_UUID = "12345678-1234-1234-1234-1234567890ab"
CHAR_UUID = "abcdefab-1234-5678-1234-abcdefabcdef"

# Label name prefix
LABEL_NAME_PREFIX = "ESL-"


async def find_label_by_serial(
    serial_prefix: str,
    timeout: float = 10.0
) -> Optional[str]:
    """
    Find a label's BLE address by its serial number prefix.
    
    Args:
        serial_prefix: First 8 chars of the serial number
        timeout: Scan timeout in seconds
        
    Returns:
        BLE address if found, None otherwise
    """
    target_name = f"{LABEL_NAME_PREFIX}{serial_prefix}"
    
    logger.debug(f"Scanning for device: {target_name}")
    
    devices = await BleakScanner.discover(timeout=timeout)
    
    for device in devices:
        if device.name and device.name.lower() == target_name.lower():
            logger.info(f"Found {target_name} at {device.address}")
            return device.address
    
    logger.warning(f"Device {target_name} not found")
    return None


async def send_frame_to_address(
    address: str,
    frame: bytes,
    retries: int = 3
) -> bool:
    """
    Send a 96-byte frame to a label at a specific BLE address.
    
    Args:
        address: BLE address of the label
        frame: 96-byte frame data (12x8 pixels, 0 or 1)
        retries: Number of connection retries
        
    Returns:
        True if successful, False otherwise
    """
    if len(frame) != 96:
        raise ValueError(f"Frame must be 96 bytes, got {len(frame)}")
    
    for attempt in range(retries):
        try:
            logger.debug(f"Connecting to {address} (attempt {attempt + 1}/{retries})")
            
            async with BleakClient(address, timeout=10.0) as client:
                if not client.is_connected:
                    logger.warning(f"Failed to connect to {address}")
                    continue
                
                logger.debug(f"Connected to {address}")
                
                await client.write_gatt_char(CHAR_UUID, frame, response=False)
                
                logger.info(f"Frame sent to {address}")
                return True
                
        except BleakError as e:
            logger.warning(f"BLE error (attempt {attempt + 1}): {e}")
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            await asyncio.sleep(1)
    
    logger.error(f"Failed to send frame to {address} after {retries} attempts")
    return False


async def send_frame_to_serial(
    serial_prefix: str,
    frame: bytes,
    scan_timeout: float = 10.0,
    retries: int = 3
) -> bool:
    """
    Find a label by serial and send a frame.
    
    Args:
        serial_prefix: First 8 chars of the serial number
        frame: 96-byte frame data
        scan_timeout: How long to scan for the device
        retries: Connection retries
        
    Returns:
        True if successful, False otherwise
    """
    address = await find_label_by_serial(serial_prefix, scan_timeout)
    
    if not address:
        return False
    
    return await send_frame_to_address(address, frame, retries)


# Cache of known addresses to speed up subsequent sends
_address_cache: dict[str, str] = {}


async def send_frame_cached(
    serial_prefix: str,
    frame: bytes,
    scan_timeout: float = 5.0,
) -> bool:
    """
    Send a frame, using cached address if available.
    
    Args:
        serial_prefix: First 8 chars of the serial number
        frame: 96-byte frame data
        scan_timeout: Scan timeout if not cached
        
    Returns:
        True if successful, False otherwise
    """
    serial_lower = serial_prefix.lower()
    
    # Try cached address first
    if serial_lower in _address_cache:
        address = _address_cache[serial_lower]
        logger.debug(f"Using cached address for {serial_prefix}: {address}")
        
        if await send_frame_to_address(address, frame, retries=2):
            return True
        
        # Cache miss, remove and rescan
        logger.debug(f"Cached address failed, rescanning...")
        del _address_cache[serial_lower]
    
    # Scan for device
    address = await find_label_by_serial(serial_prefix, scan_timeout)
    
    if not address:
        return False
    
    # Cache the address
    _address_cache[serial_lower] = address
    
    return await send_frame_to_address(address, frame, retries=2)


def clear_address_cache():
    """Clear the address cache."""
    _address_cache.clear()


def populate_address_cache(discovered_labels: list) -> None:
    """
    Populate the address cache from discovered labels.
    
    Args:
        discovered_labels: List of DiscoveredLabel objects from scan
    """
    for label in discovered_labels:
        serial_lower = label.serial_number[:8].lower()
        _address_cache[serial_lower] = label.address
        logger.debug(f"Cached address for {label.serial_number[:8]}: {label.address}")


# For testing
if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.DEBUG)
    
    async def main():
        if len(sys.argv) < 2:
            print("Usage: python ble_sender.py <serial_prefix>")
            print("Example: python ble_sender.py 550e8400")
            return
        
        serial = sys.argv[1]
        
        # Create a test pattern (checkerboard)
        frame = bytes([((x + y) % 2) for y in range(8) for x in range(12)])
        
        print(f"Sending test pattern to {serial}...")
        success = await send_frame_to_serial(serial, frame)
        
        if success:
            print("Success!")
        else:
            print("Failed!")
    
    asyncio.run(main())
