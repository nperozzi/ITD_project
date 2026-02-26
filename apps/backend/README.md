# Backend

Flask + Socket.IO service for the ESL system.

## What it does

- Serves the web UI and HTTP routes
- Publishes price updates over MQTT
- Receives battery updates and pushes realtime UI events

## Useful commands (from repo root)

- `bun run nx run backend:serve`
- `bun run nx run backend:check`
