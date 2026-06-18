from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxResearchCanaryOrphanOutputRegistryPolicyOperatorDecisionRecord.v1"
RECORD_ID = "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_RECORD_001"
PLAN_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan_001.latest.json"
)
POLICY_REVIEW_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_policy_review_001.latest.json"
)
RECORD_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_policy_operator_decision_record_001.latest.json"
)
RECORD_MD_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_policy_operator_decision_record_001.latest.md"
)
CHAIN_CLOSURE_LANE = "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_CHAIN_CLOSURE_RECEIPT_001"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
DEFAULT_DECISION = "MAINTAIN_EXCLUDE_FROM_CANONICAL_REPAIR"
DEFAULT_DISPOSITION = "MAINTAIN_EXCLUDE_FROM_CANONICAL_REPAIR"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _orphan_dispositions(review: Mapping[str, Any]) -> list[dict[str, str]]:
    dispositions: list[dict[str, str]] = []
    for item in review.get("orphan_records", []):
        if not isinstance(item, dict):
            continue
        dispositions.append(
            {
                "output_json_path": str(item.get("output_json_path", NOT_COMPUTABLE)),
                "lane_id_observed": str(item.get("lane_id_observed", NOT_COMPUTABLE)),
                "policy_disposition": DEFAULT_DISPOSITION,
            }
        )
    return sorted(dispositions, key=lambda record: record["output_json_path"])


def build_abx_research_canary_orphan_output_registry_policy_operator_decision_record(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    plan = _read_json(root / PLAN_JSON_PATH)
    review = _read_json(root / POLICY_REVIEW_JSON_PATH)

    plan_ready = (
        plan.get("schema_version") == "AbxResearchCanaryOrphanOutputRegistryPolicyOperatorDecisionRecordPlan.v1"
        and plan.get("status")
        == "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_RECORD_PLAN_READY"
        and plan.get("execution_authority") is False
        and plan.get("registry_mutation_performed") is False
    )
    review_ready = (
        review.get("status") == "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_REVIEW_HELD_FOR_OPERATOR"
        and review.get("orphan_count") == 10
    )
    record_ready = plan_ready and review_ready
    orphan_dispositions = _orphan_dispositions(review) if record_ready else []

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": RECORD_ID,
        "status": (
            "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_RECORD_EMITTED"
            if record_ready
            else "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_RECORD_BLOCKED"
        ),
        "decision_record_id": RECORD_ID,
        "command": "BUILD_ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_RECORD_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "decision_scope": str(plan.get("decision_scope", NOT_COMPUTABLE)),
        "selected_decision": DEFAULT_DECISION if record_ready else NOT_COMPUTABLE,
        "decision_outcome_summary": (
            "All 10 orphan research outputs remain excluded from canonical P103-P130 registry repair. "
            "No registry mutation, P130 activation, orphan inclusion, or execution authority is authorized."
        ),
        "decision_rationale": (
            "Operator maintains orphan exclusion from canonical registry repair per policy review recommendation "
            "while preserving separate orphan registry governance and P130 advisory hold."
        ),
        "operator_id": "thread_operator",
        "operator_name": "appliedalchemylabs",
        "operator_role": "governed_operator",
        "operator_instruction_observed": DEFAULT_DECISION,
        "decision_timestamp_utc": "2026-06-17T00:00:00Z",
        "decision_scope_acknowledged": True,
        "per_orphan_disposition_acknowledged": True,
        "advisory_only_acknowledged": True,
        "non_authoritative_acknowledged": True,
        "execution_authority_denied_acknowledged": True,
        "p130_advisory_hold_preservation_acknowledged": True,
        "separate_orphan_registry_governance_acknowledged": True,
        "runtime_mutation_denied_acknowledged": True,
        "canon_mutation_denied_acknowledged": True,
        "queue_mutation_denied_acknowledged": True,
        "implementation_authorized": False,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "registry_mutation_allowed": False,
        "registry_mutation_performed": False,
        "approval_granted": record_ready,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "safe_to_auto_continue": False,
        "operator_input_required": False,
        "orphan_count": len(orphan_dispositions),
        "per_orphan_dispositions": orphan_dispositions,
        "recommended_next_action": (
            "seal orphan policy governance via chain closure receipt; do not authorize orphan registry inclusion"
            if record_ready
            else "repair decision record plan prerequisites before operator decision record emission"
        ),
        "recommended_next_lane": CHAIN_CLOSURE_LANE if record_ready else NOT_COMPUTABLE,
        "downstream_status": "READY_FOR_ORPHAN_POLICY_CHAIN_CLOSURE" if record_ready else NOT_COMPUTABLE,
        "allowed_follow_on_actions": [
            "SEAL_ORPHAN_POLICY_GOVERNANCE",
            "MAINTAIN_ORPHAN_EXCLUSION",
            "MAINTAIN_P130_ADVISORY_HOLD",
        ],
        "blocked_actions": list(plan.get("disallowed_follow_on_actions", [])),
        "governance_preservation": {
            "p130_hold_preserved": True,
            "orphan_exclusion_preserved": True,
            "research_canary_spine_refresh_performed": False,
            "separate_orphan_registry_governance_required": True,
        },
        "reviewed_request_id": str(plan.get("source_request_id", NOT_COMPUTABLE)),
        "reviewed_request_hash": str(plan.get("source_hashes", {}).get("operator_decision_request", NOT_COMPUTABLE)),
        "reviewed_policy_review_hash": str(plan.get("source_hashes", {}).get("orphan_policy_review", NOT_COMPUTABLE)),
        "source_plan_path": str(PLAN_JSON_PATH),
        "source_plan_hash": str(plan.get("decision_record_plan_hash", NOT_COMPUTABLE)),
    }
    return {**packet, "decision_record_hash": canonical_hash(packet)}


def render_abx_research_canary_orphan_output_registry_policy_operator_decision_record_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Research Canary Orphan Output Registry Policy Operator Decision Record 001",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `selected_decision`: `{packet['selected_decision']}`",
        f"- `orphan_count`: `{packet['orphan_count']}`",
        f"- `registry_mutation_performed`: `{packet['registry_mutation_performed']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        "",
        "## Decision Boundary",
        "",
        str(packet["decision_outcome_summary"]),
        "",
        "## Per-Orphan Dispositions",
    ]
    for item in packet.get("per_orphan_dispositions", []):
        if isinstance(item, dict):
            lines.append(
                f"- `{item.get('output_json_path')}`: `{item.get('policy_disposition')}` "
                f"(`{item.get('lane_id_observed')}`)"
            )
    return lines


def write_abx_research_canary_orphan_output_registry_policy_operator_decision_record(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_orphan_output_registry_policy_operator_decision_record(root)
    write_canonical_json(target_root / RECORD_JSON_PATH, packet)
    _write_markdown(
        target_root / RECORD_MD_PATH,
        render_abx_research_canary_orphan_output_registry_policy_operator_decision_record_markdown(packet),
    )
    return packet
