from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

from core.aal_viz_graph_render_packet import build_aal_viz_graph_render_packet
from core.aal_viz_runtime_projection import build_runtime_projection_packet
from core.coherence_field_operator_surface import (
    BLOCKED,
    NOT_COMPUTABLE,
    build_coherence_field_operator_surface_markdown,
    build_coherence_field_operator_surface_packet,
    summarize_coherence_field_operator_surface,
)
from core.generated_artifact_registry import (
    build_generated_artifact_registry,
    list_ci_drift_artifact_paths,
)
from scripts import run_coherence_field_operator_surface


def _p27_payload(
    *,
    aggregate: float = 0.82,
    resonance: float = 0.77,
    dissonance: float = 0.18,
    phase_alignment_bucket: str = "HIGH",
    dominant_coherence_component: str = "replay_resonance",
    replay_resonance_zone_count: int = 2,
    topology_alignment_zone_count: int = 1,
    authority_granted: bool = False,
    mutation_allowed: bool = False,
) -> dict[str, Any]:
    return {
        "schema": "TemporalResonanceCoherencePacket.v1",
        "packet_id": "temporal_resonance_coherence_001",
        "packet_hash": "p27-hash",
        "aggregate_coherence_score": aggregate,
        "resonance_score": resonance,
        "dissonance_score": dissonance,
        "phase_alignment_bucket": phase_alignment_bucket,
        "dominant_coherence_component": dominant_coherence_component,
        "replay_resonance_zone_count": replay_resonance_zone_count,
        "topology_alignment_zone_count": topology_alignment_zone_count,
        "authority_granted": authority_granted,
        "mutation_allowed": mutation_allowed,
    }


def _optional_payload() -> dict[str, Any]:
    return {
        "schema": "OptionalContext.v1",
        "authority_granted": False,
        "mutation_allowed": False,
    }


def _write_payloads(
    tmp_path: Path,
    *,
    include_p27: bool = True,
    corrupt_p27: bool = False,
    p27_override: dict[str, Any] | None = None,
    optional_authority_violation: bool = False,
) -> dict[str, str]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    payloads: dict[str, Any] = {
        "aal_viz_runtime_projection": _optional_payload(),
        "aal_viz_graph_render_packet": _optional_payload(),
        "operator_action_queue": _optional_payload(),
    }
    if optional_authority_violation:
        payloads["aal_viz_graph_render_packet"] = {
            "schema": "AALVizGraphRenderPacket.v1",
            "authority_granted": True,
        }
    if include_p27:
        payloads["temporal_resonance_coherence"] = p27_override or _p27_payload()

    paths: dict[str, str] = {}
    for key, payload in payloads.items():
        path = tmp_path / f"{key}.json"
        if key == "temporal_resonance_coherence" and corrupt_p27:
            path.write_text("{bad json", encoding="utf-8")
        else:
            path.write_text(json.dumps(payload), encoding="utf-8")
        paths[key] = path.as_posix()

    if not include_p27:
        paths["temporal_resonance_coherence"] = (tmp_path / "__missing_temporal_resonance_coherence__.json").as_posix()
    return paths


def test_deterministic_json_hash_stability(tmp_path: Path) -> None:
    sources = _write_payloads(tmp_path)
    packet_a = build_coherence_field_operator_surface_packet(source_artifact_paths=sources)
    packet_b = build_coherence_field_operator_surface_packet(source_artifact_paths=sources)
    assert packet_a["surface_hash"] == packet_b["surface_hash"]
    assert packet_a["coherence_cards"] == packet_b["coherence_cards"]
    assert packet_a["coherence_rails"] == packet_b["coherence_rails"]


def test_deterministic_markdown_stability(tmp_path: Path) -> None:
    packet = build_coherence_field_operator_surface_packet(
        source_artifact_paths=_write_payloads(tmp_path)
    )
    md_a = build_coherence_field_operator_surface_markdown(packet)
    md_b = build_coherence_field_operator_surface_markdown(packet)
    assert md_a == md_b
    assert md_a.endswith("\n")
    assert "# P28 Coherence Field Operator Surface" in md_a


def test_missing_p27_is_not_computable(tmp_path: Path) -> None:
    packet = build_coherence_field_operator_surface_packet(
        source_artifact_paths=_write_payloads(tmp_path, include_p27=False)
    )
    assert packet["coherence_field_operator_surface_status"] == NOT_COMPUTABLE
    assert packet["operator_coherence_posture"] == NOT_COMPUTABLE


