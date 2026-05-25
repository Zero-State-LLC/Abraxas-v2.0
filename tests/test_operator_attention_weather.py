from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.generated_artifact_registry import build_generated_artifact_registry, list_ci_drift_artifact_paths
from core.operator_attention_weather import (
    NOT_COMPUTABLE,
    build_operator_attention_weather_packet,
    write_operator_attention_weather_packet,
)


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _sources(tmp_path: Path, *, missing: str | None = None, corrupt: str | None = None) -> dict[str, str]:
    paths = {
        "coherence_field_operator_surface": tmp_path / "coherence.json",
        "temporal_coherence_chain": tmp_path / "chain.json",
        "temporal_upstream_evidence": tmp_path / "evidence.json",
    }
    payloads = {
        "coherence_field_operator_surface": {"coherence_field_operator_surface_status": "PRESENT", "operator_attention_level": "LOW", "remaining_blockers": []},
        "temporal_coherence_chain": {"final_chain_status": "ADVISORY_ONLY", "blockers": []},
        "temporal_upstream_evidence": {"final_evidence_status": "READY", "checked_artifacts": []},
    }
    for k,p in payloads.items():
        if k == missing:
            continue
        if k == corrupt:
            paths[k].write_text("{bad", encoding="utf-8")
        else:
            _write(paths[k], p)
    return {k: v.as_posix() for k,v in paths.items()}


def test_healthy_build_clear_or_watch(tmp_path: Path) -> None:
    p = build_operator_attention_weather_packet(source_artifact_paths=_sources(tmp_path))
    assert p["final_status"] == "ADVISORY_ONLY"
    assert p["weather_posture"] in {"CLEAR", "WATCH"}


def test_missing_source_not_computable_blocked(tmp_path: Path) -> None:
    p = build_operator_attention_weather_packet(source_artifact_paths=_sources(tmp_path, missing="temporal_coherence_chain"))
    assert p["final_status"] == NOT_COMPUTABLE
    assert p["weather_posture"] == "BLOCKED"


def test_corrupt_source_not_computable_or_blocked(tmp_path: Path) -> None:
    p = build_operator_attention_weather_packet(source_artifact_paths=_sources(tmp_path, corrupt="temporal_upstream_evidence"))
    assert p["final_status"] in {NOT_COMPUTABLE, "BLOCKED"}


def test_blockers_propagate(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    _write(Path(src["temporal_coherence_chain"]), {"final_chain_status": "BLOCKED", "blockers": ["x"]})
    p = build_operator_attention_weather_packet(source_artifact_paths=src)
    assert "x" in p["blocker_summary"]


def test_governance_flags_locked(tmp_path: Path) -> None:
    p = build_operator_attention_weather_packet(source_artifact_paths=_sources(tmp_path))
    g = p["governance_flags"]
    assert g["authority_granted"] is False and g["mutation_allowed"] is False and g["execution_authority"] is False
    assert g["forecast_authority"] is False and g["queue_mutation_allowed"] is False


def test_deterministic_repeat_and_hashes_stable(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    a = build_operator_attention_weather_packet(source_artifact_paths=src)
    b = build_operator_attention_weather_packet(source_artifact_paths=src)
    assert a["weather_hash"] == b["weather_hash"]
    assert a["source_hashes"] == b["source_hashes"]


def test_writer_emits_final_newline(tmp_path: Path) -> None:
    p = build_operator_attention_weather_packet(source_artifact_paths=_sources(tmp_path))
    out = tmp_path / "out.json"
    write_operator_attention_weather_packet(out, p)
    assert out.with_suffix('.md').read_text(encoding='utf-8').endswith("\n")


def test_inputs_not_mutated(tmp_path: Path) -> None:
    src_packets = {
        "coherence_field_operator_surface": {"coherence_field_operator_surface_status": "PRESENT", "operator_attention_level": "LOW"},
        "temporal_coherence_chain": {"final_chain_status": "ADVISORY_ONLY", "blockers": []},
        "temporal_upstream_evidence": {"final_evidence_status": "READY", "checked_artifacts": []},
    }
    before = deepcopy(src_packets)
    build_operator_attention_weather_packet(source_packets=src_packets, source_artifact_paths={})
    assert src_packets == before


def test_registry_classification_derived_optional() -> None:
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    json_entry = next(e for e in registry.entries if e.artifact_path == "out/projections/operator_attention_weather_001.latest.json")
    md_entry = next(e for e in registry.entries if e.artifact_path == "out/projections/operator_attention_weather_001.latest.md")
    assert json_entry.determinism_class == "DERIVED_OPTIONAL"
    assert md_entry.determinism_class == "DERIVED_OPTIONAL"
    assert "out/projections/operator_attention_weather_001.latest.json" not in list_ci_drift_artifact_paths(registry)
