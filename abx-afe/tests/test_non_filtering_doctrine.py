from __future__ import annotations

from afe.non_filtering_doctrine import (
    FORBIDDEN_EFFECTS,
    attach_doctrine_observation,
    build_non_filtering_doctrine_packet,
)


def test_non_filtering_doctrine_is_deterministic_observation_only() -> None:
    first = build_non_filtering_doctrine_packet()
    second = build_non_filtering_doctrine_packet()

    assert first == second
    assert first["authority"] == "SHADOW_ONLY_TRACE"
    assert first["output_effect"] == "OBSERVATION_ONLY"
    assert first["observation_only"] is True
    assert first["non_filtering_compliance"] is True


def test_non_filtering_doctrine_denies_all_filtering_and_mutation_effects() -> None:
    packet = build_non_filtering_doctrine_packet()

    assert packet["required_output_handling_pattern"]["display_output"] is True
    assert packet["required_output_handling_pattern"]["metric_trigger_filters_output"] is False
    assert packet["forecast_lane_clarification"]["may_change_forecast_weights_without_governance"] is False
    assert set(packet["forbidden_metric_effects"]) == set(FORBIDDEN_EFFECTS)
    assert set(packet["forbidden_metric_effects"].values()) == {False}
    assert packet["shadow_lane_clarification"]["detects_only"] is True
    assert packet["shadow_lane_clarification"]["may_determine_truth"] is False


def test_doctrine_observation_copies_output_without_rewrite_or_filter() -> None:
    output = {"text": "Keep this intact.", "items": ["a", "b"]}

    attached = attach_doctrine_observation(output, labels=["high_mdi"], metrics={"MDI": 0.99})
    output["text"] = "mutated after attach"
    output["items"].append("c")

    assert attached["abraxas_output"] == {"text": "Keep this intact.", "items": ["a", "b"]}
    assert attached["afe_observation"]["labels"] == ["high_mdi"]
    assert attached["afe_observation"]["metrics"] == {"MDI": 0.99}
    assert set(attached["forbidden_effects"].values()) == {False}


def test_doctrine_golden_tests_cover_required_blockers() -> None:
    packet = build_non_filtering_doctrine_packet()

    assert len(packet["golden_tests"]) == 10
    assert "high_mdi_still_displays_original_output" in packet["golden_tests"]
    assert "metric_trigger_never_filters_output" in packet["golden_tests"]
    assert "forecast_weights_do_not_change_without_governance" in packet["golden_tests"]
    assert "safety_ethics_moral_gate_flags_remain_false" in packet["golden_tests"]
