# Beginner Guide: How This Monorepo Works

This guide explains the project in beginner-friendly language and includes learning links.

## 1) Big picture

This repo contains multiple services that work together:

- **Backend** (`apps/backend`): web app + API + real-time updates.
- **Gateway** (`apps/gateway`): forwards MQTT messages between backend and tag namespaces.
- **Tag simulator** (`apps/tag`): acts like a physical shelf label device.
- **Broker config** (`infra/mosquitto`): MQTT broker settings.

If you are new to these tools:

- Docker overview: https://docs.docker.com/get-started/
- Docker Compose overview: https://docs.docker.com/compose/
- Bun runtime/package manager: https://bun.sh/docs
- Nx monorepo concepts: https://nx.dev/getting-started/intro
- MQTT basics: https://mqtt.org/getting-started/
- Flask docs: https://flask.palletsprojects.com/
- Socket.IO docs: https://socket.io/docs/v4/

## 2) Why there are helper scripts

The scripts in `scripts/` are used to make commands **consistent across Linux, macOS, and Windows**.

- `scripts/docker-compose-runner.mjs`
  - Runs `docker compose` with a project-local Docker config (`.docker/config.json`)
  - Avoids machine-specific credential helper problems
- `scripts/python-runner.mjs`
  - Finds the right Python executable (`python3`, `python`, or `py`) depending on platform

## 3) Why JSON files do not have comments

Files like `package.json`, `nx.json`, and `project.json` are strict JSON.
JSON does **not** allow comments.

Beginner references for those files:

- `package.json`: npm/bun package metadata and scripts
  - https://docs.npmjs.com/cli/v10/configuring-npm/package-json
- `nx.json`: workspace-wide Nx behavior
  - https://nx.dev/reference/nx-json
- `project.json`: per-project Nx targets
  - https://nx.dev/reference/project-configuration

## 4) Common commands

Install dependencies:

```bash
bun install
```

Start all services:

```bash
bun run compose:up
```

Stop all services:

```bash
bun run compose:down
```

Run backend-only (plus broker) with Nx:

```bash
bun run nx run backend:serve
```

Run quick Python syntax checks for service code:

```bash
bun run nx run-many -t check --projects=backend,gateway,tag
```

## 5) Data flow in this demo

1. Browser updates a product price through `PATCH /api/products/{productId}`.
2. Backend stores the new product price in the database.
3. Backend generates a fresh tag payload for each tag assigned to that product.
4. Backend publishes each payload to MQTT topic `b-g/tag{tagId}/payload`.
5. Gateway forwards the payload to the tag-side namespace.
6. Tag simulator publishes battery to `g-t/tag1/battery`.
7. Gateway forwards battery to `b-g/tag1/battery`.
8. Backend stores battery and emits `battery_update` to browser via Socket.IO.

That is why all four services are needed for full end-to-end behavior.
