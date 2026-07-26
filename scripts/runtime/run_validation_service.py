#!/usr/bin/env python3
"""CLI entry for Validation Service v1 (WP-B).

Usage:
  python scripts/runtime/run_validation_service.py --request path/to/request.json
  python scripts/runtime/run_validation_service.py --schema-ref contracts/... --payload path.json

Does not write to out/ by default (stdout only). Optional --out uses canonical writer.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SCRIPT_DIR_KEY = _SCRIPT_DIR.casefold()
sys.path = [
    path
    for path in sys.path
    if os.path.abspath(path or os.curdir).casefold() != _SCRIPT_DIR_KEY
]

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.services.validation_service import (
    REQUEST_SCHEMA_VERSION,
    SERVICE_ID,
    SERVICE_VERSION,
    validate,
)


def main() -> int:
    import warnings

    warnings.warn(
        (
            "scripts.runtime.run_validation_service is a compatibility shim. "
            "Prefer: `python -m abraxas validate --schema-ref ... --payload ...` "
            "(removal target: abraxas>=3.0 / Production Convergence CLEAR phase)."
        ),
        DeprecationWarning,
        stacklevel=2,
    )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, help="Path to full request JSON")
    parser.add_argument("--schema-ref", type=str, help="contracts/... schema path")
    parser.add_argument("--payload", type=Path, help="Path to payload JSON")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional path to write response via canonical JSON writer",
    )
    args = parser.parse_args()

    if args.request:
        request = json.loads(args.request.read_text(encoding="utf-8"))
    elif args.schema_ref and args.payload:
        request = {
            "schema_version": REQUEST_SCHEMA_VERSION,
            "service_id": SERVICE_ID,
            "service_version": SERVICE_VERSION,
            "schema_ref": args.schema_ref,
            "payload": json.loads(args.payload.read_text(encoding="utf-8")),
        }
    else:
        print("Provide --request or both --schema-ref and --payload", file=sys.stderr)
        return 2

    response = validate(request, repo_root=REPO_ROOT)
    text = json.dumps(response, indent=2, sort_keys=True) + "\n"
    print(text, end="")
    if args.out is not None:
        # Optional --out may be outside repo out/; confine to the destination parent.
        write_classified_json(
            args.out,
            response,
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
            out_root=args.out.resolve().parent,
        )

    if response.get("status") == "ERROR":
        return 1
    if response.get("status") == "OK" and response.get("valid") is False:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
