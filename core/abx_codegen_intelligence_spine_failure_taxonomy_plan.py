from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_artifact_registry_integration_plan import (
    OUT_JSON as SOURCE_ARTIFACT_REGISTRY_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineFailureTaxonomyPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_FAILURE_TAXONOMY_PLAN_001"
OUT_JSON = "out/audit/abx_codegen_intelligence_spine_failure_taxonomy_plan_001.latest.json"
OUT_MD = "out/audit/abx_codegen_intelligence_spine_failure_taxonomy_plan_001.latest.md"

NOTION_SPEC = {
    "title": "Error & Failure Taxonomy - Codegen Intelligence Spine",
    "page_id": "37d3e8ba-2f5c-8140-963c-e1379a660411",
    "observed_as_of": "2026-06-12",
    "status": "Planning Spec (Advisory)",
}

EXPECTED_SOURCE_STATUS = "ABX_CODEGEN_ARTIFACT_REGISTRY_INTEGRATION_PLAN_READY"


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _read_json(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _categories(source_ready: bool) -> list[dict[str, Any]]:
    status = "PLANNING_ONLY" if source_ready else "NOT_COMPUTABLE"
    return [
        {
            "category": "Validation",
            "code_prefix": "VAL-",
            "description": "Problems with the structure or content of an ImprovementProposal.v1",
            "taxonomy_status": status,
            "automated_response_authorized": False,
        },
        {
            "category": "Replay",
            "code_prefix": "RPL-",
            "description": "Failures during deterministic shadow replay execution",
            "taxonomy_status": status,
            "automated_response_authorized": False,
        },
        {
            "category": "Governance",
            "code_prefix": "GOV-",
            "description": "Violations of authority locks, self-modification rules, or policy",
            "taxonomy_status": status,
            "automated_response_authorized": False,
        },
        {
            "category": "Meta-Gate",
            "code_prefix": "META-",
            "description": "Issues specific to the elevated self-improvement path",
            "taxonomy_status": status,
            "automated_response_authorized": False,
        },
        {
            "category": "Integration",
            "code_prefix": "INT-",
            "description": "Problems with upstream/downstream systems such as Continuity or Registry",
            "taxonomy_status": status,
            "automated_response_authorized": False,
        },
        {
            "category": "Internal",
            "code_prefix": "INTL-",
            "description": "Unexpected errors inside the harness itself",
            "taxonomy_status": status,
            "automated_response_authorized": False,
        },
    ]


def _error_codes(source_ready: bool) -> list[dict[str, Any]]:
    status = "PLANNING_ONLY" if source_ready else "NOT_COMPUTABLE"
    rows = [
        ("VAL-001", "Validation", "Missing required field in proposal", ["REJECT", "REFINE_PROPOSAL"]),
        ("VAL-002", "Validation", "Invalid enum value such as bad proposal_type", ["REJECT", "REFINE_PROPOSAL"]),
        ("VAL-003", "Validation", "Malformed contract_deltas", ["REJECT", "REFINE_PROPOSAL"]),
        (
            "VAL-004",
            "Validation",
            "self_modification_risk set without proper justification",
            ["REJECT", "REFINE_PROPOSAL"],
        ),
        ("RPL-001", "Replay", "Hash divergence across runs", ["BLOCK_REPLAY_FAILURE", "HOLD_FOR_OPERATOR"]),
        (
            "RPL-002",
            "Replay",
            "Insufficient replay run count completed",
            ["BLOCK_REPLAY_FAILURE", "HOLD_FOR_OPERATOR"],
        ),
        ("RPL-003", "Replay", "Missing required proof flags", ["BLOCK_REPLAY_FAILURE", "HOLD_FOR_OPERATOR"]),
        (
            "RPL-004",
            "Replay",
            "Replay timed out or exceeded resource limits",
            ["BLOCK_REPLAY_FAILURE", "HOLD_FOR_OPERATOR"],
        ),
        (
            "RPL-005",
            "Replay",
            "Contract delta application failed during simulation",
            ["BLOCK_REPLAY_FAILURE", "HOLD_FOR_OPERATOR"],
        ),
        (
            "GOV-001",
            "Governance",
            "Attempt to modify Red Zone surface",
            ["BLOCK_POLICY_VIOLATION"],
        ),
        (
            "GOV-002",
            "Governance",
            "Self-modification detected without Meta-Gate path",
            ["BLOCK_POLICY_VIOLATION"],
        ),
        (
            "GOV-003",
            "Governance",
            "Governance compliance flag false after replay",
            ["BLOCK_POLICY_VIOLATION"],
        ),
        ("GOV-004", "Governance", "Authority lock violation observed", ["BLOCK_POLICY_VIOLATION"]),
        (
            "META-001",
            "Meta-Gate",
            "Meta-Gate invariants not satisfied",
            ["HOLD_FOR_META_GATE", "BLOCK_POLICY_VIOLATION"],
        ),
        (
            "META-002",
            "Meta-Gate",
            "Elevated governance rent requirements not met",
            ["HOLD_FOR_META_GATE", "BLOCK_POLICY_VIOLATION"],
        ),
        (
            "META-003",
            "Meta-Gate",
            "Attempt to bypass Meta-Gate on self-improvement proposal",
            ["HOLD_FOR_META_GATE", "BLOCK_POLICY_VIOLATION"],
        ),
        ("INT-001", "Integration", "Failed to register artifact in Artifact Registry", ["HOLD_FOR_OPERATOR"]),
        ("INT-002", "Integration", "Continuity lane creation failed", ["HOLD_FOR_OPERATOR"]),
        (
            "INT-003",
            "Integration",
            "Upstream diagnosis packet malformed or missing",
            ["HOLD_FOR_OPERATOR"],
        ),
        ("INTL-001", "Internal", "Unexpected exception in harness", ["HOLD_FOR_OPERATOR"]),
        ("INTL-002", "Internal", "Canonical JSON serialization failure", ["HOLD_FOR_OPERATOR"]),
    ]
    return [
        {
            "error_code": code,
            "category": category,
            "description": description,
            "recommended_responses": responses,
            "taxonomy_status": status,
            "response_authorized": False,
        }
        for code, category, description, responses in rows
    ]


def _promotion_blockers(source_ready: bool) -> list[dict[str, Any]]:
    status = "PLANNING_ONLY" if source_ready else "NOT_COMPUTABLE"
    return [
        {
            "error_code": "RPL-001",
            "promotion_blocker": "replay_hash_divergence",
            "mapping_status": status,
            "receipt_mutation_authorized": False,
        },
        {
            "error_code": "GOV-003",
            "promotion_blocker": "governance_compliance_failed",
            "mapping_status": status,
            "receipt_mutation_authorized": False,
        },
        {
            "error_code": "GOV-002",
            "promotion_blocker": "self_modification_detected",
            "mapping_status": status,
            "receipt_mutation_authorized": False,
        },
    ]


def build_abx_codegen_intelligence_spine_failure_taxonomy_plan(
    *,
    repo_root: str | Path,
    source_artifact_registry_integration_plan_path: str | Path = SOURCE_ARTIFACT_REGISTRY_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_artifact_registry_integration_plan_path).as_posix()
    source = _read_json(root / source_artifact_registry_integration_plan_path)
    source_ready = (
        source.get("artifact_type")
        == "AbxCodegenIntelligenceSpineArtifactRegistryIntegrationPlan.v1"
        and source.get("artifact_registry_integration_plan_status") == EXPECTED_SOURCE_STATUS
        and source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and source.get("safe_to_auto_continue") is False
        and source.get("execution_authority") is False
        and source.get("valid_for_implementation") is False
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "failure_taxonomy_plan_status": (
            "ABX_CODEGEN_FAILURE_TAXONOMY_PLAN_READY" if source_ready else "NOT_COMPUTABLE"
        ),
        "source_notion_spec": {
            **NOTION_SPEC,
            "spec_hash_policy": "source_observed_metadata_only",
            "notion_writeback_performed": False,
        },
        "source_artifact_registry_integration_plan": {
            "path": source_path,
            "hash": _sha256(root / source_artifact_registry_integration_plan_path),
            "artifact_registry_integration_plan_status": str(
                source.get("artifact_registry_integration_plan_status", "NOT_COMPUTABLE")
            ),
            "recommended_next_lane": str(source.get("recommended_next_lane", "NOT_COMPUTABLE")),
            "source_ready": source_ready,
        },
        "top_level_categories": _categories(source_ready),
        "detailed_error_codes": _error_codes(source_ready),
        "promotion_blocker_mapping": _promotion_blockers(source_ready),
        "response_strategy_by_category": [
            {
                "category": "Validation",
                "strategy": "Early rejection with clear feedback to proposer",
                "strategy_status": "PLANNING_ONLY" if source_ready else "NOT_COMPUTABLE",
                "automated_response_authorized": False,
            },
            {
                "category": "Replay/Governance",
                "strategy": "Hard BLOCK or HOLD with populated blockers",
                "strategy_status": "PLANNING_ONLY" if source_ready else "NOT_COMPUTABLE",
                "automated_response_authorized": False,
            },
            {
                "category": "Meta-Gate",
                "strategy": "Route to Meta-Gate process or hard block",
                "strategy_status": "PLANNING_ONLY" if source_ready else "NOT_COMPUTABLE",
                "automated_response_authorized": False,
            },
            {
                "category": "Integration/Internal",
                "strategy": "HOLD_FOR_OPERATOR with operator investigation",
                "strategy_status": "PLANNING_ONLY" if source_ready else "NOT_COMPUTABLE",
                "automated_response_authorized": False,
            },
        ],
        "recommended_next_lane": "NOT_COMPUTABLE",
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "authority_locks": {
            "auto_approval": False,
            "automated_failure_routing": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "harness_implementation": False,
            "meta_gate_authorization": False,
            "meta_gate_process_execution": False,
            "notion_writeback": False,
            "operator_decision_record_creation": False,
            "promotion_blocker_mutation": False,
            "queue_mutation": False,
            "registry_registration": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "shadow_replay_execution": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_failure_taxonomy_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_failure_taxonomy_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Failure Taxonomy Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- failure_taxonomy_plan_status: {packet['failure_taxonomy_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Top-Level Categories",
    ]
    for category in packet.get("top_level_categories", []):
        if isinstance(category, Mapping):
            lines.append(
                f"- {category['category']} ({category['code_prefix']}): "
                f"{category['taxonomy_status']}"
            )
    lines.extend(["", "## Promotion Blocker Mapping"])
    for mapping in packet.get("promotion_blocker_mapping", []):
        if isinstance(mapping, Mapping):
            lines.append(
                f"- {mapping['error_code']} -> {mapping['promotion_blocker']} "
                f"(receipt_mutation_authorized={mapping['receipt_mutation_authorized']})"
            )
    return lines


def write_abx_codegen_intelligence_spine_failure_taxonomy_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(render_abx_codegen_intelligence_spine_failure_taxonomy_plan_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
