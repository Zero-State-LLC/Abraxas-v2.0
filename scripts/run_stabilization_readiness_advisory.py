#!/usr/bin/env python3
"""CLI entry for stabilization readiness advisory (campaign director route)."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "skills" / "abx-stabilization-readiness" / "run_advisory.py"

if __name__ == "__main__":
    sys.argv[0] = str(RUNNER)
    runpy.run_path(str(RUNNER), run_name="__main__")