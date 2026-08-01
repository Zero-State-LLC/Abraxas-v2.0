#!/usr/bin/env python3
"""Run familiar_ingestion from an EvidencePack.v0 path (SHADOW receipt only).

No network. Validates pack via core.signal, emits FamiliarIngestionReceipt.v0.

Example:
  env -u PYTHONPATH -u PYTHONHOME python \\
    scripts/ingest/run_familiar_ingestion_from_pack.py \\
    --pack skills/abx-familiar-signal-forager/fixtures/evidence_pack_hermes_skill_os_2026-07-27.v0.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.ingest.familiar_ingestion_receipt import (
    build_familiar_ingestion_receipt_from_path,
    write_familiar_ingestion_receipt,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pack",
        type=Path,
        required=True,
        help="Path to EvidencePack.v0 JSON",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output JSON path (default: out/ingest/familiar_ingestion/<pack_stem>_receipt.v0.json)",
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Do not write files; print receipt JSON only",
    )
    args = parser.parse_args(argv)

    receipt = build_familiar_ingestion_receipt_from_path(args.pack, repo_root=ROOT)

    if args.print_only:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        if args.out is not None:
            out_path = args.out
        else:
            stem = Path(args.pack).stem.replace(".v0", "")
            out_dir = ROOT / "out" / "ingest" / "familiar_ingestion"
            out_path = out_dir / f"{stem}_receipt.v0.json"
        write_familiar_ingestion_receipt(
            out_path,
            receipt,
            out_root=ROOT / "out",
        )
        print(json.dumps({"wrote": str(out_path), "status": receipt["status"], "receipt_id": receipt["receipt_id"], "receipt_hash": receipt["receipt_hash"]}, indent=2))

    return 0 if receipt.get("status") == "INGESTED_SHADOW" else 2


if __name__ == "__main__":
    raise SystemExit(main())
