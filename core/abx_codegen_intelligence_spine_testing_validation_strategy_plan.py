from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_failure_taxonomy_plan import (
    OUT_JSON as SOURCE_FAILURE_TAXONOMY_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineTestingValidationStrategyPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_TESTING_VALIDATION_STRATEGY_PLAN_001"
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_testing_validation_strategy_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_testing_validation_strategy_plan_001.latest.md"
)

NOTION_SPEC = {
    "title": "Testing & Validation Strategy - Codegen Intelligence Spine",
    "page_id": "37d3e8ba-2f5c-8152-9f8c-d88593af42c1",
    "observed_as_of": "2026-06-12",
    "status": "Planning Spec (Advisory)",
}

EXPECTED_SOURCE_STATUS = "ABX_CODEGEN_FAILURE_TAXONOMY_PLAN_READY"


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


def _layers(source_ready: bool) -> list[dict[str, Any]]:
    layer_status = "PLANNING_ONLY" if source_ready else "NOT_COMPUTABLE"
    return [
        {
            "layer": "Unit Tests",
            "requirements": [
                "Harness validation functions",
                "Config building",
                "Proof flag evaluation",
                "Recommendation logic",
                "Schema validation for all packet types",
            ],
            "layer_status": layer_status,
            "test_implementation_authorized": False,
            "harness_execution_authorized": False,
        },
        {
            "layer": "Integration Tests",
            "requirements": [
                "Proposal to Replay to Receipt flow",
                "Meta-Gate path testing for self-modification proposals",
                "Error injection and recovery testing",
            ],
            "layer_status": layer_status,
            "test_implementation_authorized": False,
            "harness_execution_authorized": False,
        },
        {
            "layer": "Property-Based / Determinism Tests",
            "requirements": [
                "12-run invariance",
                "24-run invariance for Meta-Gate",
                "Hash consistency across identical inputs and seed",
                "Replay safety under different constraint settings",
            ],
            "layer_status": layer_status,
            "test_implementation_authorized": False,
            "harness_execution_authorized": False,
        },
        {
            "layer": "Adversarial / Negative Tests",
            "requirements": [
                "Use adversarial fixtures already created",
                "Boundary violations such as Red Zone modifications",
                "Malformed proposals and missing fields",
            ],
            "layer_status": layer_status,
            "test_implementation_authorized": False,
            "harness_execution_authorized": False,
        },
        {
            "layer": "Governance Compliance Tests",
            "requirements": [
                "Verify forbidden actions are blocked early",
                "Confirm promotion_blockers are correctly populated",
                "Ensure self-modification always routes to Meta-Gate",
            ],
            "layer_status": layer_status,
            "test_implementation_authorized": False,
            "harness_execution_authorized": False,
        },
    ]


def build_abx_codegen_intelligence_spine_testing_validation_strategy_plan(
    *,
    repo_root: str | Path,
    source_failure_taxonomy_plan_path: str | Path = SOURCE_FAILURE_TAXONOMY_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_failure_taxonomy_plan_path).as_posix()
    source = _read_json(root / source_failure_taxonomy_plan_path)
    source_ready = (
        source.get("artifact_type") == "AbxCodegenIntelligenceSpineFailureTaxonomyPlan.v1"
        and source.get("failure_taxonomy_plan_status") == EXPECTED_SOURCE_STATUS
        and source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and source.get("safe_to_auto_continue") is False
        and source.get("execution_authority") is False
        and source.get("valid_for_implementation") is False
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "testing_validation_strategy_plan_status": (
            "ABX_CODEGEN_TESTING_VALIDATION_STRATEGY_PLAN_READY"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_notion_spec": {
            **NOTION_SPEC,
            "spec_hash_policy": "source_observed_metadata_only",
            "notion_writeback_performed": False,
        },
        "source_failure_taxonomy_plan": {
            "path": source_path,
            "hash": _sha256(root / source_failure_taxonomy_plan_path),
            "failure_taxonomy_plan_status": str(
                source.get("failure_taxonomy_plan_status", "NOT_COMPUTABLE")
            ),
            "recommended_next_lane": str(source.get("recommended_next_lane", "NOT_COMPUTABLE")),
            "source_ready": source_ready,
        },
        "testing_layers": _layers(source_ready),
        "recommended_test_structure": {
            "root": "tests/codegen/",
            "files": [
                "test_harness.py",
                "test_schemas.py",
                "test_meta_gate.py",
                "test_error_taxonomy.py",
            ],
            "fixture_directories": ["fixtures/golden/", "fixtures/adversarial/"],
            "structure_status": "PLANNING_ONLY" if source_ready else "NOT_COMPUTABLE",
            "directory_creation_authorized": False,
            "test_file_creation_authorized": False,
        },
        "golden_fixture_strategy": {
            "normal_proposal_pairs_required": True,
            "self_improvement_proposal_pairs_required": True,
            "sample_fixtures_may_seed_strategy": True,
            "adversarial_cases_may_seed_strategy": True,
            "fixture_generation_authorized": False,
            "fixture_promotion_authorized": False,
        },
        "continuous_validation": {
            "all_tests_deterministic": True,
            "all_tests_replay_safe": True,
            "property_based_testing_recommended": True,
            "governance_tests_in_regular_suite": True,
            "hypothesis_dependency_authorized": False,
            "harness_test_execution_authorized": False,
            "meta_gate_test_execution_authorized": False,
        },
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
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "dependency_addition": False,
            "file_writeback": False,
            "fixture_generation": False,
            "forecast_routing": False,
            "github_writeback": False,
            "harness_implementation": False,
            "harness_test_execution": False,
            "meta_gate_authorization": False,
            "meta_gate_test_execution": False,
            "notion_writeback": False,
            "operator_decision_record_creation": False,
            "property_based_test_execution": False,
            "queue_mutation": False,
            "registry_registration": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "shadow_replay_execution": False,
            "test_file_creation": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_testing_validation_strategy_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_testing_validation_strategy_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Testing Validation Strategy Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- testing_validation_strategy_plan_status: {packet['testing_validation_strategy_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Testing Layers",
    ]
    for layer in packet.get("testing_layers", []):
        if isinstance(layer, Mapping):
            lines.append(
                f"- {layer['layer']}: {layer['layer_status']} "
                f"(test_implementation_authorized={layer['test_implementation_authorized']})"
            )
    lines.extend(["", "## Continuous Validation"])
    continuous = packet.get("continuous_validation", {})
    if isinstance(continuous, Mapping):
        lines.append(f"- all_tests_deterministic: {continuous['all_tests_deterministic']}")
        lines.append(f"- all_tests_replay_safe: {continuous['all_tests_replay_safe']}")
        lines.append(
            f"- harness_test_execution_authorized: {continuous['harness_test_execution_authorized']}"
        )
    return lines


def write_abx_codegen_intelligence_spine_testing_validation_strategy_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_testing_validation_strategy_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
