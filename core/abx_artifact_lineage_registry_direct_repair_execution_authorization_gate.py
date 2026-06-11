from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan import (
    BLOCKED_ACTIONS as SPEC_PLAN_BLOCKED_ACTIONS,
)
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxArtifactLineageRegistryDirectRepairExecutionAuthorizationGate.v1"
SPEC_PLAN_JSON_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan_001.latest.json"
)
AUTHORIZATION_GATE_JSON_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_gate_001.latest.json"
)
AUTHORIZATION_GATE_MD_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_gate_001.latest.md"
)

BLOCKED_ACTIONS = [
    *SPEC_PLAN_BLOCKED_ACTIONS,
    "EXECUTION_AUTHORITY_GRANT_WITHOUT_OPERATOR_RECORD",
]

REQUIRED_OPERATOR_AUTHORIZATION_FIELDS = [
    "operator_id",
    "operator_name",
    "operator_role",
    "authorization_timestamp_utc",
    "authorization_scope_acknowledged",
    "execution_rationale",
    "runner_casing_policy_decision",
    "notion_mapping_evidence_disposition",
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_abx_artifact_lineage_registry_direct_repair_execution_authorization_gate(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    spec_plan = _read_json(root / SPEC_PLAN_JSON_PATH)
    source_spec_plan_ready = (
        spec_plan.get("schema_version") == "AbxArtifactLineageRegistryDirectRepairSeparateExecutionSpecPlan.v1"
        and spec_plan.get("status")
        == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SEPARATE_EXECUTION_SPEC_PLAN_READY"
        and spec_plan.get("execution_allowed") is False
        and spec_plan.get("repair_execution_performed") is False
        and spec_plan.get("valid_for_execution") is False
        and spec_plan.get("valid_for_repair") is False
    )

    source_blocked_actions = list(spec_plan.get("blocked_actions", []))
    blocked_actions = list(dict.fromkeys([*source_blocked_actions, *BLOCKED_ACTIONS]))

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_GATE",
        "status": "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR"
        if source_spec_plan_ready
        else "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_GATE_BLOCKED",
        "authorization_gate_id": "abx_artifact_lineage_registry_direct_repair_execution_authorization_gate_001",
        "authorization_gate_hash": "",
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_GATE_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "authorization_gate_only": True,
        "source_spec_plan": {
            "source_spec_plan_path": str(SPEC_PLAN_JSON_PATH),
            "source_spec_plan_hash": str(spec_plan.get("spec_plan_hash", "NOT_COMPUTABLE")),
            "source_status": str(spec_plan.get("status", "NOT_COMPUTABLE")),
            "source_authorization_scope": str(spec_plan.get("authorization_scope", "NOT_COMPUTABLE")),
            "source_spec_plan_ready": source_spec_plan_ready,
        },
        "authorization_scope": "DIRECT_REPAIR_EXECUTION_AUTHORIZATION_GATE_ONLY",
        "operator_authorization_required": True,
        "operator_authorization_observed": False,
        "authorization_granted": False,
        "execution_authority": False,
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
        "safe_to_prepare_execution_pr": False,
        "required_operator_authorization_fields": list(REQUIRED_OPERATOR_AUTHORIZATION_FIELDS),
        "required_evidence": list(spec_plan.get("required_evidence", [])),
        "validation_gates": [
            {
                "gate_id": "source_spec_plan_ready_gate",
                "required_status": "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SEPARATE_EXECUTION_SPEC_PLAN_READY",
                "passed": source_spec_plan_ready,
            },
            {
                "gate_id": "operator_authorization_absence_gate",
                "required_value": False,
                "observed_value": False,
                "passed": True,
            },
            {
                "gate_id": "no_execution_authority_gate",
                "required_value": False,
                "observed_value": False,
                "passed": True,
            },
            {
                "gate_id": "blocked_actions_preserved_gate",
                "required_blocked_actions": blocked_actions,
                "passed": all(item in blocked_actions for item in SPEC_PLAN_BLOCKED_ACTIONS),
            },
        ],
        "blocked_actions": blocked_actions,
        "downstream_status": "NOT_COMPUTABLE",
        "recommended_next_lane": "NOT_COMPUTABLE",
        "recommended_next_action": (
            "collect explicit operator authorization evidence before any direct registry, output-pairing, "
            "or docs-reference repair execution; this gate does not grant execution authority"
        ),
        "provenance": {
            "source_spec_plan_path": str(SPEC_PLAN_JSON_PATH),
            "source_spec_plan_hash": str(spec_plan.get("spec_plan_hash", "NOT_COMPUTABLE")),
            "source_spec_plan_status": str(spec_plan.get("status", "NOT_COMPUTABLE")),
            "source_recommended_next_action": str(spec_plan.get("recommended_next_action", "NOT_COMPUTABLE")),
        },
    }
    packet["authorization_gate_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "authorization_gate_hash"}
    )
    return packet


def render_abx_artifact_lineage_registry_direct_repair_execution_authorization_gate_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Artifact Lineage Registry Direct Repair Execution Authorization Gate",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `artifact_id`: `{packet['artifact_id']}`",
        f"- `authorization_scope`: `{packet['authorization_scope']}`",
        f"- `operator_authorization_required`: `{packet['operator_authorization_required']}`",
        f"- `operator_authorization_observed`: `{packet['operator_authorization_observed']}`",
        f"- `authorization_granted`: `{packet['authorization_granted']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        f"- `execution_allowed`: `{packet['execution_allowed']}`",
        f"- `repair_execution_performed`: `{packet['repair_execution_performed']}`",
        f"- `downstream_status`: `{packet['downstream_status']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        "",
        "## Required Operator Authorization Fields",
        "",
    ]
    for item in packet["required_operator_authorization_fields"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Blocked Actions", ""])
    for item in packet["blocked_actions"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Required Evidence", ""])
    for item in packet["required_evidence"]:
        lines.append(f"- `{item}`")
    return lines


def write_abx_artifact_lineage_registry_direct_repair_execution_authorization_gate(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_artifact_lineage_registry_direct_repair_execution_authorization_gate(root)
    write_canonical_json(target_root / AUTHORIZATION_GATE_JSON_PATH, packet)
    _write_markdown(
        target_root / AUTHORIZATION_GATE_MD_PATH,
        render_abx_artifact_lineage_registry_direct_repair_execution_authorization_gate_markdown(packet),
    )
    return packet
