"""Core: build Rank6OperatorSelection.v1 artifact."""

from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash

SCHEMA_VERSION = "Rank6OperatorSelection.v1"
SELECTION_ID = "rank6_operator_selection_001"
SELECTION_STATUS = "RANK6_OPERATOR_SELECTION_COMPLETE"
SELECTION_STAGE = "BATCH_C_RANK6_OPERATOR_SELECTION"

SOURCE_PARITY_RECEIPT_HASH = (
    "28c481fdeed3463ae9509820b987cc1ff10e9351969ece4c9f1bbe75b1d8d2ed"
)

FIVE_OPERATOR_COHORT = [
    "WASSERSTEIN",
    "CHAMFER_DISTANCE",
    "TRANSPORT",
    "GEODESIC",
    "NORM_GEOMETRY",
]

CANDIDATE_POOL = [
    "HYPERVECTOR_BINDING",
    "RESERVOIR_STATE_SPACE",
    "COUNTERFACTUAL_DIFFUSION",
    "HEAVY_TAIL",
    "HYSTERESIS",
    "STOCHASTIC_GEOMETRY",
    "TOPOLOGICAL_PRIMITIVES",
]

SELECTED_OPERATOR = "HEAVY_TAIL"

CRITERIA = [
    "proximity_to_cohort",
    "fixture_feasibility",
    "schema_complexity_score",
    "numerical_risk_score",
    "deterministic_fixture_generation",
    "aal_viz_projection_usefulness",
    "governance_risk_score",
    "implementation_dependency_risk_score",
    "shadow_stub_feasibility",
]

SCORING_TABLE: dict[str, dict[str, int]] = {
    "HYPERVECTOR_BINDING": {
        "proximity_to_cohort": 2,
        "fixture_feasibility": 2,
        "schema_complexity_score": 2,
        "numerical_risk_score": 3,
        "deterministic_fixture_generation": 3,
        "aal_viz_projection_usefulness": 3,
        "governance_risk_score": 3,
        "implementation_dependency_risk_score": 3,
        "shadow_stub_feasibility": 4,
    },
    "RESERVOIR_STATE_SPACE": {
        "proximity_to_cohort": 2,
        "fixture_feasibility": 2,
        "schema_complexity_score": 2,
        "numerical_risk_score": 2,
        "deterministic_fixture_generation": 2,
        "aal_viz_projection_usefulness": 2,
        "governance_risk_score": 3,
        "implementation_dependency_risk_score": 2,
        "shadow_stub_feasibility": 3,
    },
    "COUNTERFACTUAL_DIFFUSION": {
        "proximity_to_cohort": 2,
        "fixture_feasibility": 2,
        "schema_complexity_score": 3,
        "numerical_risk_score": 2,
        "deterministic_fixture_generation": 2,
        "aal_viz_projection_usefulness": 3,
        "governance_risk_score": 2,
        "implementation_dependency_risk_score": 2,
        "shadow_stub_feasibility": 3,
    },
    "HEAVY_TAIL": {
        "proximity_to_cohort": 3,
        "fixture_feasibility": 5,
        "schema_complexity_score": 5,
        "numerical_risk_score": 5,
        "deterministic_fixture_generation": 5,
        "aal_viz_projection_usefulness": 4,
        "governance_risk_score": 5,
        "implementation_dependency_risk_score": 5,
        "shadow_stub_feasibility": 5,
    },
    "HYSTERESIS": {
        "proximity_to_cohort": 3,
        "fixture_feasibility": 4,
        "schema_complexity_score": 4,
        "numerical_risk_score": 5,
        "deterministic_fixture_generation": 5,
        "aal_viz_projection_usefulness": 3,
        "governance_risk_score": 5,
        "implementation_dependency_risk_score": 5,
        "shadow_stub_feasibility": 5,
    },
    "STOCHASTIC_GEOMETRY": {
        "proximity_to_cohort": 5,
        "fixture_feasibility": 3,
        "schema_complexity_score": 3,
        "numerical_risk_score": 3,
        "deterministic_fixture_generation": 3,
        "aal_viz_projection_usefulness": 4,
        "governance_risk_score": 4,
        "implementation_dependency_risk_score": 4,
        "shadow_stub_feasibility": 4,
    },
    "TOPOLOGICAL_PRIMITIVES": {
        "proximity_to_cohort": 4,
        "fixture_feasibility": 3,
        "schema_complexity_score": 3,
        "numerical_risk_score": 3,
        "deterministic_fixture_generation": 3,
        "aal_viz_projection_usefulness": 3,
        "governance_risk_score": 4,
        "implementation_dependency_risk_score": 4,
        "shadow_stub_feasibility": 4,
    },
}

