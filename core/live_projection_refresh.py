"""Deterministic live projection refresh loop packet builders."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.aal_viz_runtime_projection import build_runtime_projection_packet
from core.canonical.json import canonical_hash, write_canonical_json

PATCH_ID = "PATCH-P14-LIVE-PROJECTION-REFRESH-LOOP-001"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
ADVISORY_ONLY = "ADVISORY_ONLY"
BLOCKED = "BLOCKED"

_HARD_INVARIANTS: dict[str, Any] = {
    "projection_only": True,
    "advisory_only": True,
    "analytics_only": True,
    "detection_only": True,
    "authority_granted": False,
    "mutation_allowed": False,
    "promotion_allowed": False,
    "inference_authority": False,
    "forecast_authority": False,
    "execution_authority": False,
    "command_channel": False,
    "bidirectional_control": False,
    "autonomous_adaptation": False,
}


def _apply_invariants(payload: dict[str, Any]) -> dict[str, Any]:
    return {**payload, **_HARD_INVARIANTS}


def _sorted_unique_strings(values: list[str] | None) -> list[str]:
    if not values:
        return []
    return sorted({str(value) for value in values if str(value)})


def _is_not_computable_packet(packet: dict[str, Any]) -> bool:
    return (
        packet.get("final_status") == NOT_COMPUTABLE
        or packet.get("status") == NOT_COMPUTABLE
        or packet.get("packet_hash") == NOT_COMPUTABLE
    )


def _merge_lineage(lineages: list[list[str]]) -> list[str]:
    merged: list[str] = []
    for lineage in lineages:
        for value in lineage:
            hash_value = str(value)
            if not merged or merged[-1] != hash_value:
                merged.append(hash_value)
    return merged


def _safe_ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 6)


def build_projection_refresh_snapshot(
    *,
    refresh_id: str,
    cycle_id: str,
    source_projection_hash: str,
    refreshed_packet: dict[str, Any],
    refresh_reason: str,
    refresh_timestamp: str,
    refresh_duration_ns: int,
    advisory_flags: list[str] | None = None,
) -> dict[str, Any]:
    """Build a ProjectionRefreshSnapshot.v1 packet."""
    refreshed_projection_hash = (
        NOT_COMPUTABLE
        if _is_not_computable_packet(refreshed_packet)
        else str(canonical_hash(refreshed_packet))
    )
    source_hash = str(source_projection_hash)
    projection_equivalence = (
        refreshed_projection_hash != NOT_COMPUTABLE
        and bool(source_hash)
        and source_hash == refreshed_projection_hash
    )
    continuity_status = (
        "INVALIDATED"
        if refreshed_projection_hash == NOT_COMPUTABLE
        else ("EQUIVALENT" if projection_equivalence else "DIVERGED")
    )
    snapshot_hash = (
        NOT_COMPUTABLE
        if refreshed_projection_hash == NOT_COMPUTABLE
        else str(
            canonical_hash(
                {
                    "patch_id": PATCH_ID,
                    "refresh_id": refresh_id,
                    "cycle_id": cycle_id,
                    "source_projection_hash": source_hash,
                    "refreshed_projection_hash": refreshed_projection_hash,
                    "refresh_reason": refresh_reason,
                    "refresh_timestamp": refresh_timestamp,
                    "refresh_duration_ns": int(refresh_duration_ns),
                }
            )
        )
    )
    flags = _sorted_unique_strings(advisory_flags)
    if refreshed_projection_hash == NOT_COMPUTABLE:
        flags = _sorted_unique_strings(flags + ["not_computable", "refresh_build_failed"])
    return _apply_invariants(
        {
            "schema": "ProjectionRefreshSnapshot.v1",
            "patch_id": PATCH_ID,
            "refresh_id": str(refresh_id),
            "cycle_id": str(cycle_id),
            "source_projection_hash": source_hash,
            "refreshed_projection_hash": refreshed_projection_hash,
            "refresh_reason": str(refresh_reason),
            "refresh_timestamp": str(refresh_timestamp),
            "projection_lineage": [source_hash, refreshed_projection_hash],
            "continuity_status": continuity_status,
            "projection_equivalence": projection_equivalence,
            "refresh_duration_ns": int(refresh_duration_ns),
            "advisory_flags": flags,
            "snapshot_hash": snapshot_hash,
        }
    )


def build_projection_refresh_cycle(
    *,
    cycle_id: str,
    cycle_index: int,
    snapshots: list[dict[str, Any]],
    advisory_flags: list[str] | None = None,
) -> dict[str, Any]:
    """Build a ProjectionRefreshCycle.v1 packet."""
    ordered_snapshots = list(snapshots)
    lineage = _merge_lineage(
        [
            [str(value) for value in snapshot.get("projection_lineage", [])]
            for snapshot in ordered_snapshots
        ]
    )
    drift_count = sum(
        1
        for snapshot in ordered_snapshots
        if snapshot.get("projection_equivalence") is False
    )
    not_computable_count = sum(
        1
        for snapshot in ordered_snapshots
        if str(snapshot.get("refreshed_projection_hash", "")) == NOT_COMPUTABLE
    )
    if not_computable_count > 0:
        continuity_posture = NOT_COMPUTABLE
    elif drift_count > 0:
        continuity_posture = "DRIFTED"
    else:
        continuity_posture = "STABLE"
    total_duration_ns = sum(
        int(snapshot.get("refresh_duration_ns", 0)) for snapshot in ordered_snapshots
    )
    flags = _sorted_unique_strings(advisory_flags)
    if not_computable_count > 0:
        flags = _sorted_unique_strings(flags + ["not_computable"])
    cycle_hash = str(
        canonical_hash(
            {
                "patch_id": PATCH_ID,
                "cycle_id": str(cycle_id),
                "cycle_index": int(cycle_index),
                "snapshot_hashes": [
                    str(snapshot.get("snapshot_hash", NOT_COMPUTABLE))
                    for snapshot in ordered_snapshots
                ],
                "continuity_posture": continuity_posture,
            }
        )
    )
    return _apply_invariants(
        {
            "schema": "ProjectionRefreshCycle.v1",
            "patch_id": PATCH_ID,
            "cycle_id": str(cycle_id),
            "cycle_index": int(cycle_index),
            "snapshot_count": len(ordered_snapshots),
            "snapshots": ordered_snapshots,
            "projection_lineage": lineage,
            "continuity_posture": continuity_posture,
            "drift_count": drift_count,
            "not_computable_count": not_computable_count,
            "total_duration_ns": total_duration_ns,
            "advisory_flags": flags,
            "cycle_hash": cycle_hash,
        }
    )


def build_projection_refresh_ledger(
    *,
    ledger_id: str,
    cycles: list[dict[str, Any]],
    refresh_cadence_status: str = "ADVISORY",
    advisory_flags: list[str] | None = None,
) -> dict[str, Any]:
    """Build a ProjectionRefreshLedger.v1 packet."""
    ordered_cycles = list(cycles)
    cycle_count = len(ordered_cycles)
    total_snapshots = sum(int(cycle.get("snapshot_count", 0)) for cycle in ordered_cycles)
    total_duration_ns = sum(
        int(cycle.get("total_duration_ns", 0)) for cycle in ordered_cycles
    )
    total_drift_events = sum(int(cycle.get("drift_count", 0)) for cycle in ordered_cycles)
    total_not_computable_cycles = sum(
        1
        for cycle in ordered_cycles
        if str(cycle.get("continuity_posture", "")) == NOT_COMPUTABLE
    )
    projection_lineage = _merge_lineage(
        [
            [str(value) for value in cycle.get("projection_lineage", [])]
            for cycle in ordered_cycles
        ]
    )
    if total_not_computable_cycles > 0 or any(
        value == NOT_COMPUTABLE for value in projection_lineage
    ):
        overall_continuity = NOT_COMPUTABLE
    elif total_drift_events > 0:
        overall_continuity = "DRIFTED"
    else:
        overall_continuity = "STABLE"
    drift_summary = {
        "total_drift_events": total_drift_events,
        "total_snapshots": total_snapshots,
        "drift_rate": _safe_ratio(total_drift_events, total_snapshots),
        "cycles_with_drift": sum(
            1 for cycle in ordered_cycles if int(cycle.get("drift_count", 0)) > 0
        ),
    }
    flags = _sorted_unique_strings(advisory_flags)
    if overall_continuity == NOT_COMPUTABLE:
        flags = _sorted_unique_strings(flags + ["not_computable"])
    ledger_hash = str(
        canonical_hash(
            {
                "patch_id": PATCH_ID,
                "ledger_id": str(ledger_id),
                "cycle_hashes": [
                    str(cycle.get("cycle_hash", NOT_COMPUTABLE)) for cycle in ordered_cycles
                ],
                "overall_continuity": overall_continuity,
                "drift_summary": drift_summary,
            }
        )
    )
    return _apply_invariants(
        {
            "schema": "ProjectionRefreshLedger.v1",
            "patch_id": PATCH_ID,
            "ledger_id": str(ledger_id),
            "cycle_count": cycle_count,
            "cycles": ordered_cycles,
            "total_snapshots": total_snapshots,
            "total_duration_ns": total_duration_ns,
            "projection_lineage": projection_lineage,
            "drift_summary": drift_summary,
            "overall_continuity": overall_continuity,
            "refresh_cadence_status": str(refresh_cadence_status),
            "advisory_flags": flags,
            "ledger_hash": ledger_hash,
        }
    )


def build_projection_continuity_receipt(
    *,
    receipt_id: str,
    ledger: dict[str, Any],
    source_packet_hash: str,
    final_packet_hash: str,
) -> dict[str, Any]:
    """Build a ProjectionContinuityReceipt.v1 packet."""
    projection_lineage = [str(value) for value in ledger.get("projection_lineage", [])]
    source_hash = str(source_packet_hash)
    final_hash = str(final_packet_hash)
    lineage_valid = bool(
        projection_lineage
        and projection_lineage[0] == source_hash
        and projection_lineage[-1] == final_hash
        and source_hash != NOT_COMPUTABLE
        and final_hash != NOT_COMPUTABLE
    )
    overall_continuity = str(ledger.get("overall_continuity", NOT_COMPUTABLE))
    continuity_verified = lineage_valid and overall_continuity in {"STABLE", "DRIFTED"}
    receipt_hash = str(
        canonical_hash(
            {
                "patch_id": PATCH_ID,
                "receipt_id": str(receipt_id),
                "source_packet_hash": source_hash,
                "final_packet_hash": final_hash,
                "lineage_valid": lineage_valid,
                "continuity_verified": continuity_verified,
                "overall_continuity": overall_continuity,
            }
        )
    )
    return _apply_invariants(
        {
            "schema": "ProjectionContinuityReceipt.v1",
            "patch_id": PATCH_ID,
            "receipt_id": str(receipt_id),
            "source_packet_hash": source_hash,
            "final_packet_hash": final_hash,
            "projection_lineage": projection_lineage,
            "lineage_valid": lineage_valid,
            "continuity_verified": continuity_verified,
            "overall_continuity": overall_continuity,
            "receipt_hash": receipt_hash,
        }
    )


class ProjectionRefreshScheduler:
    """Deterministic advisory scheduler for projection refresh cycles."""

    def __init__(
        self,
        *,
        max_cycles: int,
        source_artifact_paths: dict[str, str | Path] | None = None,
    ) -> None:
        self._max_cycles = max(1, int(max_cycles))
        self._source_artifact_paths = source_artifact_paths
        self._cycles: list[dict[str, Any]] = []

    def _build_projection_packet(self) -> dict[str, Any]:
        try:
            packet = build_runtime_projection_packet(
                source_artifact_paths=self._source_artifact_paths
            )
            if not isinstance(packet, dict):
                raise TypeError("runtime projection builder returned non-dict payload")
            return packet
        except Exception:
            return _apply_invariants(
                {
                    "schema": "RuntimeProjectionPacket.v1",
                    "status": NOT_COMPUTABLE,
                    "final_status": NOT_COMPUTABLE,
                    "remaining_blockers": ["refresh_build_failed"],
                    "packet_hash": NOT_COMPUTABLE,
                }
            )

    def plan_refresh(
        self,
        *,
        cycle_index: int,
        refresh_reasons: list[str] | None = None,
        timestamps: list[str] | None = None,
        durations_ns: list[int] | None = None,
        advisory_flags: list[str] | None = None,
    ) -> dict[str, Any]:
        reasons = refresh_reasons or ["manual_trigger"]
        cycle_timestamps = timestamps or [f"refresh_cycle_{cycle_index}_ts_0"]
        cycle_durations = durations_ns or [0]
        count = max(len(reasons), len(cycle_timestamps), len(cycle_durations))
        normalized_reasons = (reasons * count)[:count]
        normalized_timestamps = (cycle_timestamps * count)[:count]
        normalized_durations = (cycle_durations * count)[:count]
        cycle_id = str(
            canonical_hash(
                {
                    "patch_id": PATCH_ID,
                    "cycle_index": int(cycle_index),
                    "refresh_reasons": normalized_reasons,
                }
            )
        )
        source_packet = self._build_projection_packet()
        source_hash = (
            NOT_COMPUTABLE
            if _is_not_computable_packet(source_packet)
            else str(canonical_hash(source_packet))
        )
        snapshots: list[dict[str, Any]] = []
        for index, (reason, timestamp, duration_ns) in enumerate(
            zip(normalized_reasons, normalized_timestamps, normalized_durations)
        ):
            refresh_id = str(
                canonical_hash(
                    {
                        "patch_id": PATCH_ID,
                        "cycle_id": cycle_id,
                        "snapshot_index": index,
                        "refresh_reason": str(reason),
                        "refresh_timestamp": str(timestamp),
                    }
                )
            )
            refreshed_packet = self._build_projection_packet()
            snapshot = build_projection_refresh_snapshot(
                refresh_id=refresh_id,
                cycle_id=cycle_id,
                source_projection_hash=source_hash,
                refreshed_packet=refreshed_packet,
                refresh_reason=str(reason),
                refresh_timestamp=str(timestamp),
                refresh_duration_ns=int(duration_ns),
                advisory_flags=advisory_flags,
            )
            snapshots.append(snapshot)
        cycle = build_projection_refresh_cycle(
            cycle_id=cycle_id,
            cycle_index=int(cycle_index),
            snapshots=snapshots,
            advisory_flags=advisory_flags,
        )
        self._cycles.append(cycle)
        return cycle

    def run_refresh_loop(
        self,
        *,
        refresh_reasons: list[str] | None = None,
        timestamps: list[str] | None = None,
        durations_ns: list[int] | None = None,
        advisory_flags: list[str] | None = None,
    ) -> dict[str, Any]:
        self._cycles = []
        for cycle_index in range(self._max_cycles):
            self.plan_refresh(
                cycle_index=cycle_index,
                refresh_reasons=refresh_reasons,
                timestamps=timestamps,
                durations_ns=durations_ns,
                advisory_flags=advisory_flags,
            )
        return build_projection_refresh_ledger(
            ledger_id=str(
                canonical_hash(
                    {
                        "patch_id": PATCH_ID,
                        "max_cycles": self._max_cycles,
                        "cycle_hashes": [
                            str(cycle.get("cycle_hash", NOT_COMPUTABLE))
                            for cycle in self._cycles
                        ],
                    }
                )
            ),
            cycles=self._cycles,
            advisory_flags=advisory_flags,
        )


def verify_projection_continuity(ledger: dict[str, Any]) -> dict[str, Any]:
    """Build a deterministic ProjectionContinuityVerification.v1 report."""
    lineage = [str(value) for value in ledger.get("projection_lineage", [])]
    continuity_posture = str(ledger.get("overall_continuity", NOT_COMPUTABLE))
    blockers: list[str] = []
    if not lineage:
        blockers.append("continuity:empty_lineage")
    for index, hash_value in enumerate(lineage):
        if not hash_value or hash_value == NOT_COMPUTABLE:
            blockers.append(f"continuity:invalid_hash:{index}")
    if continuity_posture not in {"STABLE", "DRIFTED", NOT_COMPUTABLE}:
        blockers.append("continuity:missing_or_invalid_posture")
    continuity_verified = not blockers and continuity_posture in {"STABLE", "DRIFTED"}
    return _apply_invariants(
        {
            "schema": "ProjectionContinuityVerification.v1",
            "patch_id": PATCH_ID,
            "lineage_length": len(lineage),
            "continuity_posture": continuity_posture,
            "continuity_verified": continuity_verified,
            "continuity_blockers": sorted(set(blockers)),
            "drift_summary": ledger.get("drift_summary", {}),
        }
    )


def check_refresh_drift(cycles: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a deterministic ProjectionDriftReport.v1 packet from refresh cycles."""
    drift_events: list[dict[str, Any]] = []
    total_snapshots = 0
    for cycle in cycles:
        snapshots = list(cycle.get("snapshots", []))
        total_snapshots += len(snapshots)
        for snapshot in snapshots:
            if snapshot.get("projection_equivalence") is False:
                drift_events.append(
                    {
                        "cycle_id": str(cycle.get("cycle_id", "")),
                        "cycle_index": int(cycle.get("cycle_index", 0)),
                        "refresh_id": str(snapshot.get("refresh_id", "")),
                        "continuity_status": str(
                            snapshot.get("continuity_status", NOT_COMPUTABLE)
                        ),
                        "source_projection_hash": str(
                            snapshot.get("source_projection_hash", NOT_COMPUTABLE)
                        ),
                        "refreshed_projection_hash": str(
                            snapshot.get("refreshed_projection_hash", NOT_COMPUTABLE)
                        ),
                    }
                )
    ordered_events = sorted(
        drift_events,
        key=lambda event: (
            int(event["cycle_index"]),
            str(event["cycle_id"]),
            str(event["refresh_id"]),
            str(event["source_projection_hash"]),
            str(event["refreshed_projection_hash"]),
        ),
    )
    drift_event_count = len(ordered_events)
    return _apply_invariants(
        {
            "schema": "ProjectionDriftReport.v1",
            "patch_id": PATCH_ID,
            "drift_detected": drift_event_count > 0,
            "drift_event_count": drift_event_count,
            "drift_rate": _safe_ratio(drift_event_count, total_snapshots),
            "drift_events": ordered_events,
        }
    )


