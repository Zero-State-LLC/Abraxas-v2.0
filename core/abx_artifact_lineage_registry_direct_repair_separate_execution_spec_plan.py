from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxArtifactLineageRegistryDirectRepairSeparateExecutionSpecPlan.v1"
DECISION_RECORD_JSON_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_001.latest.json"
)
SPEC_PLAN_JSON_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan_001.latest.json"
)
SPEC_PLAN_MD_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan_001.latest.md"
)

BLOCKED_ACTIONS = [
    "DIRECT_REGISTRY_REPAIR_EXECUTION",
    "OUTPUT_PAIRING_REPAIR_EXECUTION",
    "DOCS_REFERENCE_REPAIR_EXECUTION",
    "RUNNER_CASING_POLICY_OVERRIDE",
    "NOTION_MAPPING_COMPLETENESS_CLAIM",
    "RUNTIME_MUTATION",
    "CANON_MUTATION",
    "QUEUE_MUTATION",
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    decision = _read_json(root / DECISION_RECORD_JSON_PATH)
    source_authorized = (
        decision.get("schema_version") == "AbxArtifactLineageRegistryDirectRepairOperatorDecisionRecord.v1"
        and decision.get("selected_decision") == "AUTHORIZE_SEPARATE_DIRECT_REPAIR_EXECUTION_SPEC"
        and decision.get("separate_execution_spec_authoring_approved") is True
        and decision.get("implementation_authorized") is False
        and decision.get("execution_authority") is False
        and decision.get("valid_for_repair") is False
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SEPARATE_EXECUTION_SPEC_PLAN",
        "status": "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SEPARATE_EXECUTION_SPEC_PLAN_READY"
        if source_authorized
        else "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SEPARATE_EXECUTION_SPEC_PLAN_BLOCKED",
        "spec_plan_id": "abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan_001",
        "spec_plan_hash": "",
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SEPARATE_EXECUTION_SPEC_PLAN_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "source_authorization": {
            "source_decision_record_path": str(DECISION_RECORD_JSON_PATH),
            "source_decision_record_hash": str(decision.get("decision_record_hash", "NOT_COMPUTABLE")),
            "source_status": str(decision.get("status", "NOT_COMPUTABLE")),
            "selected_decision": str(decision.get("selected_decision", "NOT_COMPUTABLE")),
            "spec_authoring_approved": source_authorized,
        },
        "authorization_scope": "SEPARATE_DIRECT_REPAIR_EXECUTION_SPEC_AUTHORING_ONLY",
        "execution_allowed": False,
        "repair_execution_performed": False,
        "implementation_authorized": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "notion_completeness_claim_allowed": False,
        "runner_casing_policy_override_allowed": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_planning_pr": False,
        "required_evidence": [
            "final_operator_authorization_for_direct_repair_execution",
            "runner_casing_policy_decision",
            "notion_mapping_evidence_or_explicit_notion_scope_exclusion",
            "pre_repair_registry_gap_snapshot",
            "pre_repair_output_pairing_gap_snapshot",
            "pre_repair_docs_reference_gap_snapshot",
            "post_repair_validation_plan",
        ],
        "proposed_phases": [
            {
                "phase_id": "DIRECT_REPAIR_SPEC_PHASE_001",
                "phase_name": "registry_gap_classification",
                "execution_allowed": False,
                "repair_execution_performed": False,
            },
            {
                "phase_id": "DIRECT_REPAIR_SPEC_PHASE_002",
                "phase_name": "output_pairing_gap_classification",
                "execution_allowed": False,
                "repair_execution_performed": False,
            },
            {
                "phase_id": "DIRECT_REPAIR_SPEC_PHASE_003",
                "phase_name": "docs_reference_gap_classification",
                "execution_allowed": False,
                "repair_execution_performed": False,
            },
            {
                "phase_id": "DIRECT_REPAIR_SPEC_PHASE_004",
                "phase_name": "future_operator_authorization_gate",
                "execution_allowed": False,
                "repair_execution_performed": False,
            },
        ],
        "validation_gates": [
            {
                "gate_id": "source_authorization_scope_gate",
                "required_status": "AUTHORIZE_SEPARATE_DIRECT_REPAIR_EXECUTION_SPEC",
                "passed": source_authorized,
            },
            {
                "gate_id": "no_repair_execution_gate",
                "required_value": False,
                "observed_value": False,
                "passed": True,
            },
            {
                "gate_id": "blocked_actions_preserved_gate",
                "required_blocked_actions": list(BLOCKED_ACTIONS),
                "passed": True,
            },
            {
                "gate_id": "future_operator_authorization_required_gate",
                "required_before": "any direct repair execution",
                "passed": True,
            },
        ],
        "blocked_actions": list(BLOCKED_ACTIONS),
        "blocked_delivery_surfaces": [
            "core/generated_artifact_registry.py direct repair mutations",
            "out/* generated repair target rewrites",
            "Scripts runner casing normalization",
            "Notion mapping completeness assertions",
            "runtime route or scheduler mutations",
        ],
        "downstream_status": "NOT_COMPUTABLE",
        "recommended_next_lane": "NOT_COMPUTABLE",
        "recommended_next_action": (
            "review the separate execution spec plan; require a future explicit operator authorization gate before "
            "any direct registry, output-pairing, or docs-reference repair execution"
        ),
        "provenance": {
            "source_decision_record_path": str(DECISION_RECORD_JSON_PATH),
            "source_decision_record_hash": str(decision.get("decision_record_hash", "NOT_COMPUTABLE")),
            "source_decision_record_status": str(decision.get("status", "NOT_COMPUTABLE")),
            "source_recommended_next_patch": str(decision.get("recommended_next_patch", "NOT_COMPUTABLE")),
        },
    }
    packet["spec_plan_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "spec_plan_hash"})
    return packet


def render_abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Artifact Lineage Registry Direct Repair Separate Execution Spec Plan",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `artifact_id`: `{packet['artifact_id']}`",
        f"- `authorization_scope`: `{packet['authorization_scope']}`",
        f"- `execution_allowed`: `{packet['execution_allowed']}`",
        f"- `repair_execution_performed`: `{packet['repair_execution_performed']}`",
        f"- `downstream_status`: `{packet['downstream_status']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        "",
        "## Proposed Phases",
        "",
    ]
    for item in packet["proposed_phases"]:
        lines.append(f"- `{item['phase_id']}`: `{item['phase_name']}`")
    lines.extend(["", "## Blocked Actions", ""])
    for item in packet["blocked_actions"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Required Evidence", ""])
    for item in packet["required_evidence"]:
        lines.append(f"- `{item}`")
    return lines


def write_abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan(root)
    write_canonical_json(target_root / SPEC_PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / SPEC_PLAN_MD_PATH,
        render_abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan_markdown(packet),
    )
    return packet