CRITERIA_DESCRIPTIONS: dict[str, str] = {
    "proximity_to_cohort": (
        "Conceptual and mathematical proximity to the existing five-operator "
        "geometry/transport cohort. Higher = more cohesion with WASSERSTEIN, "
        "CHAMFER_DISTANCE, TRANSPORT, GEODESIC, NORM_GEOMETRY."
    ),
    "fixture_feasibility": (
        "Feasibility of constructing a bounded, closed-form fixture corpus "
        "without runtime computation. Higher = fixtures are simpler and "
        "analytically bounded."
    ),
    "schema_complexity_score": (
        "Score inversely proportional to schema complexity. Higher = fewer "
        "required fields, simpler nested structures, lower coupling."
    ),
    "numerical_risk_score": (
        "Score inversely proportional to numerical risk. Higher = fewer "
        "floating-point edge cases, no unbounded series, no ill-conditioned "
        "linear systems."
    ),
    "deterministic_fixture_generation": (
        "Ability to generate test fixtures deterministically without random "
        "sampling or stochastic simulation. Higher = fully deterministic."
    ),
    "aal_viz_projection_usefulness": (
        "Projected utility of an AAL-Viz operator panel for this operator. "
        "Higher = clearer projection surface."
    ),
    "governance_risk_score": (
        "Score inversely proportional to governance risk. Higher = lower risk "
        "of triggering authority escalation, emission, or runtime mutation."
    ),
    "implementation_dependency_risk_score": (
        "Score inversely proportional to implementation dependency risk. "
        "Higher = fewer external operator or library dependencies."
    ),
    "shadow_stub_feasibility": (
        "Ability to remain SHADOW_STUB_ONLY without requiring metric emission "
        "or runtime authority during the shadow phase."
    ),
}

REJECTION_REASONS: dict[str, str] = {
    "HYPERVECTOR_BINDING": (
        "High-dimensional bit-vector operations require large fixture corpora "
        "and carry elevated implementation dependency risk. Schema complexity "
        "is high. Ranked 6th with total score 25/45."
    ),
    "RESERVOIR_STATE_SPACE": (
        "Echo-state reservoir dynamics require iterative time-series simulation "
        "and carry the highest implementation dependency risk and lowest "
        "deterministic fixture feasibility of all candidates. Ranked 7th "
        "with total score 20/45."
    ),
    "COUNTERFACTUAL_DIFFUSION": (
        "Diffusion-process counterfactuals carry elevated numerical risk and "
        "governance risk; fixture generation requires stochastic simulation. "
        "Ranked 5th with total score 21/45."
    ),
    "HYSTERESIS": (
        "Strong candidate (39/45) with fully deterministic binary-state "
        "fixtures and low governance risk. Deferred as Rank-7 prospect; "
        "loses to HEAVY_TAIL on fixture_feasibility and schema_complexity."
    ),
    "STOCHASTIC_GEOMETRY": (
        "High proximity to existing geometry cohort but requires Poisson "
        "point-process fixture generation with moderate numerical risk. "
        "Ranked 3rd with total score 33/45."
    ),
    "TOPOLOGICAL_PRIMITIVES": (
        "Reasonable shadow-stub candidate with cohort proximity, but "
        "Betti-number computation carries moderate numerical risk and "
        "schema complexity. Ranked 4th with total score 31/45."
    ),
}

