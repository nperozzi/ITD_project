# Gateway

The gateway is the message-routing layer of the ESL platform. It ensures communication can flow cleanly between central services and device-facing channels.

## Role in the System

- Relays operational messages between backend-side and tag-side communication paths.
- Keeps messaging boundaries organized so each side can evolve with minimal coupling.
- Supports reliable end-to-end propagation of pricing and status events.

## Why It Matters

This module provides separation of concerns in the messaging architecture. It helps the platform remain maintainable as communication patterns grow.

## Audience

New contributors should think of this module as the bridge that connects application logic to device-oriented message flows.
