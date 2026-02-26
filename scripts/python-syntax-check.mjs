import { spawnSync } from "node:child_process";

const rootPath = process.argv[2];
if (!rootPath) {
  console.error("Usage: bun run scripts/python-syntax-check.mjs <root-path>");
  process.exit(1);
}

const candidates =
  process.platform === "win32"
    ? ["py", "python", "python3"]
    : ["python3", "python"];

const pythonCode = `
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
if not root.exists():
    print(f"Path does not exist: {root}")
    sys.exit(1)

had_error = False
for py_file in sorted(root.rglob('*.py')):
    try:
        source = py_file.read_text(encoding='utf-8')
        compile(source, str(py_file), 'exec')
    except SyntaxError as exc:
        had_error = True
        print(f"SyntaxError in {py_file}:{exc.lineno}:{exc.offset} - {exc.msg}")

if had_error:
    sys.exit(1)

print(f"OK: Python syntax check passed for {root}")
`;

for (const executable of candidates) {
  const check = spawnSync(executable, ["--version"], { stdio: "ignore" });
  if (check.status !== 0) {
    continue;
  }

  const result = spawnSync(executable, ["-c", pythonCode, rootPath], {
    stdio: "inherit",
  });
  process.exit(result.status ?? 1);
}

console.error(
  "Python not found. Install Python 3 and ensure it is available in PATH.",
);
process.exit(1);
