from __future__ import annotations

from afe.real_world_mapping import attach_mapping_to_output, build_batch004_mapping_packet


def test_batch004_mapping_is_deterministic_and_annotation_only() -> None:
    first = build_batch004_mapping_packet()
    second = build_batch004_mapping_packet()

    assert first == second
    assert first["authority"] == "SHADOW_ONLY_TRACE"
    assert first["output_effect"] == "ANNOTATION_ONLY"
    assert first["live_ingestion_performed"] is False
    assert first["original_output_preserved"] is True
    assert len(first["observations"]) == 7


def test_batch004_abx_metric_frame_bounds() -> None:
    packet = build_batch004_mapping_packet()
    frame = packet["abx_metric_frame"]

    assert frame["packet_type"] == "ABXMetricFrame.v1"
    assert frame["annotation_only"] is True
    assert frame["source"] == ["AFE-BATCH-004"]
    for value in frame["metrics"].values():
        assert 0.0 <= value <= 1.0


def test_batch004_mapping_cannot_filter_original_output() -> None:
    original = {"body": "display this exactly", "forecast_weight": 0.5}
    observation = build_batch004_mapping_packet()["observations"][1]

    attached = attach_mapping_to_output(original, observation)

    assert attached["original_output"] == original
    assert attached["output_effect"] == "ANNOTATION_ONLY"
    assert attached["non_filtering_compliance"] is True
    assert "batch004_mapping_label" in attached
