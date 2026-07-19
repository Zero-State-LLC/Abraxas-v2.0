from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_PAYLOAD = Path(
    "operator_input/daniel_meyer_operator_hold_clearance_attestation_001.json"
)
REQUIRED_GROUPS = (
    "operator_identity",
    "clearance_scope",
    "authority_boundary_acknowledgement",
)
PLACEHOLDER_PREFIX = "REPLACE_WITH_"


def _read_json(path: Path) -> dict | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _is_placeholder(value: Any) -> bool:
    return isinstance(value, str) and value.startswith(PLACEHOLDER_PREFIX)


def _placeholder_blockers(value: Any, prefix: str) -> list[str]:
    blockers: list[str] = []
    if _is_placeholder(value):
        blockers.append(f"{prefix}_placeholder_not_allowed")
    if isinstance(value, Mapping):
        for key, item in value.items():
            blockers.extend(_placeholder_blockers(item, f"{prefix}.{key}"))
    return blockers


def validate_payload(payload: dict | None, *, template_mode: bool = False) -> list[str]:
    if payload is None:
        return ["payload_missing_or_unreadable"]
    blockers: list[str] = []
    for group in REQUIRED_GROUPS:
        if not isinstance(payload.get(group), dict):
            blockers.append(f"{group}_missing")
    identity = payload.get("operator_identity", {})
    if identity.get("operator_id") != "daniel_meyer":
        blockers.append("operator_id_must_be_daniel_meyer")
    attestation_hash = identity.get("operator_attestation_hash")
    if not isinstance(attestation_hash, str) or not attestation_hash.strip():
        blockers.append("operator_attestation_hash_invalid")
    elif not template_mode:
        if _is_placeholder(attestation_hash):
            blockers.append("operator_attestation_hash_placeholder_not_allowed")
        elif not attestation_hash.startswith("sha256:"):
            blockers.append("operator_attestation_hash_invalid")
    if not template_mode:
        blockers.extend(_placeholder_blockers(payload, "payload"))
    return sorted(set(blockers))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preflight Daniel Meyer operator hold clearance attestation payload."
    )
    parser.add_argument("payload_path", nargs="?", default=DEFAULT_PAYLOAD.as_posix())
    parser.add_argument(
        "--template",
        action="store_true",
        help="Allow REPLACE_WITH_... placeholders in example templates.",
    )
    args = parser.parse_args()
    path = Path(args.payload_path)
    payload = _read_json(path if path.is_absolute() else ROOT / path)
    blockers = validate_payload(payload, template_mode=args.template)
    print(f"payload_path: {path.as_posix()}")
    print(f"template_mode: {args.template}")
    print(f"valid: {not blockers}")
    for blocker in blockers:
        print(f"blocker: {blocker}")
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
