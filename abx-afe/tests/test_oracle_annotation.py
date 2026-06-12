from __future__ import annotations

from afe.batch import build_hybrid_batch
from afe.oracle_annotation import attach_annotation_to_oracle_output, build_oracle_annotation
from afe.real_world_mapping import build_batch004_mapping_packet


def test_oracle_annotation_is_deterministic_and_annotation_only() -> None:
    traces = build_hybrid_batch(
        batch_id="AFE-BATCH-001",
        runs=3,
        seed_start=42,
        environment_set=("baseline", "scarcity", "high-noise"),
    )["agent_trace_intake_export"]["trace_packets"]
    batch004 = build_batch004_mapping_packet()

    first = build_oracle_annotation(trace_packets=traces, batch004_packet=batch004)
    second = build_oracle_annotation(trace_packets=traces, batch004_packet=batch004)

    assert first == second
    observation = first["afe_observation"]
    assert observation["authority"] == "SHADOW_ONLY_TRACE"
    assert observation["non_filtering_compliance"] is True
    assert observation["output_effect"] == "ANNOTATION_ONLY"
    assert "authority narrative stress" in observation["labels"]


def test_oracle_annotation_cannot_change_oracle_output() -> None:
    oracle_output = {"text": "show this exactly", "mode": "answer", "rank": 1}
    annotation = build_oracle_annotation(batch004_packet=build_batch004_mapping_packet())

    attached = attach_annotation_to_oracle_output(oracle_output, annotation)

    assert attached["oracle_output"] == oracle_output
    assert attached["afe_shadow_observation_panel"] == annotation["afe_observation"]
    assert attached["output_effect"] == "ANNOTATION_ONLY"
    assert attached["forbidden_effects"]["rewrite_oracle_text"] is False
    assert attached["forbidden_effects"]["mutate_oracle_mode_routing"] is False


def test_oracle_annotation_not_computable_when_no_sources() -> None:
    annotation = build_oracle_annotation(trace_packets=[], batch004_packet={"abx_metric_frame": {"source": []}})

    observation = annotation["afe_observation"]
    assert observation["labels"] == ["NOT_COMPUTABLE"]
    assert observation["source_run_ids"] == []
    assert set(observation["metrics"].values()) == {0.0}
