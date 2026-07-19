#!/usr/bin/env python3
"""Sole-writer for oracle execution boundary (TD Wave 1)."""

from __future__ import annotations

import json
from pathlib import Path

from core.abraxas_oracle_execution_boundary import create_execution_boundary
from core.canonical.json import write_canonical_json


def main() -> None:
    b = create_execution_boundary()
    out = Path("out/oracle_execution/execution_boundary.v1.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    write_canonical_json(out, b)
    print(json.dumps(b, indent=2, sort_keys=True))
    print("Boundary written with hash", b["boundary_hash"])


if __name__ == "__main__":
    main()