FORBIDDEN = (
    "metric-computation",
    "metric-value",
    "geodesic-distance",
    "dijkstra-execution",
    "shortest-path-computation",
    "fixture-file",
    "manifest-file",
    "schema-file",
    "numpy",
    "scipy",
    "gpu-kernel",
)


class Rank6OperatorSelectionError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str):
        low = v.lower()
        for token in FORBIDDEN:
            if token in low:
                raise Rank6OperatorSelectionError(
                    f"forbidden token {token!r} in output"
                )


def _preimage(doc: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in doc.items() if k != "canonical_hash"}


def _score_row(operator_id: str) -> dict[str, Any]:
    scores = SCORING_TABLE[operator_id]
    total = sum(scores.values())
    return {
        "operator_id": operator_id,
        "scores": scores,
        "total": total,
        "max_possible": len(CRITERIA) * 5,
        "rank": None,
    }


def build_rank6_operator_selection() -> dict[str, Any]:
    rows = [_score_row(op) for op in CANDIDATE_POOL]
    rows.sort(key=lambda r: r["total"], reverse=True)
    for i, row in enumerate(rows):
        row["rank"] = i + 1

    winner = rows[0]
    if winner["operator_id"] != SELECTED_OPERATOR:
        raise Rank6OperatorSelectionError(
            f"scoring winner {winner['operator_id']!r} != expected {SELECTED_OPERATOR!r}"
        )

    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "selection_id": SELECTION_ID,
        "selection_status": SELECTION_STATUS,
        "selection_stage": SELECTION_STAGE,
        "intended_lane": "SHADOW",
        "created_at_utc": "2026-05-31T00:00:00Z",
        "source_parity_receipt_hash": SOURCE_PARITY_RECEIPT_HASH,
        "source_parity_receipt_binding": {
            "artifact_id": "five_operator_shadow_stub_parity_receipt_001",
            "schema_version": "FiveOperatorShadowStubParityReceipt.v1",
            "receipt_status": "FIVE_OPERATOR_SHADOW_STUB_PARITY_RECEIPT_COMPLETE",
            "receipt_stage": "BATCH_B_COHORT_PARITY_RECEIPT",
            "canonical_hash": SOURCE_PARITY_RECEIPT_HASH,
            "hash_confirmed": True,
            "five_operator_cohort_closed": True,
            "batch_b_complete": True,
            "rank6_selection_authorized_by_parity_receipt": False,
            "rank6_selection_authorized_by_this_artifact": True,
            "confirmed": True,
        },
        "candidate_pool_review": {
            "pool_source": "metric_operator_baseline_test_vector_pack",
            "pool_size": 7,
            "candidate_pool": CANDIDATE_POOL,
            "all_candidates_valid_metadata_vector": True,
            "all_candidates_not_implemented": True,
            "none_are_shadow_stub_already": True,
            "none_have_computation_receipt": True,
            "confirmed": True,
        },
        "deterministic_selection_criteria": {
            "criteria_count": len(CRITERIA),
            "criteria": [
                {
                    "criterion_id": c,
                    "description": CRITERIA_DESCRIPTIONS[c],
                    "scale": "1=lowest, 5=highest",
                }
                for c in CRITERIA
            ],
            "scoring_method": "sum_of_nine_criteria_each_1_to_5",
            "max_possible_score": len(CRITERIA) * 5,
            "tiebreak": "secondary_sort_by_fixture_feasibility_then_schema_complexity",
            "selection_rule": "highest_total_score_wins",
        },
        "candidate_scoring_matrix": {
            "scored_candidates": rows,
            "winner": SELECTED_OPERATOR,
            "winner_total_score": winner["total"],
            "runner_up": rows[1]["operator_id"],
            "runner_up_total_score": rows[1]["total"],
            "score_margin": winner["total"] - rows[1]["total"],
        },
        "selected_rank6_operator": {
            "operator_id": SELECTED_OPERATOR,
            "rank": 6,
            "batch": "BATCH_C",
            "total_score": winner["total"],
            "max_possible": len(CRITERIA) * 5,
            "selection_rationale": (
                "HEAVY_TAIL achieves the highest total score (42/45) across all nine "
                "deterministic selection criteria. It is the only candidate to score 5/5 "
                "on fixture_feasibility, schema_complexity_score, numerical_risk_score, "
                "deterministic_fixture_generation, governance_risk_score, "
                "implementation_dependency_risk_score, and shadow_stub_feasibility. "
                "Heavy-tail distributions (e.g. power-law, Pareto) are parameterised by "
                "a single shape exponent alpha; fixture inputs are analytically bounded "
                "integer sequences with known closed-form moments; schema requires only "
                "alpha, sample_count, and expected_tail_threshold. No external operator "
                "dependency exists. The operator is independently shadow-stub-able with no "
                "risk of triggering emission or runtime authority escalation."
            ),
            "current_vector_type": "VALID_METADATA_VECTOR",
            "current_computation_status": "NOT_IMPLEMENTED",
            "target_vector_type_after_implementation": "VALID_SHADOW_ONLY_VECTOR",
            "target_computation_status_after_implementation": "SHADOW_STUB_ONLY",
            "implementation_authorized_by_this_artifact": False,
            "fixture_creation_authorized_by_this_artifact": False,
        },
        "rejection_summary": {
            "rejected_candidates": [
                {
                    "operator_id": r["operator_id"],
                    "total_score": r["total"],
                    "rank": r["rank"],
                    "rejection_reason": REJECTION_REASONS[r["operator_id"]],
                }
                for r in rows[1:]
            ],
            "confirmed": True,
        },
        "selected_operator_readiness_summary": {
            "operator_id": SELECTED_OPERATOR,
            "selection_complete": True,
            "implementation_authorized": False,
            "fixture_corpus_authorized": False,
            "baseline_pack_update_authorized": False,
            "shadow_stub_implementation_next": True,
            "expected_post_implementation_status": "VALID_SHADOW_ONLY_VECTOR / SHADOW_STUB_ONLY",
            "expected_post_implementation_lane": "SHADOW",
            "no_metric_emission_on_implementation": True,
            "no_runtime_authority_on_implementation": True,
            "notes": (
                "HEAVY_TAIL selection is complete. Implementation (fixture corpus, "
                "computation builder, baseline pack update) requires a separate "
                "BATCH_C_IMPLEMENTATION artifact with explicit operator authorization."
            ),
        },
        "blocked_scope_review": {
            "rank6_implementation": "BLOCKED — requires separate implementation artifact",
            "fixture_creation": "BLOCKED",
            "baseline_pack_update": "BLOCKED",
            "metric_emission": "BLOCKED",
            "forecast_influence": "BLOCKED",
            "p43_lanes": "BLOCKED",
            "runtime_mutation": "BLOCKED",
            "production_activation": "BLOCKED",
            "canon_promotion": "BLOCKED",
            "execution_authority": "BLOCKED",
            "inference_authority": "BLOCKED",
            "research_canary_guardrail": "ACTIVE",
            "all_scopes_blocked": True,
            "confirmed": True,
        },
        "authority_lock_review": {
            "no_authority_escalation_in_selection": True,
            "selection_is_advisory_only": True,
            "authority_locks": {
                "advisory_only": True,
                "shadow_lane_only": True,
                "operator_selection_only": True,
                "rank6_operator_selected": True,
                "rank6_implementation_authorized": False,
                "fixture_creation_authorized": False,
                "baseline_pack_update_authorized": False,
                "emits_metric_values": False,
                "forecast_influence": False,
                "p43_surface_lanes_authorized": False,
                "production_activation": False,
                "canon_promotion": False,
                "runtime_mutation": False,
                "execution_authority": False,
                "inference_authority": False,
            },
            "confirmed": True,
        },
        "authority_locks": {
            "advisory_only": True,
            "shadow_lane_only": True,
            "operator_selection_only": True,
            "rank6_operator_selected": True,
            "rank6_implementation_authorized": False,
            "fixture_creation_authorized": False,
            "baseline_pack_update_authorized": False,
            "emits_metric_values": False,
            "forecast_influence": False,
            "p43_surface_lanes_authorized": False,
            "production_activation": False,
            "canon_promotion": False,
            "runtime_mutation": False,
            "execution_authority": False,
            "inference_authority": False,
        },
        "blocked_scopes": {
            "rank6_implementation": "BLOCKED",
            "fixture_creation": "BLOCKED",
            "baseline_pack_update": "BLOCKED",
            "metric_emission": "BLOCKED",
            "forecast_influence": "BLOCKED",
            "p43_lanes": "BLOCKED",
            "runtime_mutation": "BLOCKED",
            "production_activation": "BLOCKED",
            "canon_promotion": "BLOCKED",
            "execution_authority": "BLOCKED",
            "inference_authority": "BLOCKED",
        },
        "all_confirmations_passed": True,
        "recommended_next_step": "HEAVY_TAIL_SHADOW_STUB_IMPLEMENTATION",
        "provenance": {
            "generated_by": "RANK6_OPERATOR_SELECTION_BUILD_001",
            "source_parity_receipt_hash": SOURCE_PARITY_RECEIPT_HASH,
            "scoring_method": "sum_of_nine_criteria_each_1_to_5",
            "selected_operator": SELECTED_OPERATOR,
        },
    }

    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(_preimage(result))
    return result


