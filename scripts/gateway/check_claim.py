#!/usr/bin/env python3
"""
Check Claim Status

Standalone script to check if the gateway has been claimed.
"""

import argparse
import sys
from pathlib import Path

from gateway_client import get_client


def main():
    parser = argparse.ArgumentParser(
        description="Check if the gateway has been claimed"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to config.json file",
    )
    args = parser.parse_args()
    
    try:
        client = get_client(args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    print(f"Gateway Serial: {client.serial_number}")
    print(f"Server: {client.server_url}")
    print()
    
    try:
        status = client.check_claim_status()
        
        print(f"Status: {status.status}")
        
        if status.is_claimed:
            print(f"Gateway ID: {status.gateway_id}")
            print(f"Name: {status.name}")
            print(f"Owner ID: {status.owner_id}")
            print(f"API Key: {status.api_key[:8]}...{status.api_key[-4:]}")
            print()
            print("✓ Gateway is claimed and ready to sync!")
            sys.exit(0)
        elif not status.is_valid:
            print(f"Error: {status.message}")
            print()
            print("✗ Serial number is not registered. Please register it first.")
            sys.exit(2)
        else:
            print()
            print("⏳ Gateway is not yet claimed.")
            print("   Waiting for a user to claim this gateway via the web dashboard...")
            print()
            print("   The user needs to enter this serial number:")
            print(f"   {client.serial_number}")
            sys.exit(3)
            
    except Exception as e:
        print(f"Error checking claim status: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
