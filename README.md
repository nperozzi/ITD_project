# Electronic Shelves Label System

Quickstart for local setup and daily commands.
This repo uses Bun + Nx for orchestration and Docker Compose for runtime.

## Quickstart

### 1) Install Bun runtime

Linux / macOS:

```bash
curl -fsSL https://bun.sh/install | bash
```

Windows (PowerShell):

```powershell
powershell -c "irm bun.sh/install.ps1 | iex"
```

Verify:

```bash
bun --version
```

### 2) Install Nx extension in VS Code (Nx Console)

From terminal:

```bash
code --install-extension nrwl.angular-console
```

Or install from Marketplace:

```text
https://marketplace.visualstudio.com/items?itemName=nrwl.angular-console
```

### 3) Install project dependencies

```bash
bun install
```

### 4) Start services

```bash
bun run compose:up
```

Frontend UI: http://localhost:4200

### 5) Stop services

```bash
bun run compose:down
```

### 6) Build services

```bash
bun run compose:build
```

### 7) Nx workspace commands

```bash
bun run nx show projects
bun run nx run esl-project:up
bun run nx run esl-project:down
bun run nx run backend:serve
bun run nx run gateway:serve
bun run nx run tag:serve
bun run nx run-many -t check --projects=backend,gateway,tag,mosquitto
```
