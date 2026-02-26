# Gateway

MQTT topic bridge between backend and tag namespaces.

## What it does

- Forwards `b-g/*` topics to `g-t/*`
- Forwards `g-t/*` topics to `b-g/*`

## Useful commands (from repo root)

- `bun run nx run gateway:serve`
- `bun run nx run gateway:check`