def test_corrupt_p27_is_not_computable(tmp_path: Path) -> None:
    packet = build_coherence_field_operator_surface_packet(
        source_artifact_paths=_write_payloads(tmp_path, corrupt_p27=True)
    )
    assert packet["coherence_field_operator_surface_status"] == NOT_COMPUTABLE
    assert packet["operator_attention_level"] == NOT_COMPUTABLE


def test_authority_violation_is_blocked(tmp_path: Path) -> None:
    packet = build_coherence_field_operator_surface_packet(
        source_artifact_paths=_write_payloads(tmp_path, optional_authority_violation=True)
    )
    assert packet["coherence_field_operator_surface_status"] == BLOCKED
    assert packet["blocker_code"] == "authority_boundary_violation"
    assert packet["operator_attention_level"] == "CRITICAL"


def test_posture_thresholds_locked_stable_watch_degraded(tmp_path: Path) -> None:
    locked = build_coherence_field_operator_surface_packet(
        source_artifact_paths=_write_payloads(
            tmp_path / "locked",
            p27_override=_p27_payload(aggregate=0.9, dissonance=0.1),
        )
    )
    stable = build_coherence_field_operator_surface_packet(
        source_artifact_paths=_write_payloads(
            tmp_path / "stable",
            p27_override=_p27_payload(aggregate=0.75, dissonance=0.2),
        )
    )
    watch = build_coherence_field_operator_surface_packet(
        source_artifact_paths=_write_payloads(
            tmp_path / "watch",
            p27_override=_p27_payload(aggregate=0.55, dissonance=0.5),
        )
    )
    degraded = build_coherence_field_operator_surface_packet(
        source_artifact_paths=_write_payloads(
            tmp_path / "degraded",
            p27_override=_p27_payload(aggregate=0.3, dissonance=0.7),
        )
    )
    assert locked["operator_coherence_posture"] == "LOCKED"
    assert stable["operator_coherence_posture"] == "STABLE"
    assert watch["operator_coherence_posture"] == "WATCH"
    assert degraded["operator_coherence_posture"] == "DEGRADED"


def test_attention_thresholds(tmp_path: Path) -> None:
    low = build_coherence_field_operator_surface_packet(
        source_artifact_paths=_write_payloads(
            tmp_path / "low", p27_override=_p27_payload(aggregate=0.9, dissonance=0.1)
        )
    )
    medium = build_coherence_field_operator_surface_packet(
        source_artifact_paths=_write_payloads(
            tmp_path / "medium",
            p27_override=_p27_payload(aggregate=0.4, dissonance=0.36),
        )
    )
    high = build_coherence_field_operator_surface_packet(
        source_artifact_paths=_write_payloads(
            tmp_path / "high",
            p27_override=_p27_payload(aggregate=0.45, dissonance=0.62),
        )
    )
    critical = build_coherence_field_operator_surface_packet(
        source_artifact_paths=_write_payloads(
            tmp_path / "critical", optional_authority_violation=True
        )
    )
    not_computable = build_coherence_field_operator_surface_packet(
        source_artifact_paths=_write_payloads(tmp_path / "not_computable", include_p27=False)
    )
    assert low["operator_attention_level"] == "LOW"
    assert medium["operator_attention_level"] == "MEDIUM"
    assert high["operator_attention_level"] == "HIGH"
    assert critical["operator_attention_level"] == "CRITICAL"
    assert not_computable["operator_attention_level"] == NOT_COMPUTABLE


def test_artifact_registry_classification_remains_derived_optional() -> None:
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    json_entry = next(
        item
        for item in registry.entries
        if item.artifact_path
        == "out/projections/coherence_field_operator_surface_001.latest.json"
    )
    md_entry = next(
        item
        for item in registry.entries
        if item.artifact_path
        == "out/projections/coherence_field_operator_surface_001.latest.md"
    )
    assert json_entry.determinism_class == "DERIVED_OPTIONAL"
    assert md_entry.determinism_class == "DERIVED_OPTIONAL"
    assert (
        "out/projections/coherence_field_operator_surface_001.latest.json"
        not in list_ci_drift_artifact_paths(registry)
    )


