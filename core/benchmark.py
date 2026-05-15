"""Runtime benchmark contracts and drift guard for ABRAXAS v2.0.

PATCH-P10-RUNTIME-BENCHMARK-AND-DRIFT-GUARD-001

All outputs are:
  - observational-only
  - deterministic canonical JSON
  - authority_granted=False, mutation_allowed=False, promotion_allowed=False

No optimization auto-apply logic.  Drift guard is advisory-only.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter_ns
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.diagnostics import stable_correlation_id

PATCH_ID = "PATCH-P10-RUNTIME-BENCHMARK-AND-DRIFT-GUARD-001"

# ---------------------------------------------------------------------------
# Variance threshold for drift detection (nanoseconds).  Advisory-only.
# ---------------------------------------------------------------------------
_DEFAULT_VARIANCE_SPIKE_THRESHOLD_NS: int = 10_000_000  # 10 ms


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _sorted_dict(d: dict[str, Any]) -> dict[str, Any]:
    return {k: d[k] for k in sorted(d)}


# ---------------------------------------------------------------------------
# RuntimeBenchmarkResult.v1
# ---------------------------------------------------------------------------


def build_benchmark_result(
    *,
    surface: str,
    run_index: int,
    duration_ns: int,
    cache_hits: int = 0,
    cache_misses: int = 0,
    artifact_writes: int = 0,
    replay_traversals: int = 0,
    registry_loads: int = 0,
    serialization_counts: int = 0,
    output_hash: str = "",
) -> dict[str, Any]:
    """Build a RuntimeBenchmarkResult.v1 packet.

    Observational-only.  Does not mutate runtime or authority state.
    """
    return {
        "schema": "RuntimeBenchmarkResult.v1",
        "patch_id": PATCH_ID,
        "surface": surface,
        "run_index": run_index,
        "duration_ns": duration_ns,
        "cache_hits": cache_hits,
        "cache_misses": cache_misses,
        "artifact_writes": artifact_writes,
        "replay_traversals": replay_traversals,
        "registry_loads": registry_loads,
        "serialization_counts": serialization_counts,
        "output_hash": output_hash,
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }


# ---------------------------------------------------------------------------
# RuntimeBenchmarkSuite.v1
# ---------------------------------------------------------------------------


def build_benchmark_suite(
    *,
    suite_id: str,
    surface: str,
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Aggregate a list of RuntimeBenchmarkResult.v1 packets into a suite.

    Computes deterministic statistics across repeated runs.
    Observational-only.
    """
    durations = [r["duration_ns"] for r in results]
    n = len(durations)
    mean_ns = int(sum(durations) / n) if n else 0
    variance_ns = int(statistics.variance(durations)) if n > 1 else 0
    min_ns = min(durations) if n else 0
    max_ns = max(durations) if n else 0

    output_hashes = [r["output_hash"] for r in results]
    unique_hashes = sorted(set(output_hashes))
    hash_stable = len(unique_hashes) <= 1

    total_cache_hits = sum(r["cache_hits"] for r in results)
    total_cache_misses = sum(r["cache_misses"] for r in results)
    total_artifact_writes = sum(r["artifact_writes"] for r in results)
    total_replay_traversals = sum(r["replay_traversals"] for r in results)
    total_registry_loads = sum(r["registry_loads"] for r in results)
    total_serialization_counts = sum(r["serialization_counts"] for r in results)

    suite_hash = canonical_hash(
        {
            "suite_id": suite_id,
            "surface": surface,
            "run_count": n,
            "mean_ns": mean_ns,
            "unique_hashes": unique_hashes,
        }
    )

    return {
        "schema": "RuntimeBenchmarkSuite.v1",
        "patch_id": PATCH_ID,
        "suite_id": suite_id,
        "surface": surface,
        "run_count": n,
        "duration_ns": {
            "mean": mean_ns,
            "variance": variance_ns,
            "min": min_ns,
            "max": max_ns,
        },
        "cache": {
            "total_hits": total_cache_hits,
            "total_misses": total_cache_misses,
        },
        "artifact_writes": total_artifact_writes,
        "replay_traversals": total_replay_traversals,
        "registry_loads": total_registry_loads,
        "serialization_counts": total_serialization_counts,
        "output_hash_stable": hash_stable,
        "unique_output_hashes": unique_hashes,
        "suite_hash": suite_hash,
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }


# ---------------------------------------------------------------------------
# RuntimeOptimizationDriftReport.v1
# ---------------------------------------------------------------------------


