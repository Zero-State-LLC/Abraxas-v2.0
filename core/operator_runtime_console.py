"""Operator-facing runtime console packet builder for ABRAXAS v2.0.

PATCH-P11-OPERATOR-RUNTIME-CONSOLE-001

Builds a deterministic, projection-only packet that summarizes:
  - runtime profiling
  - benchmark results
  - optimization drift
  - artifact health
  - authority boundary
  - cache safety
  - replay equivalence

Hard posture:
  - authority_granted=False
  - mutation_allowed=False
  - promotion_allowed=False
  - projection_only=True
  - advisory_only=True

No runtime semantic changes.  No authority changes.
No forecast/canon changes.  No replay behaviour changes.
No optimization auto-apply.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.diagnostics import stable_correlation_id

PATCH_ID = "PATCH-P11-OPERATOR-RUNTIME-CONSOLE-001"

# ---------------------------------------------------------------------------
# Sentinel values used when a source artifact is absent or unreadable.
# ---------------------------------------------------------------------------
_NOT_COMPUTABLE = "NOT_COMPUTABLE"
_BLOCKED = "BLOCKED"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load_json(path: str | Path) -> dict[str, Any] | None:
    """Load a JSON artifact from *path*.

    Returns the parsed dict on success, or None when the file is absent or
    cannot be parsed.  Does not raise.
    """
    try:
        text = Path(path).read_text(encoding="utf-8")
        value: Any = json.loads(text)
        if isinstance(value, dict):
            return value
        return None
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _artifact_status(path: str | Path, data: dict[str, Any] | None) -> str:
    """Return PRESENT, MISSING, or NOT_COMPUTABLE for an artifact."""
    if data is None:
        return "MISSING"
    raw_status = data.get("final_status") or data.get("status") or ""
    if str(raw_status).upper() in (_NOT_COMPUTABLE, _BLOCKED):
        return _NOT_COMPUTABLE
    return "PRESENT"


# ---------------------------------------------------------------------------
# Per-section summarisers
# ---------------------------------------------------------------------------


def _summarise_runtime_profile(
    data: dict[str, Any] | None,
    path: str | Path,
) -> dict[str, Any]:
    if data is None:
        return {
            "status": _NOT_COMPUTABLE,
            "source_artifact": str(path),
            "detail": "Source artifact absent; cannot compute profile summary.",
        }
    measured_surfaces = data.get("measured_surfaces", [])
    phase_count = len(data.get("phase_timings", {}))
    profile_enabled = data.get("profile_enabled", False)
    return {
        "status": "PRESENT",
        "source_artifact": str(path),
        "profile_enabled": profile_enabled,
        "measured_surface_count": len(measured_surfaces),
        "measured_surfaces": sorted(measured_surfaces),
        "phase_count": phase_count,
        "final_status": data.get("final_status", _NOT_COMPUTABLE),
    }


def _summarise_benchmark(
    data: dict[str, Any] | None,
    path: str | Path,
) -> dict[str, Any]:
    if data is None:
        return {
            "status": _NOT_COMPUTABLE,
            "source_artifact": str(path),
            "detail": "Source artifact absent; cannot compute benchmark summary.",
        }
    baseline = data.get("baseline_suite", {})
    optimized = data.get("optimized_suite", {})
    drift_report = data.get("drift_report", {})
    return {
        "status": "PRESENT",
        "source_artifact": str(path),
        "baseline_run_count": baseline.get("run_count", 0),
        "optimized_run_count": optimized.get("run_count", 0),
        "baseline_mean_ns": baseline.get("duration_ns", {}).get("mean", 0),
        "optimized_mean_ns": optimized.get("duration_ns", {}).get("mean", 0),
        "output_hash_stable": baseline.get("output_hash_stable", False),
        "drift_detected": drift_report.get("drift_detected", False),
    }


def _summarise_drift(
    data: dict[str, Any] | None,
    path: str | Path,
) -> dict[str, Any]:
    if data is None:
        return {
            "status": _NOT_COMPUTABLE,
            "source_artifact": str(path),
            "detail": "Source artifact absent; cannot compute drift summary.",
        }
    drift_report = data.get("drift_report", {})
    detections: list[str] = sorted(drift_report.get("detections", []))
    advisory: dict[str, Any] = drift_report.get("advisory", {})
    return {
        "status": "PRESENT",
        "source_artifact": str(path),
        "drift_detected": drift_report.get("drift_detected", False),
        "detections": detections,
        "advisory": advisory,
        "performance_delta": drift_report.get("performance_delta", {}),
    }


def _summarise_artifact_health(
    sources: dict[str, dict[str, Any] | None],
    paths: dict[str, str | Path],
) -> dict[str, Any]:
    health: dict[str, str] = {}
    blockers: list[str] = []
    for name, data in sources.items():
        status = _artifact_status(paths[name], data)
        health[name] = status
        if status in (_NOT_COMPUTABLE, _BLOCKED, "MISSING"):
            blockers.append(name)
    overall = "HEALTHY" if not blockers else _NOT_COMPUTABLE
    return {
        "status": overall,
        "artifact_statuses": health,
        "blockers": sorted(blockers),
    }


def _summarise_authority_boundary(
    stabilization: dict[str, Any] | None,
    freeze: dict[str, Any] | None,
) -> dict[str, Any]:
    stabilization_auth: dict[str, Any] = {}
    if stabilization:
        ab = stabilization.get("authority_boundary_status", {})
        stabilization_auth = {
            "authority_granted": ab.get("authority_granted", False),
            "mutation_allowed": ab.get("mutation_allowed", False),
            "promotion_allowed": ab.get("promotion_allowed", False),
            "status": ab.get("status", _NOT_COMPUTABLE),
        }
    freeze_status = freeze.get("freeze_status", _NOT_COMPUTABLE) if freeze else _NOT_COMPUTABLE
    return {
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
        "stabilization_authority": stabilization_auth,
        "freeze_status": freeze_status,
        "boundary_integrity": "locked",
    }


def _summarise_cache_safety(
    benchmark_data: dict[str, Any] | None,
) -> dict[str, Any]:
    if benchmark_data is None:
        return {
            "status": _NOT_COMPUTABLE,
            "detail": "Benchmark artifact absent; cannot compute cache safety.",
        }
    drift_report = benchmark_data.get("drift_report", {})
    advisory = drift_report.get("advisory", {})
    cache_contamination = advisory.get("cache_contamination_detected", False)
    baseline = benchmark_data.get("baseline_suite", {})
    cache_info = baseline.get("cache", {})
    return {
        "status": "SAFE" if not cache_contamination else "CONTAMINATION_DETECTED",
        "cache_contamination_detected": cache_contamination,
        "baseline_cache_hits": cache_info.get("total_hits", 0),
        "baseline_cache_misses": cache_info.get("total_misses", 0),
    }


def _summarise_replay_equivalence(
    benchmark_data: dict[str, Any] | None,
) -> dict[str, Any]:
    if benchmark_data is None:
        return {
            "status": _NOT_COMPUTABLE,
            "detail": "Benchmark artifact absent; cannot compute replay equivalence.",
        }
    baseline = benchmark_data.get("baseline_suite", {})
    optimized = benchmark_data.get("optimized_suite", {})
    drift_report = benchmark_data.get("drift_report", {})
    advisory = drift_report.get("advisory", {})
    replay_divergence = advisory.get("replay_divergence_detected", False)
    hash_drift = advisory.get("output_hash_drift", False)
    baseline_stable = baseline.get("output_hash_stable", False)
    optimized_stable = optimized.get("output_hash_stable", False)
    equivalent = not replay_divergence and not hash_drift and baseline_stable and optimized_stable
    return {
        "status": "EQUIVALENT" if equivalent else "DIVERGENCE_DETECTED",
        "replay_divergence_detected": replay_divergence,
        "output_hash_drift": hash_drift,
        "baseline_output_hash_stable": baseline_stable,
        "optimized_output_hash_stable": optimized_stable,
    }


def _compute_operator_next_actions(
    blockers: list[str],
    drift_detected: bool,
    replay_equivalent: bool,
    cache_safe: bool,
    freeze_status: str,
) -> list[str]:
    actions: list[str] = []
    if blockers:
        for b in sorted(blockers):
            actions.append(f"Resolve missing/blocked source artifact: {b}")
    if drift_detected:
        actions.append(
            "Review optimization drift detections before any runtime promotion."
        )
    if not replay_equivalent:
        actions.append(
            "Investigate replay divergence or output hash drift before any promotion."
        )
    if not cache_safe:
        actions.append(
            "Investigate cache contamination detected in benchmark suite."
        )
    if freeze_status == "FROZEN":
        actions.append(
            "Governance freeze is active — any future changes require a separate PR with tests and audit artifact."
        )
    if not actions:
        actions.append(
            "No blockers detected. Console packet is advisory-only; no automated action taken."
        )
    return actions


def _compute_final_posture(
    blockers: list[str],
    source_artifact_statuses: dict[str, str],
) -> str:
    if not blockers:
        return "PASS"
    all_missing = all(
        v in (_NOT_COMPUTABLE, _BLOCKED, "MISSING")
        for v in source_artifact_statuses.values()
    )
    if all_missing:
        return _BLOCKED
    return _NOT_COMPUTABLE


# ---------------------------------------------------------------------------
# Top-level packet builder
# ---------------------------------------------------------------------------


def build_operator_runtime_console_packet(
    *,
    packet_id: str,
    runtime_profile_path: str | Path,
    benchmark_path: str | Path,
    stabilization_path: str | Path,
    governance_freeze_path: str | Path,
) -> dict[str, Any]:
    """Build a deterministic operator runtime console packet.

    Projection-only.  Advisory-only.  Does not mutate runtime or authority state.
    """
    # --- load source artifacts ---
    profile_data = _load_json(runtime_profile_path)
    benchmark_data = _load_json(benchmark_path)
    stabilization_data = _load_json(stabilization_path)
    freeze_data = _load_json(governance_freeze_path)

    source_artifact_map: dict[str, dict[str, Any] | None] = {
        "runtime_performance_profile": profile_data,
        "runtime_benchmark": benchmark_data,
        "stabilization_release_readiness": stabilization_data,
        "governance_freeze_baseline": freeze_data,
    }
    path_map: dict[str, str | Path] = {
        "runtime_performance_profile": runtime_profile_path,
        "runtime_benchmark": benchmark_path,
        "stabilization_release_readiness": stabilization_path,
        "governance_freeze_baseline": governance_freeze_path,
    }

    # --- per-section summaries ---
    profile_summary = _summarise_runtime_profile(profile_data, runtime_profile_path)
    benchmark_summary = _summarise_benchmark(benchmark_data, benchmark_path)
    drift_summary = _summarise_drift(benchmark_data, benchmark_path)
    artifact_health = _summarise_artifact_health(source_artifact_map, path_map)
    authority_boundary = _summarise_authority_boundary(stabilization_data, freeze_data)
    cache_safety = _summarise_cache_safety(benchmark_data)
    replay_equivalence = _summarise_replay_equivalence(benchmark_data)

    # --- derived values for actions and posture ---
    blockers: list[str] = artifact_health["blockers"]
    drift_detected: bool = drift_summary.get("drift_detected", False) if benchmark_data else True
    replay_equivalent = replay_equivalence["status"] == "EQUIVALENT"
    cache_safe = cache_safety["status"] == "SAFE"
    freeze_status = (freeze_data or {}).get("freeze_status", _NOT_COMPUTABLE)

    operator_next_actions = _compute_operator_next_actions(
        blockers=blockers,
        drift_detected=drift_detected,
        replay_equivalent=replay_equivalent,
        cache_safe=cache_safe,
        freeze_status=str(freeze_status),
    )

    final_posture = _compute_final_posture(
        blockers=blockers,
        source_artifact_statuses=artifact_health["artifact_statuses"],
    )

    source_artifacts = {
        "governance_freeze_baseline": str(governance_freeze_path),
        "runtime_benchmark": str(benchmark_path),
        "runtime_performance_profile": str(runtime_profile_path),
        "stabilization_release_readiness": str(stabilization_path),
    }

    correlation_id = stable_correlation_id(
        f"operator_runtime_console.{packet_id}",
        context={"packet_id": packet_id},
    )

    packet: dict[str, Any] = {
        "advisory_only": True,
        "artifact_health_summary": artifact_health,
        "authority_boundary_summary": authority_boundary,
        "authority_granted": False,
        "benchmark_summary": benchmark_summary,
        "cache_safety_summary": cache_safety,
        "correlation_id": correlation_id,
        "final_posture": final_posture,
        "mutation_allowed": False,
        "operator_next_actions": operator_next_actions,
        "optimization_drift_summary": drift_summary,
        "packet_id": packet_id,
        "patch_id": PATCH_ID,
        "projection_only": True,
        "promotion_allowed": False,
        "remaining_blockers": sorted(blockers),
        "replay_equivalence_summary": replay_equivalence,
        "runtime_profile_summary": profile_summary,
        "schema": "OperatorRuntimeConsolePacket.v1",
        "source_artifacts": source_artifacts,
    }

    packet_hash = canonical_hash(
        {
            "packet_id": packet_id,
            "patch_id": PATCH_ID,
            "final_posture": final_posture,
            "remaining_blockers": sorted(blockers),
        }
    )
    packet["packet_hash"] = packet_hash

    return packet


def write_operator_runtime_console_packet(
    path: str | Path,
    packet: dict[str, Any],
) -> Path:
    """Write operator runtime console packet to *path* as canonical JSON."""
    target = Path(path)
    write_canonical_json(target, packet)
    return target


def build_markdown_summary(packet: dict[str, Any]) -> str:
    """Build a concise, operator-readable Markdown summary of the console packet."""
    lines: list[str] = []
    lines.append(f"# Operator Runtime Console — {packet.get('packet_id', 'UNKNOWN')}")
    lines.append("")
    lines.append(f"**Patch:** `{packet.get('patch_id', '')}`")
    lines.append(f"**Final Posture:** `{packet.get('final_posture', '')}`")
    lines.append(
        f"**Flags:** `projection_only={packet.get('projection_only')}` "
        f"`advisory_only={packet.get('advisory_only')}` "
        f"`authority_granted={packet.get('authority_granted')}` "
        f"`mutation_allowed={packet.get('mutation_allowed')}` "
        f"`promotion_allowed={packet.get('promotion_allowed')}`"
    )
    lines.append("")

    # Artifact health
    health = packet.get("artifact_health_summary", {})
    lines.append("## Artifact Health")
    for art, status in sorted((health.get("artifact_statuses") or {}).items()):
        lines.append(f"- `{art}`: {status}")
    blockers = packet.get("remaining_blockers", [])
    if blockers:
        lines.append("")
        lines.append(f"**Remaining Blockers:** {', '.join(f'`{b}`' for b in blockers)}")
    lines.append("")

    # Benchmark summary
    bench = packet.get("benchmark_summary", {})
    lines.append("## Benchmark Summary")
    lines.append(f"- Status: `{bench.get('status', 'N/A')}`")
    if bench.get("status") == "PRESENT":
        lines.append(f"- Baseline runs: {bench.get('baseline_run_count', 0)}")
        lines.append(f"- Baseline mean: {bench.get('baseline_mean_ns', 0)} ns")
        lines.append(f"- Output hash stable: {bench.get('output_hash_stable', False)}")
        lines.append(f"- Drift detected: {bench.get('drift_detected', False)}")
    lines.append("")

    # Drift summary
    drift = packet.get("optimization_drift_summary", {})
    lines.append("## Optimization Drift Summary")
    lines.append(f"- Status: `{drift.get('status', 'N/A')}`")
    if drift.get("status") == "PRESENT":
        detections = drift.get("detections", [])
        lines.append(f"- Drift detected: {drift.get('drift_detected', False)}")
        if detections:
            lines.append(f"- Detections: {', '.join(f'`{d}`' for d in detections)}")
    lines.append("")

    # Cache safety
    cache = packet.get("cache_safety_summary", {})
    lines.append("## Cache Safety")
    lines.append(f"- Status: `{cache.get('status', 'N/A')}`")
    lines.append("")

    # Replay equivalence
    replay = packet.get("replay_equivalence_summary", {})
    lines.append("## Replay Equivalence")
    lines.append(f"- Status: `{replay.get('status', 'N/A')}`")
    lines.append("")

    # Operator next actions
    lines.append("## Operator Next Actions")
    for action in packet.get("operator_next_actions", []):
        lines.append(f"1. {action}")
    lines.append("")

    return "\n".join(lines)
