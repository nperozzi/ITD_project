#!/usr/bin/env python3
"""
ESL Gateway Daemon

Main daemon process that runs on the Raspberry Pi Pico 2 W gateway.
Handles:
- Initial claim checking
- BLE scanning for Arduino labels
- Syncing discovered labels with web server
- Pushing product updates to label displays

Usage:
    python gateway_daemon.py [--config CONFIG_PATH]
"""

import argparse
import asyncio
import signal
import socket
import sys
from pathlib import Path
from typing import Optional

from ble_scanner import DiscoveredLabel, scan_for_labels
from ble_sender import (clear_address_cache, populate_address_cache,
                        send_frame_cached)
from gateway_client import (GatewayClient, GatewayUnclaimed, LabelReport,
                            LabelUpdate, UpdateResult, get_client, load_config)
from matrix_renderer import matrix_to_bytes, render_product

# Global flag for graceful shutdown
running = True


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    global running
    print("\nShutdown signal received. Stopping...")
    running = False


def get_local_ip() -> Optional[str]:
    """Get the local IP address of the gateway."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


async def wait_for_claim(
    client: GatewayClient,
    check_interval: int
) -> bool:
    """
    Wait until the gateway is claimed by a user.
    
    Args:
        client: Gateway client instance
        check_interval: Seconds between claim checks
        
    Returns:
        True if claimed, False if interrupted
    """
    print("=" * 50)
    print("WAITING FOR CLAIM")
    print("=" * 50)
    print()
    print(f"Serial Number: {client.serial_number}")
    print()
    print("Please claim this gateway in the web dashboard.")
    print(f"Checking every {check_interval} seconds...")
    print()
    
    while running:
        try:
            status = client.check_claim_status()
            
            if status.is_claimed:
                print()
                print("✓ Gateway claimed!")
                print(f"  Name: {status.name}")
                print(f"  Gateway ID: {status.gateway_id}")
                return True
            elif not status.is_valid:
                print(f"✗ Invalid serial number: {status.message}")
                print("  Please register this serial number first.")
                return False
            else:
                import time
                print(f"  Still waiting... (checked at {time.strftime('%H:%M:%S')})")
                
        except Exception as e:
            print(f"  Error checking claim: {e}")
        
        # Wait for next check
        for _ in range(check_interval):
            if not running:
                return False
            await asyncio.sleep(1)
    
    return False


def discovered_to_report(label: DiscoveredLabel) -> LabelReport:
    """Convert a discovered label to a report for the server."""
    return LabelReport(
        serial_number=label.serial_number,
        status="online",
        rssi=label.rssi,
        battery_percent=None,  # Arduino doesn't report battery
    )


async def push_update_to_label(update: LabelUpdate) -> UpdateResult:
    """
    Push a display update to a physical Arduino label.
    
    Args:
        update: The update containing product info
        
    Returns:
        UpdateResult indicating success or failure
    """
    print(f"    → Pushing update to {update.serial_number}")
    
    # Get first 8 chars of serial (what Arduino advertises)
    serial_prefix = update.serial_number[:8]
    
    if update.product:
        print(f"      Product: {update.product.get('name', 'Unknown')}")
    else:
        print(f"      Clearing display (no product)")
    
    # Render product to LED matrix
    matrix = render_product(update.product)
    frame = matrix_to_bytes(matrix)
    
    # Send to Arduino via BLE
    try:
        success = await send_frame_cached(serial_prefix, frame)
        
        if success:
            print(f"      ✓ Display updated")
            return UpdateResult(label_id=update.label_id, success=True)
        else:
            error = "Failed to connect to label"
            print(f"      ✗ {error}")
            return UpdateResult(label_id=update.label_id, success=False, error=error)
            
    except Exception as e:
        error = str(e)
        print(f"      ✗ Error: {error}")
        return UpdateResult(label_id=update.label_id, success=False, error=error)


async def sync_loop(
    client: GatewayClient,
    sync_interval: int,
    ble_scan_timeout: float
) -> bool:
    """
    Main sync loop - scans for labels and syncs with server.
    
    Args:
        client: Gateway client instance
        sync_interval: Seconds between syncs
        ble_scan_timeout: BLE scan timeout in seconds
        
    Returns:
        True if loop was stopped normally, False if gateway was unclaimed
    """
    print()
    print("=" * 50)
    print("SYNC LOOP STARTED")
    print("=" * 50)
    print()
    print(f"Syncing every {sync_interval} seconds...")
    print(f"BLE scan timeout: {ble_scan_timeout}s")
    print("Press Ctrl+C to stop.")
    print()
    
    ip_address = get_local_ip()
    if ip_address:
        print(f"Local IP: {ip_address}")
    
    while running:
        try:
            import time
            print(f"\n[{time.strftime('%H:%M:%S')}] Starting sync cycle...")
            
            # Scan for Arduino labels via BLE
            print("  Scanning for labels...")
            discovered = await scan_for_labels(timeout=ble_scan_timeout)
            
            # Populate address cache from discovered labels
            populate_address_cache(discovered)
            
            # Convert to reports
            labels = [discovered_to_report(label) for label in discovered]
            
            print(f"  Found {len(labels)} labels")
            for label in labels:
                print(f"    - {label.serial_number} (RSSI: {label.rssi})")
            
            # Sync with server
            print("  Syncing with server...")
            response = client.sync_labels(labels, ip_address=ip_address)
            
            if not response.success:
                print(f"  ✗ Sync failed: {response.error}")
            else:
                print(f"  ✓ Sync complete:")
                print(f"    Pending labels: {len(response.pending_labels)}")
                print(f"    Labels to update: {len(response.updates)}")
                
                # Process any updates
                if response.updates:
                    print(f"\n  Processing {len(response.updates)} display updates...")
                    
                    results = []
                    for update in response.updates:
                        result = await push_update_to_label(update)
                        results.append(result)
                    
                    # Acknowledge updates
                    if results:
                        ack = client.acknowledge_updates(results)
                        successful = ack.get('successful', 0)
                        failed = ack.get('failed', 0)
                        print(f"  Acknowledged: {successful} successful, {failed} failed")
                else:
                    print("  No display updates pending")
        
        except GatewayUnclaimed as e:
            print()
            print("!" * 50)
            print("GATEWAY UNCLAIMED")
            print("!" * 50)
            print()
            print(f"  {e}")
            print("  The gateway has been deleted from the dashboard.")
            print("  Returning to claim-waiting state...")
            return False
                    
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Wait for next sync
        print(f"\n  Next sync in {sync_interval}s...")
        for _ in range(sync_interval):
            if not running:
                return True
            await asyncio.sleep(1)
    
    return True


async def main_async(config_path: Optional[Path] = None):
    """Async main entry point."""
    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║          ESL GATEWAY DAEMON                      ║")
    print("║      Raspberry Pi Pico 2 W + Arduino R4          ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    # Load config
    try:
        config_path = config_path or Path(__file__).parent / "config.json"
        config = load_config(config_path)
        client = get_client(config_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    print(f"Server URL: {client.server_url}")
    print(f"Gateway Serial: {client.serial_number}")
    print(f"Firmware Version: {client.firmware_version}")
    print()
    
    # Get intervals from config
    sync_interval = config.get("sync_interval_seconds", 30)
    claim_check_interval = config.get("claim_check_interval_seconds", 10)
    ble_scan_timeout = config.get("ble_scan_timeout", 10.0)
    
    # Main loop - handles claim/unclaim cycles
    while running:
        # If not claimed, wait for claim
        if not client.api_key:
            if not await wait_for_claim(client, claim_check_interval):
                print("Exiting.")
                sys.exit(0)
        else:
            print("✓ Already claimed (API key present)")
        
        # Clear BLE address cache at start
        clear_address_cache()
        
        # Run sync loop - returns False if gateway was unclaimed
        was_normal_stop = await sync_loop(client, sync_interval, ble_scan_timeout)
        
        if was_normal_stop:
            # Normal shutdown (Ctrl+C or signal)
            break
        else:
            # Gateway was unclaimed, loop back to wait for claim
            print()
            print("Restarting claim check loop...")
            print()
    
    print()
    print("Daemon stopped.")


def main():
    global running
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    parser = argparse.ArgumentParser(description="ESL Gateway Daemon")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to config.json file",
    )
    args = parser.parse_args()
    
    # Run async main
    asyncio.run(main_async(args.config))


if __name__ == "__main__":
    main()
