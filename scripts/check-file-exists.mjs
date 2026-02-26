import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, '..');

const relativePath = process.argv[2];
if (!relativePath) {
  console.error('Usage: bun run scripts/check-file-exists.mjs <relative-path>');
  process.exit(1);
}

const targetPath = path.resolve(repoRoot, relativePath);
if (!existsSync(targetPath)) {
  console.error(`Missing required file: ${relativePath}`);
  process.exit(1);
}

console.log(`OK: ${relativePath}`);
