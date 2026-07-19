#!/usr/bin/env python3
"""CLI for Artifact & Provenance Service v0 (WP-J)."""

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

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.services.artifact_provenance_service import (  # noqa: E402
    REQUEST_SCHEMA_VERSION,
    SERVICE_ID,
    SERVICE_VERSION,
    execute,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, help="Full request JSON path")
    parser.add_argument(
        "--operation",
        choices=["hash", "dumps", "write", "write_if_changed"],
    )
    parser.add_argument("--payload", type=Path, help="Payload JSON path")
    parser.add_argument("--path", type=str, help="out/... path for write ops")
    args = parser.parse_args()

    if args.request:
        request = json.loads(args.request.read_text(encoding="utf-8"))
    elif args.operation and args.payload:
        request = {
            "schema_version": REQUEST_SCHEMA_VERSION,
            "service_id": SERVICE_ID,
            "service_version": SERVICE_VERSION,
            "operation": args.operation,
            "payload": json.loads(args.payload.read_text(encoding="utf-8")),
        }
        if args.path:
            request["path"] = args.path
    else:
        print("Provide --request or --operation + --payload", file=sys.stderr)
        return 2

    response = execute(request, repo_root=REPO_ROOT)
    print(json.dumps(response, indent=2, sort_keys=True))
    return 0 if response.get("status") == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
