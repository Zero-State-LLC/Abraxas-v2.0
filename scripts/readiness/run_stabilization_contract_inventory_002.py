#!/usr/bin/env python
"""Runner for WO-ABX-STABILIZATION-CONTRACT-INVENTORY-002.

Emits complete executable contract inventory with ownership and cross-language evidence.
"""

import sys
from pathlib import Path

# Ensure repo root on path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.contract_inventory.discovery_002 import run_contract_inventory_002

def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = run_contract_inventory_002(repo_root)
    print(f"contract inventory 002: {result['status']} -> {result['output']} (contracts={result['contract_count']})")

if __name__ == "__main__":
    main()
