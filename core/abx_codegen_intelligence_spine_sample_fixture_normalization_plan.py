from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_fixture_validation_harness_plan import (
    OUT_JSON as SOURCE_FIXTURE_VALIDATION_HARNESS_PLAN_JSON,
)
from core.abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan import (
    OUT_JSON as SOURCE_SAMPLE_META_GATE_CHAIN_VALIDATION_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineSampleFixtureNormalizationPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_SAMPLE_FIXTURE_NORMALIZATION_PLAN_001"
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_sample_fixture_normalization_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_sample_fixture_normalization_plan_001.latest.md"
)

EXPECTED_FIXTURE_HARNESS_STATUS = (
    "ABX_CODEGEN_INTELLIGENCE_SPINE_FIXTURE_VALIDATION_HARNESS_PLAN_READY"
)
EXPECTED_SAMPLE_CHAIN_STATUS = "ABX_CODEGEN_SAMPLE_META_GATE_CHAIN_VALIDATION_PLAN_HELD_FOR_OPERATOR"

NOTION_SPEC = {
    "title": "Codegen Intelligence Spine - Sample Fixtures & Test Vectors v1",
    "page_id": "37d3e8ba-2f5c-81d8-bfea-c295f875e36d",
    "observed_as_of": "2026-06-12",
    "status": "Advisory Planning Samples",
    "version": "v1",
    "timestamp_policy": "source_observed_example_values_only_no_wall_clock_generation",
}


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


def _fixture_inventory(repo_root: Path) -> dict[str, Any]:
    fixture_root = repo_root / "tests/fixtures/codegen"
    fixtures: list[dict[str, str]] = []
    for target in sorted(fixture_root.glob("*.json")):
        fixtures.append(
            {
                "path": target.relative_to(repo_root).as_posix(),
                "fixture_class": "NEGATIVE" if target.name.startswith("invalid_") else "VALID",
                "source_hash": _sha256(target),
            }
        )
    return {
        "fixture_root": "tests/fixtures/codegen",
        "fixture_count": len(fixtures),
        "valid_fixture_count": sum(
            1 for fixture in fixtures if fixture["fixture_class"] == "VALID"
        ),
        "negative_fixture_count": sum(
            1 for fixture in fixtures if fixture["fixture_class"] == "NEGATIVE"
        ),
        "fixtures": fixtures,
    }


def _planning_status(sources_ready: bool) -> str:
    return "SAMPLE_FIXTURE_NORMALIZATION_DEFINED_HELD_FOR_OPERATOR" if sources_ready else "NOT_COMPUTABLE"


