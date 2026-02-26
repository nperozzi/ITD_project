# Electronic Shelves Label System

This repository is organized as a monorepo so teams can work independently per service.

## Monorepo tooling

This monorepo uses **Nx** for workspace orchestration (project discovery + standard targets).
Docker Compose remains the runtime layer for the multi-container stack.
All repo commands use a project-local Docker client config (`.docker/config.json`) to avoid host credential-helper issues.

### Install Nx dependencies

```bash
bun install
```

### Useful Nx commands

```bash
bun run nx show projects
bun run nx run platform:up
bun run nx run platform:down
bun run nx run backend:serve
bun run nx run gateway:serve
bun run nx run tag:serve
bun run nx run-many -t check --projects=backend,gateway,tag
```

## Monorepo structure

```
apps/
	backend/      # Flask + Socket.IO API
	frontend/     # Frontend app (currently empty)
	gateway/      # MQTT topic bridge
	tag/          # Tag simulator
infra/
	mosquitto/    # Broker configuration
docs/
	team_ground_rules.md
docker-compose.yml
```

## Team ownership pattern

- `apps/backend`: backend team
- `apps/frontend`: frontend team
- `apps/gateway`: gateway/device integration team
- `apps/tag`: embedded simulator/testing team
- `infra/mosquitto`: infrastructure/config team
- `docs`: shared project documentation

## Run with Docker Compose

1. Make sure Docker is running.
2. From the repo root (where `docker-compose.yml` is), run:

```bash
docker compose up --build
```

3. Open:

```text
http://localhost:5000
```

## Quick test

Enter a price and send it from the UI. You should see tag updates in logs, for example:

```text
tag-1  | Tag display updated: 1
```

