from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxArtifactLineageRegistryDirectRepairExecutionAuthorizationRecord.v1"
AUTHORIZATION_GATE_JSON_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_gate_001.latest.json"
)
AUTHORIZATION_RECORD_JSON_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_record_001.latest.json"
)
AUTHORIZATION_RECORD_MD_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_record_001.latest.md"
)
SCOPED_EXECUTION_RECEIPT_JSON_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_001.latest.json"
)

SCOPED_REPAIR_ACTIONS = [
    "DIRECT_REGISTRY_REPAIR_EXECUTION_PR_PREPARATION",
    "OUTPUT_PAIRING_REPAIR_EXECUTION_PR_PREPARATION",
    "DOCS_REFERENCE_REPAIR_EXECUTION_PR_PREPARATION",
]

BLOCKED_ACTIONS = [
    "RUNNER_CASING_POLICY_OVERRIDE",
    "NOTION_MAPPING_COMPLETENESS_CLAIM",
    "RUNTIME_MUTATION",
    "CANON_MUTATION",
    "QUEUE_MUTATION",
    "LIVE_NOTION_WRITEBACK",
    "GITHUB_WRITEBACK_AUTOMATION",
    "UNSCOPED_REPAIR_EXECUTION",
    "REPAIR_EXECUTION_WITHOUT_VALIDATION_PR",
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_optional_json(path: Path) -> dict[str, Any]:
    try:
        return _read_json(path)
    except (OSError, json.JSONDecodeError):
        return {}


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_abx_artifact_lineage_registry_direct_repair_execution_authorization_record(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    gate = _read_json(root / AUTHORIZATION_GATE_JSON_PATH)
    gate_ready = (
        gate.get("schema_version") == "AbxArtifactLineageRegistryDirectRepairExecutionAuthorizationGate.v1"
        and gate.get("status")
        == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR"
        and gate.get("operator_authorization_required") is True
        and gate.get("authorization_granted") is False
        and gate.get("execution_authority") is False
        and gate.get("execution_allowed") is False
        and gate.get("repair_execution_performed") is False
        and gate.get("valid_for_execution") is False
        and gate.get("valid_for_repair") is False
    )
    scoped_receipt = _read_optional_json(root / SCOPED_EXECUTION_RECEIPT_JSON_PATH)
    scoped_receipt_observed = (
        scoped_receipt.get("schema_version")
        == "AbxArtifactLineageRegistryDirectRepairScopedExecutionReceipt.v1"
        and scoped_receipt.get("status")
        == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SCOPED_EXECUTION_RECEIPT_EMITTED"
        and scoped_receipt.get("repair_execution_performed") is True
        and scoped_receipt.get("execution_allowed") is False
        and scoped_receipt.get("valid_for_execution") is False
        and scoped_receipt.get("valid_for_repair") is False
    )
    consumed_by_scoped_receipt = gate_ready and scoped_receipt_observed

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_RECORD",
        "status": (
            "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_RECORD_CONSUMED_BY_SCOPED_EXECUTION_RECEIPT"
            if consumed_by_scoped_receipt
            else "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_RECORD_GRANTED_FOR_SCOPED_EXECUTION_PR"
            if gate_ready
            else "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_RECORD_BLOCKED"
        ),
        "authorization_record_id": "abx_artifact_lineage_registry_direct_repair_execution_authorization_record_001",
        "authorization_record_hash": "",
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_RECORD_001",
        "advisory_only": False,
        "projection_only": False,
        "non_authoritative": False,
        "authorization_record_only": True,
        "source_authorization_gate": {
            "source_authorization_gate_path": str(AUTHORIZATION_GATE_JSON_PATH),
            "source_authorization_gate_hash": str(gate.get("authorization_gate_hash", "NOT_COMPUTABLE")),
            "source_status": str(gate.get("status", "NOT_COMPUTABLE")),
            "source_gate_ready": gate_ready,
        },
        "operator_authorization": {
            "operator_id": "thread_operator",
            "operator_name": "appliedalchemylabs",
            "operator_role": "governed_operator",
            "operator_instruction_observed": "authorize",
            "authorization_timestamp_utc": "2026-06-11T00:00:00Z",
            "authorization_scope_acknowledged": "SCOPED_DIRECT_ARTIFACT_LINEAGE_REPAIR_EXECUTION_PR_ONLY",
            "execution_rationale": (
                "Operator authorized continuation from the held execution authorization gate into a scoped "
                "direct repair execution PR preparation lane."
            ),
            "runner_casing_policy_decision": "NO_RUNNER_CASING_POLICY_OVERRIDE_AUTHORIZED",
            "notion_mapping_evidence_disposition": "NO_NOTION_MAPPING_COMPLETENESS_CLAIM_AUTHORIZED",
        },
        "authorization_scope": "SCOPED_DIRECT_ARTIFACT_LINEAGE_REPAIR_EXECUTION_PR_ONLY",
        "authorization_granted": gate_ready,
        "execution_authority": gate_ready,
        "execution_allowed": False,
        "repair_execution_performed": False,
        "implementation_authorized": gate_ready,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_execution_pr": gate_ready and not consumed_by_scoped_receipt,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "notion_completeness_claim_allowed": False,
        "runner_casing_policy_override_allowed": False,
        "github_writeback_allowed": False,
        "notion_writeback_allowed": False,
        "scoped_repair_actions": list(SCOPED_REPAIR_ACTIONS),
        "blocked_actions": list(BLOCKED_ACTIONS),
        "required_pre_execution_validation": [
            "pre_repair_registry_gap_snapshot",
            "pre_repair_output_pairing_gap_snapshot",
            "pre_repair_docs_reference_gap_snapshot",
            "scoped_repair_diff_review",
            "post_repair_validation_plan",
            "fast_ci_before_pr",
        ],
        "validation_gates": [
            {
                "gate_id": "source_gate_ready_for_operator_authorization",
                "required_status": "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR",
                "passed": gate_ready,
            },
            {
                "gate_id": "operator_authorization_observed_gate",
                "required_instruction": "authorize",
                "observed_instruction": "authorize",
                "passed": True,
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
            "status": str(scoped_receipt.get("status", "NOT_COMPUTABLE")),
            "observed": consumed_by_scoped_receipt,
        },
        "downstream_status": (
            "SCOPED_EXECUTION_RECEIPT_OBSERVED"
            if consumed_by_scoped_receipt
            else "READY_FOR_SCOPED_EXECUTION_PR_PREPARATION"
            if gate_ready
            else "NOT_COMPUTABLE"
        ),
        "recommended_next_lane": (
            "ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_REGENERATION"
            if consumed_by_scoped_receipt
            else "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SCOPED_EXECUTION_PR"
            if gate_ready
            else "NOT_COMPUTABLE"
        ),
        "recommended_next_action": (
            "scoped direct repair receipt has been observed; do not prepare another execution PR from this authorization record"
            if consumed_by_scoped_receipt
            else "prepare a scoped direct repair execution PR that fixes registry/output-pairing/docs-reference gaps only; "
            "do not override runner casing policy, claim Notion mapping completeness, or mutate runtime/canon/queue state"
        ),
        "provenance": {
            "source_authorization_gate_path": str(AUTHORIZATION_GATE_JSON_PATH),
            "source_authorization_gate_hash": str(gate.get("authorization_gate_hash", "NOT_COMPUTABLE")),
            "source_authorization_gate_status": str(gate.get("status", "NOT_COMPUTABLE")),
            "source_recommended_next_action": str(gate.get("recommended_next_action", "NOT_COMPUTABLE")),
        },
    }
    packet["authorization_record_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "authorization_record_hash"}
    )
    return packet


def render_abx_artifact_lineage_registry_direct_repair_execution_authorization_record_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Artifact Lineage Registry Direct Repair Execution Authorization Record",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `artifact_id`: `{packet['artifact_id']}`",
        f"- `authorization_scope`: `{packet['authorization_scope']}`",
        f"- `authorization_granted`: `{packet['authorization_granted']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        f"- `execution_allowed`: `{packet['execution_allowed']}`",
        f"- `repair_execution_performed`: `{packet['repair_execution_performed']}`",
        f"- `safe_to_prepare_execution_pr`: `{packet['safe_to_prepare_execution_pr']}`",
        f"- `downstream_status`: `{packet['downstream_status']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        "",
        "## Scoped Repair Actions",
        "",
    ]
    for item in packet["scoped_repair_actions"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Blocked Actions", ""])
    for item in packet["blocked_actions"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Required Pre-Execution Validation", ""])
    for item in packet["required_pre_execution_validation"]:
        lines.append(f"- `{item}`")
    return lines


def write_abx_artifact_lineage_registry_direct_repair_execution_authorization_record(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_artifact_lineage_registry_direct_repair_execution_authorization_record(root)
    write_canonical_json(target_root / AUTHORIZATION_RECORD_JSON_PATH, packet)
    _write_markdown(
        target_root / AUTHORIZATION_RECORD_MD_PATH,
        render_abx_artifact_lineage_registry_direct_repair_execution_authorization_record_markdown(packet),
    )
    return packet
