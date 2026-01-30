#!/usr/bin/env python3
"""
Sync Labels Script

Syncs discovered labels with the server and processes any updates.
This script demonstrates the sync flow for testing purposes.

Usage:
    python sync_labels.py [--config CONFIG_PATH] [--labels LABEL_SERIALS...]
    
Examples:
    # Sync with no labels
    python sync_labels.py
    
    # Sync with specific labels
    python sync_labels.py --labels 550e8400-e29b-41d4-a716-446655440000 f47ac10b-58cc-4372-a567-0e02b2c3d479
"""

import argparse
import random
import sys
from pathlib import Path

from gateway_client import get_client, LabelReport, UpdateResult


def generate_mock_label(serial_number: str) -> LabelReport:
    """Generate a mock label report with simulated data."""
    return LabelReport(
        serial_number=serial_number,
        battery_percent=random.randint(20, 100),
        rssi=random.randint(-90, -30),
        firmware_version="1.0.0",
    )


def push_update_to_label(update) -> UpdateResult:
    """
    Simulate pushing an update to a physical label.
    
    In a real implementation, this would:
    1. Connect to the label via BLE/RF
    2. Send the display update data
    3. Wait for acknowledgment
    
    Returns:
        UpdateResult indicating success or failure
    """
    print(f"  Pushing update to label {update.serial_number}...")
    
    if update.product:
        print(f"    Product: {update.product.get('name', 'Unknown')}")
        print(f"    Price: {update.product.get('price', 'N/A')}")
    else:
        print(f"    Clearing display (no product assigned)")
    
    # Simulate success (in real implementation, this would actually push to hardware)
    success = random.random() > 0.1  # 90% success rate for demo
    
    if success:
        print(f"    ✓ Update pushed successfully")
        return UpdateResult(label_id=update.label_id, success=True)
    else:
        error = "Communication timeout"
        print(f"    ✗ Failed: {error}")
        return UpdateResult(label_id=update.label_id, success=False, error=error)


def main():
    parser = argparse.ArgumentParser(
        description="Sync labels with the server"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to config.json file",
    )
    parser.add_argument(
        "--labels",
        nargs="*",
        default=[],
        help="Serial numbers of labels to report",
    )
    args = parser.parse_args()
    
    try:
        client = get_client(args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    if not client.api_key:
        print("Error: No API key found. Run check_claim.py first.")
        sys.exit(1)
    
    print(f"Gateway Serial: {client.serial_number}")
    print(f"Server: {client.server_url}")
    print()
    
    # Create label reports
    labels = [generate_mock_label(serial) for serial in args.labels]
    
    print(f"Syncing {len(labels)} labels...")
    for label in labels:
        print(f"  - {label.serial_number} (battery: {label.battery_percent}%, rssi: {label.rssi}dBm)")
    print()
    
    try:
        # Sync with server
        response = client.sync_labels(labels)
        
        if not response.success:
            print(f"Sync failed: {response.error}")
            sys.exit(1)
        
        print("Sync successful!")
        print(f"  Discovered: {response.labels.get('discovered', 0)}")
        print(f"  Registered: {response.labels.get('registered', 0)}")
        print(f"  Updated: {response.labels.get('updated', 0)}")
        print()
        
        # Process updates
        if response.updates:
            print(f"Processing {len(response.updates)} updates...")
            print()
            
            results = []
            for update in response.updates:
                result = push_update_to_label(update)
                results.append(result)
            
            print()
            
            # Acknowledge updates
            ack_response = client.acknowledge_updates(results)
            
            if ack_response.get("success"):
                print(f"Acknowledgment sent: {ack_response.get('successful', 0)} successful, "
                      f"{ack_response.get('failed', 0)} failed")
            else:
                print(f"Acknowledgment failed: {ack_response.get('error')}")
        else:
            print("No updates to process.")
        
        print()
        print("✓ Sync complete!")
        
    except Exception as e:
        print(f"Error during sync: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
