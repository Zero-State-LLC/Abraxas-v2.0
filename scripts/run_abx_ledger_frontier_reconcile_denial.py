from __future__ import annotations

from pathlib import Path

from scripts.abx_ledger_frontier import (
    DEFAULT_OUT,
    DEFAULT_TIMESTAMP,
    FRONTIER_STATUS,
    build_receipt,
    write_receipt,
)

DEFAULT_COMMIT = "7815e720"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    receipt = build_receipt(root, DEFAULT_COMMIT, DEFAULT_TIMESTAMP)
    write_receipt(root / DEFAULT_OUT, receipt)
    print(f"receipt_status: {FRONTIER_STATUS}")
    print(f"canonical_hash: {receipt['canonical_hash']}")
    print(f"receipt_path: {DEFAULT_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