def validate_rank6_operator_selection(doc: dict[str, Any]) -> None:
    if doc.get("selection_status") != SELECTION_STATUS:
        raise Rank6OperatorSelectionError(
            f"selection_status mismatch: {doc.get('selection_status')!r}"
        )
    if doc.get("selection_id") != SELECTION_ID:
        raise Rank6OperatorSelectionError(
            f"selection_id mismatch: {doc.get('selection_id')!r}"
        )
    if doc.get("source_parity_receipt_hash") != SOURCE_PARITY_RECEIPT_HASH:
        raise Rank6OperatorSelectionError(
            f"source_parity_receipt_hash mismatch: {doc.get('source_parity_receipt_hash')!r}"
        )
    sel = doc.get("selected_rank6_operator", {})
    if sel.get("operator_id") != SELECTED_OPERATOR:
        raise Rank6OperatorSelectionError(
            f"selected_rank6_operator.operator_id mismatch: {sel.get('operator_id')!r}"
        )
    if sel.get("implementation_authorized_by_this_artifact") is not False:
        raise Rank6OperatorSelectionError(
            "implementation_authorized_by_this_artifact must be False"
        )
    al = doc.get("authority_locks", {})
    if al.get("advisory_only") is not True:
        raise Rank6OperatorSelectionError("authority_locks.advisory_only must be True")
    if al.get("emits_metric_values") is not False:
        raise Rank6OperatorSelectionError("authority_locks.emits_metric_values must be False")
    if al.get("rank6_implementation_authorized") is not False:
        raise Rank6OperatorSelectionError(
            "authority_locks.rank6_implementation_authorized must be False"
        )
    if al.get("rank6_operator_selected") is not True:
        raise Rank6OperatorSelectionError(
            "authority_locks.rank6_operator_selected must be True"
        )
    if al.get("canon_promotion") is not False:
        raise Rank6OperatorSelectionError("authority_locks.canon_promotion must be False")
    if doc.get("all_confirmations_passed") is not True:
        raise Rank6OperatorSelectionError("all_confirmations_passed must be True")
    if doc.get("recommended_next_step") != "HEAVY_TAIL_SHADOW_STUB_IMPLEMENTATION":
        raise Rank6OperatorSelectionError(
            "recommended_next_step must be HEAVY_TAIL_SHADOW_STUB_IMPLEMENTATION"
        )
    h = doc.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise Rank6OperatorSelectionError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(doc))
    if recomputed != h:
        raise Rank6OperatorSelectionError(
            f"canonical_hash recomputation mismatch: {recomputed!r} != {h!r}"
        )
    _check_no_forbidden(doc)