def build_drift_report(
    *,
    report_id: str,
    baseline_suite: dict[str, Any],
    optimized_suite: dict[str, Any],
    variance_spike_threshold_ns: int = _DEFAULT_VARIANCE_SPIKE_THRESHOLD_NS,
) -> dict[str, Any]:
    """Compare a baseline and optimized benchmark suite and report drift.

    Advisory-only.  Does not mutate runtime, disable systems, or modify canon.
    """
    surface = baseline_suite.get("surface", "")

    # --- hash drift ---
    baseline_hashes = set(baseline_suite.get("unique_output_hashes", []))
    optimized_hashes = set(optimized_suite.get("unique_output_hashes", []))
    output_hash_drift = baseline_hashes != optimized_hashes

    # --- replay divergence: output hashes changed between runs ---
    baseline_hash_stable = baseline_suite.get("output_hash_stable", True)
    optimized_hash_stable = optimized_suite.get("output_hash_stable", True)
    replay_divergence_detected = (not baseline_hash_stable) or (not optimized_hash_stable)

    # --- cache contamination: misses rose vs baseline ---
    baseline_misses = baseline_suite.get("cache", {}).get("total_misses", 0)
    optimized_misses = optimized_suite.get("cache", {}).get("total_misses", 0)
    cache_contamination_detected = optimized_misses > baseline_misses

    # --- variance spike ---
    baseline_variance = baseline_suite.get("duration_ns", {}).get("variance", 0)
    optimized_variance = optimized_suite.get("duration_ns", {}).get("variance", 0)
    variance_spike_detected = (
        abs(optimized_variance - baseline_variance) > variance_spike_threshold_ns
    )

    # --- serialization instability: serialization counts differ ---
    baseline_serial = baseline_suite.get("serialization_counts", 0)
    optimized_serial = optimized_suite.get("serialization_counts", 0)
    serialization_instability_detected = baseline_serial != optimized_serial

    # --- artifact ordering drift: artifact_writes differ ---
    baseline_writes = baseline_suite.get("artifact_writes", 0)
    optimized_writes = optimized_suite.get("artifact_writes", 0)
    artifact_ordering_drift_detected = baseline_writes != optimized_writes

    # --- performance delta ---
    baseline_mean = baseline_suite.get("duration_ns", {}).get("mean", 0)
    optimized_mean = optimized_suite.get("duration_ns", {}).get("mean", 0)
    delta_ns = optimized_mean - baseline_mean
    delta_pct = round((delta_ns / baseline_mean) * 100, 6) if baseline_mean else 0.0  # guard: baseline is zero → no percentage

    detections: list[str] = []
    if output_hash_drift:
        detections.append("output_hash_drift")
    if replay_divergence_detected:
        detections.append("replay_divergence")
    if cache_contamination_detected:
        detections.append("cache_contamination")
    if variance_spike_detected:
        detections.append("variance_spike")
    if serialization_instability_detected:
        detections.append("serialization_instability")
    if artifact_ordering_drift_detected:
        detections.append("artifact_ordering_drift")

    drift_detected = len(detections) > 0

    report_hash = canonical_hash(
        {
            "report_id": report_id,
            "surface": surface,
            "baseline_suite_hash": baseline_suite.get("suite_hash", ""),
            "optimized_suite_hash": optimized_suite.get("suite_hash", ""),
            "drift_detected": drift_detected,
            "detections": sorted(detections),
        }
    )

    return {
        "schema": "RuntimeOptimizationDriftReport.v1",
        "patch_id": PATCH_ID,
        "report_id": report_id,
        "surface": surface,
        "baseline_suite_hash": baseline_suite.get("suite_hash", ""),
        "optimized_suite_hash": optimized_suite.get("suite_hash", ""),
        "performance_delta": {
            "delta_ns": delta_ns,
            "delta_pct": delta_pct,
            "baseline_mean_ns": baseline_mean,
            "optimized_mean_ns": optimized_mean,
        },
        "drift_detected": drift_detected,
        "detections": sorted(detections),
        "advisory": {
            "output_hash_drift": output_hash_drift,
            "replay_divergence_detected": replay_divergence_detected,
            "cache_contamination_detected": cache_contamination_detected,
            "variance_spike_detected": variance_spike_detected,
            "serialization_instability_detected": serialization_instability_detected,
            "artifact_ordering_drift_detected": artifact_ordering_drift_detected,
        },
        "report_hash": report_hash,
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }


# ---------------------------------------------------------------------------
# BenchmarkRunner — collects timed passes over a callable surface
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class BenchmarkRunner:
    """Execute repeated benchmark passes over a named surface.

    Results are observational-only and do not mutate runtime state.
    """

    surface: str
    run_count: int = 3
    _results: list[dict[str, Any]] = field(default_factory=list, init=False)

    def run(
        self,
        fn: Any,
        *,
        cache_hits: int = 0,
        cache_misses: int = 0,
        artifact_writes: int = 0,
        replay_traversals: int = 0,
        registry_loads: int = 0,
        serialization_counts: int = 0,
    ) -> list[dict[str, Any]]:
        """Execute *fn* for ``run_count`` iterations and collect results."""
        self._results = []
        for i in range(self.run_count):
            t0 = perf_counter_ns()
            output = fn()
            duration_ns = max(perf_counter_ns() - t0, 0)
            output_hash = canonical_hash(output) if output is not None else ""
            self._results.append(
                build_benchmark_result(
                    surface=self.surface,
                    run_index=i,
                    duration_ns=duration_ns,
                    cache_hits=cache_hits,
                    cache_misses=cache_misses,
                    artifact_writes=artifact_writes,
                    replay_traversals=replay_traversals,
                    registry_loads=registry_loads,
                    serialization_counts=serialization_counts,
                    output_hash=output_hash,
                )
            )
        return list(self._results)

    def build_suite(self, suite_id: str) -> dict[str, Any]:
        """Aggregate collected results into a RuntimeBenchmarkSuite.v1."""
        return build_benchmark_suite(
            suite_id=suite_id,
            surface=self.surface,
            results=self._results,
        )


