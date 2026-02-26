# Frontend

Standalone React app for the ESL customer dashboard.

## Current status

- React + TypeScript + Vite app lives fully under `apps/frontend`
- Tailwind CSS is configured
- ShadCN-compatible setup is included (`components.json` + `src/components/ui`)
- SWR is used for typed backend data hooks (`/api/*`)
- Live battery updates are consumed via Socket.IO (`battery_update`)
- Price updates can be sent to backend via `POST /set_price`
- Auth flow is intentionally excluded

## Backend integration

- Default API mode uses same-origin relative paths (`/api`, `/set_price`, `/battery`, `/socket.io`)
- In Compose, Vite proxies to backend using `VITE_PROXY_TARGET=http://backend:5000`
- Override direct backend host with `VITE_BACKEND_URL` when needed
- Expected runtime: `bun run compose:up` from repo root
- UI is served from the `frontend` Docker service on `http://localhost:4200`

## Useful commands (from repo root)

- `bun run nx run frontend:serve`
- `bun run nx run frontend:build`
- `bun run nx run frontend:check`

## Direct local commands

From `apps/frontend`:

- `bun install`
- `bun run dev`
- `bun run build`
- `bun run check`

## Notes

- `bun run nx run frontend:build` is the supported Nx invocation from root.
