from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_improvement_proposal_shadow_replay_wiring_spec_plan import (
    OUT_JSON as SOURCE_WIRING_SPEC_PLAN_JSON,
)
from core.abx_codegen_intelligence_spine_meta_gate_authorization_record_template_plan import (
    OUT_JSON as SOURCE_META_GATE_AUTHORIZATION_RECORD_TEMPLATE_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineSampleMetaGateChainValidationPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_SAMPLE_META_GATE_CHAIN_VALIDATION_PLAN_001"
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan_001.latest.md"
)

EXPECTED_WIRING_STATUS = (
    "ABX_CODEGEN_IMPROVEMENT_PROPOSAL_SHADOW_REPLAY_WIRING_SPEC_PLAN_HELD_FOR_OPERATOR"
)
EXPECTED_TEMPLATE_STATUS = (
    "ABX_CODEGEN_META_GATE_AUTHORIZATION_RECORD_TEMPLATE_PLAN_HELD_FOR_OPERATOR"
)

NOTION_SPEC = {
    "title": "Sample Meta-Gate Chain Artifacts - Complete Example",
    "page_id": "37d3e8ba-2f5c-8126-8d69-ed197b228066",
    "observed_as_of": "2026-06-12",
    "status": "Example Data (Advisory)",
    "version": "source_observed",
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


def _planning_status(sources_ready: bool) -> str:
    return "SAMPLE_CHAIN_VALIDATION_DEFINED_HELD_FOR_OPERATOR" if sources_ready else "NOT_COMPUTABLE"


def build_abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan(
    *,
    repo_root: str | Path,
    source_wiring_spec_plan_path: str | Path = SOURCE_WIRING_SPEC_PLAN_JSON,
    source_meta_gate_authorization_record_template_plan_path: str
    | Path = SOURCE_META_GATE_AUTHORIZATION_RECORD_TEMPLATE_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    wiring_path = Path(source_wiring_spec_plan_path).as_posix()
    template_path = Path(source_meta_gate_authorization_record_template_plan_path).as_posix()
    wiring = _read_json(root / source_wiring_spec_plan_path)
    template = _read_json(root / source_meta_gate_authorization_record_template_plan_path)

    wiring_ready = (
        wiring.get("artifact_type")
        == "AbxCodegenIntelligenceSpineImprovementProposalShadowReplayWiringSpecPlan.v1"
        and wiring.get("wiring_spec_plan_status") == EXPECTED_WIRING_STATUS
        and wiring.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and wiring.get("safe_to_auto_continue") is False
        and wiring.get("execution_authority") is False
        and wiring.get("valid_for_implementation") is False
    )
    template_ready = (
        template.get("artifact_type")
        == "AbxCodegenIntelligenceSpineMetaGateAuthorizationRecordTemplatePlan.v1"
        and template.get("meta_gate_authorization_record_template_plan_status")
        == EXPECTED_TEMPLATE_STATUS
        and template.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and template.get("safe_to_auto_continue") is False
        and template.get("execution_authority") is False
        and template.get("valid_for_implementation") is False
    )
    sources_ready = wiring_ready and template_ready
    status = _planning_status(sources_ready)

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "sample_meta_gate_chain_validation_plan_status": (
            "ABX_CODEGEN_SAMPLE_META_GATE_CHAIN_VALIDATION_PLAN_HELD_FOR_OPERATOR"
            if sources_ready
            else "NOT_COMPUTABLE"
        ),
        "source_notion_spec": {**NOTION_SPEC, "notion_writeback_performed": False},
        "source_wiring_spec_plan": {
            "path": wiring_path,
            "hash": _sha256(root / source_wiring_spec_plan_path),
            "wiring_spec_plan_status": str(
                wiring.get("wiring_spec_plan_status", "NOT_COMPUTABLE")
            ),
            "source_ready": wiring_ready,
        },
        "source_meta_gate_authorization_record_template_plan": {
            "path": template_path,
            "hash": _sha256(root / source_meta_gate_authorization_record_template_plan_path),
            "meta_gate_authorization_record_template_plan_status": str(
                template.get(
                    "meta_gate_authorization_record_template_plan_status",
                    "NOT_COMPUTABLE",
                )
            ),
            "source_ready": template_ready,
        },
        "sample_chain_artifacts": [
            {
                "artifact_role": "ImprovementProposal.v1",
                "sample_status": status,
                "observed_recommendation_or_decision": "SELF_IMPROVEMENT",
                "requires_schema_validation_before_fixture_use": True,
                "canonical_fixture_emission_authorized": False,
            },
            {
                "artifact_role": "ShadowImprovementReceipt.v1",
                "sample_status": status,
                "observed_recommendation_or_decision": "HOLD_FOR_META_GATE",
                "requires_schema_validation_before_fixture_use": True,
                "canonical_fixture_emission_authorized": False,
            },
            {
                "artifact_role": "Meta-Gate Operator Decision Record",
                "sample_status": status,
                "observed_recommendation_or_decision": "APPROVE_META_GATE",
                "requires_real_operator_attestation": True,
                "record_creation_authorized": False,
            },
            {
                "artifact_role": "Meta-Gate Authorization Record",
                "sample_status": status,
                "observed_recommendation_or_decision": "Proceed to Meta-Gate Chain Seal",
                "requires_real_operator_attestation": True,
                "record_creation_authorized": False,
            },
            {
                "artifact_role": "Meta-Gate Chain Seal",
                "sample_status": status,
                "observed_recommendation_or_decision": "SEALED",
                "requires_real_operator_attestation": True,
                "seal_creation_authorized": False,
            },
        ],
        "normalization_policy": {
            "example_timestamps_are_source_observed_only": True,
            "wall_clock_generation_authorized": False,
            "ellipsis_blocks_must_be_replaced_before_fixture_use": True,
            "simplified_records_are_not_operator_evidence": True,
            "sample_hashes_are_reference_values_only": True,
            "canonical_fixture_output_authorized": False,
        },
        "validation_rules": [
            {
                "rule": "self_improvement_proposal_must_route_to_hold_for_meta_gate",
                "planned_validation_status": status,
                "validation_execution_authorized": False,
            },
            {
                "rule": "hold_or_block_receipts_must_populate_promotion_blockers",
                "planned_validation_status": status,
                "validation_execution_authorized": False,
            },
            {
                "rule": "meta_gate_operator_decision_requires_real_operator_attestation",
                "planned_validation_status": status,
                "validation_execution_authorized": False,
            },
            {
                "rule": "authorization_record_cannot_authorize_direct_implementation",
                "planned_validation_status": status,
                "validation_execution_authorized": False,
            },
            {
                "rule": "real_chain_seal_example_cannot_be_treated_as_actual_seal",
                "planned_validation_status": status,
                "validation_execution_authorized": False,
            },
            {
                "rule": "post_seal_step_is_canary_review_only_not_execution",
                "planned_validation_status": status,
                "validation_execution_authorized": False,
            },
        ],
        "example_limitations": [
            "notion_examples_are_illustrative_not_canonical_fixtures",
            "examples_contain_source_observed_timestamps",
            "examples_contain_ellipsis_blocks",
            "simplified_odr_record_lacks_full_operator_attestation_fields",
            "simplified_authorization_record_lacks_full_provenance_chain",
            "real_seal_example_is_not_a_repo_observed_seal",
            "no_operator_attestation_exists_in_repo_visible_evidence",
        ],
        "blocked_actions": [
            "canonical_fixture_creation",
            "shadow_improvement_receipt_creation",
            "operator_decision_record_creation",
            "operator_attestation_fabrication",
            "meta_gate_authorization_record_creation",
            "meta_gate_chain_seal_creation",
            "canary_promotion_routing",
            "codegen_harness_execution",
            "runtime_mutation",
            "canon_mutation",
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
            "canary_promotion": False,
            "canonical_fixture_creation": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "file_writeback": False,
            "github_writeback": False,
            "harness_execution": False,
            "meta_gate_authorization_record_creation": False,
            "meta_gate_chain_seal_creation": False,
            "notion_writeback": False,
            "operator_attestation": False,
            "operator_decision_record_creation": False,
            "queue_mutation": False,
            "receipt_creation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "validation_execution": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Sample Meta-Gate Chain Validation Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        "- sample_meta_gate_chain_validation_plan_status: "
        f"{packet['sample_meta_gate_chain_validation_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Sample Chain Artifacts",
    ]
    for item in packet.get("sample_chain_artifacts", []):
        if isinstance(item, Mapping):
            lines.append(
                f"- {item['artifact_role']}: {item['sample_status']} "
                f"({item['observed_recommendation_or_decision']})"
            )
    lines.extend(["", "## Validation Rules"])
    for rule in packet.get("validation_rules", []):
        if isinstance(rule, Mapping):
            lines.append(
                f"- {rule['rule']}: {rule['planned_validation_status']} "
                f"(validation_execution_authorized={rule['validation_execution_authorized']})"
            )
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- {action}")
    return lines


def write_abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_sample_meta_gate_chain_validation_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
