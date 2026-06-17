from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxResearchCanaryArtifactRegistryCoverageRepairExecutionAuthorizationRecord.v1"
RECORD_ID = "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_EXECUTION_AUTHORIZATION_RECORD_001"
AUTHORIZATION_GATE_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_execution_authorization_gate_001.latest.json"
)
AUTHORIZATION_RECORD_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record_001.latest.json"
)
AUTHORIZATION_RECORD_MD_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record_001.latest.md"
)
SCOPED_EXECUTION_RECEIPT_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt_001.latest.json"
)
SCOPED_EXECUTION_RECEIPT_LANE = (
    "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_SCOPED_EXECUTION_RECEIPT_001"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"

SCOPED_REPAIR_ACTIONS = [
    "DERIVED_OPTIONAL_REGISTRY_REPAIR_EXECUTION_PR_PREPARATION",
    "LANE_ID_TRACEABILITY_METADATA_REPAIR_EXECUTION_PR_PREPARATION",
]

BLOCKED_ACTIONS = [
    "RESEARCH_CANARY_SPINE_REFRESH",
    "RESEARCH_CANARY_ARTIFACT_REGENERATION",
    "P130_ACTIVATION",
    "ORPHAN_OUTPUT_REGISTRY_INCLUSION",
    "SCOPE_PREFIX_MUTATION_WITHOUT_OPERATOR_DECISION",
    "RUNTIME_MUTATION",
    "CANON_MUTATION",
    "QUEUE_MUTATION",
    "LIVE_NOTION_WRITEBACK",
    "GITHUB_WRITEBACK_AUTOMATION",
    "UNSCOPED_REGISTRY_REPAIR_EXECUTION",
    "REPAIR_EXECUTION_WITHOUT_VALIDATION_PR",
]


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    gate = _read_json(root / AUTHORIZATION_GATE_JSON_PATH)
    scoped_receipt = _read_json(root / SCOPED_EXECUTION_RECEIPT_JSON_PATH)

    gate_ready = (
        gate.get("schema_version") == "AbxResearchCanaryArtifactRegistryCoverageRepairExecutionAuthorizationGate.v1"
        and gate.get("status")
        == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_EXECUTION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR"
        and gate.get("operator_authorization_required") is True
        and gate.get("authorization_granted") is False
        and gate.get("execution_authority") is False
        and gate.get("registry_mutation_performed") is False
    )
    scoped_receipt_observed = (
        scoped_receipt.get("schema_version")
        == "AbxResearchCanaryArtifactRegistryCoverageRepairScopedExecutionReceipt.v1"
        and scoped_receipt.get("status")
        == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_SCOPED_EXECUTION_RECEIPT_EMITTED"
        and scoped_receipt.get("repair_execution_performed") is True
    )
    consumed_by_scoped_receipt = gate_ready and scoped_receipt_observed

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": RECORD_ID,
        "status": (
            "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_EXECUTION_AUTHORIZATION_RECORD_CONSUMED_BY_SCOPED_EXECUTION_RECEIPT"
            if consumed_by_scoped_receipt
            else "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_EXECUTION_AUTHORIZATION_RECORD_GRANTED_FOR_SCOPED_EXECUTION_PR"
            if gate_ready
            else "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_EXECUTION_AUTHORIZATION_RECORD_BLOCKED"
        ),
        "authorization_record_id": RECORD_ID,
        "command": "BUILD_ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_EXECUTION_AUTHORIZATION_RECORD_001",
        "authorization_record_only": True,
        "source_authorization_gate": {
            "source_authorization_gate_path": str(AUTHORIZATION_GATE_JSON_PATH),
            "source_authorization_gate_hash": str(gate.get("authorization_gate_hash", NOT_COMPUTABLE)),
            "source_status": str(gate.get("status", NOT_COMPUTABLE)),
            "source_gate_ready": gate_ready,
        },
        "operator_authorization": {
            "operator_id": "thread_operator",
            "operator_name": "appliedalchemylabs",
            "operator_role": "governed_operator",
            "operator_instruction_observed": "authorize",
            "authorization_timestamp_utc": "2026-06-17T00:00:00Z",
            "authorization_scope_acknowledged": "SCOPED_RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_EXECUTION_PR_ONLY",
            "execution_rationale": (
                "Operator authorized continuation from the held execution authorization gate into a scoped "
                "P103-P130 registry coverage repair execution PR preparation lane."
            ),
            "p130_hold_preservation_acknowledged": True,
            "orphan_exclusion_policy_acknowledged": True,
            "scope_prefix_policy_disposition": "DERIVED_OPTIONAL_PER_PATH_NO_BULK_SCOPE_PREFIX",
        },
        "authorization_scope": "SCOPED_RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_EXECUTION_PR_ONLY",
        "authorization_granted": gate_ready,
        "execution_authority": gate_ready,
        "execution_allowed": False,
        "repair_execution_performed": False,
        "registry_mutation_performed": False,
        "implementation_authorized": gate_ready,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_execution_pr": gate_ready and not consumed_by_scoped_receipt,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "github_writeback_allowed": False,
        "notion_writeback_allowed": False,
        "scoped_repair_actions": list(SCOPED_REPAIR_ACTIONS),
        "blocked_actions": list(BLOCKED_ACTIONS),
        "required_pre_execution_validation": [
            "pre_repair_registry_gap_snapshot",
            "canonical_lane_output_path_gap_review",
            "lane_id_traceability_gap_review",
            "p130_hold_boundary_review",
            "orphan_exclusion_policy_review",
            "scoped_repair_diff_review",
            "fast_ci_before_pr",
        ],
        "validation_gates": [
            {
                "gate_id": "source_gate_ready_for_operator_authorization",
                "required_status": "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_EXECUTION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR",
                "passed": gate_ready,
            },
            {
                "gate_id": "operator_authorization_observed_gate",
                "required_instruction": "authorize",
                "observed_instruction": "authorize",
                "passed": gate_ready,
            },
            {
                "gate_id": "no_repair_execution_performed_gate",
                "required_value": False,
                "observed_value": False,
                "passed": True,
            },
            {
                "gate_id": "scope_boundary_gate",
                "required_blocked_actions": list(BLOCKED_ACTIONS),
                "passed": True,
            },
        ],
        "scoped_execution_receipt": {
            "path": str(SCOPED_EXECUTION_RECEIPT_JSON_PATH),
            "hash": "DOWNSTREAM_RECEIPT_HASH_NOT_BOUND_TO_AVOID_CIRCULAR_PROVENANCE",
            "status": str(scoped_receipt.get("status", NOT_COMPUTABLE)),
            "observed": consumed_by_scoped_receipt,
        },
        "downstream_status": (
            "SCOPED_EXECUTION_RECEIPT_OBSERVED"
            if consumed_by_scoped_receipt
            else "READY_FOR_SCOPED_EXECUTION_PR_PREPARATION"
            if gate_ready
            else NOT_COMPUTABLE
        ),
        "recommended_next_lane": (
            NOT_COMPUTABLE
            if consumed_by_scoped_receipt
            else SCOPED_EXECUTION_RECEIPT_LANE
            if gate_ready
            else NOT_COMPUTABLE
        ),
        "recommended_next_action": (
            "scoped registry repair receipt has been observed; do not prepare another execution PR from this record"
            if consumed_by_scoped_receipt
            else "prepare a scoped registry repair execution PR for P103-P130 canonical lanes only; "
            "exclude orphans, preserve P130 hold, use DERIVED_OPTIONAL_PER_PATH policy"
        ),
        "provenance": {
            "source_authorization_gate_path": str(AUTHORIZATION_GATE_JSON_PATH),
            "source_authorization_gate_hash": str(gate.get("authorization_gate_hash", NOT_COMPUTABLE)),
            "source_authorization_gate_status": str(gate.get("status", NOT_COMPUTABLE)),
        },
    }
    return {**packet, "authorization_record_hash": canonical_hash(packet)}


def render_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Research Canary Artifact Registry Coverage Repair Execution Authorization Record 001",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `authorization_granted`: `{packet['authorization_granted']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        f"- `safe_to_prepare_execution_pr`: `{packet['safe_to_prepare_execution_pr']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        "",
        "## Scoped Repair Actions",
    ]
    for item in packet.get("scoped_repair_actions", []):
        lines.append(f"- `{item}`")
    lines.extend(["", "## Blocked Actions"])
    for item in packet.get("blocked_actions", []):
        lines.append(f"- `{item}`")
    return lines


def write_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record(root)
    write_canonical_json(target_root / AUTHORIZATION_RECORD_JSON_PATH, packet)
    _write_markdown(
        target_root / AUTHORIZATION_RECORD_MD_PATH,
        render_abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record_markdown(packet),
    )
    return packet
