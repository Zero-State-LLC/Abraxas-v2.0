from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker, validate

from core.abx_codegen_intelligence_spine_advisory_spec_plan import (
    build_abx_codegen_intelligence_spine_advisory_spec_plan,
    validate_codegen_packet_semantics,
)
from core.canonical.json import canonical_hash
from scripts import run_abx_codegen_intelligence_spine_advisory_spec_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = REPO_ROOT / "tests/fixtures/codegen"
PLAN_SCHEMA_PATH = (
    "contracts/canon/abx_codegen_intelligence_spine_advisory_spec_plan.v1.schema.json"
)
PACKET_SCHEMA_PATHS = {
    "GapDiagnosisPacket.v1": "contracts/canon/gap_diagnosis_packet.v1.schema.json",
    "ImprovementProposal.v1": "contracts/canon/improvement_proposal.v1.schema.json",
    "ShadowImprovementReceipt.v1": "contracts/canon/shadow_improvement_receipt.v1.schema.json",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validator(schema_version: str) -> Draft202012Validator:
    schema = _load_json(REPO_ROOT / PACKET_SCHEMA_PATHS[schema_version])
    return Draft202012Validator(schema, format_checker=FormatChecker())


def test_codegen_advisory_spec_plan_is_advisory_only() -> None:
    packet = build_abx_codegen_intelligence_spine_advisory_spec_plan(repo_root=REPO_ROOT)

    assert packet["artifact_type"] == "AbxCodegenIntelligenceSpineAdvisorySpecPlan.v1"
    assert packet["plan_status"] == "ABX_CODEGEN_INTELLIGENCE_SPINE_ADVISORY_SPEC_PLAN_READY"
    assert packet["target_surface"] == "ABX_CODEGEN_INTELLIGENCE_SPINE_001"
    assert packet["codegen_engine_implementation_performed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["non_authoritative"] is True
    assert all(value is False for value in packet["authority_locks"].values())
    assert "shadow_replay_execution" in packet["blocked_actions"]
    assert "self_authorization" in packet["blocked_actions"]


def test_codegen_advisory_spec_plan_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_advisory_spec_plan(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = _load_json(REPO_ROOT / PLAN_SCHEMA_PATH)
    validate(packet, schema)


def test_codegen_packet_valid_fixtures_validate_and_have_no_semantic_errors() -> None:
    valid_fixture_names = [
        "gap_diagnosis_golden.v1.json",
        "improvement_proposal_golden.v1.json",
        "shadow_receipt_golden.v1.json",
        "self_improvement_meta_gate_receipt.v1.json",
    ]

    for fixture_name in valid_fixture_names:
        fixture = _load_json(FIXTURE_ROOT / fixture_name)
        errors = sorted(_validator(fixture["schema_version"]).iter_errors(fixture), key=str)
        assert errors == []
        assert validate_codegen_packet_semantics(fixture) == []


def test_codegen_packet_negative_fixtures_return_concrete_rule_names() -> None:
    expected_errors = {
        "invalid_gap_diagnosis_missing_hash.v1.json": {
            "self_diagnosis_requires_medium_severity",
            "evidence_source_hash_required",
        },
        "invalid_improvement_proposal_canon_jump.v1.json": {
            "canon_promotion_requires_prior_canary_success",
            "self_modification_requires_operator_decision",
        },
        "invalid_improvement_proposal_missing_operator_decision.v1.json": {
            "self_modification_requires_operator_decision",
        },
        "invalid_shadow_receipt_promote_failure.v1.json": {
            "promotion_requires_governance_compliance",
            "promotion_requires_12_run_invariance",
            "self_modification_requires_operator_review",
            "self_modification_requires_hold_recommendation",
        },
        "invalid_improvement_proposal_missing_provenance.v1.json": {
            "core_policy_auto_mutation_denied",
            "provenance_source_gap_analysis_required",
        },
    }

    for fixture_name, expected in expected_errors.items():
        fixture = _load_json(FIXTURE_ROOT / fixture_name)
        actual = set(validate_codegen_packet_semantics(fixture))
        assert expected <= actual


def test_codegen_fixture_ids_are_deterministic_label_hashes() -> None:
    expected = {
        "gap_diagnosis_golden.v1.json": ("diagnosis_id", "gap-diagnosis-golden"),
        "improvement_proposal_golden.v1.json": ("proposal_id", "improvement-proposal-golden"),
        "shadow_receipt_golden.v1.json": ("receipt_id", "shadow-receipt-golden"),
        "self_improvement_meta_gate_receipt.v1.json": (
            "receipt_id",
            "self-improvement-shadow-receipt",
        ),
    }

    for fixture_name, (field, label) in expected.items():
        fixture = _load_json(FIXTURE_ROOT / fixture_name)
        assert fixture[field] == hashlib.sha256(label.encode("utf-8")).hexdigest()


def test_codegen_advisory_spec_plan_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = (
        tmp_path / "out/audit/abx_codegen_intelligence_spine_advisory_spec_plan_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_advisory_spec_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_advisory_spec_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
    assert first_md.startswith("# ABX Codegen Intelligence Spine Advisory Spec Plan\n")
