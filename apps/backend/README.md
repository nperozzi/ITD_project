# Backend

Flask + Socket.IO service for the ESL system.

## What it does

- Serves HTTP + Socket.IO APIs for the frontend app
- Publishes price updates over MQTT
- Receives battery updates and pushes realtime UI events

## Useful commands (from repo root)

- `bun run nx run backend:serve`
- `bun run nx run backend:check`