def validate_snapshot_lineage(snapshots: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a deterministic SnapshotLineageValidation.v1 report."""
    violations: list[str] = []
    for index, snapshot in enumerate(snapshots):
        prefix = f"snapshot[{index}]"
        if snapshot.get("schema") != "ProjectionRefreshSnapshot.v1":
            violations.append(f"{prefix}:wrong_schema")
        projection_lineage = snapshot.get("projection_lineage")
        if not isinstance(projection_lineage, list) or len(projection_lineage) != 2:
            violations.append(f"{prefix}:lineage_length_not_2")
        if not str(snapshot.get("refresh_id", "")):
            violations.append(f"{prefix}:missing_refresh_id")
        for key, expected in _HARD_INVARIANTS.items():
            if snapshot.get(key) is not expected:
                violations.append(f"{prefix}:invariant_violation:{key}")
    return _apply_invariants(
        {
            "schema": "SnapshotLineageValidation.v1",
            "patch_id": PATCH_ID,
            "snapshot_count": len(snapshots),
            "lineage_valid": len(violations) == 0,
            "violations": sorted(set(violations)),
        }
    )


def build_aal_viz_refresh_cadence_extension(
    ledger: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build a deterministic AALVizRefreshCadenceExtension.v1 summary."""
    if ledger is None:
        return _apply_invariants(
            {
                "schema": "AALVizRefreshCadenceExtension.v1",
                "patch_id": PATCH_ID,
                "status": NOT_COMPUTABLE,
                "refresh_cadence_status": NOT_COMPUTABLE,
                "snapshot_freshness": NOT_COMPUTABLE,
                "continuity_posture": NOT_COMPUTABLE,
                "projection_drift_posture": NOT_COMPUTABLE,
                "refresh_lineage_summary": NOT_COMPUTABLE,
                "advisory_flags": ["not_computable"],
                "remaining_blockers": ["no_refresh_ledger"],
            }
        )
    drift_summary = ledger.get("drift_summary", {})
    total_snapshots = int(ledger.get("total_snapshots", 0))
    total_drift_events = int(drift_summary.get("total_drift_events", 0))
    remaining_blockers = _sorted_unique_strings(
        [
            blocker
            for blocker in ledger.get("advisory_flags", [])
            if str(blocker).startswith("remaining_blocker:")
            or str(blocker).startswith("blocker:")
        ]
    )
    return _apply_invariants(
        {
            "schema": "AALVizRefreshCadenceExtension.v1",
            "patch_id": PATCH_ID,
            "status": "PRESENT",
            "refresh_cadence_status": str(
                ledger.get("refresh_cadence_status", NOT_COMPUTABLE)
            ),
            "snapshot_freshness": "FRESH" if total_snapshots > 0 else NOT_COMPUTABLE,
            "continuity_posture": str(ledger.get("overall_continuity", NOT_COMPUTABLE)),
            "projection_drift_posture": (
                "DRIFT_DETECTED" if total_drift_events > 0 else "NO_DRIFT"
            ),
            "refresh_lineage_summary": {
                "cycle_count": int(ledger.get("cycle_count", 0)),
                "total_snapshots": total_snapshots,
                "lineage_length": len(ledger.get("projection_lineage", [])),
                "ledger_hash": str(ledger.get("ledger_hash", NOT_COMPUTABLE)),
            },
            "advisory_flags": _sorted_unique_strings(
                ["projection_only", "advisory_only", "analytics_only", "detection_only"]
            ),
            "remaining_blockers": remaining_blockers,
        }
    )


def build_live_projection_refresh_packet(
    *,
    packet_id: str = "live_projection_refresh_001",
    max_cycles: int = 1,
    source_artifact_paths: dict[str, str | Path] | None = None,
    refresh_reasons: list[str] | None = None,
    timestamps: list[str] | None = None,
    durations_ns: list[int] | None = None,
    advisory_flags: list[str] | None = None,
) -> dict[str, Any]:
    """Build a deterministic LiveProjectionRefreshPacket.v1 packet."""
    scheduler = ProjectionRefreshScheduler(
        max_cycles=max_cycles,
        source_artifact_paths=source_artifact_paths,
    )
    ledger = scheduler.run_refresh_loop(
        refresh_reasons=refresh_reasons,
        timestamps=timestamps,
        durations_ns=durations_ns,
        advisory_flags=advisory_flags,
    )
    cycles = list(scheduler._cycles)
    snapshots = [snapshot for cycle in cycles for snapshot in cycle.get("snapshots", [])]

    continuity_verification = verify_projection_continuity(ledger)
    drift_report = check_refresh_drift(cycles)
    snapshot_lineage_validation = validate_snapshot_lineage(snapshots)

    lineage = [str(value) for value in ledger.get("projection_lineage", [])]
    source_hash = lineage[0] if lineage else NOT_COMPUTABLE
    final_hash = lineage[-1] if lineage else NOT_COMPUTABLE
    continuity_receipt = build_projection_continuity_receipt(
        receipt_id=str(
            canonical_hash(
                {
                    "patch_id": PATCH_ID,
                    "packet_id": packet_id,
                    "source_hash": source_hash,
                    "final_hash": final_hash,
                }
            )
        ),
        ledger=ledger,
        source_packet_hash=source_hash,
        final_packet_hash=final_hash,
    )

    aal_extension = build_aal_viz_refresh_cadence_extension(ledger)

    remaining_blockers = _sorted_unique_strings(
        list(continuity_verification.get("continuity_blockers", []))
        + list(snapshot_lineage_validation.get("violations", []))
        + list(aal_extension.get("remaining_blockers", []))
    )
    has_not_computable = (
        ledger.get("overall_continuity") == NOT_COMPUTABLE
        or continuity_verification.get("continuity_posture") == NOT_COMPUTABLE
        or source_hash == NOT_COMPUTABLE
        or final_hash == NOT_COMPUTABLE
        or any(str(value) == NOT_COMPUTABLE for value in lineage)
    )
    final_status = (
        NOT_COMPUTABLE
        if has_not_computable
        else (BLOCKED if remaining_blockers else ADVISORY_ONLY)
    )
    if has_not_computable:
        remaining_blockers = _sorted_unique_strings(
            remaining_blockers + ["not_computable:projection_refresh_continuity"]
        )

    packet_hash = str(
        canonical_hash(
            {
                "patch_id": PATCH_ID,
                "packet_id": str(packet_id),
                "ledger_hash": str(ledger.get("ledger_hash", NOT_COMPUTABLE)),
                "continuity_receipt_hash": str(
                    continuity_receipt.get("receipt_hash", NOT_COMPUTABLE)
                ),
                "continuity_verified": bool(
                    continuity_verification.get("continuity_verified", False)
                ),
                "drift_event_count": int(drift_report.get("drift_event_count", 0)),
                "snapshot_lineage_valid": bool(
                    snapshot_lineage_validation.get("lineage_valid", False)
                ),
                "final_status": final_status,
                "remaining_blockers": remaining_blockers,
            }
        )
    )

    return _apply_invariants(
        {
            "schema": "LiveProjectionRefreshPacket.v1",
            "patch_id": PATCH_ID,
            "packet_id": str(packet_id),
            "ledger": ledger,
            "continuity_receipt": continuity_receipt,
            "continuity_verification": continuity_verification,
            "drift_report": drift_report,
            "snapshot_lineage_validation": snapshot_lineage_validation,
            "aal_viz_refresh_cadence_extension": aal_extension,
            "status": final_status,
            "final_status": final_status,
            "remaining_blockers": remaining_blockers,
            "packet_hash": packet_hash,
        }
    )


def write_live_projection_refresh_packet(path: str | Path, packet: dict[str, Any]) -> Path:
    """Write live projection refresh packet as canonical JSON with trailing newline."""
    target = Path(path)
    write_canonical_json(target, packet)
    return target


def build_refresh_markdown(packet: dict[str, Any]) -> str:
    """Build deterministic markdown summary for a refresh packet."""
    cadence = packet.get("aal_viz_refresh_cadence_extension", {})
    drift = packet.get("drift_report", {})
    continuity = packet.get("continuity_verification", {})
    blockers = [str(value) for value in packet.get("remaining_blockers", [])]
    lines = [
        f"# Live Projection Refresh — {packet.get('packet_id', '')}",
        "",
        f"**Patch:** `{packet.get('patch_id', '')}`",
        f"**Final Status:** `{packet.get('final_status', NOT_COMPUTABLE)}`",
        f"**Packet Hash:** `{packet.get('packet_hash', NOT_COMPUTABLE)}`",
        "",
        "## Refresh Cadence",
        f"- refresh_cadence_status: `{cadence.get('refresh_cadence_status', NOT_COMPUTABLE)}`",
        f"- snapshot_freshness: `{cadence.get('snapshot_freshness', NOT_COMPUTABLE)}`",
        f"- continuity_posture: `{cadence.get('continuity_posture', NOT_COMPUTABLE)}`",
        f"- projection_drift_posture: `{cadence.get('projection_drift_posture', NOT_COMPUTABLE)}`",
        "",
        "## Drift",
        f"- drift_detected: `{drift.get('drift_detected', False)}`",
        f"- drift_event_count: `{drift.get('drift_event_count', 0)}`",
        f"- drift_rate: `{drift.get('drift_rate', 0.0)}`",
        "",
        "## Continuity",
        f"- continuity_verified: `{continuity.get('continuity_verified', False)}`",
        f"- continuity_posture: `{continuity.get('continuity_posture', NOT_COMPUTABLE)}`",
        "",
        "## Remaining Blockers",
    ]
    if blockers:
        lines.extend(f"- {blocker}" for blocker in blockers)
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)
