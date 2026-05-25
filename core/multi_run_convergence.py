"""Deterministic multi-run convergence and regime analytics for P14-P20 surfaces."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

PATCH_ID = "PATCH-P21-MULTI-RUN-CONVERGENCE-AND-REGIME-ANALYTICS-001"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
BLOCKED = "BLOCKED"

_ALLOWED_TREND_DIRECTIONS = {
    "STABLE",
    "DECREASING",
    "INCREASING",
    "ALTERNATING",
    "MIXED",
    NOT_COMPUTABLE,
    BLOCKED,
}

_INVARIANTS: dict[str, Any] = {
    "advisory_only": True,
    "analytics_only": True,
    "detection_only": True,
    "execution_authority": False,
    "authority_granted": False,
    "mutation_allowed": False,
    "promotion_allowed": False,
    "auto_execute": False,
    "auto_approve": False,
    "command_channel": False,
    "bidirectional_control": False,
    "inference_authority": False,
}

_FORBIDDEN_TRUE_FLAGS = {
    "execution_authority",
    "authority_granted",
    "mutation_allowed",
    "promotion_allowed",
    "auto_execute",
    "auto_approve",
    "command_channel",
    "bidirectional_control",
    "inference_authority",
}


def _apply_invariants(payload: dict[str, Any]) -> dict[str, Any]:
    return {**payload, **_INVARIANTS}


def _as_str(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        return value
    return default


def _as_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(float(value))
        except ValueError:
            return default
    return default


def _as_float(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return default
    return default


def _list_of_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item)]


def _scan_forbidden_true_flags(payload: Any, prefix: str = "") -> list[str]:
    matches: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            key_str = str(key)
            path = f"{prefix}.{key_str}" if prefix else key_str
            if key_str in _FORBIDDEN_TRUE_FLAGS and value is True:
                matches.append(path)
            matches.extend(_scan_forbidden_true_flags(value, path))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            path = f"{prefix}[{index}]" if prefix else f"[{index}]"
            matches.extend(_scan_forbidden_true_flags(value, path))
    return sorted(set(matches))


def _read_artifact(path: str | Path) -> tuple[dict[str, Any] | None, str]:
    target = Path(path)
    if not target.exists():
        return None, "MISSING"
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, "CORRUPT"
    except OSError:
        return None, "UNREADABLE"
    if isinstance(payload, dict):
        return payload, "PRESENT"
    return None, "CORRUPT"


def _safe_hash(payload: dict[str, Any] | None) -> str | None:
    if not isinstance(payload, dict):
        return None
    try:
        return str(canonical_hash(payload))
    except (TypeError, ValueError):
        return None


def _extract_packet_id(payload: dict[str, Any] | None) -> str:
    if not isinstance(payload, dict):
        return NOT_COMPUTABLE
    for key in ("packet_id", "queue_id", "projection_id", "artifact_id"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return NOT_COMPUTABLE


def _extract_run_id(
    payload: dict[str, Any] | None,
    *,
    packet_id: str,
    source_artifact: str,
    source_hash: str | None,
) -> str:
    if isinstance(payload, dict):
        run_id = payload.get("run_id")
        if isinstance(run_id, str) and run_id:
            return run_id
    if packet_id != NOT_COMPUTABLE:
        return packet_id
    hash_prefix = (source_hash or "NO_HASH")[:12]
    return f"{Path(source_artifact).name}:{hash_prefix}"


def _extract_timestamp_or_sequence(
    payload: dict[str, Any] | None, packet_id: str, source_artifact: str
) -> str:
    if isinstance(payload, dict):
        for key in (
            "timestamp_or_sequence",
            "projection_timestamp",
            "deterministic_timestamp",
            "cursor",
        ):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value
        bounds = payload.get("transport_cursor_bounds")
        if isinstance(bounds, dict):
            last = bounds.get("last")
            if isinstance(last, str) and last:
                return last
    return f"{Path(source_artifact).name}:{packet_id}"


def _extract_final_status(payload: dict[str, Any] | None) -> str:
    if not isinstance(payload, dict):
        return NOT_COMPUTABLE
    for key in (
        "final_status",
        "status",
        "operator_action_queue_status",
        "read_only_transport_status",
        "temporal_state_diff_status",
    ):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return "PRESENT"


def _extract_replay_status(payload: dict[str, Any] | None) -> str:
    if not isinstance(payload, dict):
        return NOT_COMPUTABLE
    direct = payload.get("replay_equivalence_change_status")
    if isinstance(direct, str) and direct:
        return direct
    replay = payload.get("replay_topology")
    if isinstance(replay, dict):
        status = replay.get("replay_equivalence_status")
        if isinstance(status, dict):
            verified = status.get("equivalence_verified")
            if verified is True:
                return "STABLE"
            if verified is False:
                return "SHIFT_DETECTED"
    return NOT_COMPUTABLE


def _extract_drift_event_count(payload: dict[str, Any] | None) -> int:
    if not isinstance(payload, dict):
        return 0
    if isinstance(payload.get("drift_timeline"), dict):
        return _as_int(payload["drift_timeline"].get("drift_event_count"), 0)
    return _as_int(payload.get("drift_event_count"), 0)


def _extract_drift_acceleration_status(payload: dict[str, Any] | None) -> str:
    if not isinstance(payload, dict):
        return NOT_COMPUTABLE
    value = payload.get("drift_acceleration_status")
    if isinstance(value, str) and value:
        return value
    drift = payload.get("drift_timeline")
    if isinstance(drift, dict):
        timeline_status = drift.get("drift_timeline_status")
        if isinstance(timeline_status, str) and timeline_status:
            return timeline_status
    return NOT_COMPUTABLE


def _extract_advisory_flags(payload: dict[str, Any] | None) -> list[str]:
    if not isinstance(payload, dict):
        return []
    flags: set[str] = set()
    for key in (
        "advisory_flags",
        "chronoscope_advisory_flags",
        "render_advisory_flags",
        "queue_advisory_flags",
        "transport_advisory_flags",
        "diff_advisory_flags",
        "convergence_advisory_flags",
    ):
        flags.update(_list_of_strings(payload.get(key)))
    return sorted(flags)


def _build_run_observation(source_artifact: str | Path) -> dict[str, Any]:
    source = str(source_artifact)
    payload, source_status = _read_artifact(source)
    source_hash = _safe_hash(payload)
    packet_id = _extract_packet_id(payload)
    final_status = _extract_final_status(payload)
    authority_violations = (
        _scan_forbidden_true_flags(payload) if isinstance(payload, dict) else []
    )
    authority_boundary_valid = not authority_violations

    remaining_blockers: list[str] = []
    if isinstance(payload, dict):
        remaining_blockers.extend(_list_of_strings(payload.get("remaining_blockers")))

    if source_status == "MISSING":
        final_status = NOT_COMPUTABLE
        remaining_blockers.append(f"missing_artifact:{source}")
    elif source_status == "CORRUPT":
        final_status = BLOCKED
        remaining_blockers.append(f"corrupt_artifact:{source}")
    elif source_status == "UNREADABLE":
        final_status = BLOCKED
        remaining_blockers.append(f"unreadable_artifact:{source}")

    if source_hash is None and source_status == "PRESENT":
        final_status = BLOCKED
        remaining_blockers.append(f"hash_not_computable:{source}")

    if authority_violations:
        final_status = BLOCKED
        remaining_blockers.extend(
            f"authority_boundary_violation:{path}" for path in authority_violations
        )

    if source_status == "MISSING":
        observation_status = NOT_COMPUTABLE
    elif final_status == BLOCKED:
        observation_status = BLOCKED
    else:
        observation_status = "PRESENT"

    blocked_count = len(remaining_blockers)
    not_computable_count = (
        1 if final_status == NOT_COMPUTABLE or source_status == "MISSING" else 0
    )

    advisory_flags = sorted(
        {
            *_extract_advisory_flags(payload),
            "multi_run_convergence",
            "advisory_only",
            "analytics_only",
            "detection_only",
            "fail_closed",
            *(["blocked"] if observation_status == BLOCKED else []),
            *(["not_computable"] if observation_status == NOT_COMPUTABLE else []),
            *(["authority_boundary_violation"] if authority_violations else []),
        }
    )

    run_id = _extract_run_id(
        payload,
        packet_id=packet_id,
        source_artifact=source,
        source_hash=source_hash,
    )

    return _apply_invariants(
        {
            "schema": "RunObservation.v1",
            "run_id": run_id,
            "source_artifact": source,
            "source_hash": source_hash,
            "timestamp_or_sequence": _extract_timestamp_or_sequence(
                payload, packet_id, source
            ),
            "packet_id": packet_id,
            "final_status": final_status,
            "topology_change_count": _as_int((payload or {}).get("topology_change_count"), 0),
            "lineage_shift_count": _as_int((payload or {}).get("lineage_shift_count"), 0),
            "drift_event_count": _extract_drift_event_count(payload),
            "drift_acceleration_status": _extract_drift_acceleration_status(payload),
            "replay_equivalence_change_status": _extract_replay_status(payload),
            "queue_delta_count": _as_int((payload or {}).get("queue_delta_count"), 0),
            "transport_delta_count": _as_int(
                (payload or {}).get("transport_delta_count"), 0
            ),
            "blocked_count": blocked_count,
            "not_computable_count": not_computable_count,
            "advisory_flags": advisory_flags,
            "authority_boundary_valid": authority_boundary_valid,
            "observation_status": observation_status,
            "remaining_blockers": sorted(set(remaining_blockers)),
        }
    )


def _is_alternating(values: list[int]) -> bool:
    if len(values) < 3:
        return False
    diffs = [values[idx + 1] - values[idx] for idx in range(len(values) - 1)]
    if any(diff == 0 for diff in diffs):
        return False
    return all(diffs[idx] * diffs[idx + 1] < 0 for idx in range(len(diffs) - 1))


def _is_increasing(values: list[int]) -> bool:
    if len(values) < 2:
        return False
    return all(values[idx] <= values[idx + 1] for idx in range(len(values) - 1)) and any(
        values[idx] < values[idx + 1] for idx in range(len(values) - 1)
    )


def _is_decreasing(values: list[int]) -> bool:
    if len(values) < 2:
        return False
    return all(values[idx] >= values[idx + 1] for idx in range(len(values) - 1)) and any(
        values[idx] > values[idx + 1] for idx in range(len(values) - 1)
    )


def _trend_direction(values: list[int | str], *, numeric: bool) -> str:
    if len(values) < 2:
        return NOT_COMPUTABLE
    if numeric:
        numeric_values = [int(value) for value in values]
        if len(set(numeric_values)) == 1:
            return "STABLE"
        if _is_increasing(numeric_values):
            return "INCREASING"
        if _is_decreasing(numeric_values):
            return "DECREASING"
        if _is_alternating(numeric_values):
            return "ALTERNATING"
        return "MIXED"

    string_values = [str(value) for value in values]
    if len(set(string_values)) == 1:
        return "STABLE"
    if len(string_values) >= 3 and len(set(string_values[:2])) == 2:
        first = string_values[0]
        second = string_values[1]
        if all(
            (
                string_values[idx] == first
                if idx % 2 == 0
                else string_values[idx] == second
            )
            for idx in range(len(string_values))
        ):
            return "ALTERNATING"
    return "MIXED"


def _build_metric_summary(
    *,
    metric_name: str,
    values: list[int | str],
    numeric: bool,
    blocked: bool,
) -> dict[str, Any]:
    evidence_count = len(values)
    if blocked:
        return _apply_invariants(
            {
                "schema": "ConvergenceMetricSummary.v1",
                "metric_name": metric_name,
                "evidence_count": evidence_count,
                "stable_count": 0,
                "changed_count": 0,
                "recurrence_count": 0,
                "persistence_ratio": 0.0,
                "volatility_score": 1.0,
                "trend_direction": BLOCKED,
            }
        )

    if evidence_count < 2:
        return _apply_invariants(
            {
                "schema": "ConvergenceMetricSummary.v1",
                "metric_name": metric_name,
                "evidence_count": evidence_count,
                "stable_count": 0,
                "changed_count": 0,
                "recurrence_count": 0,
                "persistence_ratio": 0.0,
                "volatility_score": 0.0,
                "trend_direction": NOT_COMPUTABLE,
            }
        )

    stable_count = sum(
        1 for idx in range(evidence_count - 1) if values[idx] == values[idx + 1]
    )
    changed_count = (evidence_count - 1) - stable_count
    recurrence_count = sum(count - 1 for count in Counter(values).values())
    persistence_ratio = round(stable_count / (evidence_count - 1), 6)
    volatility_score = round(changed_count / (evidence_count - 1), 6)
    trend_direction = _trend_direction(values, numeric=numeric)
    if trend_direction not in _ALLOWED_TREND_DIRECTIONS:
        trend_direction = "MIXED"

    return _apply_invariants(
        {
            "schema": "ConvergenceMetricSummary.v1",
            "metric_name": metric_name,
            "evidence_count": evidence_count,
            "stable_count": stable_count,
            "changed_count": changed_count,
            "recurrence_count": recurrence_count,
            "persistence_ratio": persistence_ratio,
            "volatility_score": volatility_score,
            "trend_direction": trend_direction,
        }
    )


def _summary_status(summary: dict[str, Any]) -> str:
    trend_direction = _as_str(summary.get("trend_direction"), NOT_COMPUTABLE)
    if trend_direction in {BLOCKED, NOT_COMPUTABLE}:
        return trend_direction
    if trend_direction == "STABLE":
        return "STABLE"
    if trend_direction == "DECREASING":
        return "CONVERGING"
    if trend_direction == "INCREASING":
        return "DIVERGING"
    return "VOLATILE"


def _build_regime_classification(
    valid_observations: list[dict[str, Any]],
    *,
    comparison_blocked: bool,
) -> tuple[dict[str, Any], list[str], list[str]]:
    rule_hits: list[str] = []
    remaining_blockers: list[str] = []

    comparable_change_counts = [
        _as_int(obs.get("topology_change_count"))
        + _as_int(obs.get("lineage_shift_count"))
        + _as_int(obs.get("drift_event_count"))
        + _as_int(obs.get("queue_delta_count"))
        + _as_int(obs.get("transport_delta_count"))
        for obs in valid_observations
    ]
    blocker_counts = [_as_int(obs.get("blocked_count")) for obs in valid_observations]
    not_computable_counts = [
        _as_int(obs.get("not_computable_count")) for obs in valid_observations
    ]
    replay_shift_counts = [
        0
        if _as_str(obs.get("replay_equivalence_change_status"))
        in {"NO_CHANGE", "PASS", "STABLE", "EQUIVALENT"}
        else 1
        for obs in valid_observations
    ]

    if comparison_blocked:
        regime = BLOCKED
        rule_hits.append("authority_or_corrupt_evidence_blocked")
    elif len(valid_observations) < 2:
        regime = NOT_COMPUTABLE
        rule_hits.append("insufficient_valid_run_observations")
        remaining_blockers.append("insufficient_run_observations")
    elif _is_increasing(blocker_counts) or _is_increasing(not_computable_counts):
        regime = "DEGRADED"
        rule_hits.append("blocker_or_not_computable_increasing")
    elif _is_alternating(comparable_change_counts):
        regime = "VOLATILE"
        rule_hits.append("alternating_change_direction")
    elif _is_increasing(comparable_change_counts) or _is_increasing(replay_shift_counts):
        regime = "DIVERGING"
        rule_hits.append("change_or_replay_shift_increasing")
    elif _is_decreasing(comparable_change_counts) and not _is_increasing(blocker_counts):
        regime = "CONVERGING"
        rule_hits.append("comparable_changes_decreasing")
    elif (
        sum(comparable_change_counts) <= len(comparable_change_counts)
        and not _is_increasing(blocker_counts)
        and not _is_increasing(not_computable_counts)
    ):
        regime = "STABLE"
        rule_hits.append("low_total_change_with_nonincreasing_blockers")
    else:
        regime = "VOLATILE"
        rule_hits.append("mixed_change_direction")

    return (
        _apply_invariants(
            {
                "schema": "RegimeClassification.v1",
                "regime_classification": regime,
                "evidence_count": len(valid_observations),
                "rule_hits": sorted(rule_hits),
                "comparison_blocked": comparison_blocked,
            }
        ),
        sorted(set(rule_hits)),
        sorted(set(remaining_blockers)),
    )


def _default_source_artifacts(paths: RuntimePaths) -> list[str]:
    ordered = [
        paths.temporal_state_diff_latest,
        paths.read_only_transport_latest,
        paths.operator_action_queue_latest,
        paths.aal_viz_graph_render_packet_latest,
        paths.projection_chronoscope_latest,
        paths.projection_bus_latest,
        paths.temporal_snapshot_spine_latest,
        paths.live_projection_refresh_latest,
        paths.aal_viz_runtime_projection_latest,
    ]
    return [path.as_posix() for path in ordered]


def build_multi_run_convergence_packet(
    *,
    packet_id: str = "multi_run_convergence_001",
    source_artifacts: Iterable[str | Path] | None = None,
) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    cross_run_topology_fusion_payload, _ = _read_artifact(
        paths.cross_run_topology_fusion_latest
    )
    ordered_sources = (
        [str(item) for item in source_artifacts]
        if source_artifacts is not None
        else _default_source_artifacts(paths)
    )

    observations = [_build_run_observation(source) for source in ordered_sources]
    observations = sorted(
        observations,
        key=lambda obs: (
            _as_str(obs.get("timestamp_or_sequence"), ""),
            _as_str(obs.get("run_id"), ""),
            _as_str(obs.get("source_hash"), ""),
        ),
    )

    comparison_blocked = any(
        (obs.get("authority_boundary_valid") is False)
        or any(
            blocker.startswith("corrupt_artifact:")
            or blocker.startswith("unreadable_artifact:")
            or blocker.startswith("hash_not_computable:")
            for blocker in _list_of_strings(obs.get("remaining_blockers"))
        )
        for obs in observations
    )

    valid_observations = [
        obs
        for obs in observations
        if _as_str(obs.get("observation_status")) == "PRESENT"
        and bool(obs.get("authority_boundary_valid", False))
    ]

    topology_metric = _build_metric_summary(
        metric_name="topology_change_count",
        values=[_as_int(obs.get("topology_change_count")) for obs in valid_observations],
        numeric=True,
        blocked=comparison_blocked,
    )
    drift_metric = _build_metric_summary(
        metric_name="drift_event_count",
        values=[_as_int(obs.get("drift_event_count")) for obs in valid_observations],
        numeric=True,
        blocked=comparison_blocked,
    )
    lineage_metric = _build_metric_summary(
        metric_name="lineage_shift_count",
        values=[_as_int(obs.get("lineage_shift_count")) for obs in valid_observations],
        numeric=True,
        blocked=comparison_blocked,
    )
    replay_metric = _build_metric_summary(
        metric_name="replay_equivalence_change_status",
        values=[
            _as_str(obs.get("replay_equivalence_change_status"), NOT_COMPUTABLE)
            for obs in valid_observations
        ],
        numeric=False,
        blocked=comparison_blocked,
    )
    transport_metric = _build_metric_summary(
        metric_name="transport_delta_count",
        values=[_as_int(obs.get("transport_delta_count")) for obs in valid_observations],
        numeric=True,
        blocked=comparison_blocked,
    )
    queue_metric = _build_metric_summary(
        metric_name="queue_delta_count",
        values=[_as_int(obs.get("queue_delta_count")) for obs in valid_observations],
        numeric=True,
        blocked=comparison_blocked,
    )
    blocker_metric = _build_metric_summary(
        metric_name="blocked_count",
        values=[_as_int(obs.get("blocked_count")) for obs in observations],
        numeric=True,
        blocked=comparison_blocked,
    )
    not_computable_metric = _build_metric_summary(
        metric_name="not_computable_count",
        values=[_as_int(obs.get("not_computable_count")) for obs in observations],
        numeric=True,
        blocked=comparison_blocked,
    )

    regime_classification, regime_rule_hits, regime_blockers = _build_regime_classification(
        valid_observations,
        comparison_blocked=comparison_blocked,
    )

    remaining_blockers = sorted(
        {
            blocker
            for obs in observations
            for blocker in _list_of_strings(obs.get("remaining_blockers"))
            if blocker
        }
        | set(regime_blockers)
    )

    if regime_classification["regime_classification"] == BLOCKED:
        convergence_status = BLOCKED
    elif regime_classification["regime_classification"] == NOT_COMPUTABLE:
        convergence_status = NOT_COMPUTABLE
    else:
        convergence_status = "ADVISORY_ONLY"

    topology_persistence_summary = _apply_invariants(
        {
            "schema": "TopologyPersistenceSummary.v1",
            "metric_summary": topology_metric,
            "topology_persistence_ratio": topology_metric["persistence_ratio"],
            "topology_trend_direction": topology_metric["trend_direction"],
        }
    )
    drift_persistence_summary = _apply_invariants(
        {
            "schema": "DriftPersistenceSummary.v1",
            "metric_summary": drift_metric,
            "drift_persistence_ratio": drift_metric["persistence_ratio"],
            "drift_trend_direction": drift_metric["trend_direction"],
        }
    )
    lineage_persistence_summary = _apply_invariants(
        {
            "schema": "LineagePersistenceSummary.v1",
            "metric_summary": lineage_metric,
            "lineage_persistence_ratio": lineage_metric["persistence_ratio"],
            "lineage_trend_direction": lineage_metric["trend_direction"],
        }
    )
    replay_stability_summary = _apply_invariants(
        {
            "schema": "ReplayStabilitySummary.v1",
            "metric_summary": replay_metric,
            "replay_stability_status": _summary_status(replay_metric),
        }
    )
    transport_stability_summary = _apply_invariants(
        {
            "schema": "TransportStabilitySummary.v1",
            "metric_summary": transport_metric,
            "transport_stability_status": _summary_status(transport_metric),
        }
    )
    queue_stability_summary = _apply_invariants(
        {
            "schema": "QueueStabilitySummary.v1",
            "metric_summary": queue_metric,
            "queue_stability_status": _summary_status(queue_metric),
        }
    )
    blocker_persistence_summary = _apply_invariants(
        {
            "schema": "BlockerPersistenceSummary.v1",
            "metric_summary": blocker_metric,
            "blocker_persistence_status": _summary_status(blocker_metric),
        }
    )

    advisory_flags = sorted(
        {
            "advisory_only",
            "analytics_only",
            "detection_only",
            "deterministic_ordering",
            "fail_closed",
            "evidence_backed",
            *(
                ["insufficient_run_observations"]
                if "insufficient_run_observations" in remaining_blockers
                else []
            ),
            *(
                ["authority_boundary_violation"]
                if any(
                    "authority_boundary_violation:" in blocker
                    for blocker in remaining_blockers
                )
                else []
            ),
        }
    )

    recommended_operator_next_actions: list[str]
    if "insufficient_run_observations" in remaining_blockers:
        recommended_operator_next_actions = [
            "Collect additional deterministic run artifacts before convergence comparison.",
            "Continue advisory-only monitoring without promotion or execution.",
        ]
    elif remaining_blockers:
        recommended_operator_next_actions = [
            "Review and resolve blocked or not-computable source evidence.",
            "Regenerate missing/corrupt artifacts and rerun convergence analytics.",
            "Continue advisory-only monitoring without runtime mutation.",
        ]
    else:
        recommended_operator_next_actions = [
            "Continue advisory-only convergence monitoring.",
            "Preserve non-authoritative posture and require operator review for actions.",
        ]

    packet_hash = canonical_hash(
        {
            "packet_id": packet_id,
            "run_observations": observations,
            "topology_persistence_summary": topology_persistence_summary,
            "drift_persistence_summary": drift_persistence_summary,
            "lineage_persistence_summary": lineage_persistence_summary,
            "replay_stability_summary": replay_stability_summary,
            "transport_stability_summary": transport_stability_summary,
            "queue_stability_summary": queue_stability_summary,
            "blocker_persistence_summary": blocker_persistence_summary,
            "not_computable_persistence_summary": not_computable_metric,
            "regime_classification": regime_classification,
            "convergence_status": convergence_status,
            "remaining_blockers": remaining_blockers,
        }
    )

    return _apply_invariants(
        {
            "schema": "MultiRunConvergencePacket.v1",
            "patch_id": PATCH_ID,
            "packet_id": packet_id,
            "packet_hash": packet_hash,
            "source_artifacts": ordered_sources,
            "run_observations": observations,
            "run_observation_count": len(observations),
            "valid_run_count": len(valid_observations),
            "convergence_status": convergence_status,
            "regime_classification": regime_classification["regime_classification"],
            "regime_classification_summary": regime_classification,
            "convergence_rule_hits": regime_rule_hits,
            "topology_persistence_summary": topology_persistence_summary,
            "drift_persistence_summary": drift_persistence_summary,
            "lineage_persistence_summary": lineage_persistence_summary,
            "replay_stability_summary": replay_stability_summary,
            "transport_stability_summary": transport_stability_summary,
            "queue_stability_summary": queue_stability_summary,
            "blocker_persistence_summary": blocker_persistence_summary,
            "not_computable_persistence_summary": not_computable_metric,
            "convergence_evidence_count": len(valid_observations),
            "multi_run_convergence_status": convergence_status,
            "topology_persistence_ratio": topology_persistence_summary[
                "topology_persistence_ratio"
            ],
            "drift_persistence_ratio": drift_persistence_summary["drift_persistence_ratio"],
            "lineage_persistence_ratio": lineage_persistence_summary[
                "lineage_persistence_ratio"
            ],
            "replay_stability_status": replay_stability_summary["replay_stability_status"],
            "transport_stability_status": transport_stability_summary[
                "transport_stability_status"
            ],
            "queue_stability_status": queue_stability_summary["queue_stability_status"],
            "blocker_persistence_status": blocker_persistence_summary[
                "blocker_persistence_status"
            ],
            "not_computable_persistence_status": _summary_status(not_computable_metric),
            "convergence_advisory_flags": advisory_flags,
            "cross_run_topology_fusion_status": _as_str(
                (
                    cross_run_topology_fusion_payload.get(
                        "cross_run_topology_fusion_status", NOT_COMPUTABLE
                    )
                    if isinstance(cross_run_topology_fusion_payload, dict)
                    else NOT_COMPUTABLE
                ),
                NOT_COMPUTABLE,
            ),
            "fusion_node_count": _as_int(
                (
                    cross_run_topology_fusion_payload.get("fusion_node_count", 0)
                    if isinstance(cross_run_topology_fusion_payload, dict)
                    else 0
                )
            ),
            "fusion_edge_count": _as_int(
                (
                    cross_run_topology_fusion_payload.get("fusion_edge_count", 0)
                    if isinstance(cross_run_topology_fusion_payload, dict)
                    else 0
                )
            ),
            "persistent_cluster_count": _as_int(
                (
                    cross_run_topology_fusion_payload.get(
                        "persistent_cluster_count", 0
                    )
                    if isinstance(cross_run_topology_fusion_payload, dict)
                    else 0
                )
            ),
            "lineage_corridor_count": _as_int(
                (
                    cross_run_topology_fusion_payload.get("lineage_corridor_count", 0)
                    if isinstance(cross_run_topology_fusion_payload, dict)
                    else 0
                )
            ),
            "replay_continuity_status": _as_str(
                (
                    cross_run_topology_fusion_payload.get(
                        "replay_continuity_status", NOT_COMPUTABLE
                    )
                    if isinstance(cross_run_topology_fusion_payload, dict)
                    else NOT_COMPUTABLE
                ),
                NOT_COMPUTABLE,
            ),
            "transport_continuity_status": _as_str(
                (
                    cross_run_topology_fusion_payload.get(
                        "transport_continuity_status", NOT_COMPUTABLE
                    )
                    if isinstance(cross_run_topology_fusion_payload, dict)
                    else NOT_COMPUTABLE
                ),
                NOT_COMPUTABLE,
            ),
            "topology_stability_score": _as_float(
                (
                    cross_run_topology_fusion_payload.get("topology_stability_score", 0.0)
                    if isinstance(cross_run_topology_fusion_payload, dict)
                    else 0.0
                ),
                0.0,
            ),
            "fusion_advisory_flags": _list_of_strings(
                (
                    cross_run_topology_fusion_payload.get("fusion_advisory_flags", [])
                    if isinstance(cross_run_topology_fusion_payload, dict)
                    else []
                )
            ),
            "final_status": convergence_status,
            "remaining_blockers": remaining_blockers,
            "recommended_operator_next_actions": recommended_operator_next_actions,
        }
    )


def write_multi_run_convergence_packet(path: str | Path, packet: dict[str, Any]) -> Path:
    target = Path(path)
    write_canonical_json(target, packet)
    return target


def build_multi_run_convergence_markdown(packet: dict[str, Any]) -> str:
    lines = [
        f"# Multi-Run Convergence — {packet.get('packet_id', '')}",
        "",
        f"**Patch:** `{packet.get('patch_id', '')}`",
        f"**Final Status:** `{packet.get('final_status', '')}`",
        f"**Run Observation Count:** `{packet.get('run_observation_count', 0)}`",
        f"**Valid Run Count:** `{packet.get('valid_run_count', 0)}`",
        f"**Regime Classification:** `{packet.get('regime_classification', NOT_COMPUTABLE)}`",
        f"**Convergence Status:** `{packet.get('multi_run_convergence_status', NOT_COMPUTABLE)}`",
        f"**Topology Persistence Ratio:** `{packet.get('topology_persistence_ratio', 0.0)}`",
        f"**Drift Persistence Ratio:** `{packet.get('drift_persistence_ratio', 0.0)}`",
        f"**Lineage Persistence Ratio:** `{packet.get('lineage_persistence_ratio', 0.0)}`",
        f"**Replay Stability:** `{packet.get('replay_stability_status', NOT_COMPUTABLE)}`",
        f"**Transport Stability:** `{packet.get('transport_stability_status', NOT_COMPUTABLE)}`",
        f"**Queue Stability:** `{packet.get('queue_stability_status', NOT_COMPUTABLE)}`",
        f"**Blocker Persistence:** `{packet.get('blocker_persistence_status', NOT_COMPUTABLE)}`",
        (
            f"**NOT_COMPUTABLE Persistence:** "
            f"`{packet.get('not_computable_persistence_status', NOT_COMPUTABLE)}`"
        ),
        "",
        "## Remaining Blockers",
    ]
    blockers = _list_of_strings(packet.get("remaining_blockers"))
    if blockers:
        lines.extend(f"- `{item}`" for item in blockers)
    else:
        lines.append("- None")

    lines.extend(["", "## Operator Next Actions"])
    actions = _list_of_strings(packet.get("recommended_operator_next_actions"))
    if actions:
        lines.extend(f"- {item}" for item in actions)
    else:
        lines.append("- Continue advisory-only monitoring.")

    lines.append("")
    return "\n".join(lines)
