#!/usr/bin/env python3
"""Sole-writer for oracle pre-execution snapshot (TD Wave 1)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.abraxas_oracle_pre_execution_snapshot import snapshot  # noqa: E402
from core.canonical.json import write_canonical_json  # noqa: E402


def main() -> None:
    snap = snapshot()
    out = Path("out/oracle_execution/pre_execution_snapshot.v1.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    write_canonical_json(out, snap)
    print("Snapshot written.")


if __name__ == "__main__":
    main()
