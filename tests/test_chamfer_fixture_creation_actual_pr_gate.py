from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.chamfer_fixture_creation_actual_pr_gate import (
    ChamferFixtureCreationActualPRGateValidationError,
    build_chamfer_fixture_creation_actual_pr_gate,
    compute_chamfer_fixture_creation_actual_pr_gate_hash,
    default_blockers,
    default_fixture_batches,
    default_gate_constraints,
    default_output_contract,
    default_proposed_fixture_directories,
    default_source_refs,
    default_validation_requirements,
    serialize_chamfer_fixture_creation_actual_pr_gate,
)


def _payload() -> dict:
    return {
        "gate_id": "chamfer-fixture-creation-actual-pr-gate-001",
        "gate_scope": {"intended_lane": "SHADOW", "gate_stage": "ACTUAL_PR_GATE_ONLY"},
        "proposed_manifest_path": "fixtures/chamfer/manifest/chamfer_fixture_manifest.v1.json",
        "required_future_pr_name": "CHAMFER_FIXTURE_FILES_ACTUAL_PR_V1",
        "required_operator_approval_state": "EXPLICIT_OPERATOR_APPROVAL_REQUIRED",
        "stop_rule": "Stop unless explicit operator approval is recorded for fixture creation.",
        "authority_state": "ADVISORY_ONLY",
        "provenance": {
            "source": "CHAMFER_FIXTURE_CREATION_ACTUAL_PR_GATE_V1",
            "evidence_refs": ["evidence-001"],
            "generated_by": "agent",
            "upstream_schema_refs": ["contracts/canon/chamfer_fixture_creation_actual_pr_gate.v1.schema.json"],
        },
        "created_at_utc": "2026-05-28T00:00:00Z",
        "governance_flags": {k: False for k in (
            "production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation",
            "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved",
            "authorization_granted"
        )},
    }


def test_deterministic_hash_and_serialization() -> None:
    a = build_chamfer_fixture_creation_actual_pr_gate(_payload())
    b = build_chamfer_fixture_creation_actual_pr_gate(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_chamfer_fixture_creation_actual_pr_gate(a) == serialize_chamfer_fixture_creation_actual_pr_gate(b)


def test_non_empty_defaults() -> None:
    p = build_chamfer_fixture_creation_actual_pr_gate(_payload())
    assert p["source_pr_plan_refs"] == default_source_refs()["source_pr_plan_refs"]
    assert p["source_archive_receipt_refs"] == default_source_refs()["source_archive_receipt_refs"]
    assert p["proposed_fixture_directories"] == sorted(default_proposed_fixture_directories())
    assert p["proposed_fixture_batches"] == default_fixture_batches()
    assert p["validation_requirements"] == sorted(default_validation_requirements())
    assert p["blockers"] == default_blockers()
    assert p["gate_constraints"] == default_gate_constraints()
    assert p["output_contract"] == default_output_contract()


def test_enum_duplicate_and_lock_failures() -> None:
    p = _payload()
    p["gate_scope"]["intended_lane"] = "BAD"
    with pytest.raises(ChamferFixtureCreationActualPRGateValidationError, match="unknown_intended_lane"):
        build_chamfer_fixture_creation_actual_pr_gate(p)

    p = _payload()
    b = default_blockers()[0]
    p["blockers"] = [b, dict(b)]
    with pytest.raises(ChamferFixtureCreationActualPRGateValidationError, match="duplicate_blocker_id"):
        build_chamfer_fixture_creation_actual_pr_gate(p)

    p = _payload()
    p["gate_constraints"] = dict(default_gate_constraints(), fixture_files_added=True)
    with pytest.raises(ChamferFixtureCreationActualPRGateValidationError, match="invalid_gate_constraints"):
        build_chamfer_fixture_creation_actual_pr_gate(p)

    p = _payload()
    p["governance_flags"]["runtime_authority"] = True
    with pytest.raises(ChamferFixtureCreationActualPRGateValidationError, match="authority_lock_must_be_false"):
        build_chamfer_fixture_creation_actual_pr_gate(p)


def test_forbidden_provenance_and_schema() -> None:
    p = _payload()
    p["provenance"]["source"] = "authorization-granted"
    with pytest.raises(ChamferFixtureCreationActualPRGateValidationError, match="forbidden_provenance_reference_detected"):
        build_chamfer_fixture_creation_actual_pr_gate(p)

    packet = build_chamfer_fixture_creation_actual_pr_gate(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_chamfer_fixture_creation_actual_pr_gate_hash(packet) == compute_chamfer_fixture_creation_actual_pr_gate_hash(altered)

    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/chamfer_fixture_creation_actual_pr_gate.v1.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(packet, schema)
