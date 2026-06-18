from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.research_canary_final_activation_operator_decision_record import (
    DEFAULT_PAYLOAD_PATH,
    build_research_canary_final_activation_operator_decision_record,
)

ARTIFACT_TYPE = "ResearchCanaryAdvisoryShadowActivationRecord.v1"
LANE_ID = "P132_RESEARCH_CANARY_ADVISORY_SHADOW_ACTIVATION_RECORD"
UPSTREAM_LANE_ID = "P131_RESEARCH_CANARY_FINAL_ACTIVATION_OPERATOR_DECISION_RECORD"
OUT_PATH = Path("out/research_canary_advisory_shadow_activation_record/latest.json")
P131_EMITTED_STATUS = "OPERATOR_DECISION_RECORD_EMITTED"
NOT_COMPUTABLE = "NOT_COMPUTABLE"

AUTHORITY_LOCK_KEYS: tuple[str, ...] = (
    "production_activation",
    "execution_authority",
    "runtime_authority",
    "scheduler_mutation",
    "canon_promotion",
    "forecast_influence",
    "token_minting_allowed",
    "valid_for_execution",
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _authority_locks() -> dict[str, bool]:
    return {key: False for key in AUTHORITY_LOCK_KEYS}


def advisory_shadow_activation_eligible(
    p131_packet: Mapping[str, Any] | None,
) -> bool:
    if p131_packet is None:
        return False
    if p131_packet.get("status") != P131_EMITTED_STATUS:
        return False
    records = p131_packet.get("candidate_decision_records", [])
    if not isinstance(records, list):
        return False
    return any(
        isinstance(item, Mapping) and item.get("advisory_shadow_activation_approved") is True
        for item in records
    )


def build_research_canary_advisory_shadow_activation_record(
    repo_root: str | Path = ".",
    attestation_payload_path: str | Path = DEFAULT_PAYLOAD_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    p131 = build_research_canary_final_activation_operator_decision_record(
        root, attestation_payload_path=attestation_payload_path
    )
    payload = _read_json(root / Path(attestation_payload_path))
    base = {
        "lane_id": LANE_ID,
        "artifact_type": ARTIFACT_TYPE,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_packet_hash": p131.get("packet_hash") if p131 else None,
        "authority_locks": _authority_locks(),
        "governance_posture": "ADVISORY_ONLY",
        "advisory_only": True,
        "projection_only": True,
        "recommended_next_lane": NOT_COMPUTABLE,
    }
    if p131 is None or payload is None:
        return _finalize(
            {
                **base,
                "status": "NOT_COMPUTABLE",
                "lane_status": "NOT_COMPUTABLE",
                "operator_id": NOT_COMPUTABLE,
                "operator_attestation_hash": NOT_COMPUTABLE,
                "candidate_activation_records": [],
            }
        )
    if not advisory_shadow_activation_eligible(p131):
        return _finalize(
            {
                **base,
                "status": "RESEARCH_CANARY_ADVISORY_SHADOW_ACTIVATION_RECORD_BLOCKED",
                "lane_status": "NOT_COMPUTABLE",
                "operator_id": p131.get("operator_id", NOT_COMPUTABLE),
                "operator_attestation_hash": (
                    payload.get("operator_identity", {}).get("operator_attestation_hash", NOT_COMPUTABLE)
                    if isinstance(payload.get("operator_identity"), Mapping)
                    else NOT_COMPUTABLE
                ),
                "candidate_activation_records": [],
            }
        )
    identity = payload.get("operator_identity", {})
    records = []
    for item in sorted(p131.get("candidate_decision_records", []), key=lambda x: x["candidate_id"]):
        if not isinstance(item, Mapping):
            continue
        records.append(
            {
                "candidate_id": item["candidate_id"],
                "advisory_shadow_activation_approved": (
                    item.get("advisory_shadow_activation_approved") is True
                ),
                "wiring_mode": "SHADOW_ADVISORY_ONLY",
                "execution_authority": False,
                "production_activation": False,
            }
        )
    return _finalize(
        {
            **base,
            "status": "RESEARCH_CANARY_ADVISORY_SHADOW_ACTIVATION_RECORD_EMITTED",
            "lane_status": "ADVISORY_SHADOW_ACTIVATION_RECORD_EMITTED",
            "operator_id": identity.get("operator_id") if isinstance(identity, Mapping) else NOT_COMPUTABLE,
            "operator_attestation_hash": (
                identity.get("operator_attestation_hash")
                if isinstance(identity, Mapping)
                else NOT_COMPUTABLE
            ),
            "candidate_activation_records": records,
        }
    )


def write_research_canary_advisory_shadow_activation_record(
    repo_root: str | Path = ".",
    out_path: Path | None = None,
    attestation_payload_path: str | Path = DEFAULT_PAYLOAD_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    packet = build_research_canary_advisory_shadow_activation_record(
        root, attestation_payload_path=attestation_payload_path
    )
    target = out_path if out_path is not None else root / OUT_PATH
    write_canonical_json(target, packet)
    return packet
