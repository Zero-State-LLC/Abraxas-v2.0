#!/usr/bin/env python3
"""Sole-writer for oracle pre-execution snapshot (TD Wave 1)."""

from __future__ import annotations

from pathlib import Path

from core.abraxas_oracle_pre_execution_snapshot import snapshot
from core.canonical.json import write_canonical_json


def main() -> None:
    snap = snapshot()
    out = Path("out/oracle_execution/pre_execution_snapshot.v1.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    write_canonical_json(out, snap)
    print("Snapshot written.")


if __name__ == "__main__":
    main()
