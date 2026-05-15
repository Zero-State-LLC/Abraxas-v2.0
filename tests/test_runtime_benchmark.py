"""Benchmark invariance tests for PATCH-P10-RUNTIME-BENCHMARK-AND-DRIFT-GUARD-001.

Proves:
- stable benchmark packet shape
- identical output hashes pre/post benchmark
- deterministic benchmark aggregation
- cache isolation across runs
- replay equivalence preserved
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

from core.benchmark import (
    PATCH_ID,
    BenchmarkRunner,
    build_benchmark_artifact,
    build_benchmark_result,
    build_benchmark_suite,
    build_drift_report,
    write_benchmark_artifact,
)
from core.canonical.json import canonical_hash
from scripts import run_runtime_benchmark


# ---------------------------------------------------------------------------
# RuntimeBenchmarkResult.v1 — packet shape
# ---------------------------------------------------------------------------


def test_benchmark_result_packet_shape_is_stable() -> None:
    result = build_benchmark_result(
        surface="test_surface",
        run_index=0,
        duration_ns=1_000_000,
        cache_hits=2,
        cache_misses=1,
        artifact_writes=1,
        replay_traversals=3,
        registry_loads=1,
        serialization_counts=2,
        output_hash="abc123",
    )

    assert list(result) == [
        "schema",
        "patch_id",
        "surface",
        "run_index",
        "duration_ns",
        "cache_hits",
        "cache_misses",
        "artifact_writes",
        "replay_traversals",
        "registry_loads",
        "serialization_counts",
        "output_hash",
        "authority_granted",
        "mutation_allowed",
        "promotion_allowed",
    ]
    assert result["schema"] == "RuntimeBenchmarkResult.v1"
    assert result["patch_id"] == PATCH_ID
    assert result["authority_granted"] is False
    assert result["mutation_allowed"] is False
    assert result["promotion_allowed"] is False


def test_benchmark_result_authority_flags_all_false() -> None:
    result = build_benchmark_result(
        surface="test_surface",
        run_index=0,
        duration_ns=500,
    )
    assert result["authority_granted"] is False
    assert result["mutation_allowed"] is False
    assert result["promotion_allowed"] is False


# ---------------------------------------------------------------------------
# RuntimeBenchmarkSuite.v1 — deterministic aggregation
# ---------------------------------------------------------------------------


def _make_results(
    surface: str,
    durations: list[int],
    output_hash: str = "stable_hash",
) -> list[dict[str, Any]]:
    return [
        build_benchmark_result(
            surface=surface,
            run_index=i,
            duration_ns=d,
            output_hash=output_hash,
        )
        for i, d in enumerate(durations)
    ]


def test_benchmark_suite_packet_shape_is_stable() -> None:
    results = _make_results("reg.baseline", [1_000, 2_000, 3_000])
    suite = build_benchmark_suite(
        suite_id="test_suite_001",
        surface="reg.baseline",
        results=results,
    )

    assert list(suite) == [
        "schema",
        "patch_id",
        "suite_id",
        "surface",
        "run_count",
        "duration_ns",
        "cache",
        "artifact_writes",
        "replay_traversals",
        "registry_loads",
        "serialization_counts",
        "output_hash_stable",
        "unique_output_hashes",
        "suite_hash",
        "authority_granted",
        "mutation_allowed",
        "promotion_allowed",
    ]
    assert suite["schema"] == "RuntimeBenchmarkSuite.v1"
    assert suite["patch_id"] == PATCH_ID


def test_benchmark_suite_authority_flags_all_false() -> None:
    results = _make_results("s", [100])
    suite = build_benchmark_suite(suite_id="sid", surface="s", results=results)
    assert suite["authority_granted"] is False
    assert suite["mutation_allowed"] is False
    assert suite["promotion_allowed"] is False


def test_benchmark_suite_aggregation_is_deterministic() -> None:
    """Same inputs must produce identical suite_hash across calls."""
    durations = [1_000_000, 2_000_000, 3_000_000]
    results = _make_results("registry.baseline", durations, output_hash="h1")

    suite_a = build_benchmark_suite(
        suite_id="suite_det_001",
        surface="registry.baseline",
        results=results,
    )
    suite_b = build_benchmark_suite(
        suite_id="suite_det_001",
        surface="registry.baseline",
        results=results,
    )

    assert suite_a["suite_hash"] == suite_b["suite_hash"]


def test_benchmark_suite_mean_computed_correctly() -> None:
    results = _make_results("s", [1_000, 3_000])
    suite = build_benchmark_suite(suite_id="sid", surface="s", results=results)
    assert suite["duration_ns"]["mean"] == 2_000
    assert suite["run_count"] == 2


def test_benchmark_suite_output_hash_stable_when_hashes_identical() -> None:
    results = _make_results("s", [1_000, 2_000, 3_000], output_hash="same_hash")
    suite = build_benchmark_suite(suite_id="sid", surface="s", results=results)
    assert suite["output_hash_stable"] is True
    assert suite["unique_output_hashes"] == ["same_hash"]


def test_benchmark_suite_output_hash_unstable_when_hashes_differ() -> None:
    results = [
        build_benchmark_result(surface="s", run_index=0, duration_ns=100, output_hash="h1"),
        build_benchmark_result(surface="s", run_index=1, duration_ns=200, output_hash="h2"),
    ]
    suite = build_benchmark_suite(suite_id="sid", surface="s", results=results)
    assert suite["output_hash_stable"] is False
    assert sorted(suite["unique_output_hashes"]) == ["h1", "h2"]


# ---------------------------------------------------------------------------
# Cache isolation across runs
# ---------------------------------------------------------------------------


def test_cache_counts_are_isolated_per_result() -> None:
    """Each result carries its own cache counts; they are summed in the suite."""
    results = [
        build_benchmark_result(surface="s", run_index=0, duration_ns=100, cache_hits=5, cache_misses=1),
        build_benchmark_result(surface="s", run_index=1, duration_ns=200, cache_hits=3, cache_misses=0),
    ]
    suite = build_benchmark_suite(suite_id="sid", surface="s", results=results)
    assert suite["cache"]["total_hits"] == 8
    assert suite["cache"]["total_misses"] == 1


# ---------------------------------------------------------------------------
# RuntimeOptimizationDriftReport.v1 — drift detection
# ---------------------------------------------------------------------------


def _make_suite(
    suite_id: str,
    surface: str,
    *,
    durations: list[int] | None = None,
    output_hash: str = "stable",
    cache_misses: int = 0,
    serialization_counts: int = 1,
    artifact_writes: int = 1,
) -> dict[str, Any]:
    if durations is None:
        durations = [1_000_000, 1_100_000, 1_050_000]
    results = [
        build_benchmark_result(
            surface=surface,
            run_index=i,
            duration_ns=d,
            output_hash=output_hash,
            cache_misses=cache_misses,
            serialization_counts=serialization_counts,
            artifact_writes=artifact_writes,
        )
        for i, d in enumerate(durations)
    ]
    return build_benchmark_suite(suite_id=suite_id, surface=surface, results=results)


def test_drift_report_packet_shape_is_stable() -> None:
    baseline = _make_suite("b", "reg")
    optimized = _make_suite("o", "reg")
    report = build_drift_report(
        report_id="test_report_001",
        baseline_suite=baseline,
        optimized_suite=optimized,
    )

    assert list(report) == [
        "schema",
        "patch_id",
        "report_id",
        "surface",
        "baseline_suite_hash",
        "optimized_suite_hash",
        "performance_delta",
        "drift_detected",
        "detections",
        "advisory",
        "report_hash",
        "authority_granted",
        "mutation_allowed",
        "promotion_allowed",
    ]
    assert report["schema"] == "RuntimeOptimizationDriftReport.v1"
    assert report["patch_id"] == PATCH_ID


def test_drift_report_authority_flags_all_false() -> None:
    baseline = _make_suite("b", "s")
    optimized = _make_suite("o", "s")
    report = build_drift_report(report_id="rid", baseline_suite=baseline, optimized_suite=optimized)
    assert report["authority_granted"] is False
    assert report["mutation_allowed"] is False
    assert report["promotion_allowed"] is False


def test_drift_report_no_drift_when_identical() -> None:
    baseline = _make_suite("b", "reg", durations=[1_000_000, 1_000_000, 1_000_000])
    optimized = _make_suite("o", "reg", durations=[1_000_000, 1_000_000, 1_000_000])
    report = build_drift_report(report_id="rid", baseline_suite=baseline, optimized_suite=optimized)
    assert report["drift_detected"] is False
    assert report["detections"] == []


def test_drift_report_detects_output_hash_drift() -> None:
    baseline = _make_suite("b", "s", output_hash="hash_a")
    optimized = _make_suite("o", "s", output_hash="hash_b")
    report = build_drift_report(report_id="rid", baseline_suite=baseline, optimized_suite=optimized)
    assert report["drift_detected"] is True
    assert "output_hash_drift" in report["detections"]


def test_drift_report_detects_cache_contamination() -> None:
    baseline = _make_suite("b", "s", cache_misses=0)
    optimized = _make_suite("o", "s", cache_misses=5)
    report = build_drift_report(report_id="rid", baseline_suite=baseline, optimized_suite=optimized)
    assert report["drift_detected"] is True
    assert "cache_contamination" in report["detections"]


def test_drift_report_detects_serialization_instability() -> None:
    baseline = _make_suite("b", "s", serialization_counts=2)
    optimized = _make_suite("o", "s", serialization_counts=4)
    report = build_drift_report(report_id="rid", baseline_suite=baseline, optimized_suite=optimized)
    assert "serialization_instability" in report["detections"]


def test_drift_report_detects_artifact_ordering_drift() -> None:
    baseline = _make_suite("b", "s", artifact_writes=1)
    optimized = _make_suite("o", "s", artifact_writes=3)
    report = build_drift_report(report_id="rid", baseline_suite=baseline, optimized_suite=optimized)
    assert "artifact_ordering_drift" in report["detections"]


def test_drift_report_is_advisory_only() -> None:
    """Drift detection must never mutate runtime state."""
    baseline = _make_suite("b", "s", output_hash="h1")
    optimized = _make_suite("o", "s", output_hash="h2")
    report = build_drift_report(report_id="rid", baseline_suite=baseline, optimized_suite=optimized)
    # Advisory flags exist; mutation flags stay False
    assert report["drift_detected"] is True
    assert report["authority_granted"] is False
    assert report["mutation_allowed"] is False
    assert report["promotion_allowed"] is False


def test_drift_report_hash_is_deterministic() -> None:
    baseline = _make_suite("b", "s")
    optimized = _make_suite("o", "s")
    report_a = build_drift_report(report_id="rid", baseline_suite=baseline, optimized_suite=optimized)
    report_b = build_drift_report(report_id="rid", baseline_suite=baseline, optimized_suite=optimized)
    assert report_a["report_hash"] == report_b["report_hash"]


# ---------------------------------------------------------------------------
# BenchmarkRunner
# ---------------------------------------------------------------------------


def test_benchmark_runner_collects_results() -> None:
    runner = BenchmarkRunner(surface="test_surface", run_count=3)
    results = runner.run(lambda: {"key": "value"})
    assert len(results) == 3
    for i, r in enumerate(results):
        assert r["run_index"] == i
        assert r["surface"] == "test_surface"
        assert r["duration_ns"] >= 0


def test_benchmark_runner_output_hash_stable_for_deterministic_fn() -> None:
    runner = BenchmarkRunner(surface="s", run_count=3)
    runner.run(lambda: {"constant": 42})
    suite = runner.build_suite("sid")
    assert suite["output_hash_stable"] is True


def test_benchmark_runner_suite_authority_flags_all_false() -> None:
    runner = BenchmarkRunner(surface="s", run_count=2)
    runner.run(lambda: None)
    suite = runner.build_suite("sid")
    assert suite["authority_granted"] is False
    assert suite["mutation_allowed"] is False
    assert suite["promotion_allowed"] is False


# ---------------------------------------------------------------------------
# Identical output hashes pre/post benchmark
# ---------------------------------------------------------------------------


def test_output_hash_unchanged_across_benchmark_runs() -> None:
    """The benchmark must not change the output produced by the surface fn."""
    target = {"a": 1, "b": 2}
    expected_hash = canonical_hash(target)

    runner = BenchmarkRunner(surface="hash_check", run_count=5)
    results = runner.run(lambda: target)

    for r in results:
        assert r["output_hash"] == expected_hash


# ---------------------------------------------------------------------------
# Replay equivalence preserved
# ---------------------------------------------------------------------------


def test_replay_equivalence_preserved_across_runs() -> None:
    """Multiple runs of the same surface must produce identical output hashes."""
    call_count = 0

    def deterministic_surface() -> dict[str, int]:
        nonlocal call_count
        call_count += 1
        return {"result": 1}

    runner = BenchmarkRunner(surface="replay_check", run_count=4)
    results = runner.run(deterministic_surface)

    hashes = [r["output_hash"] for r in results]
    assert len(set(hashes)) == 1, "All runs must produce the same output hash"
    assert call_count == 4


# ---------------------------------------------------------------------------
# Benchmark artifact write + canonical JSON
# ---------------------------------------------------------------------------


def test_benchmark_artifact_write_is_canonical_json(tmp_path: Path) -> None:
    baseline = _make_suite("b", "s")
    optimized = _make_suite("o", "s")
    artifact = build_benchmark_artifact(
        artifact_id="test_artifact_001",
        baseline_suite=baseline,
        optimized_suite=optimized,
        output_path=tmp_path / "bench.json",
    )
    written = write_benchmark_artifact(tmp_path / "bench.json", artifact)

    text = written.read_text(encoding="utf-8")
    assert text.endswith("\n")
    payload = json.loads(text)
    assert payload["patch_id"] == PATCH_ID
    assert payload["authority_granted"] is False
    assert payload["mutation_allowed"] is False
    assert payload["promotion_allowed"] is False


def test_benchmark_artifact_schema_field_present() -> None:
    baseline = _make_suite("b", "s")
    optimized = _make_suite("o", "s")
    artifact = build_benchmark_artifact(
        artifact_id="aid",
        baseline_suite=baseline,
        optimized_suite=optimized,
        output_path=Path("out/audit/runtime_benchmark_001.latest.json"),
    )
    assert artifact["schema"] == "RuntimeBenchmarkArtifact.v1"


# ---------------------------------------------------------------------------
# Script integration — output path unchanged + no side effects
# ---------------------------------------------------------------------------


def test_benchmark_script_writes_artifact(tmp_path: Path) -> None:
    runtime_paths = __import__("core.config", fromlist=["RuntimePaths"]).RuntimePaths(
        contracts_dir=Path("contracts"),
        out_dir=tmp_path / "out",
    )
    out_path = runtime_paths.runtime_benchmark_latest

    with (
        patch.object(run_runtime_benchmark, "_PATHS", runtime_paths),
        patch.object(run_runtime_benchmark, "OUT_PATH", out_path),
        patch.object(run_runtime_benchmark, "CONTRACTS_DIR", Path("contracts/pipelines")),
    ):
        run_runtime_benchmark.main()

    assert out_path.exists()
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["patch_id"] == PATCH_ID
    assert payload["authority_granted"] is False
    assert payload["mutation_allowed"] is False
    assert payload["promotion_allowed"] is False


def test_benchmark_script_output_hash_stable_across_calls(tmp_path: Path) -> None:
    """Running the benchmark script twice must not change the artifact hash."""
    runtime_paths = __import__("core.config", fromlist=["RuntimePaths"]).RuntimePaths(
        contracts_dir=Path("contracts"),
        out_dir=tmp_path / "out",
    )
    out_path = runtime_paths.runtime_benchmark_latest

    with (
        patch.object(run_runtime_benchmark, "_PATHS", runtime_paths),
        patch.object(run_runtime_benchmark, "OUT_PATH", out_path),
        patch.object(run_runtime_benchmark, "CONTRACTS_DIR", Path("contracts/pipelines")),
    ):
        run_runtime_benchmark.main()
        first_text = out_path.read_text(encoding="utf-8")
        first_payload = json.loads(first_text)

        run_runtime_benchmark.main()
        second_payload = json.loads(out_path.read_text(encoding="utf-8"))

    # The schema and authority flags must be identical across calls
    for key in ("schema", "patch_id", "authority_granted", "mutation_allowed", "promotion_allowed"):
        assert first_payload[key] == second_payload[key]


def test_runtime_benchmark_path_in_config() -> None:
    """RuntimePaths must expose the runtime_benchmark_latest property."""
    from core.config import RuntimePaths

    paths = RuntimePaths(contracts_dir=Path("contracts"), out_dir=Path("out"))
    assert paths.runtime_benchmark_latest == Path("out/audit/runtime_benchmark_001.latest.json")