def test_invariant_authority_fields_cannot_become_true(tmp_path: Path) -> None:
    packet = build_coherence_field_operator_surface_packet(
        source_artifact_paths=_write_payloads(tmp_path, optional_authority_violation=True)
    )
    assert packet["mutation_allowed"] is False
    assert packet["authority_granted"] is False
    assert packet["forecast_authority"] is False
    assert packet["execution_authority"] is False
    assert packet["command_channel"] is False
    assert packet["bidirectional_control"] is False
    assert packet["autonomous_adaptation"] is False


def test_deterministic_badge_and_card_ordering(tmp_path: Path) -> None:
    packet = build_coherence_field_operator_surface_packet(
        source_artifact_paths=_write_payloads(tmp_path)
    )
    assert packet["coherence_badges"] == sorted(packet["coherence_badges"])
    assert packet["coherence_cards"] == sorted(
        packet["coherence_cards"],
        key=lambda item: (
            {
                "BLOCKED": 0,
                "CRITICAL": 1,
                "DEGRADED": 2,
                "HIGH": 3,
                "WATCH": 4,
                "MEDIUM": 5,
                "STABLE": 6,
                "LOW": 7,
                "LOCKED": 8,
                NOT_COMPUTABLE: 9,
            }.get(str(item.get("status")), 999),
            -float(item.get("score", 0.0)),
            str(item.get("card_id", "")),
        ),
    )


def test_downstream_projection_summaries_preserve_boundaries(tmp_path: Path) -> None:
    surface_packet = build_coherence_field_operator_surface_packet(
        source_artifact_paths=_write_payloads(tmp_path)
    )
    surface_summary = summarize_coherence_field_operator_surface(surface_packet)
    assert surface_summary["projection_only"] is True
    assert surface_summary["authority_granted"] is False
    assert surface_summary["mutation_allowed"] is False

    runtime_payloads: dict[str, dict[str, Any] | None] = {
        "out/projections/coherence_field_operator_surface_001.latest.json": surface_packet,
    }
    graph_payloads: dict[str, dict[str, Any] | None] = {
        "out/projections/coherence_field_operator_surface_001.latest.json": surface_packet,
    }

    def _runtime_load(path: str | Path | None) -> dict[str, Any] | None:
        return runtime_payloads.get(str(path), None)

    def _graph_load(path: str | Path | None) -> dict[str, Any] | None:
        return graph_payloads.get(str(path), None)

    with patch("core.aal_viz_runtime_projection._load_artifact", side_effect=_runtime_load):
        runtime_packet = build_runtime_projection_packet()
    with patch(
        "core.aal_viz_graph_render_packet._load_artifact", side_effect=_graph_load
    ):
        graph_packet = build_aal_viz_graph_render_packet()

    assert runtime_packet["projection_only"] is True
    assert runtime_packet["authority_granted"] is False
    assert runtime_packet["coherence_field_operator_surface_status"] in {
        "PRESENT",
        NOT_COMPUTABLE,
        BLOCKED,
    }
    assert runtime_packet["operator_coherence_posture"] in {
        "LOCKED",
        "STABLE",
        "WATCH",
        "DEGRADED",
        BLOCKED,
        NOT_COMPUTABLE,
    }
    assert graph_packet["projection_only"] is True
    assert graph_packet["authority_granted"] is False
    assert graph_packet["coherence_field_operator_surface_status"] in {
        "PRESENT",
        NOT_COMPUTABLE,
        BLOCKED,
    }


def test_run_script_writes_artifacts(tmp_path: Path) -> None:
    runtime_paths = run_coherence_field_operator_surface.RuntimePaths(
        contracts_dir=tmp_path / "contracts",
        out_dir=tmp_path / "out",
    )
    sources = _write_payloads(tmp_path / "sources")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(sources, sort_keys=True), encoding="utf-8")

    with (
        patch.object(run_coherence_field_operator_surface, "_PATHS", runtime_paths),
        patch.object(
            run_coherence_field_operator_surface,
            "OUT_PATH",
            runtime_paths.coherence_field_operator_surface_latest,
        ),
    ):
        run_coherence_field_operator_surface.main(["--manifest", manifest.as_posix()])

    assert runtime_paths.coherence_field_operator_surface_latest.exists()
    assert runtime_paths.coherence_field_operator_surface_latest.with_suffix(".md").exists()