def build_abx_codegen_intelligence_spine_sample_fixture_normalization_plan(
    *,
    repo_root: str | Path,
    source_fixture_validation_harness_plan_path: str
    | Path = SOURCE_FIXTURE_VALIDATION_HARNESS_PLAN_JSON,
    source_sample_meta_gate_chain_validation_plan_path: str
    | Path = SOURCE_SAMPLE_META_GATE_CHAIN_VALIDATION_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    fixture_plan_path = Path(source_fixture_validation_harness_plan_path).as_posix()
    sample_chain_path = Path(source_sample_meta_gate_chain_validation_plan_path).as_posix()
    fixture_plan = _read_json(root / source_fixture_validation_harness_plan_path)
    sample_chain_plan = _read_json(root / source_sample_meta_gate_chain_validation_plan_path)

    fixture_plan_ready = (
        fixture_plan.get("artifact_type")
        == "AbxCodegenIntelligenceSpineFixtureValidationHarnessPlan.v1"
        and fixture_plan.get("plan_status") == EXPECTED_FIXTURE_HARNESS_STATUS
        and fixture_plan.get("advisory_only") is True
        and fixture_plan.get("valid_for_execution") is False
        and fixture_plan.get("valid_for_implementation") is False
    )
    sample_chain_ready = (
        sample_chain_plan.get("artifact_type")
        == "AbxCodegenIntelligenceSpineSampleMetaGateChainValidationPlan.v1"
        and sample_chain_plan.get("sample_meta_gate_chain_validation_plan_status")
        == EXPECTED_SAMPLE_CHAIN_STATUS
        and sample_chain_plan.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and sample_chain_plan.get("safe_to_auto_continue") is False
        and sample_chain_plan.get("execution_authority") is False
        and sample_chain_plan.get("valid_for_implementation") is False
    )
    sources_ready = fixture_plan_ready and sample_chain_ready
    status = _planning_status(sources_ready)
    fixture_inventory = _fixture_inventory(root)

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "sample_fixture_normalization_plan_status": (
            "ABX_CODEGEN_SAMPLE_FIXTURE_NORMALIZATION_PLAN_HELD_FOR_OPERATOR"
            if sources_ready
            else "NOT_COMPUTABLE"
        ),
        "source_notion_spec": {**NOTION_SPEC, "notion_writeback_performed": False},
        "source_fixture_validation_harness_plan": {
            "path": fixture_plan_path,
            "hash": _sha256(root / source_fixture_validation_harness_plan_path),
            "plan_status": str(fixture_plan.get("plan_status", "NOT_COMPUTABLE")),
            "source_ready": fixture_plan_ready,
        },
        "source_sample_meta_gate_chain_validation_plan": {
            "path": sample_chain_path,
            "hash": _sha256(root / source_sample_meta_gate_chain_validation_plan_path),
            "sample_meta_gate_chain_validation_plan_status": str(
                sample_chain_plan.get(
                    "sample_meta_gate_chain_validation_plan_status", "NOT_COMPUTABLE"
                )
            ),
            "source_ready": sample_chain_ready,
        },
        "notion_sample_classes": [
            {
                "sample_class": "GapDiagnosisPacket.v1 self-diagnosis",
                "sample_status": status,
                "fixture_use": "reference_only_requires_normalization",
            },
            {
                "sample_class": "ImprovementProposal.v1 normal refactor",
                "sample_status": status,
                "fixture_use": "reference_only_requires_normalization",
            },
            {
                "sample_class": "ImprovementProposal.v1 self-improvement",
                "sample_status": status,
                "fixture_use": "reference_only_requires_normalization",
            },
            {
                "sample_class": "ShadowImprovementReceipt.v1 successful shadow run",
                "sample_status": status,
                "fixture_use": "reference_only_requires_normalization",
            },
            {
                "sample_class": "ShadowImprovementReceipt.v1 self-modification hold",
                "sample_status": status,
                "fixture_use": "reference_only_requires_normalization",
            },
            {
                "sample_class": "Adversarial negative cases A-D",
                "sample_status": status,
                "fixture_use": "negative_fixture_requirements_only",
            },
            {
                "sample_class": "v1.1 HOLD/BLOCK receipt examples E-F",
                "sample_status": status,
                "fixture_use": "governance_recommendation_requirements_only",
            },
        ],
        "normalization_requirements": [
            {
                "requirement": "replace_source_observed_timestamps_with_deterministic_fixture_values",
                "requirement_status": status,
                "normalization_execution_authorized": False,
            },
            {
                "requirement": "replace_illustrative_or_notional_hashes_with_real_fixture_hashes",
                "requirement_status": status,
                "normalization_execution_authorized": False,
            },
            {
                "requirement": "remove_json_comments_and_ellipsis_before_schema_validation",
                "requirement_status": status,
                "normalization_execution_authorized": False,
            },
            {
                "requirement": "preserve_hold_block_recommendation_semantics",
                "requirement_status": status,
                "normalization_execution_authorized": False,
            },
            {
                "requirement": "keep_promote_to_canary_operator_review_required",
                "requirement_status": status,
                "normalization_execution_authorized": False,
            },
            {
                "requirement": "never_treat_samples_as_observed_runtime_receipts",
                "requirement_status": status,
                "normalization_execution_authorized": False,
            },
        ],
        "negative_case_expectations": [
            {
                "case_id": "A",
                "expected_rejection_reasons": [
                    "missing_evidence_hash",
                    "self_diagnosis_severity_too_low",
                ],
            },
            {
                "case_id": "B",
                "expected_rejection_reasons": [
                    "invalid_canon_promotion_path",
                    "missing_operator_decision_required_for_self_modification",
                ],
            },
            {
                "case_id": "C",
                "expected_rejection_reasons": [
                    "governance_violation_with_promote_recommendation",
                    "invariance_failure_with_promote_recommendation",
                    "self_modification_without_operator_review",
                ],
            },
            {
                "case_id": "D",
                "expected_rejection_reasons": [
                    "missing_provenance_source_gap_analysis",
                    "core_policy_mutation_attempt",
                ],
            },
            {
                "case_id": "E",
                "expected_rejection_reasons": [],
                "required_semantics": ["HOLD_FOR_META_GATE", "promotion_blockers_present"],
            },
            {
                "case_id": "F",
                "expected_rejection_reasons": [],
                "required_semantics": ["BLOCK_REPLAY_FAILURE", "promotion_blockers_present"],
            },
        ],
        "repo_fixture_alignment": {
            **fixture_inventory,
            "repo_fixtures_are_canonical_test_material": True,
            "notion_samples_are_canonical_test_material": False,
            "fixture_write_authorized": False,
            "schema_validation_execution_authorized": False,
        },
        "blocked_actions": [
            "fixture_file_creation",
            "fixture_file_mutation",
            "schema_validation_execution",
            "shadow_replay_execution",
            "receipt_creation",
            "operator_decision_record_creation",
            "meta_gate_authorization_record_creation",
            "meta_gate_chain_seal_creation",
            "notion_writeback",
            "github_writeback",
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
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "file_writeback": False,
            "fixture_file_creation": False,
            "fixture_file_mutation": False,
            "github_writeback": False,
            "meta_gate_authorization_record_creation": False,
            "meta_gate_chain_seal_creation": False,
            "notion_writeback": False,
            "operator_decision_record_creation": False,
            "queue_mutation": False,
            "receipt_creation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "schema_validation_execution": False,
            "shadow_replay_execution": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_sample_fixture_normalization_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_sample_fixture_normalization_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Sample Fixture Normalization Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        "- sample_fixture_normalization_plan_status: "
        f"{packet['sample_fixture_normalization_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Notion Sample Classes",
    ]
    for item in packet.get("notion_sample_classes", []):
        if isinstance(item, Mapping):
            lines.append(
                f"- {item['sample_class']}: {item['sample_status']} "
                f"({item['fixture_use']})"
            )
    lines.extend(["", "## Normalization Requirements"])
    for requirement in packet.get("normalization_requirements", []):
        if isinstance(requirement, Mapping):
            lines.append(
                f"- {requirement['requirement']}: {requirement['requirement_status']} "
                f"(normalization_execution_authorized="
                f"{requirement['normalization_execution_authorized']})"
            )
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- {action}")
    return lines


def write_abx_codegen_intelligence_spine_sample_fixture_normalization_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_sample_fixture_normalization_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
