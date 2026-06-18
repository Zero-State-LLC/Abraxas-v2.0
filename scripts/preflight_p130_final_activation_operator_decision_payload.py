from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.research_canary_final_activation_operator_decision_record import (  # noqa: E402
    DEFAULT_PAYLOAD_PATH,
    P130_PATH,
    _validate_payload,
)

PLACEHOLDER_PREFIX = "REPLACE_WITH_"
ALLOWED_DECISIONS = frozenset(
    {
        "MAINTAIN_ADVISORY_HOLD_ALL_CANDIDATES",
        "APPROVE_ADVISORY_SHADOW_ACTIVATION_PILOT",
    }
)


def _read_json(path: Path) -> dict[str, Any] | None:
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


def validate_payload(
    payload: Mapping[str, Any] | None,
    *,
    p130_packet: Mapping[str, Any] | None,
    template_mode: bool = False,
) -> list[str]:
    if payload is None:
        return ["payload_missing_or_unreadable"]
    blockers: list[str] = []
    if p130_packet is None:
        blockers.append("p130_source_not_observed")
    else:
        blockers.extend(_validate_payload(payload, p130_packet))
        if template_mode and "upstream_packet_hash_mismatch" in blockers:
            blockers = [item for item in blockers if item != "upstream_packet_hash_mismatch"]
    disposition = payload.get("operator_disposition", {})
    selected = disposition.get("selected_decision") if isinstance(disposition, Mapping) else None
    if selected not in ALLOWED_DECISIONS:
        blockers.append("selected_decision_invalid")
    identity = payload.get("operator_identity", {})
    if not isinstance(identity, Mapping) or identity.get("operator_id") != "daniel_meyer":
        blockers.append("operator_id_must_be_daniel_meyer")
    if not template_mode:
        blockers.extend(_placeholder_blockers(payload, "payload"))
        attestation_hash = identity.get("operator_attestation_hash") if isinstance(identity, Mapping) else None
        if isinstance(attestation_hash, str):
            if _is_placeholder(attestation_hash):
                blockers.append("operator_identity.operator_attestation_hash_placeholder_not_allowed")
            elif not attestation_hash.startswith("sha256:"):
                blockers.append("operator_identity.operator_attestation_hash_invalid")
    return sorted(set(blockers))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preflight P130 final activation operator decision payload."
    )
    parser.add_argument("payload_path", nargs="?", default=DEFAULT_PAYLOAD_PATH.as_posix())
    parser.add_argument(
        "--template",
        action="store_true",
        help="Allow REPLACE_WITH_... placeholders in example templates.",
    )
    args = parser.parse_args()
    path = Path(args.payload_path)
    payload = _read_json(path if path.is_absolute() else ROOT / path)
    p130 = _read_json(ROOT / P130_PATH)
    blockers = validate_payload(payload, p130_packet=p130, template_mode=args.template)
    print(f"payload_path: {path.as_posix()}")
    print(f"template_mode: {args.template}")
    print(f"expected_upstream_packet_hash: {p130.get('packet_hash') if p130 else 'NOT_OBSERVED'}")
    print(f"allowed_decisions: {','.join(sorted(ALLOWED_DECISIONS))}")
    print(f"valid: {not blockers}")
    for blocker in blockers:
        print(f"blocker: {blocker}")
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
