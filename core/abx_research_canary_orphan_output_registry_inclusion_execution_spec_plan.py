from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_research_canary_orphan_output_registry_inclusion_constants import (
    INCLUSION_POLICY,
    ORPHAN_OUTPUT_JSON_PATHS,
)
from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "AbxResearchCanaryOrphanOutputRegistryInclusionExecutionSpecPlan.v1"
SPEC_PLAN_ID = "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_SPEC_PLAN_001"
AUTHORIZATION_RECORD_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_operator_authorization_record_001.latest.json"
)
POLICY_REVIEW_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_policy_review_001.latest.json"
)
SPEC_PLAN_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_execution_spec_plan_001.latest.json"
)
SPEC_PLAN_MD_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_execution_spec_plan_001.latest.md"
)
AUTHORIZATION_GATE_LANE = (
    "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_AUTHORIZATION_GATE_001"
)

BLOCKED_ACTIONS = [
    "RESEARCH_CANARY_SPINE_REFRESH",
    "RESEARCH_CANARY_ARTIFACT_REGENERATION",
    "P130_ACTIVATION",
    "CANONICAL_REPAIR_CHAIN_REOPEN",
    "RUNTIME_MUTATION",
    "CANON_MUTATION",
    "QUEUE_MUTATION",
    "UNSCOPED_REGISTRY_MUTATION",
]


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _orphan_inclusion_steps(review: Mapping[str, Any]) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    for index, item in enumerate(review.get("orphan_records", []), start=1):
        if not isinstance(item, dict):
            continue
        steps.append(
            {
                "step_id": f"ORPHAN_INCLUSION_STEP_{index:03d}",
                "output_json_path": str(item.get("output_json_path", NOT_COMPUTABLE)),
                "lane_id_observed": str(item.get("lane_id_observed", NOT_COMPUTABLE)),
                "registry_policy": INCLUSION_POLICY,
                "target_surface": "core/generated_artifact_registry.py _DERIVED_OPTIONAL_ARTIFACTS",
                "execution_allowed": False,
                "registry_mutation_performed": False,
            }
        )
    return sorted(steps, key=lambda step: step["output_json_path"])


def build_abx_research_canary_orphan_output_registry_inclusion_execution_spec_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    authorization = _read_json(root / AUTHORIZATION_RECORD_JSON_PATH)
    review = _read_json(root / POLICY_REVIEW_JSON_PATH)

    source_authorized = (
        authorization.get("schema_version")
        == "AbxResearchCanaryOrphanOutputRegistryInclusionOperatorAuthorizationRecord.v1"
        and authorization.get("status")
        == "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_OPERATOR_AUTHORIZATION_RECORD_EMITTED"
        and authorization.get("inclusion_spec_authoring_approved") is True
        and authorization.get("registry_mutation_performed") is False
        and authorization.get("execution_authority") is False
    )
    steps = _orphan_inclusion_steps(review) if source_authorized else []

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": SPEC_PLAN_ID,
        "status": (
            "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_SPEC_PLAN_READY"
            if source_authorized and len(steps) == len(ORPHAN_OUTPUT_JSON_PATHS)
            else "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_SPEC_PLAN_BLOCKED"
        ),
        "spec_plan_id": SPEC_PLAN_ID,
        "command": "BUILD_ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_SPEC_PLAN_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "authorization_scope": "ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_SPEC_AUTHORING_ONLY",
        "inclusion_policy": INCLUSION_POLICY,
        "orphan_count": len(ORPHAN_OUTPUT_JSON_PATHS),
        "proposed_inclusion_steps": steps,
        "execution_allowed": False,
        "repair_execution_performed": False,
        "registry_mutation_performed": False,
        "implementation_authorized": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "safe_to_auto_continue": False,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "governance_preservation": {
            "p130_hold_preserved": True,
            "research_canary_spine_refresh_performed": False,
            "repair_chain_remains_sealed": True,
            "separate_orphan_registry_governance_required": True,
        },
        "source_authorization_record": {
            "path": str(AUTHORIZATION_RECORD_JSON_PATH),
            "hash": str(authorization.get("authorization_record_hash", NOT_COMPUTABLE)),
            "status": str(authorization.get("status", NOT_COMPUTABLE)),
            "observed": source_authorized,
        },
        "recommended_next_lane": AUTHORIZATION_GATE_LANE if source_authorized else NOT_COMPUTABLE,
        "downstream_status": "READY_FOR_INCLUSION_EXECUTION_AUTHORIZATION_GATE" if source_authorized else NOT_COMPUTABLE,
    }
    return {**packet, "spec_plan_hash": canonical_hash(packet)}


def render_markdown(packet: Mapping[str, Any]) -> list[str]:
    lines = [
        "# ABX Research Canary Orphan Output Registry Inclusion Execution Spec Plan 001",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `inclusion_policy`: `{packet['inclusion_policy']}`",
        f"- `orphan_count`: `{packet['orphan_count']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        "",
        "## Proposed Inclusion Steps",
    ]
    for step in packet.get("proposed_inclusion_steps", []):
        if isinstance(step, dict):
            lines.append(f"- `{step.get('output_json_path')}` → `{step.get('registry_policy')}`")
    return lines


def write_abx_research_canary_orphan_output_registry_inclusion_execution_spec_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_orphan_output_registry_inclusion_execution_spec_plan(root)
    write_canonical_json(target_root / SPEC_PLAN_JSON_PATH, packet)
    _write_markdown(target_root / SPEC_PLAN_MD_PATH, render_markdown(packet))
    return packet
