from __future__ import annotations

from afe.aal_viz_overlay import build_aal_viz_overlay_packet


def test_aal_viz_overlay_is_deterministic_and_projection_only() -> None:
    first = build_aal_viz_overlay_packet()
    second = build_aal_viz_overlay_packet()

    assert first == second
    assert first["authority"] == "SHADOW_ONLY_TRACE"
    assert first["output_effect"] == "VISUAL_ANNOTATION_ONLY"
    assert first["projection_only"] is True
    assert first["non_filtering_compliance"] is True


def test_aal_viz_overlay_keeps_raw_layer_visible() -> None:
    packet = build_aal_viz_overlay_packet()

    assert packet["raw_layer"]["always_visible"] is True
    assert packet["raw_layer"]["readable_at_all_times"] is True
    assert all(node["raw_visible"] is True for node in packet["raw_layer"]["nodes"])
    assert all(edge["raw_visible"] is True for edge in packet["raw_layer"]["edges"])


def test_aal_viz_overlay_opacity_and_forbidden_rendering() -> None:
    packet = build_aal_viz_overlay_packet()

    assert all(layer["opacity"] <= 0.6 for layer in packet["overlay_layers"])
    assert all(layer["annotation_required"] is True for layer in packet["overlay_layers"])
    assert all(layer["raw_layer_remains_visible"] is True for layer in packet["overlay_layers"])
    assert set(packet["rendering_locks"].values()) == {False, 0.6}
