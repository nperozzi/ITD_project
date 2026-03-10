# This is necessary to be able run tests in bash.

from __future__ import annotations

import sys
from pathlib import Path


# Ensure tests can import from apps/backend/src regardless of current working dir.
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))
