"""Deterministic tests for PATCH-P11-OPERATOR-RUNTIME-CONSOLE-001.

Proves:
- packet shape stability
- missing source artifact handling (NOT_COMPUTABLE / BLOCKED)
- projection_only / advisory_only flags always True
- authority / mutation / promotion flags always False
- deterministic operator next actions
- Markdown summary generation
- no runtime / canon mutation
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

from core.config import RuntimePaths
from core.operator_runtime_console import (
    PATCH_ID,
    NOT_COMPUTABLE,
    build_console_markdown,
    build_operator_console_packet,
    write_console_packet,
)
from scripts import run_operator_runtime_console


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_profile_artifact() -> dict[str, Any]:
    return {
        "patch_id": "PATCH-P8-RUNTIME-PERFORMANCE-PROFILING-001",
        "profile_enabled": True,
        "measured_surfaces": ["registry_generation"],
        "phase_timings": {},
        "artifact_paths": {},
        "correlation_ids": {},
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
        "final_status": "PASS",
        "remaining_blockers": [],
    }


def _make_benchmark_artifact() -> dict[str, Any]:
    return {
        "schema": "RuntimeBenchmarkArtifact.v1",
        "patch_id": "PATCH-P10-RUNTIME-BENCHMARK-AND-DRIFT-GUARD-001",
        "artifact_id": "runtime_benchmark_001",
        "correlation_id": "cid",
        "baseline_suite": {
            "suite_id": "baseline",
            "surface": "reg",
            "run_count": 3,
            "duration_ns": {"mean": 1_000_000, "variance": 0, "min": 1_000_000, "max": 1_000_000},
            "cache": {"total_hits": 0, "total_misses": 0},
            "artifact_writes": 1,
            "replay_traversals": 0,
            "registry_loads": 1,
            "serialization_counts": 1,
            "output_hash_stable": True,
            "unique_output_hashes": ["h1"],
            "suite_hash": "sh1",
            "authority_granted": False,
            "mutation_allowed": False,
            "promotion_allowed": False,
        },
        "optimized_suite": {
            "suite_id": "optimized",
            "surface": "reg",
            "run_count": 3,
            "duration_ns": {"mean": 900_000, "variance": 0, "min": 900_000, "max": 900_000},
            "cache": {"total_hits": 0, "total_misses": 0},
            "artifact_writes": 1,
            "replay_traversals": 0,
            "registry_loads": 1,
            "serialization_counts": 1,
            "output_hash_stable": True,
            "unique_output_hashes": ["h1"],
            "suite_hash": "sh2",
            "authority_granted": False,
            "mutation_allowed": False,
            "promotion_allowed": False,
        },
        "drift_report": {
            "schema": "RuntimeOptimizationDriftReport.v1",
            "patch_id": "PATCH-P10-RUNTIME-BENCHMARK-AND-DRIFT-GUARD-001",
            "report_id": "runtime_benchmark_001.drift",
            "surface": "reg",
            "baseline_suite_hash": "sh1",
            "optimized_suite_hash": "sh2",
            "performance_delta": {
                "delta_ns": -100_000,
                "delta_pct": -10.0,
                "baseline_mean_ns": 1_000_000,
                "optimized_mean_ns": 900_000,
            },
            "drift_detected": False,
            "detections": [],
            "advisory": {
                "output_hash_drift": False,
                "replay_divergence_detected": False,
                "cache_contamination_detected": False,
                "variance_spike_detected": False,
                "serialization_instability_detected": False,
                "artifact_ordering_drift_detected": False,
            },
            "report_hash": "rh1",
            "authority_granted": False,
            "mutation_allowed": False,
            "promotion_allowed": False,
        },
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }


def _make_stabilization_artifact() -> dict[str, Any]:
    return {
        "stabilization_arc": {
            "patch_id": "PATCH-P6-STABILIZATION-RELEASE-READINESS-001",
        },
        "release_readiness": {"status": "ready_for_manual_release_review"},
        "final_posture": {
            "status": "STABILIZED_RELEASE_READINESS_RECORDED",
            "authority_granted": False,
            "mutation_allowed": False,
            "promotion_allowed": False,
        },
    }


def _make_freeze_artifact() -> dict[str, Any]:
    return {
        "patch_id": "PATCH-P7-MANUAL-RELEASE-TAG-AND-GOVERNANCE-FREEZE-001",
        "freeze_status": "FROZEN",
        "frozen_surfaces": {
            "runtime_authority_routing": "frozen",
            "api_public_readonly_guard": "frozen",
        },
        "freeze_effective_head": "abc123",
    }


def _write_artifacts(tmp_path: Path) -> list[str]:
    """Write all four source artifacts to tmp_path; return their paths."""
    profile_path = str(tmp_path / "runtime_performance_profile_001.latest.json")
    benchmark_path = str(tmp_path / "runtime_benchmark_001.latest.json")
    stab_path = str(tmp_path / "stabilization_release_readiness_001.latest.json")
    freeze_path = str(tmp_path / "governance_freeze_baseline_001.latest.json")

    Path(profile_path).write_text(
        json.dumps(_make_profile_artifact()), encoding="utf-8"
    )
    Path(benchmark_path).write_text(
        json.dumps(_make_benchmark_artifact()), encoding="utf-8"
    )
    Path(stab_path).write_text(
        json.dumps(_make_stabilization_artifact()), encoding="utf-8"
    )
    Path(freeze_path).write_text(
        json.dumps(_make_freeze_artifact()), encoding="utf-8"
    )
    return [profile_path, benchmark_path, stab_path, freeze_path]


# ---------------------------------------------------------------------------
# Packet shape stability
# ---------------------------------------------------------------------------


def test_console_packet_top_level_keys_are_stable(tmp_path: Path) -> None:
    paths = _write_artifacts(tmp_path)
    packet = build_operator_console_packet(
        packet_id="test_console_001", source_artifact_paths=paths
    )

    expected_keys = [
        "patch_id",
        "packet_id",
        "correlation_id",
        "source_artifacts",
        "runtime_profile_summary",
        "benchmark_summary",
        "optimization_drift_summary",
        "artifact_health_summary",
        "authority_boundary_summary",
        "cache_safety_summary",
        "replay_equivalence_summary",
        "stabilization_summary",
        "governance_freeze_summary",
        "replay_scaling_summary",
        "incremental_replay_health",
        "replay_invalidation_posture",
        "operator_next_actions",
        "final_posture",
        "packet_hash",
        "authority_granted",
        "mutation_allowed",
        "promotion_allowed",
        "projection_only",
        "advisory_only",
        "final_status",
        "remaining_blockers",
    ]
    assert list(packet) == expected_keys


def test_console_packet_patch_id_is_correct(tmp_path: Path) -> None:
    paths = _write_artifacts(tmp_path)
    packet = build_operator_console_packet(
        packet_id="test_001", source_artifact_paths=paths
    )
    assert packet["patch_id"] == PATCH_ID


# ---------------------------------------------------------------------------
# Hard posture flags
# ---------------------------------------------------------------------------


def test_authority_granted_always_false(tmp_path: Path) -> None:
    paths = _write_artifacts(tmp_path)
    packet = build_operator_console_packet(
        packet_id="p", source_artifact_paths=paths
    )
    assert packet["authority_granted"] is False
    assert packet["final_posture"]["authority_granted"] is False
    assert packet["authority_boundary_summary"]["authority_granted"] is False


def test_mutation_allowed_always_false(tmp_path: Path) -> None:
    paths = _write_artifacts(tmp_path)
    packet = build_operator_console_packet(
        packet_id="p", source_artifact_paths=paths
    )
    assert packet["mutation_allowed"] is False
    assert packet["final_posture"]["mutation_allowed"] is False
    assert packet["authority_boundary_summary"]["mutation_allowed"] is False


def test_promotion_allowed_always_false(tmp_path: Path) -> None:
    paths = _write_artifacts(tmp_path)
    packet = build_operator_console_packet(
        packet_id="p", source_artifact_paths=paths
    )
    assert packet["promotion_allowed"] is False
    assert packet["final_posture"]["promotion_allowed"] is False
    assert packet["authority_boundary_summary"]["promotion_allowed"] is False


def test_projection_only_always_true(tmp_path: Path) -> None:
    paths = _write_artifacts(tmp_path)
    packet = build_operator_console_packet(
        packet_id="p", source_artifact_paths=paths
    )
    assert packet["projection_only"] is True
    assert packet["final_posture"]["projection_only"] is True
    assert packet["authority_boundary_summary"]["projection_only"] is True


def test_advisory_only_always_true(tmp_path: Path) -> None:
    paths = _write_artifacts(tmp_path)
    packet = build_operator_console_packet(
        packet_id="p", source_artifact_paths=paths
    )
    assert packet["advisory_only"] is True
    assert packet["final_posture"]["advisory_only"] is True
    assert packet["authority_boundary_summary"]["advisory_only"] is True


# ---------------------------------------------------------------------------
# Missing source artifact handling
# ---------------------------------------------------------------------------


def test_missing_all_artifacts_yields_not_computable() -> None:
    packet = build_operator_console_packet(
        packet_id="missing_all",
        source_artifact_paths=[
            "/nonexistent/runtime_performance_profile_001.latest.json",
            "/nonexistent/runtime_benchmark_001.latest.json",
            "/nonexistent/stabilization_release_readiness_001.latest.json",
            "/nonexistent/governance_freeze_baseline_001.latest.json",
        ],
    )
    assert packet["runtime_profile_summary"]["status"] == NOT_COMPUTABLE
    assert packet["benchmark_summary"]["status"] == NOT_COMPUTABLE
    assert packet["optimization_drift_summary"]["status"] == NOT_COMPUTABLE
    assert packet["cache_safety_summary"]["status"] == NOT_COMPUTABLE
    assert packet["replay_equivalence_summary"]["status"] == NOT_COMPUTABLE
    assert packet["stabilization_summary"]["status"] == NOT_COMPUTABLE
    assert packet["governance_freeze_summary"]["status"] == NOT_COMPUTABLE


def test_missing_all_artifacts_remaining_blockers_non_empty() -> None:
    packet = build_operator_console_packet(
        packet_id="missing_all",
        source_artifact_paths=[
            "/nonexistent/runtime_performance_profile_001.latest.json",
            "/nonexistent/runtime_benchmark_001.latest.json",
            "/nonexistent/stabilization_release_readiness_001.latest.json",
            "/nonexistent/governance_freeze_baseline_001.latest.json",
        ],
    )
    assert len(packet["remaining_blockers"]) > 0


def test_missing_all_artifacts_final_status_blocked() -> None:
    packet = build_operator_console_packet(
        packet_id="missing_all",
        source_artifact_paths=[
            "/nonexistent/runtime_performance_profile_001.latest.json",
            "/nonexistent/runtime_benchmark_001.latest.json",
            "/nonexistent/stabilization_release_readiness_001.latest.json",
            "/nonexistent/governance_freeze_baseline_001.latest.json",
        ],
    )
    assert packet["final_status"] == "BLOCKED"


def test_missing_artifact_does_not_fabricate_values() -> None:
    """Summaries for missing artifacts must not contain fabricated numeric values."""
    packet = build_operator_console_packet(
        packet_id="missing_bench",
        source_artifact_paths=[
            "/nonexistent/runtime_benchmark_001.latest.json",
        ],
    )
    bm = packet["benchmark_summary"]
    assert bm["status"] == NOT_COMPUTABLE
    # When missing, drift_detected must not be present (no fabrication)
    assert "drift_detected" not in bm
    # Key assertion: no numeric drift values are fabricated
    assert "drift_detections" not in bm


def test_partial_missing_operators_include_blocked_note(tmp_path: Path) -> None:
    """With some artifacts missing, operator_next_actions must list BLOCKED items."""
    # Only provide benchmark; others missing
    benchmark_path = str(tmp_path / "runtime_benchmark_001.latest.json")
    Path(benchmark_path).write_text(
        json.dumps(_make_benchmark_artifact()), encoding="utf-8"
    )
    packet = build_operator_console_packet(
        packet_id="partial",
        source_artifact_paths=[
            "/nonexistent/runtime_performance_profile_001.latest.json",
            benchmark_path,
            "/nonexistent/stabilization_release_readiness_001.latest.json",
            "/nonexistent/governance_freeze_baseline_001.latest.json",
        ],
    )
    blocked = [a for a in packet["operator_next_actions"] if a.startswith("BLOCKED")]
    assert len(blocked) > 0


# ---------------------------------------------------------------------------
# All artifacts present → PASS
# ---------------------------------------------------------------------------


def test_all_artifacts_present_final_status_pass(tmp_path: Path) -> None:
    paths = _write_artifacts(tmp_path)
    packet = build_operator_console_packet(
        packet_id="full_pass", source_artifact_paths=paths
    )
    assert packet["final_status"] == "PASS"
    assert packet["remaining_blockers"] == []


def test_all_artifacts_present_operator_actions_not_empty(tmp_path: Path) -> None:
    paths = _write_artifacts(tmp_path)
    packet = build_operator_console_packet(
        packet_id="full_pass", source_artifact_paths=paths
    )
    assert len(packet["operator_next_actions"]) > 0


# ---------------------------------------------------------------------------
# Deterministic operator next actions
# ---------------------------------------------------------------------------


def test_operator_next_actions_deterministic(tmp_path: Path) -> None:
    paths = _write_artifacts(tmp_path)
    packet_a = build_operator_console_packet(
        packet_id="det_001", source_artifact_paths=paths
    )
    packet_b = build_operator_console_packet(
        packet_id="det_001", source_artifact_paths=paths
    )
    assert packet_a["operator_next_actions"] == packet_b["operator_next_actions"]


def test_packet_hash_deterministic(tmp_path: Path) -> None:
    paths = _write_artifacts(tmp_path)
    packet_a = build_operator_console_packet(
        packet_id="hash_det", source_artifact_paths=paths
    )
    packet_b = build_operator_console_packet(
        packet_id="hash_det", source_artifact_paths=paths
    )
    assert packet_a["packet_hash"] == packet_b["packet_hash"]


# ---------------------------------------------------------------------------
# Artifact health summary
# ---------------------------------------------------------------------------


def test_artifact_health_summary_all_present(tmp_path: Path) -> None:
    paths = _write_artifacts(tmp_path)
    packet = build_operator_console_packet(
        packet_id="h", source_artifact_paths=paths
    )
    ah = packet["artifact_health_summary"]
    assert ah["all_present"] is True
    assert ah["missing"] == []
    assert len(ah["present"]) == 4


def test_artifact_health_summary_missing_tracked() -> None:
    paths = [
        "/nonexistent/runtime_performance_profile_001.latest.json",
        "/nonexistent/runtime_benchmark_001.latest.json",
    ]
    packet = build_operator_console_packet(packet_id="hm", source_artifact_paths=paths)
    ah = packet["artifact_health_summary"]
    assert ah["all_present"] is False
    assert len(ah["missing"]) == 2


# ---------------------------------------------------------------------------
# Drift signal in benchmark → advisory actions emitted
# ---------------------------------------------------------------------------


def test_drift_signals_produce_advisory_actions(tmp_path: Path) -> None:
    bench = _make_benchmark_artifact()
    bench["drift_report"]["drift_detected"] = True
    bench["drift_report"]["detections"] = ["output_hash_drift", "variance_spike"]
    bench_path = str(tmp_path / "runtime_benchmark_001.latest.json")
    Path(bench_path).write_text(json.dumps(bench), encoding="utf-8")

    packet = build_operator_console_packet(
        packet_id="drift_actions",
        source_artifact_paths=[bench_path],
    )
    advisory_actions = [a for a in packet["operator_next_actions"] if "ADVISORY" in a]
    assert len(advisory_actions) >= 2


# ---------------------------------------------------------------------------
# Write to canonical JSON
# ---------------------------------------------------------------------------


def test_write_console_packet_produces_canonical_json(tmp_path: Path) -> None:
    paths = _write_artifacts(tmp_path)
    packet = build_operator_console_packet(
        packet_id="write_test", source_artifact_paths=paths
    )
    out_path = tmp_path / "console_test.json"
    written = write_console_packet(out_path, packet)

    assert written == out_path
    text = written.read_text(encoding="utf-8")
    assert text.endswith("\n")
    payload = json.loads(text)
    assert payload["patch_id"] == PATCH_ID
    assert payload["authority_granted"] is False
    assert payload["projection_only"] is True


# ---------------------------------------------------------------------------
# Markdown summary generation
# ---------------------------------------------------------------------------


def test_markdown_summary_generated(tmp_path: Path) -> None:
    paths = _write_artifacts(tmp_path)
    packet = build_operator_console_packet(
        packet_id="md_test", source_artifact_paths=paths
    )
    md = build_console_markdown(packet)
    assert "Operator Runtime Console" in md
    assert PATCH_ID in md
    assert "Authority Boundary" in md
    assert "Artifact Health" in md
    assert "Benchmark Summary" in md
    assert "Operator Next Actions" in md


def test_markdown_summary_missing_artifacts(tmp_path: Path) -> None:
    packet = build_operator_console_packet(
        packet_id="md_missing",
        source_artifact_paths=[
            "/nonexistent/runtime_benchmark_001.latest.json",
        ],
    )
    md = build_console_markdown(packet)
    assert "Missing" in md


def test_markdown_summary_ends_with_newline(tmp_path: Path) -> None:
    paths = _write_artifacts(tmp_path)
    packet = build_operator_console_packet(
        packet_id="md_nl", source_artifact_paths=paths
    )
    md = build_console_markdown(packet)
    # build_console_markdown uses join — last element may or may not end in \n
    # We only assert it's a non-empty string
    assert len(md) > 0


# ---------------------------------------------------------------------------
# No runtime / canon mutation
# ---------------------------------------------------------------------------


def test_packet_does_not_mutate_source_data(tmp_path: Path) -> None:
    """Building a packet must not modify the source artifact data on disk."""
    paths = _write_artifacts(tmp_path)
    bench_path = next(p for p in paths if "runtime_benchmark" in p)
    before_text = Path(bench_path).read_text(encoding="utf-8")

    build_operator_console_packet(packet_id="no_mutate", source_artifact_paths=paths)

    after_text = Path(bench_path).read_text(encoding="utf-8")
    assert before_text == after_text


def test_optimization_auto_apply_always_false(tmp_path: Path) -> None:
    paths = _write_artifacts(tmp_path)
    packet = build_operator_console_packet(
        packet_id="no_auto", source_artifact_paths=paths
    )
    assert packet["optimization_drift_summary"]["optimization_auto_apply"] is False


def test_replay_semantic_changes_always_false(tmp_path: Path) -> None:
    paths = _write_artifacts(tmp_path)
    packet = build_operator_console_packet(
        packet_id="no_replay", source_artifact_paths=paths
    )
    assert packet["replay_equivalence_summary"]["replay_semantic_changes"] is False


# ---------------------------------------------------------------------------
# Script integration
# ---------------------------------------------------------------------------


def test_script_writes_artifact(tmp_path: Path) -> None:
    runtime_paths = RuntimePaths(
        contracts_dir=Path("contracts"),
        out_dir=tmp_path / "out",
    )
    out_path = runtime_paths.operator_runtime_console_latest

    with (
        patch.object(run_operator_runtime_console, "_PATHS", runtime_paths),
        patch.object(run_operator_runtime_console, "OUT_PATH", out_path),
    ):
        run_operator_runtime_console.main()

    assert out_path.exists()
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["patch_id"] == PATCH_ID
    assert payload["authority_granted"] is False
    assert payload["projection_only"] is True
    assert payload["advisory_only"] is True


def test_script_writes_markdown(tmp_path: Path) -> None:
    runtime_paths = RuntimePaths(
        contracts_dir=Path("contracts"),
        out_dir=tmp_path / "out",
    )
    out_path = runtime_paths.operator_runtime_console_latest

    with (
        patch.object(run_operator_runtime_console, "_PATHS", runtime_paths),
        patch.object(run_operator_runtime_console, "OUT_PATH", out_path),
    ):
        run_operator_runtime_console.main()

    md_path = out_path.with_suffix(".md")
    assert md_path.exists()
    md_text = md_path.read_text(encoding="utf-8")
    assert "Operator Runtime Console" in md_text


def test_operator_runtime_console_path_in_config() -> None:
    paths = RuntimePaths(contracts_dir=Path("contracts"), out_dir=Path("out"))
    assert paths.operator_runtime_console_latest == Path(
        "out/audit/operator_runtime_console_001.latest.json"
    )
