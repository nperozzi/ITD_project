// Cross-platform Python launcher used by Nx check targets.
// Why this exists:
// - Linux/macOS usually use `python3`
// - Windows often uses `py` launcher
// We try common commands in order and run the first one that exists.

import { spawnSync } from 'node:child_process';

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('Usage: bun run scripts/python-runner.mjs <python args>');
  process.exit(1);
}

// Candidate executables by platform.
const candidates = process.platform === 'win32'
  ? ['py', 'python', 'python3']
  : ['python3', 'python'];

for (const executable of candidates) {
  // Check if executable is available.
  const check = spawnSync(executable, ['--version'], { stdio: 'ignore' });
  if (check.status !== 0) {
    continue;
  }

  // Run requested Python command and return its status.
  const result = spawnSync(executable, args, { stdio: 'inherit' });
  process.exit(result.status ?? 1);
}

console.error('Python not found. Install Python 3 and ensure it is available in PATH.');
process.exit(1);