# ---------------------------------------------------------------------------
# Top-level benchmark artifact builder
# ---------------------------------------------------------------------------


def build_benchmark_artifact(
    *,
    artifact_id: str,
    baseline_suite: dict[str, Any],
    optimized_suite: dict[str, Any],
    output_path: str | Path,
) -> dict[str, Any]:
    """Build the full benchmark artifact packet including drift report.

    Observational-only.  Does not mutate runtime state.
    """
    correlation_id = stable_correlation_id(
        f"runtime_benchmark.{artifact_id}",
        artifact_path=output_path,
        context={"artifact_id": artifact_id},
    )

    drift_report = build_drift_report(
        report_id=f"{artifact_id}.drift",
        baseline_suite=baseline_suite,
        optimized_suite=optimized_suite,
    )

    artifact: dict[str, Any] = {
        "schema": "RuntimeBenchmarkArtifact.v1",
        "patch_id": PATCH_ID,
        "artifact_id": artifact_id,
        "correlation_id": correlation_id,
        "baseline_suite": baseline_suite,
        "optimized_suite": optimized_suite,
        "drift_report": drift_report,
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }

    return artifact


def write_benchmark_artifact(
    path: str | Path,
    artifact: dict[str, Any],
) -> Path:
    """Write benchmark artifact to *path* as canonical JSON."""
    target = Path(path)
    write_canonical_json(target, artifact)
    return target


# ---------------------------------------------------------------------------
# ReplayScalingComparison.v1 — observational replay cost comparison
# ---------------------------------------------------------------------------


def build_replay_scaling_comparison(
    *,
    comparison_id: str,
    full_replay_suite: dict[str, Any],
    incremental_replay_suite: dict[str, Any],
) -> dict[str, Any]:
    """Compare full vs incremental replay cost surfaces.

    Observational-only.  Does not mutate runtime, authority, or replay state.
    Does not auto-apply optimizations.

    Fields emitted:
    - full vs incremental replay traversal counts
    - full vs incremental replay chunk counts
    - artifact regeneration reduction ratio
    - performance delta between full and incremental surfaces
    - replay equivalence held flag (advisory)
    """
    full_traversals = full_replay_suite.get("replay_traversals", 0)
    inc_traversals = incremental_replay_suite.get("replay_traversals", 0)

    full_chunks = full_replay_suite.get("replay_chunk_count", 0)
    inc_chunks = incremental_replay_suite.get("replay_chunk_count", 0)

    full_artifact_writes = full_replay_suite.get("artifact_writes", 0)
    inc_artifact_writes = incremental_replay_suite.get("artifact_writes", 0)
    artifact_regeneration_reduction = (
        round(1.0 - (inc_artifact_writes / full_artifact_writes), 6)
        if full_artifact_writes > 0
        else 0.0
    )

    full_mean_ns = full_replay_suite.get("duration_ns", {}).get("mean", 0)
    inc_mean_ns = incremental_replay_suite.get("duration_ns", {}).get("mean", 0)
    replay_cost_delta_ns = inc_mean_ns - full_mean_ns
    replay_cost_delta_pct = (
        round((replay_cost_delta_ns / full_mean_ns) * 100, 6)
        if full_mean_ns > 0
        else 0.0
    )

    full_hashes = set(full_replay_suite.get("unique_output_hashes", []))
    inc_hashes = set(incremental_replay_suite.get("unique_output_hashes", []))
    replay_equivalence_held = full_hashes == inc_hashes

    comparison_hash = canonical_hash(
        {
            "comparison_id": comparison_id,
            "full_suite_hash": full_replay_suite.get("suite_hash", ""),
            "incremental_suite_hash": incremental_replay_suite.get("suite_hash", ""),
            "replay_equivalence_held": replay_equivalence_held,
        }
    )

    return {
        "schema": "ReplayScalingComparison.v1",
        "patch_id": PATCH_ID,
        "comparison_id": comparison_id,
        "full_replay_traversals": full_traversals,
        "incremental_replay_traversals": inc_traversals,
        "full_replay_chunk_count": full_chunks,
        "incremental_replay_chunk_count": inc_chunks,
        "full_artifact_writes": full_artifact_writes,
        "incremental_artifact_writes": inc_artifact_writes,
        "artifact_regeneration_reduction": artifact_regeneration_reduction,
        "replay_cost": {
            "full_mean_ns": full_mean_ns,
            "incremental_mean_ns": inc_mean_ns,
            "delta_ns": replay_cost_delta_ns,
            "delta_pct": replay_cost_delta_pct,
        },
        "replay_equivalence_held": replay_equivalence_held,
        "comparison_hash": comparison_hash,
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
        "optimization_auto_apply": False,
    }
