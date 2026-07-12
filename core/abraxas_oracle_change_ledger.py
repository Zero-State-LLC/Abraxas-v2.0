#!/usr/bin/env python3
"""
Abraxas Oracle Change Ledger v1

Deterministic ledger for every modification during oracle-guided execution.
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any

LEDGER_PATH = Path("out/oracle_execution/change_ledger.v1.json")

def stable_hash(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]

def load_ledger() -> List[Dict[str, Any]]:
    if LEDGER_PATH.exists():
        return json.loads(LEDGER_PATH.read_text())
    return []

def append_entry(entry: Dict[str, Any]) -> None:
    ledger = load_ledger()
    entry["sequence"] = len(ledger) + 1
    entry["ledger_hash"] = stable_hash(entry)
    ledger.append(entry)
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.write_text(json.dumps(ledger, indent=2, sort_keys=True))

def record_change(path: str, operation: str, reason: str, candidate_requirement: str, before_hash: str | None, after_hash: str, within_boundary: bool = True) -> Dict[str, Any]:
    entry = {
        "path": path,
        "operation": operation,
        "reason": reason,
        "candidate_requirement": candidate_requirement,
        "before_hash": before_hash,
        "after_hash": after_hash,
        "within_boundary": within_boundary,
        "authority_effect": "NONE",
        "canon_effect": "NONE",
        "production_effect": "NONE"
    }
    append_entry(entry)
    return entry

if __name__ == "__main__":
    print("Ledger module ready. Use record_change().")
