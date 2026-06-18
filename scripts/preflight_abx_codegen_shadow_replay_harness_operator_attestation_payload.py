from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.abx_codegen_shadow_replay_harness_operator_attestation_intake_gate import (  # noqa: E402
    DEFAULT_PAYLOAD_PATH,
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def validate_envelope_shape(payload: Mapping[str, Any] | None) -> list[str]:
    if payload is None:
        return ["payload_missing_or_unreadable"]
    blockers: list[str] = []
    for field in ("payload_id", "payload_version", "created_at"):
        if not payload.get(field):
            blockers.append(f"{field}_missing")
    for field in ("operator", "scope", "attestation", "governance", "seal", "downstream"):
        if not isinstance(payload.get(field), Mapping):
            blockers.append(f"{field}_missing")
    return sorted(set(blockers))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preflight codegen shadow replay harness operator attestation payload."
    )
    parser.add_argument("payload_path", nargs="?", default=DEFAULT_PAYLOAD_PATH.as_posix())
    args = parser.parse_args()
    path = Path(args.payload_path)
    payload = _read_json(path if path.is_absolute() else ROOT / path)
    blockers = validate_envelope_shape(payload)
    print(f"payload_path: {path.as_posix()}")
    print(f"valid_envelope_shape: {not blockers}")
    for blocker in blockers:
        print(f"blocker: {blocker}")
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
