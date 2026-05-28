from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.metric_operator_implementation_selection_plan import (
    build_metric_operator_implementation_selection_plan,
    compute_metric_operator_implementation_selection_plan_hash,
    default_implementation_gates,
    default_operator_candidates,
    default_output_contract,
    default_readiness_constraints,
    default_selection_policy,
    serialize_metric_operator_implementation_selection_plan,
)


def _payload() -> dict[str, object]:
    return {
        "plan_id": "metric-operator-implementation-selection-plan-001",
        "source_metric_registry_refs": ["MetricOperatorRegistry.v1:registry-001"],
        "source_test_vector_pack_refs": ["MetricOperatorBaselineTestVectorPack.v1:pack-001"],
        "source_renderer_implementation_plan_refs": ["AALVizGeometricRendererImplementationPlan.v1:plan-001"],
        "selection_scope": {
            "selection_family": "FIRST_OPERATOR_SELECTION",
            "intended_lane": "SHADOW",
            "selection_stage": "SELECTION_PLAN_ONLY",
        },
        "operator_candidates": default_operator_candidates(),
        "selection_policy": default_selection_policy(),
        "readiness_constraints": default_readiness_constraints(),
        "implementation_gates": default_implementation_gates(),
        "output_contract": default_output_contract(),
        "governance_flags": {k: False for k in (
            "production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation",
            "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved", "authorization_granted",
        )},
        "provenance": {
            "source": "METRIC_SELECTION_PLAN_v0.1_boundary_opening",
            "evidence_refs": [
                "MetricOperatorRegistry.v1:registry-001",
                "MetricOperatorBaselineTestVectorPack.v1:pack-001",
                "AALVizGeometricRendererImplementationPlan.v1:plan-001",
            ],
            "generated_by": "unit-test",
            "upstream_schema_refs": [
                "contracts/canon/metric_operator_registry.v1.schema.json",
                "contracts/canon/metric_operator_baseline_test_vector_pack.v1.schema.json",
                "contracts/canon/aal_viz_geometric_renderer_implementation_plan.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-27T00:00:00Z",
    }


def test_hash_deterministic_and_byte_stable() -> None:
    a = build_metric_operator_implementation_selection_plan(_payload())
    b = build_metric_operator_implementation_selection_plan(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_metric_operator_implementation_selection_plan(a) == serialize_metric_operator_implementation_selection_plan(b)


def test_default_candidates_non_empty_and_deterministic() -> None:
    assert default_operator_candidates()
    assert default_operator_candidates() == default_operator_candidates()


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (lambda p: p["operator_candidates"].append(dict(p["operator_candidates"][0])), "duplicate_candidate_id"),
        (lambda p: p["selection_scope"].__setitem__("selection_family", "BAD"), "unknown_selection_family"),
        (lambda p: p["selection_scope"].__setitem__("intended_lane", "BAD"), "unknown_intended_lane"),
        (lambda p: p["selection_scope"].__setitem__("selection_stage", "BAD"), "unknown_selection_stage"),
        (lambda p: p["operator_candidates"][0].__setitem__("operator_id", "BAD"), "unknown_operator_id"),
        (lambda p: p["operator_candidates"][0].__setitem__("operator_family", "BAD"), "unknown_operator_family"),
        (lambda p: p["operator_candidates"][0].__setitem__("readiness_status", "BAD"), "unknown_readiness_status"),
        (lambda p: p["operator_candidates"][0].__setitem__("implementation_risk", "BAD"), "unknown_implementation_risk"),
        (lambda p: p["operator_candidates"][0].__setitem__("implementation_status", "BAD"), "unknown_implementation_status"),
    ],
)
def test_invalid_enums(mutator, err: str) -> None:
    payload = _payload()
    mutator(payload)
    with pytest.raises(ValueError, match=err):
        build_metric_operator_implementation_selection_plan(payload)


def test_invalid_selection_rank_fails() -> None:
    payload = _payload()
    payload["operator_candidates"][0]["selection_rank"] = 0
    with pytest.raises(ValueError, match="invalid_selection_rank"):
        build_metric_operator_implementation_selection_plan(payload)


def test_locked_maps_and_flags() -> None:
    for key in default_selection_policy().keys():
        payload = _payload()
        payload["selection_policy"][key] = False
        with pytest.raises(ValueError, match="invalid_selection_policy"):
            build_metric_operator_implementation_selection_plan(payload)

    for key in default_readiness_constraints().keys():
        payload = _payload()
        payload["readiness_constraints"][key] = False
        with pytest.raises(ValueError, match="invalid_readiness_constraints"):
            build_metric_operator_implementation_selection_plan(payload)

    for key in default_implementation_gates().keys():
        payload = _payload()
        payload["implementation_gates"][key] = False
        with pytest.raises(ValueError, match="invalid_implementation_gates"):
            build_metric_operator_implementation_selection_plan(payload)

    for key in ("emits_metric_code", "emits_metric_values", "emits_scores", "emits_forecast_inputs", "emits_runtime_controls", "emits_authority_tokens"):
        payload = _payload()
        payload["output_contract"][key] = True
        with pytest.raises(ValueError, match="invalid_output_contract"):
            build_metric_operator_implementation_selection_plan(payload)

    payload = _payload()
    payload["governance_flags"]["execution_authority"] = True
    with pytest.raises(ValueError, match="authority_lock_must_be_false"):
        build_metric_operator_implementation_selection_plan(payload)


def test_provenance_forbidden_tokens_rejected() -> None:
    payload = _payload()
    payload["provenance"]["source"] = "runtime scheduler cache forecast scoring metric-computation metric-value executable"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_metric_operator_implementation_selection_plan(payload)


def test_hash_excludes_canonical_hash_and_changes_on_meaningful_change() -> None:
    packet = build_metric_operator_implementation_selection_plan(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_metric_operator_implementation_selection_plan_hash(packet) == compute_metric_operator_implementation_selection_plan_hash(altered)

    changed_payload = _payload()
    changed_payload["selection_scope"]["selection_stage"] = "READINESS_RANKING_ONLY"
    changed = build_metric_operator_implementation_selection_plan(changed_payload)
    assert packet["canonical_hash"] != changed["canonical_hash"]


def test_schema_validates_fixture() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/metric_operator_implementation_selection_plan.v1.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(build_metric_operator_implementation_selection_plan(_payload()), schema)


def test_references_are_id_only_strings() -> None:
    packet = build_metric_operator_implementation_selection_plan(_payload())
    refs = (
        packet["source_metric_registry_refs"]
        + packet["source_test_vector_pack_refs"]
        + packet["source_renderer_implementation_plan_refs"]
    )
    assert all(isinstance(r, str) for r in refs)
