# Backend

The backend is the core application service of the ESL platform. It handles user-driven actions from the dashboard and coordinates live system behavior across other modules.

## Role in the System

- Receives requests from the frontend and applies business logic.
- Coordinates pricing and status events across connected services.
- Acts as the central point for real-time updates that keep the UI current.

## Why It Matters

This module is where system decisions are made. It translates user intent (for example, changing a price) into actions that can be delivered to label devices, while also collecting device state so operators can monitor health.

## Audience

New contributors should think of this module as the orchestration layer between the user interface, messaging flow, and device-facing behavior.

## Container Testing

The backend container includes `pytest`, and the repository test directory is mounted at `/tests`.
This allows targeted checks such as:

```bash
docker compose exec -T backend python -m pytest /tests/test_mqtt_client.py -q
```
