"""Multi-level Alembic metrics — Brier only for probabilistic forecasts."""

from __future__ import annotations

from typing import Any

from core.alembic.models import ArchitectureContribution, FusionResult, RoutingDecision
from core.alembic.util import make_id
from core.scoring.brier import compute_brier_score


def score_levels(
    *,
    decision: RoutingDecision,
    contributions: tuple[ArchitectureContribution, ...],
    fusion: FusionResult | None,
    ground_truth_probability: float | None = None,
    outcome_value: float | None = None,
) -> dict[str, Any]:
    architecture_scores = []
    for contribution in sorted(contributions, key=lambda item: item.contribution_id):
        entry: dict[str, Any] = {
            "level": "architecture_contribution",
            "contribution_id": contribution.contribution_id,
            "architecture_id": contribution.architecture_id,
            "adapter_id": contribution.adapter_id,
            "status": contribution.status,
            "is_stub": contribution.is_stub,
            "metric": None,
        }
        if contribution.is_stub or contribution.status in {"STUB", "UNAVAILABLE", "NOT_IMPLEMENTED"}:
            entry["metric"] = {
                "type": "execution_success",
                "value": 0.0,
                "note": "stubs_never_scored_as_success",
            }
        elif (
            ground_truth_probability is not None
            and outcome_value is not None
            and isinstance(contribution.calibrated_confidence, (int, float))
        ):
            entry["metric"] = {
                "type": "brier",
                "value": compute_brier_score(float(contribution.calibrated_confidence), outcome_value),
                "raw_confidence": contribution.confidence,
                "calibrated_confidence": contribution.calibrated_confidence,
            }
        else:
            entry["metric"] = {
                "type": "typed_status",
                "value": 1.0 if contribution.status == "OK" else 0.0,
            }
        architecture_scores.append(entry)

    router_score = {
        "level": "router_selection_decision",
        "decision_id": decision.decision_id,
        "selected": list(decision.selected_candidates),
        "abstention_reason": decision.abstention_reason,
        "metric": {
            "type": "selection_explainability",
            "value": 1.0 if decision.selected_candidates or decision.abstention_reason else 0.0,
        },
    }

    fusion_score = None
    if fusion is not None:
        fusion_score = {
            "level": "fused_output",
            "fusion_id": fusion.fusion_id,
            "status": fusion.status,
            "metric": {
                "type": "fusion_acceptance",
                "value": 1.0 if fusion.accepted_contribution_ids else 0.0,
                "note": "confidence_not_averaged",
            },
        }

    return {
        "schema_version": "AlembicMetricReport.v1",
        "report_id": make_id("metrics", decision.decision_id),
        "levels": {
            "architecture_contribution": architecture_scores,
            "router_selection_decision": router_score,
            "fused_output": fusion_score,
            "architecture_family": "NOT_COMPUTABLE",
            "hybrid_plan": "NOT_COMPUTABLE" if decision.hybrid_plan is None else {
                "plan_id": decision.hybrid_plan.plan_id,
                "node_count": len(decision.hybrid_plan.nodes),
            },
            "verification_stage": "see_verification_result",
            "active_versus_shadow": "see_shadow_comparison",
        },
        "brier_applied_only_to_probabilistic_forecasts": True,
        "FINAL_STATUS": "ALEMBIC_SPINE_ADVISORY_ONLY",
    }
