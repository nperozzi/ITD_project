#!/usr/bin/env python3
"""
Label Scanner Simulator

Simulates scanning for labels with randomized data.
Useful for testing without actual hardware.

Usage:
    python simulate_labels.py [--config CONFIG_PATH] [--count COUNT]
    
Examples:
    # Simulate scanning 5 random labels
    python simulate_labels.py --count 5
"""

import argparse
import random
import uuid
import sys
from pathlib import Path

from gateway_client import get_client, LabelReport, UpdateResult


def generate_random_labels(count: int) -> list[LabelReport]:
    """Generate random label reports for simulation."""
    labels = []
    for _ in range(count):
        labels.append(LabelReport(
            serial_number=str(uuid.uuid4()),
            battery_percent=random.randint(10, 100),
            rssi=random.randint(-90, -30),
            firmware_version=f"1.{random.randint(0, 5)}.{random.randint(0, 10)}",
        ))
    return labels


def simulate_push(update) -> UpdateResult:
    """Simulate pushing an update to a label."""
    # Simulate some processing time
    import time
    time.sleep(random.uniform(0.05, 0.2))
    
    # 90% success rate
    success = random.random() > 0.1
    
    if success:
        return UpdateResult(label_id=update.label_id, success=True)
    else:
        return UpdateResult(
            label_id=update.label_id,
            success=False,
            error=random.choice([
                "Communication timeout",
                "Label not responding",
                "CRC error",
            ])
        )


def main():
    parser = argparse.ArgumentParser(
        description="Simulate label scanning and syncing"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to config.json file",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=3,
        help="Number of labels to simulate (default: 3)",
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
    
    print("=" * 50)
    print("LABEL SCANNER SIMULATOR")
    print("=" * 50)
    print()
    print(f"Gateway: {client.serial_number}")
    print(f"Simulating {args.count} labels...")
    print()
    
    # Generate random labels
    labels = generate_random_labels(args.count)
    
    print("Discovered Labels:")
    for label in labels:
        print(f"  • {label.serial_number}")
        print(f"    Battery: {label.battery_percent}% | RSSI: {label.rssi} dBm | FW: {label.firmware_version}")
    print()
    
    try:
        # Sync with server
        print("Syncing with server...")
        response = client.sync_labels(labels)
        
        if not response.success:
            print(f"✗ Sync failed: {response.error}")
            sys.exit(1)
        
        stats = response.labels or {}
        print(f"✓ Sync successful!")
        print(f"  • Discovered: {stats.get('discovered', 0)}")
        print(f"  • Registered: {stats.get('registered', 0)}")
        print(f"  • Updated: {stats.get('updated', 0)}")
        print()
        
        # Process updates
        if response.updates:
            print(f"Processing {len(response.updates)} updates...")
            
            results = []
            for update in response.updates:
                print(f"\n  Updating label: {update.serial_number}")
                if update.product:
                    print(f"    Product: {update.product.get('name')}")
                    print(f"    Price: ${update.product.get('price', 0):.2f}")
                else:
                    print(f"    (Clearing display)")
                
                result = simulate_push(update)
                results.append(result)
                
                if result.success:
                    print(f"    ✓ Success")
                else:
                    print(f"    ✗ Failed: {result.error}")
            
            print()
            
            # Acknowledge
            print("Sending acknowledgments...")
            ack = client.acknowledge_updates(results)
            
            if ack.get("success"):
                print(f"✓ Acknowledged: {ack.get('successful', 0)} successful, "
                      f"{ack.get('failed', 0)} failed")
            else:
                print(f"✗ Acknowledgment failed: {ack.get('error')}")
        else:
            print("No updates to process.")
        
        print()
        print("Simulation complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
