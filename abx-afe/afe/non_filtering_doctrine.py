from __future__ import annotations

from copy import deepcopy
from typing import Any

from afe.provenance import stable_hash
from afe.trace import AUTHORITY

DOCTRINE_ID = "AFE_NON_FILTERING_OBSERVATION_DOCTRINE_V1"
OUTPUT_EFFECT = "OBSERVATION_ONLY"

ALLOWED_EFFECTS = (
    "annotate",
    "label",
    "rank_for_review",
    "visualize",
    "compare",
    "summarize",
    "flag_drift",
    "flag_instability",
    "flag_manipulation",
    "generate_shadow_notes",
    "route_to_human_review",
    "support_research_dashboards",
)

FORBIDDEN_EFFECTS = (
    "remove_output",
    "suppress_output",
    "hide_output",
    "filter_output",
    "rewrite_output",
    "soften_output",
    "sanitize_output",
    "block_output",
    "demote_invisibly",
    "change_forecast_weights_directly",
    "mutate_canon",
    "alter_user_facing_content_by_coercion",
    "function_as_safety_gate",
    "function_as_ethics_gate",
    "function_as_moral_gate",
)

GOLDEN_TESTS = (
    "high_mdi_still_displays_original_output",
    "low_trust_score_still_displays_original_output",
    "high_risk_flag_adds_label_only",
    "metric_trigger_never_filters_output",
    "oracle_text_is_not_rewritten",
    "shadow_notes_do_not_mutate_canon",
    "review_ranking_is_visible_annotation_only",
    "forecast_weights_do_not_change_without_governance",
    "safety_ethics_moral_gate_flags_remain_false",
    "provenance_confidence_metric_context_is_visible",
)


def build_non_filtering_doctrine_packet() -> dict[str, Any]:
    packet = {
        "artifact_type": "AFENonFilteringObservationDoctrine.v1",
        "doctrine_id": DOCTRINE_ID,
        "authority": AUTHORITY,
        "output_effect": OUTPUT_EFFECT,
        "observation_only": True,
        "non_filtering_compliance": True,
        "core_rule": (
            "No derived metric may remove, suppress, filter, rewrite, demote, "
            "hide, or block Abraxas output."
        ),
        "required_output_handling_pattern": {
            "display_output": True,
            "display_observation_label": True,
            "display_provenance_confidence_metric_context": True,
            "metric_trigger_filters_output": False,
        },
        "allowed_metric_effects": list(ALLOWED_EFFECTS),
        "forbidden_metric_effects": {effect: False for effect in FORBIDDEN_EFFECTS},
        "shadow_lane_clarification": {
            "detects_only": True,
            "may_determine_truth": False,
            "may_determine_harm": False,
            "may_apply_moral_gate": False,
            "may_approve_output": False,
            "may_reject_output": False,
        },
        "forecast_lane_clarification": {
            "requires_governance_promotion_for_probabilistic_analysis": True,
            "may_remove_suppress_or_filter_output": False,
            "may_change_forecast_weights_without_governance": False,
        },
        "golden_tests": list(GOLDEN_TESTS),
    }
    packet["provenance_hash"] = stable_hash(packet)
    return packet


def attach_doctrine_observation(
    abraxas_output: dict[str, Any],
    *,
    labels: list[str] | None = None,
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "abraxas_output": deepcopy(abraxas_output),
        "afe_observation": {
            "authority": AUTHORITY,
            "output_effect": OUTPUT_EFFECT,
            "labels": list(labels or []),
            "metrics": deepcopy(metrics or {}),
            "non_filtering_compliance": True,
            "display_provenance_confidence_metric_context": True,
        },
        "forbidden_effects": {effect: False for effect in FORBIDDEN_EFFECTS},
    }
