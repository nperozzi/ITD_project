// Cross-platform Docker Compose runner used by Bun/Nx scripts.
// Why this exists:
// - We want one command that works the same on Linux, macOS, and Windows.
// - Some machines have broken global Docker credential helper config.
// - This script forces Docker to use a project-local config at .docker/config.json.

import { spawn } from "node:child_process";
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");

const dockerConfigDir = path.join(repoRoot, ".docker");
const dockerConfigFile = path.join(dockerConfigDir, "config.json");

// Ensure .docker/ exists in the repository root.
if (!existsSync(dockerConfigDir)) {
  mkdirSync(dockerConfigDir, { recursive: true });
}

// Create a minimal Docker client config if missing.
// This avoids machine-specific credential helper issues.
if (!existsSync(dockerConfigFile)) {
  writeFileSync(
    dockerConfigFile,
    JSON.stringify({ auths: {} }, null, 2) + "\n",
  );
}

// Forward all user-provided args to `docker compose ...`.
// Example:
// bun run scripts/docker-compose-runner.mjs up --build
const composeArgs = process.argv.slice(2);
if (composeArgs.length === 0) {
  console.error(
    "Usage: bun run scripts/docker-compose-runner.mjs <docker compose args>",
  );
  process.exit(1);
}

// Run Docker Compose with:
// - working directory fixed to repo root
// - stdio inherited so output appears naturally in terminal
// - DOCKER_CONFIG forced to project-local .docker directory
const child = spawn("docker", ["compose", ...composeArgs], {
  cwd: repoRoot,
  stdio: "inherit",
  env: {
    ...process.env,
    DOCKER_CONFIG: dockerConfigDir,
  },
});

// Provide a clear beginner-friendly error when Docker is not installed.
child.on("error", (error) => {
  if (error.code === "ENOENT") {
    console.error(
      "Docker CLI not found in PATH. Please install Docker Desktop/Engine and retry.",
    );
  } else {
    console.error(error.message);
  }
  process.exit(1);
});

// Propagate Docker's exit code so CI and scripts behave correctly.
child.on("exit", (code) => {
  process.exit(code ?? 1);
});
