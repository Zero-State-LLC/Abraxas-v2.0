"""Operator-facing runtime console packet builder for ABRAXAS v2.0.

PATCH-P11-OPERATOR-RUNTIME-CONSOLE-001

Projection and operator summary only.  Does NOT mutate runtime, authority,
replay, forecast, canon, cache behaviour, or optimization behaviour.

Hard posture:
  authority_granted  = False
  mutation_allowed   = False
  promotion_allowed  = False
  projection_only    = True
  advisory_only      = True
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths
from core.diagnostics import stable_correlation_id
from core.operator_action_queue import summarize_operator_action_queue

from core.status_result import (
    STATUS_BLOCKED as BLOCKED,
    STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE,
)

PATCH_ID = "PATCH-P11-OPERATOR-RUNTIME-CONSOLE-001"

# ---------------------------------------------------------------------------
# Sentinel values
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Source artifact descriptors
# ---------------------------------------------------------------------------

_SOURCE_ARTIFACTS: list[str] = [
    "out/audit/runtime_performance_profile_001.latest.json",
    "out/audit/runtime_benchmark_001.latest.json",
    "out/audit/stabilization_release_readiness_001.latest.json",
    "out/audit/governance_freeze_baseline_001.latest.json",
    "out/audit/incremental_replay_001.latest.json",
    "out/projections/aal_viz_runtime_projection_001.latest.json",
]


def _load_artifact(path: str | Path) -> dict[str, Any] | None:
    """Load a JSON artifact from disk; return None if absent or unreadable."""
    try:
        text = Path(path).read_text(encoding="utf-8")
        return json.loads(text)  # type: ignore[no-any-return]
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


# ---------------------------------------------------------------------------
# Per-artifact summary extractors
# ---------------------------------------------------------------------------


def _summarize_runtime_profile(
    data: dict[str, Any] | None,
) -> dict[str, Any]:
    if data is None:
        return {
            "status": NOT_COMPUTABLE,
            "reason": "source artifact missing or unreadable",
        }
    return {
        "status": "PRESENT",
        "patch_id": data.get("patch_id", NOT_COMPUTABLE),
        "profile_enabled": data.get("profile_enabled", NOT_COMPUTABLE),
        "measured_surfaces": data.get("measured_surfaces", []),
        "final_status": data.get("final_status", NOT_COMPUTABLE),
        "authority_granted": data.get("authority_granted", False),
        "mutation_allowed": data.get("mutation_allowed", False),
    }


def _summarize_benchmark(
    data: dict[str, Any] | None,
) -> dict[str, Any]:
    if data is None:
        return {
            "status": NOT_COMPUTABLE,
            "reason": "source artifact missing or unreadable",
        }
    drift_report = data.get("drift_report", {})
    return {
        "status": "PRESENT",
        "patch_id": data.get("patch_id", NOT_COMPUTABLE),
        "artifact_id": data.get("artifact_id", NOT_COMPUTABLE),
        "drift_detected": drift_report.get("drift_detected", NOT_COMPUTABLE),
        "drift_detections": drift_report.get("detections", []),
        "authority_granted": data.get("authority_granted", False),
        "mutation_allowed": data.get("mutation_allowed", False),
    }


def _summarize_optimization_drift(
    data: dict[str, Any] | None,
) -> dict[str, Any]:
    if data is None:
        return {
            "status": NOT_COMPUTABLE,
            "reason": "source benchmark artifact missing or unreadable",
        }
    drift_report = data.get("drift_report", {})
    advisory = drift_report.get("advisory", {})
    performance_delta = drift_report.get("performance_delta", {})
    return {
        "status": "PRESENT",
        "drift_detected": drift_report.get("drift_detected", NOT_COMPUTABLE),
        "detections": drift_report.get("detections", []),
        "advisory": advisory,
        "performance_delta": performance_delta,
        "report_hash": drift_report.get("report_hash", NOT_COMPUTABLE),
        "optimization_auto_apply": False,
    }


def _summarize_stabilization(
    data: dict[str, Any] | None,
) -> dict[str, Any]:
    if data is None:
        return {
            "status": NOT_COMPUTABLE,
            "reason": "source artifact missing or unreadable",
        }
    final_posture = data.get("final_posture", {})
    return {
        "status": "PRESENT",
        "patch_id": data.get("stabilization_arc", {}).get("patch_id", NOT_COMPUTABLE),
        "release_readiness_status": data.get("release_readiness", {}).get(
            "status", NOT_COMPUTABLE
        ),
        "final_posture_status": final_posture.get("status", NOT_COMPUTABLE),
        "authority_granted": final_posture.get("authority_granted", False),
        "mutation_allowed": final_posture.get("mutation_allowed", False),
        "promotion_allowed": final_posture.get("promotion_allowed", False),
    }


def _summarize_governance_freeze(
    data: dict[str, Any] | None,
) -> dict[str, Any]:
    if data is None:
        return {
            "status": NOT_COMPUTABLE,
            "reason": "source artifact missing or unreadable",
        }
    return {
        "status": "PRESENT",
        "patch_id": data.get("patch_id", NOT_COMPUTABLE),
        "freeze_status": data.get("freeze_status", NOT_COMPUTABLE),
        "frozen_surfaces_count": len(data.get("frozen_surfaces", {})),
        "freeze_effective_head": data.get("freeze_effective_head", NOT_COMPUTABLE),
    }


def _summarize_replay_scaling(
    data: dict[str, Any] | None,
) -> dict[str, Any]:
    """Summarize incremental replay scaling health from the replay receipt."""
    if data is None:
        return {
            "status": NOT_COMPUTABLE,
            "reason": "incremental replay artifact missing or unreadable",
        }
    return {
        "status": "PRESENT",
        "patch_id": data.get("patch_id", NOT_COMPUTABLE),
        "replay_graph_hash": data.get("replay_graph_hash", NOT_COMPUTABLE),
        "invalidated_node_count": len(data.get("invalidated_nodes", [])),
        "skipped_surface_count": len(data.get("skipped_surfaces", [])),
        "replay_chunk_count": len(data.get("replay_chunks", [])),
        "replay_equivalence_verified": data.get("replay_equivalence_verified", NOT_COMPUTABLE),
        "fail_closed": data.get("fail_closed", NOT_COMPUTABLE),
        "final_status": data.get("final_status", NOT_COMPUTABLE),
        "authority_granted": data.get("authority_granted", False),
        "mutation_allowed": data.get("mutation_allowed", False),
    }


def _build_incremental_replay_health(
    replay_data: dict[str, Any] | None,
) -> dict[str, Any]:
    """Summarize incremental replay health posture."""
    if replay_data is None:
        return {
            "status": NOT_COMPUTABLE,
            "reason": "incremental replay artifact missing",
        }
    equivalence_verified = replay_data.get("replay_equivalence_verified", False)
    final_status = replay_data.get("final_status", NOT_COMPUTABLE)
    blockers = replay_data.get("remaining_blockers", [])
    health = "HEALTHY" if equivalence_verified and final_status == "PASS" else "DEGRADED"
    return {
        "status": "PRESENT",
        "health": health,
        "equivalence_verified": equivalence_verified,
        "final_status": final_status,
        "remaining_blockers": blockers,
    }


def _build_replay_invalidation_posture(
    replay_data: dict[str, Any] | None,
) -> dict[str, Any]:
    """Summarize replay invalidation posture."""
    if replay_data is None:
        return {
            "status": NOT_COMPUTABLE,
            "reason": "incremental replay artifact missing",
        }
    # A fail_closed invalidation is conservative but not a blocker in itself
    fail_closed = replay_data.get("fail_closed", False)
    invalidated_nodes = replay_data.get("invalidated_nodes", [])
    skipped_surfaces = replay_data.get("skipped_surfaces", [])
    return {
        "status": "PRESENT",
        "fail_closed": fail_closed,
        "invalidation_posture": "CONSERVATIVE" if fail_closed else "INCREMENTAL",
        "invalidated_node_count": len(invalidated_nodes),
        "skipped_surface_count": len(skipped_surfaces),
        "invalidated_nodes": sorted(invalidated_nodes),
        "skipped_surfaces": sorted(skipped_surfaces),
    }


# ---------------------------------------------------------------------------
# Aggregate summary builders
# ---------------------------------------------------------------------------


def _build_artifact_health_summary(
    artifacts: dict[str, dict[str, Any] | None],
) -> dict[str, Any]:
    present: list[str] = []
    missing: list[str] = []
    for path, data in artifacts.items():
        (present if data is not None else missing).append(path)
    return {
        "total_source_artifacts": len(artifacts),
        "present": sorted(present),
        "missing": sorted(missing),
        "all_present": len(missing) == 0,
    }


def _build_authority_boundary_summary() -> dict[str, Any]:
    """Static authority boundary — always fail-closed."""
    return {
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
        "projection_only": True,
        "advisory_only": True,
        "boundary_note": "All authority flags permanently locked for P11 console packet.",
    }


def _build_cache_safety_summary(
    benchmark_data: dict[str, Any] | None,
) -> dict[str, Any]:
    if benchmark_data is None:
        return {
            "status": NOT_COMPUTABLE,
            "reason": "benchmark artifact missing",
        }
    drift_report = benchmark_data.get("drift_report", {})
    advisory = drift_report.get("advisory", {})
    cache_contamination = advisory.get("cache_contamination_detected", False)
    return {
        "status": "PRESENT",
        "cache_contamination_detected": cache_contamination,
        "cache_safety_posture": "DEGRADED" if cache_contamination else "SAFE",
    }


def _build_replay_equivalence_summary(
    benchmark_data: dict[str, Any] | None,
) -> dict[str, Any]:
    if benchmark_data is None:
        return {
            "status": NOT_COMPUTABLE,
            "reason": "benchmark artifact missing",
        }
    drift_report = benchmark_data.get("drift_report", {})
    advisory = drift_report.get("advisory", {})
    replay_divergence = advisory.get("replay_divergence_detected", False)
    output_hash_drift = advisory.get("output_hash_drift", False)
    equivalence_held = not replay_divergence and not output_hash_drift
    return {
        "status": "PRESENT",
        "replay_divergence_detected": replay_divergence,
        "output_hash_drift": output_hash_drift,
        "equivalence_held": equivalence_held,
        "replay_semantic_changes": False,
    }


def _build_sealed_fusion_visibility_summary(
    aal_viz_runtime_projection_data: dict[str, Any] | None,
) -> dict[str, Any]:
    if aal_viz_runtime_projection_data is None:
        return {
            "status": NOT_COMPUTABLE,
            "seal_status": NOT_COMPUTABLE,
            "classification": NOT_COMPUTABLE,
            "fusion_final_status": NOT_COMPUTABLE,
            "remaining_blocker_count": 0,
            "drift_corridor_status": NOT_COMPUTABLE,
            "drift_evidence_count": 0,
            "lineage_corridor_status": NOT_COMPUTABLE,
            "lineage_evidence_count": 0,
            "seal_receipt_hash": NOT_COMPUTABLE,
            "source_artifact_hash": NOT_COMPUTABLE,
            "source_artifact_path": NOT_COMPUTABLE,
            "summary_blockers": ["missing_artifact:aal_viz_runtime_projection"],
            "advisory_only": True,
            "projection_only": True,
            "authority_granted": False,
            "forecast_authority": False,
            "mutation_allowed": False,
        }

    summary = aal_viz_runtime_projection_data.get("sealed_fusion_evidence_summary")
    if not isinstance(summary, dict):
        return {
            "status": NOT_COMPUTABLE,
            "seal_status": NOT_COMPUTABLE,
            "classification": NOT_COMPUTABLE,
            "fusion_final_status": NOT_COMPUTABLE,
            "remaining_blocker_count": 0,
            "drift_corridor_status": NOT_COMPUTABLE,
            "drift_evidence_count": 0,
            "lineage_corridor_status": NOT_COMPUTABLE,
            "lineage_evidence_count": 0,
            "seal_receipt_hash": NOT_COMPUTABLE,
            "source_artifact_hash": NOT_COMPUTABLE,
            "source_artifact_path": NOT_COMPUTABLE,
            "summary_blockers": ["missing_field:sealed_fusion_evidence_summary"],
            "advisory_only": True,
            "projection_only": True,
            "authority_granted": False,
            "forecast_authority": False,
            "mutation_allowed": False,
        }

    return {
        "status": str(summary.get("status", NOT_COMPUTABLE)),
        "seal_status": str(summary.get("seal_status", NOT_COMPUTABLE)),
        "classification": str(summary.get("classification", NOT_COMPUTABLE)),
        "fusion_final_status": str(summary.get("fusion_final_status", NOT_COMPUTABLE)),
        "remaining_blocker_count": int(summary.get("remaining_blocker_count", 0)),
        "drift_corridor_status": str(summary.get("drift_corridor_status", NOT_COMPUTABLE)),
        "drift_evidence_count": int(summary.get("drift_evidence_count", 0)),
        "lineage_corridor_status": str(summary.get("lineage_corridor_status", NOT_COMPUTABLE)),
        "lineage_evidence_count": int(summary.get("lineage_evidence_count", 0)),
        "seal_receipt_hash": str(summary.get("seal_receipt_hash", NOT_COMPUTABLE)),
        "source_artifact_hash": str(summary.get("source_artifact_hash", NOT_COMPUTABLE)),
        "source_artifact_path": str(summary.get("source_artifact_path", NOT_COMPUTABLE)),
        "summary_blockers": sorted(str(x) for x in summary.get("summary_blockers", [])),
        "advisory_only": True,
        "projection_only": True,
        "authority_granted": False,
        "forecast_authority": False,
        "mutation_allowed": False,
    }


def _derive_operator_next_actions(
    artifact_health: dict[str, Any],
    benchmark_summary: dict[str, Any],
    drift_summary: dict[str, Any],
    stabilization_summary: dict[str, Any],
) -> list[str]:
    actions: list[str] = []

    # Missing artifacts
    missing = artifact_health.get("missing", [])
    if missing:
        for path in missing:
            actions.append(f"BLOCKED: Generate missing source artifact — {path}")

    # Benchmark drift
    drift_detected = benchmark_summary.get("drift_detected")
    if drift_detected is True:
        detections = benchmark_summary.get("drift_detections", [])
        for d in detections:
            actions.append(f"ADVISORY: Investigate benchmark drift signal — {d}")

    # Stabilization
    stab_status = stabilization_summary.get("final_posture_status")
    if stab_status not in (NOT_COMPUTABLE, "STABILIZED_RELEASE_READINESS_RECORDED"):
        actions.append(
            f"ADVISORY: Review stabilization posture — final_posture_status={stab_status}"
        )

    # Cache safety
    cache_contamination = drift_summary.get("advisory", {}).get(
        "cache_contamination_detected"
    )
    if cache_contamination:
        actions.append("ADVISORY: Cache contamination detected — review cache isolation")

    if not actions:
        actions.append(
            "ADVISORY: No blocking issues found — console packet is projection-only"
        )

    return actions


def _derive_final_posture(
    artifact_health: dict[str, Any],
    benchmark_summary: dict[str, Any],
    replay_summary: dict[str, Any],
) -> dict[str, Any]:
    missing = artifact_health.get("missing", [])
    blockers: list[str] = []

    if missing:
        blockers.extend(f"missing_artifact:{p}" for p in missing)

    drift_detected = benchmark_summary.get("drift_detected")
    if drift_detected is True:
        for d in benchmark_summary.get("drift_detections", []):
            blockers.append(f"drift_signal:{d}")

    if not replay_summary.get("equivalence_held", True):
        blockers.append("replay_equivalence_not_held")

    if blockers:
        final_status = BLOCKED if missing else "ADVISORY_ONLY"
    else:
        final_status = "PASS"

    return {
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
        "projection_only": True,
        "advisory_only": True,
        "final_status": final_status,
        "remaining_blockers": sorted(blockers),
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_operator_console_packet(
    *,
    packet_id: str = "operator_runtime_console_001",
    source_artifact_paths: list[str] | None = None,
    operator_action_queue_artifact_path: str | Path | None = None,
) -> dict[str, Any]:
    """Build a deterministic operator runtime console packet.

    Projection and operator summary only.  Does not mutate any runtime state.

    If a source artifact is missing the corresponding summary fields are set to
    NOT_COMPUTABLE rather than fabricating values.
    """
    paths = source_artifact_paths if source_artifact_paths is not None else _SOURCE_ARTIFACTS

    # ---- load source artifacts ----
    profile_path = next(
        (p for p in paths if "runtime_performance_profile" in p), None
    )
    benchmark_path = next(
        (p for p in paths if "runtime_benchmark" in p), None
    )
    stabilization_path = next(
        (p for p in paths if "stabilization_release_readiness" in p), None
    )
    freeze_path = next(
        (p for p in paths if "governance_freeze_baseline" in p), None
    )
    incremental_replay_path = next(
        (p for p in paths if "incremental_replay" in p), None
    )
    aal_viz_runtime_projection_path = next(
        (p for p in paths if "aal_viz_runtime_projection" in p), None
    )

    profile_data = _load_artifact(profile_path) if profile_path else None
    benchmark_data = _load_artifact(benchmark_path) if benchmark_path else None
    stabilization_data = _load_artifact(stabilization_path) if stabilization_path else None
    freeze_data = _load_artifact(freeze_path) if freeze_path else None
    incremental_replay_data = (
        _load_artifact(incremental_replay_path) if incremental_replay_path else None
    )
    aal_viz_runtime_projection_data = (
        _load_artifact(aal_viz_runtime_projection_path)
        if aal_viz_runtime_projection_path
        else None
    )
    queue_path = (
        operator_action_queue_artifact_path
        if operator_action_queue_artifact_path is not None
        else RuntimePaths.from_env().operator_action_queue_latest
    )
    operator_action_queue_data = _load_artifact(queue_path)

    artifact_map: dict[str, dict[str, Any] | None] = {
        p: (
            profile_data
            if "runtime_performance_profile" in p
            else benchmark_data
            if "runtime_benchmark" in p
            else stabilization_data
            if "stabilization_release_readiness" in p
            else freeze_data
            if "governance_freeze_baseline" in p
            else incremental_replay_data
            if "incremental_replay" in p
            else aal_viz_runtime_projection_data
            if "aal_viz_runtime_projection" in p
            else None
        )
        for p in paths
    }

    # ---- build summaries ----
    runtime_profile_summary = _summarize_runtime_profile(profile_data)
    benchmark_summary = _summarize_benchmark(benchmark_data)
    optimization_drift_summary = _summarize_optimization_drift(benchmark_data)
    artifact_health_summary = _build_artifact_health_summary(artifact_map)
    authority_boundary_summary = _build_authority_boundary_summary()
    cache_safety_summary = _build_cache_safety_summary(benchmark_data)
    replay_equivalence_summary = _build_replay_equivalence_summary(benchmark_data)
    stabilization_summary = _summarize_stabilization(stabilization_data)
    governance_freeze_summary = _summarize_governance_freeze(freeze_data)
    replay_scaling_summary = _summarize_replay_scaling(incremental_replay_data)
    sealed_fusion_visibility_summary = _build_sealed_fusion_visibility_summary(
        aal_viz_runtime_projection_data
    )
    incremental_replay_health = _build_incremental_replay_health(incremental_replay_data)
    replay_invalidation_posture = _build_replay_invalidation_posture(incremental_replay_data)

    # ---- operator next actions ----
    operator_next_actions = _derive_operator_next_actions(
        artifact_health=artifact_health_summary,
        benchmark_summary=benchmark_summary,
        drift_summary=optimization_drift_summary,
        stabilization_summary=stabilization_summary,
    )
    operator_action_queue_summary = summarize_operator_action_queue(
        operator_action_queue_data
    )

    # ---- final posture ----
    final_posture = _derive_final_posture(
        artifact_health=artifact_health_summary,
        benchmark_summary=benchmark_summary,
        replay_summary=replay_equivalence_summary,
    )

    # ---- packet hash ----
    packet_hash = canonical_hash(
        {
            "packet_id": packet_id,
            "patch_id": PATCH_ID,
            "artifact_health_all_present": artifact_health_summary["all_present"],
            "final_status": final_posture["final_status"],
            "remaining_blockers": final_posture["remaining_blockers"],
        }
    )

    correlation_id = stable_correlation_id(
        f"operator_runtime_console.{packet_id}",
        context={"packet_id": packet_id},
    )

    return {
        "patch_id": PATCH_ID,
        "packet_id": packet_id,
        "correlation_id": correlation_id,
        "source_artifacts": sorted(paths),
        "runtime_profile_summary": runtime_profile_summary,
        "benchmark_summary": benchmark_summary,
        "optimization_drift_summary": optimization_drift_summary,
        "artifact_health_summary": artifact_health_summary,
        "authority_boundary_summary": authority_boundary_summary,
        "cache_safety_summary": cache_safety_summary,
        "replay_equivalence_summary": replay_equivalence_summary,
        "stabilization_summary": stabilization_summary,
        "governance_freeze_summary": governance_freeze_summary,
        "replay_scaling_summary": replay_scaling_summary,
        "sealed_fusion_visibility_summary": sealed_fusion_visibility_summary,
        "incremental_replay_health": incremental_replay_health,
        "replay_invalidation_posture": replay_invalidation_posture,
        "operator_next_actions": operator_next_actions,
        "operator_action_queue_status": operator_action_queue_summary[
            "operator_action_queue_status"
        ],
        "operator_action_item_count": operator_action_queue_summary[
            "operator_action_item_count"
        ],
        "pending_approval_count": operator_action_queue_summary[
            "pending_approval_count"
        ],
        "escalation_count": operator_action_queue_summary["escalation_count"],
        "top_action_categories": operator_action_queue_summary[
            "top_action_categories"
        ],
        "queue_advisory_flags": operator_action_queue_summary[
            "queue_advisory_flags"
        ],
        "temporal_state_diff_status": operator_action_queue_summary[
            "temporal_state_diff_status"
        ],
        "total_change_count": operator_action_queue_summary["total_change_count"],
        "topology_change_count": operator_action_queue_summary[
            "topology_change_count"
        ],
        "lineage_shift_count": operator_action_queue_summary["lineage_shift_count"],
        "drift_acceleration_status": operator_action_queue_summary[
            "drift_acceleration_status"
        ],
        "replay_equivalence_change_status": operator_action_queue_summary[
            "replay_equivalence_change_status"
        ],
        "queue_delta_count": operator_action_queue_summary["queue_delta_count"],
        "transport_delta_count": operator_action_queue_summary[
            "transport_delta_count"
        ],
        "diff_advisory_flags": operator_action_queue_summary["diff_advisory_flags"],
        "final_posture": final_posture,
        "packet_hash": packet_hash,
        # Hard posture — always present at top level for fast operator inspection
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
        "projection_only": True,
        "advisory_only": True,
        "final_status": final_posture["final_status"],
        "remaining_blockers": final_posture["remaining_blockers"],
    }


def write_console_packet(
    path: str | Path,
    packet: dict[str, Any],
) -> Path:
    """Write a console packet to *path* as canonical JSON."""
    target = Path(path)
    write_canonical_json(target, packet)
    return target


def build_console_markdown(packet: dict[str, Any]) -> str:
    """Build a concise operator-readable Markdown summary of the console packet."""
    lines: list[str] = []
    lines.append(f"# Operator Runtime Console — {packet.get('packet_id', '')}")
    lines.append("")
    lines.append(f"**Patch:** `{packet.get('patch_id', '')}`")
    lines.append(f"**Final Status:** `{packet.get('final_status', '')}`")
    lines.append(f"**Projection Only:** `{packet.get('projection_only', True)}`")
    lines.append(f"**Advisory Only:** `{packet.get('advisory_only', True)}`")
    lines.append("")

    # Authority boundary
    lines.append("## Authority Boundary")
    lines.append(
        "- authority_granted: `false`  mutation_allowed: `false`  "
        "promotion_allowed: `false`"
    )
    lines.append("")

    # Artifact health
    ah = packet.get("artifact_health_summary", {})
    lines.append("## Artifact Health")
    lines.append(f"- Total source artifacts: {ah.get('total_source_artifacts', '?')}")
    lines.append(f"- Present: {len(ah.get('present', []))}")
    missing = ah.get("missing", [])
    if missing:
        lines.append(f"- **Missing ({len(missing)}):**")
        for m in missing:
            lines.append(f"  - `{m}`")
    else:
        lines.append("- Missing: none")
    lines.append("")

    # Benchmark / drift
    bm = packet.get("benchmark_summary", {})
    lines.append("## Benchmark Summary")
    lines.append(f"- Status: `{bm.get('status', '?')}`")
    if bm.get("status") == "PRESENT":
        lines.append(f"- Drift detected: `{bm.get('drift_detected', '?')}`")
        detections = bm.get("drift_detections", [])
        if detections:
            lines.append(f"- Drift signals: {', '.join(f'`{d}`' for d in detections)}")
    lines.append("")

    # Cache / replay
    cs = packet.get("cache_safety_summary", {})
    rs = packet.get("replay_equivalence_summary", {})
    lines.append("## Cache & Replay")
    lines.append(f"- Cache safety: `{cs.get('cache_safety_posture', cs.get('status', '?'))}`")
    lines.append(f"- Replay equivalence held: `{rs.get('equivalence_held', rs.get('status', '?'))}`")
    lines.append("")

    # Replay scaling
    rss = packet.get("replay_scaling_summary", {})
    irh = packet.get("incremental_replay_health", {})
    rip = packet.get("replay_invalidation_posture", {})
    lines.append("## Replay Scaling")
    lines.append(f"- Status: `{rss.get('status', '?')}`")
    if rss.get("status") == "PRESENT":
        lines.append(f"- Invalidated nodes: `{rss.get('invalidated_node_count', '?')}`")
        lines.append(f"- Skipped surfaces: `{rss.get('skipped_surface_count', '?')}`")
        lines.append(f"- Replay chunks: `{rss.get('replay_chunk_count', '?')}`")
        lines.append(
            f"- Equivalence verified: `{rss.get('replay_equivalence_verified', '?')}`"
        )
    lines.append(f"- Incremental replay health: `{irh.get('health', irh.get('status', '?'))}`")
    lines.append(
        f"- Invalidation posture: `{rip.get('invalidation_posture', rip.get('status', '?'))}`"
    )
    lines.append("")

    lines.append("## Operator Action Queue")
    lines.append(
        f"- Status: `{packet.get('operator_action_queue_status', NOT_COMPUTABLE)}`"
    )
    lines.append(f"- Queue items: `{packet.get('operator_action_item_count', 0)}`")
    lines.append(f"- Pending approvals: `{packet.get('pending_approval_count', 0)}`")
    lines.append(f"- Escalations: `{packet.get('escalation_count', 0)}`")
    top_categories = packet.get("top_action_categories", [])
    if top_categories:
        lines.append(
            "- Top categories: "
            + ", ".join(f"`{category}`" for category in top_categories)
        )
    lines.append("")

    lines.append("## Temporal State Diff")
    lines.append(
        f"- Status: `{packet.get('temporal_state_diff_status', NOT_COMPUTABLE)}`"
    )
    lines.append(f"- Total changes: `{packet.get('total_change_count', 0)}`")
    lines.append(f"- Topology changes: `{packet.get('topology_change_count', 0)}`")
    lines.append(f"- Lineage shifts: `{packet.get('lineage_shift_count', 0)}`")
    lines.append(
        f"- Drift acceleration: `{packet.get('drift_acceleration_status', NOT_COMPUTABLE)}`"
    )
    lines.append(
        f"- Replay equivalence changes: `{packet.get('replay_equivalence_change_status', NOT_COMPUTABLE)}`"
    )
    lines.append(f"- Queue deltas: `{packet.get('queue_delta_count', 0)}`")
    lines.append(f"- Transport deltas: `{packet.get('transport_delta_count', 0)}`")
    lines.append("")

    # Operator next actions
    lines.append("## Operator Next Actions")
    for action in packet.get("operator_next_actions", []):
        lines.append(f"- {action}")
    lines.append("")

    # Remaining blockers
    blockers = packet.get("remaining_blockers", [])
    if blockers:
        lines.append("## Remaining Blockers")
        for b in blockers:
            lines.append(f"- `{b}`")
        lines.append("")

    return "\n".join(lines)
