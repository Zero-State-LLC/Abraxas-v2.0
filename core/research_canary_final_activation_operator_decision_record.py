from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

ARTIFACT_TYPE = "ResearchCanaryFinalActivationOperatorDecisionRecord.v1"
LANE_ID = "P131_RESEARCH_CANARY_FINAL_ACTIVATION_OPERATOR_DECISION_RECORD"
UPSTREAM_LANE_ID = "P130_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_REVIEW"
P130_PATH = Path("out/research_canary_final_activation_authorization_review/latest.json")
OUT_PATH = Path("out/research_canary_final_activation_operator_decision_record/latest.json")
DEFAULT_PAYLOAD_PATH = Path(
    "operator_input/p130_final_activation_operator_decision_payload_001.json"
)
P132_LANE = "P132_RESEARCH_CANARY_ADVISORY_SHADOW_ACTIVATION_RECORD"

HOLD_DECISIONS = frozenset({"MAINTAIN_ADVISORY_HOLD_ALL_CANDIDATES"})
SHADOW_ACTIVATION_DECISIONS = frozenset({"APPROVE_ADVISORY_SHADOW_ACTIVATION_PILOT"})

AUTHORITY_LOCK_KEYS: tuple[str, ...] = (
    "production_activation",
    "execution_authority",
    "runtime_authority",
    "scheduler_mutation",
    "canon_promotion",
    "forecast_influence",
    "token_minting_allowed",
    "valid_for_execution",
    "activation_approved",
    "authorization_granted",
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


def _selected_decision(payload: Mapping[str, Any]) -> str | None:
    disposition = payload.get("operator_disposition", {})
    if not isinstance(disposition, Mapping):
        return None
    selected = disposition.get("selected_decision")
    return str(selected) if isinstance(selected, str) else None


def _validate_payload(
    payload: Mapping[str, Any],
    p130_packet: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    upstream = payload.get("upstream_acknowledgement", {})
    if upstream.get("upstream_packet_hash") != p130_packet.get("packet_hash"):
        blockers.append("upstream_packet_hash_mismatch")
    dispositions = payload.get("candidate_dispositions")
    expected = sorted(p130_packet.get("analyzed_candidates", []))
    if not isinstance(dispositions, list):
        blockers.append("candidate_dispositions_missing")
        return blockers
    observed = sorted(
        item.get("candidate_id")
        for item in dispositions
        if isinstance(item, Mapping) and isinstance(item.get("candidate_id"), str)
    )
    if observed != expected:
        blockers.append("candidate_dispositions_mismatch")
    selected = _selected_decision(payload)
    if selected not in HOLD_DECISIONS | SHADOW_ACTIVATION_DECISIONS:
        blockers.append("selected_decision_invalid")
    approved_count = 0
    for item in dispositions:
        if not isinstance(item, Mapping):
            blockers.append("candidate_disposition_malformed")
            continue
        candidate_id = item.get("candidate_id")
        for field in ("execution_authority", "production_activation"):
            if item.get(field) is not False:
                blockers.append(f"candidate_{candidate_id}_{field}_must_be_false")
        activation = item.get("activation_approved")
        status = item.get("status")
        if selected in HOLD_DECISIONS:
            for field in (
                "activation_approved",
                "authorization_granted",
                "production_activation",
                "execution_authority",
            ):
                if item.get(field) is not False:
                    blockers.append(f"candidate_{candidate_id}_{field}_must_be_false")
            if status != "OPERATOR_DECISION_MAINTAIN_HOLD":
                blockers.append(f"candidate_{candidate_id}_status_must_be_maintain_hold")
        elif selected in SHADOW_ACTIVATION_DECISIONS:
            if activation is True:
                approved_count += 1
                if item.get("authorization_granted") is not False:
                    blockers.append(f"candidate_{candidate_id}_authorization_granted_must_be_false")
                if status != "OPERATOR_DECISION_APPROVE_ADVISORY_SHADOW":
                    blockers.append(f"candidate_{candidate_id}_status_must_be_advisory_shadow")
            elif activation is False:
                if status != "OPERATOR_DECISION_MAINTAIN_HOLD":
                    blockers.append(f"candidate_{candidate_id}_status_must_be_maintain_hold")
            else:
                blockers.append(f"candidate_{candidate_id}_activation_approved_invalid")
    if selected in SHADOW_ACTIVATION_DECISIONS and approved_count == 0:
        blockers.append("advisory_shadow_activation_requires_at_least_one_candidate")
    return sorted(set(blockers))


def build_research_canary_final_activation_operator_decision_record(
    repo_root: str | Path = ".",
    attestation_payload_path: str | Path = DEFAULT_PAYLOAD_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    p130 = _read_json(root / P130_PATH)
    payload = _read_json(root / Path(attestation_payload_path))
    base = {
        "lane_id": LANE_ID,
        "artifact_type": ARTIFACT_TYPE,
        "upstream_lane_id": UPSTREAM_LANE_ID,
        "upstream_packet_hash": p130.get("packet_hash") if p130 else None,
        "authority_locks": _authority_locks(),
        "governance_posture": "ADVISORY_ONLY",
        "advisory_only": True,
        "projection_only": True,
    }
    if p130 is None or payload is None:
        return _finalize(
            {
                **base,
                "status": "NOT_COMPUTABLE",
                "lane_status": "NOT_COMPUTABLE",
                "operator_id": NOT_COMPUTABLE,
                "operator_selected_decision": NOT_COMPUTABLE,
                "candidate_decision_records": [],
                "recommended_next_lane": NOT_COMPUTABLE,
            }
        )
    if p130.get("lane_status") != "FINAL_ACTIVATION_AUTHORIZATION_REVIEW_HELD_FOR_OPERATOR":
        return _finalize(
            {
                **base,
                "status": "NOT_COMPUTABLE",
                "lane_status": "NOT_COMPUTABLE",
                "operator_id": NOT_COMPUTABLE,
                "operator_selected_decision": NOT_COMPUTABLE,
                "candidate_decision_records": [],
                "recommended_next_lane": NOT_COMPUTABLE,
            }
        )
    blockers = _validate_payload(payload, p130)
    if blockers:
        return _finalize(
            {
                **base,
                "status": "OPERATOR_DECISION_RECORD_BLOCKED",
                "lane_status": "NOT_COMPUTABLE",
                "operator_id": payload.get("operator_identity", {}).get("operator_id", NOT_COMPUTABLE),
                "operator_selected_decision": payload.get("operator_disposition", {}).get(
                    "selected_decision", NOT_COMPUTABLE
                ),
                "candidate_decision_records": [],
                "recommended_next_lane": NOT_COMPUTABLE,
            }
        )
    identity = payload.get("operator_identity", {})
    disposition = payload.get("operator_disposition", {})
    selected = _selected_decision(payload) or ""
    candidate_records = []
    shadow_approved = False
    for item in sorted(payload.get("candidate_dispositions", []), key=lambda x: x["candidate_id"]):
        if not isinstance(item, Mapping):
            continue
        activation_approved = item.get("activation_approved") is True
        advisory_shadow = activation_approved and selected in SHADOW_ACTIVATION_DECISIONS
        shadow_approved = shadow_approved or advisory_shadow
        candidate_records.append(
            {
                "candidate_id": item["candidate_id"],
                "activation_approved": activation_approved,
                "advisory_shadow_activation_approved": advisory_shadow,
                "authorization_granted": False,
                "production_activation": False,
                "execution_authority": False,
                "status": str(item.get("status", NOT_COMPUTABLE)),
            }
        )
    return _finalize(
        {
            **base,
            "status": "OPERATOR_DECISION_RECORD_EMITTED",
            "lane_status": "OPERATOR_DECISION_RECORD_EMITTED_ADVISORY_ONLY",
            "operator_id": identity.get("operator_id"),
            "operator_selected_decision": disposition.get("selected_decision"),
            "candidate_decision_records": candidate_records,
            "recommended_next_lane": (
                P132_LANE if shadow_approved else NOT_COMPUTABLE
            ),
        }
    )


def write_research_canary_final_activation_operator_decision_record(
    repo_root: str | Path = ".",
    out_path: Path | None = None,
    attestation_payload_path: str | Path = DEFAULT_PAYLOAD_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    packet = build_research_canary_final_activation_operator_decision_record(
        root, attestation_payload_path=attestation_payload_path
    )
    target = out_path if out_path is not None else root / OUT_PATH
    write_canonical_json(target, packet)
    return packet
