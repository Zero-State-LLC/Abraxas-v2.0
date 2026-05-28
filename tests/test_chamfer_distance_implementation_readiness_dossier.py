from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.chamfer_distance_implementation_readiness_dossier import (
    build_chamfer_distance_implementation_readiness_dossier,
    compute_chamfer_distance_implementation_readiness_dossier_hash,
    serialize_chamfer_distance_implementation_readiness_dossier,
)


def _payload() -> dict[str, object]:
    return {
        "dossier_id": "chamfer-distance-implementation-readiness-dossier-001",
        "implementation_scope": {"mode": "CPU_REFERENCE_ONLY", "planning_lane": "BATCH_F1", "readiness_status": "PLANNING_ONLY"},
        "implementation_prerequisites": [{"prerequisite_id": "prereq-001", "status": "REQUIRED", "description": "Reference vectors and deterministic fixtures established.", "evidence_refs": ["MetricOperatorBaselineTestVectorPack.v1:pack-001"]}],
        "dependency_inventory": [{"dependency_id": "dep-001", "dependency_type": "TEST_VECTOR", "description": "CHAMFER baseline vector packet references.", "required": True, "evidence_refs": ["MetricOperatorBaselineTestVectorPack.v1:pack-001"]}],
        "numerical_constraints": ["No floating-point kernel execution in this lane.", "Hash/serialization determinism required."],
        "validation_strategy": [{"strategy_id": "val-001", "validation_type": "DETERMINISTIC_REPLAY", "description": "Replay dossier generation with stable hash equivalence.", "evidence_refs": ["tests/test_chamfer_distance_implementation_readiness_dossier.py"]}],
        "implementation_risks": [{"risk_id": "risk-001", "risk_level": "MEDIUM", "description": "Future kernel implementation could drift from planning constraints.", "mitigation": "Keep advisory lock checks fail-closed.", "evidence_refs": ["contracts/canon/chamfer_distance_implementation_readiness_dossier.v1.schema.json"]}],
        "governance_flags": {k: False for k in ("production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation", "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved", "authorization_granted")},
        "provenance": {"source": "CHAMFER_DISTANCE_IMPLEMENTATION_READINESS_DOSSIER_v0.1", "evidence_refs": ["MetricOperatorImplementationSelectionPlan.v1:plan-001"], "generated_by": "unit-test", "upstream_schema_refs": ["contracts/canon/metric_operator_implementation_selection_plan.v1.schema.json"]},
        "created_at_utc": "2026-05-28T00:00:00Z",
    }


def test_deterministic_hash_and_serialization() -> None:
    a = build_chamfer_distance_implementation_readiness_dossier(_payload())
    b = build_chamfer_distance_implementation_readiness_dossier(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_chamfer_distance_implementation_readiness_dossier(a) == serialize_chamfer_distance_implementation_readiness_dossier(b)


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (lambda p: p["implementation_scope"].__setitem__("mode", "BAD"), "unknown_implementation_scope_mode"),
        (lambda p: p["implementation_prerequisites"][0].__setitem__("status", "BAD"), "unknown_prerequisite_status"),
        (lambda p: p["dependency_inventory"][0].__setitem__("dependency_type", "BAD"), "unknown_dependency_type"),
        (lambda p: p["validation_strategy"][0].__setitem__("validation_type", "BAD"), "unknown_validation_type"),
        (lambda p: p["implementation_risks"][0].__setitem__("risk_level", "BAD"), "unknown_risk_level"),
    ],
)
def test_enum_failures(mutator, err: str) -> None:
    payload = _payload()
    mutator(payload)
    with pytest.raises(ValueError, match=err):
        build_chamfer_distance_implementation_readiness_dossier(payload)


def test_duplicate_id_failures() -> None:
    payload = _payload()
    payload["implementation_prerequisites"].append(dict(payload["implementation_prerequisites"][0]))
    with pytest.raises(ValueError, match="duplicate_prerequisite_id"):
        build_chamfer_distance_implementation_readiness_dossier(payload)


def test_governance_and_output_lock_failures() -> None:
    payload = _payload()
    payload["governance_flags"]["execution_authority"] = True
    with pytest.raises(ValueError, match="authority_lock_must_be_false"):
        build_chamfer_distance_implementation_readiness_dossier(payload)

    payload = _payload()
    payload["output_contract"] = {"implementation_completed": True, "runtime_enabled": False, "scheduler_enabled": False, "renderer_enabled": False, "oracle_enabled": False, "forecast_enabled": False, "production_ready": False}
    with pytest.raises(ValueError, match="invalid_output_contract"):
        build_chamfer_distance_implementation_readiness_dossier(payload)


def test_provenance_forbidden_token_rejection() -> None:
    payload = _payload()
    payload["provenance"]["source"] = "runtime activation and autonomous execution"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_chamfer_distance_implementation_readiness_dossier(payload)


def test_hash_preimage_and_meaningful_change() -> None:
    packet = build_chamfer_distance_implementation_readiness_dossier(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_chamfer_distance_implementation_readiness_dossier_hash(packet) == compute_chamfer_distance_implementation_readiness_dossier_hash(altered)

    changed_payload = _payload()
    changed_payload["implementation_scope"]["mode"] = "CPU_ONLY"
    changed = build_chamfer_distance_implementation_readiness_dossier(changed_payload)
    assert packet["canonical_hash"] != changed["canonical_hash"]


def test_schema_validation_and_id_only_refs() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/chamfer_distance_implementation_readiness_dossier.v1.schema.json").read_text(encoding="utf-8"))
    packet = build_chamfer_distance_implementation_readiness_dossier(_payload())
    jsonschema.validate(packet, schema)

    refs = packet["provenance"]["evidence_refs"]
    assert all(isinstance(r, str) and r for r in refs)
