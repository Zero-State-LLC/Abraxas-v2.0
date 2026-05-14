"""Script: build and write the global pipeline registry.

Usage:
    python scripts/run_registry.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.canonical.json import write_canonical_json
from core.config import RuntimePaths
from core.pipelines.registry import build_registry, load_contracts

_PATHS = RuntimePaths.from_env()
CONTRACTS_DIR = _PATHS.pipelines_contracts_dir
OUT_PATH = _PATHS.registry_latest


def main() -> None:
    print(f"Loading contracts from {CONTRACTS_DIR} ...")
    contracts = load_contracts(CONTRACTS_DIR)
    print(f"  Loaded {len(contracts)} contracts.")

    registry = build_registry(contracts)
    write_canonical_json(OUT_PATH, registry)
    print(f"Registry written to {OUT_PATH}")
    print(f"  status          : {registry['status']}")
    print(f"  pipeline_count  : {registry['pipeline_count']}")
    print(f"  recommended     : {registry['recommended_next_state']}")


if __name__ == "__main__":
    main()
