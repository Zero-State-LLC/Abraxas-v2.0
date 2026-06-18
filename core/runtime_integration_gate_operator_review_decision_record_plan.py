from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.runtime_integration_gate_operator_review_dry_run_review import (
    REVIEW_JSON_PATH as SOURCE_REVIEW_JSON_PATH,
)

SCHEMA_VERSION = "RuntimeIntegrationGateOperatorReviewDecisionRecordPlan.v1"
PLAN_ID = "runtime_integration_gate_operator_review_decision_record_plan_001"
PLAN_JSON_PATH = Path(
    "out/audit/runtime_integration_gate_operator_review_decision_record_plan_001.latest.json"
)
PLAN_MD_PATH = PLAN_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = (
    "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DRY_RUN_REVIEW_HELD_FOR_OPERATOR"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return NOT_COMPUTABLE


def _authority_locks() -> dict[str, bool]:
    return {
        "activation_allowed": False,
        "auto_approval_allowed": False,
        "canon_mutation_allowed": False,
        "codegen_implementation_allowed": False,
        "decision_record_creation": False,
        "execution_authority": False,
        "forecast_routing_allowed": False,
        "github_writeback_allowed": False,
        "mandatory_pre_dispatch_wiring": False,
        "notion_writeback_allowed": False,
        "operator_attestation": False,
        "queue_mutation_allowed": False,
        "replay_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "valid_for_execution": False,
        "valid_for_runtime_wiring": False,
    }


def build_runtime_integration_gate_operator_review_decision_record_plan(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    review = _read_json(root / SOURCE_REVIEW_JSON_PATH) or {}
    source_ready = (
        review.get("schema_version") == "RuntimeIntegrationGateOperatorReviewDryRunReview.v1"
        and review.get("status") == EXPECTED_SOURCE_STATUS
        and review.get("source_ready") is True
        and review.get("operator_attestation_present") is False
        and review.get("operator_input_required") is True
        and review.get("recommended_next_lane") == NOT_COMPUTABLE
        and review.get("downstream") == NOT_COMPUTABLE
    )
    required_attestation_fields = [
        "operator_id",
        "operator_name",
        "operator_role",
        "authority_owner_mapping_review_attested",
        "no_authority_seal_review_attested",
        "codegen_boundary_review_attested",
        "receipt_freshness_review_attested",
        "mandatory_pre_dispatch_wiring_denied_acknowledged",
        "runtime_mutation_denied_acknowledged",
        "valid_for_runtime_wiring_denied_acknowledged",
    ]
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "plan_id": PLAN_ID,
        "status": (
            "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DECISION_RECORD_PLAN_READY"
            if source_ready
            else "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DECISION_RECORD_PLAN_BLOCKED"
        ),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "source_review_path": SOURCE_REVIEW_JSON_PATH.as_posix(),
        "source_review_hash": str(review.get("review_hash", NOT_COMPUTABLE)),
        "source_review_ready": source_ready,
        "required_attestation_fields": required_attestation_fields,
        "recommended_default_decision": "HOLD_FOR_OPERATOR_RUNTIME_GATE_REVIEW",
        "decision_record_created": False,
        "decision_record_creation_authorized": False,
        "mandatory_pre_dispatch_wiring": False,
        "valid_for_runtime_wiring": False,
        "runtime_mutation_allowed": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "authority_locks": _authority_locks(),
        "recommended_next_lane": (
            "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DECISION_RECORD_001"
            if source_ready
            else NOT_COMPUTABLE
        ),
        "recommended_next_action": (
            "collect explicit operator attestations for runtime integration gate review "
            "without enabling mandatory pre-dispatch wiring"
            if source_ready
            else "restore runtime integration gate dry-run review evidence"
        ),
        "downstream": NOT_COMPUTABLE,
        "plan_hash": "",
    }
    packet["plan_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "plan_hash"}
    )
    return packet


def render_markdown(packet: Mapping[str, Any]) -> list[str]:
    return [
        "# Runtime Integration Gate Operator Review Decision Record Plan 001",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- status: {packet['status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        "",
        "## Required Attestation Fields",
        *[f"- {field}" for field in packet.get("required_attestation_fields", [])],
    ]


def write_runtime_integration_gate_operator_review_decision_record_plan(
    repo_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_runtime_integration_gate_operator_review_decision_record_plan(root)
    write_canonical_json(target_root / PLAN_JSON_PATH, packet)
    target_root.joinpath(PLAN_MD_PATH).parent.mkdir(parents=True, exist_ok=True)
    target_root.joinpath(PLAN_MD_PATH).write_text(
        "\n".join(render_markdown(packet)) + "\n",
        encoding="utf-8",
    )
    return packet
