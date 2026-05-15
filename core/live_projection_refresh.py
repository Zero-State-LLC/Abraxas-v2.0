"""Deterministic live-projection refresh loop for ABRAXAS v2.0.

PATCH-P14-LIVE-PROJECTION-REFRESH-LOOP-001

Governed refresh loop for AAL-Viz runtime projection packets.  Continuously
regenerates projection snapshots without granting visualization authority or
mutating runtime, replay, canon, forecast, optimization, or governance behavior.

Hard invariants (always enforced):
    projection_only     = True
    advisory_only       = True
    authority_granted   = False
    mutation_allowed    = False
    promotion_allowed   = False
    inference_authority = False

Refresh loop is deterministic.  No wall-clock nondeterminism in tests.
Refresh scheduling is advisory-only.  Fail-closed on error.
No websocket/reactive push transport.  No async/distributed execution.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.aal_viz_runtime_projection import (
    build_runtime_projection_packet,
    write_runtime_projection_packet,
)
from core.canonical.json import canonical_hash

PATCH_ID = "PATCH-P14-LIVE-PROJECTION-REFRESH-LOOP-001"

NOT_COMPUTABLE = "NOT_COMPUTABLE"

# ---------------------------------------------------------------------------
# Hard authority boundary — never changes
# ---------------------------------------------------------------------------

_AUTHORITY_BOUNDARY: dict[str, Any] = {
    "projection_only": True,
    "advisory_only": True,
    "authority_granted": False,
    "mutation_allowed": False,
    "promotion_allowed": False,
    "inference_authority": False,
}


# ---------------------------------------------------------------------------
# ProjectionRefreshSnapshot.v1
# ---------------------------------------------------------------------------


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
    """Build a ProjectionRefreshSnapshot.v1 capturing one snapshot in a refresh cycle.

    Computes the refreshed_projection_hash from the new packet and derives
    projection_equivalence by comparing it to the source hash.  All authority
    flags remain locked False.
    """
    refreshed_projection_hash = canonical_hash(refreshed_packet)
    projection_equivalence = refreshed_projection_hash == source_projection_hash
    continuity_status = "EQUIVALENT" if projection_equivalence else "DIVERGED"

    final_posture = refreshed_packet.get("final_posture", {})
    flags: list[str] = sorted(advisory_flags or [])

    snapshot_hash = canonical_hash(
        {
            "patch_id": PATCH_ID,
            "refresh_id": refresh_id,
            "cycle_id": cycle_id,
            "source_projection_hash": source_projection_hash,
            "refreshed_projection_hash": refreshed_projection_hash,
        }
    )

    return {
        "schema": "ProjectionRefreshSnapshot.v1",
        "patch_id": PATCH_ID,
        "refresh_id": refresh_id,
        "cycle_id": cycle_id,
        "source_projection_hash": source_projection_hash,
        "refreshed_projection_hash": refreshed_projection_hash,
        "refresh_reason": refresh_reason,
        "refresh_timestamp": refresh_timestamp,
        "projection_lineage": [source_projection_hash, refreshed_projection_hash],
        "continuity_status": continuity_status,
        "projection_equivalence": projection_equivalence,
        "refresh_duration_ns": refresh_duration_ns,
        "advisory_flags": flags,
        "final_posture": final_posture,
        "snapshot_hash": snapshot_hash,
        **_AUTHORITY_BOUNDARY,
    }


# ---------------------------------------------------------------------------
# ProjectionRefreshCycle.v1
# ---------------------------------------------------------------------------


def build_projection_refresh_cycle(
    *,
    cycle_id: str,
    cycle_index: int,
    snapshots: list[dict[str, Any]],
    advisory_flags: list[str] | None = None,
) -> dict[str, Any]:
    """Build a ProjectionRefreshCycle.v1 summarizing one complete refresh cycle.

    A cycle contains one or more snapshots.  Continuity is STABLE when all
    snapshots are EQUIVALENT; DRIFTED when any diverges.
    """
    equivalences = [s.get("projection_equivalence", False) for s in snapshots]
    continuity_posture = "STABLE" if all(equivalences) else "DRIFTED"

    # Projection lineage: ordered chain of all hashes
    projection_lineage: list[str] = []
    for s in snapshots:
        for h in s.get("projection_lineage", []):
            if not projection_lineage or projection_lineage[-1] != h:
                projection_lineage.append(h)

    drift_count = sum(1 for e in equivalences if not e)
    total_duration_ns = sum(s.get("refresh_duration_ns", 0) for s in snapshots)
    flags: list[str] = sorted(advisory_flags or [])

    cycle_hash = canonical_hash(
        {
            "patch_id": PATCH_ID,
            "cycle_id": cycle_id,
            "cycle_index": cycle_index,
            "snapshot_count": len(snapshots),
            "continuity_posture": continuity_posture,
        }
    )

    return {
        "schema": "ProjectionRefreshCycle.v1",
        "patch_id": PATCH_ID,
        "cycle_id": cycle_id,
        "cycle_index": cycle_index,
        "snapshot_count": len(snapshots),
        "snapshots": snapshots,
        "projection_lineage": projection_lineage,
        "continuity_posture": continuity_posture,
        "drift_count": drift_count,
        "total_duration_ns": total_duration_ns,
        "advisory_flags": flags,
        "cycle_hash": cycle_hash,
        **_AUTHORITY_BOUNDARY,
    }


# ---------------------------------------------------------------------------
# ProjectionRefreshLedger.v1
# ---------------------------------------------------------------------------


def build_projection_refresh_ledger(
    *,
    ledger_id: str,
    cycles: list[dict[str, Any]],
    refresh_cadence_status: str = "ADVISORY",
    advisory_flags: list[str] | None = None,
) -> dict[str, Any]:
    """Build a ProjectionRefreshLedger.v1 summarizing all refresh cycles.

    The ledger records the complete projection lineage across all cycles and
    derives an overall drift summary.
    """
    all_drift_counts = [c.get("drift_count", 0) for c in cycles]
    total_drift = sum(all_drift_counts)
    total_snapshots = sum(c.get("snapshot_count", 0) for c in cycles)
    total_duration_ns = sum(c.get("total_duration_ns", 0) for c in cycles)

    # Collect stable projection lineage across all cycles
    full_lineage: list[str] = []
    for cycle in cycles:
        for h in cycle.get("projection_lineage", []):
            if not full_lineage or full_lineage[-1] != h:
                full_lineage.append(h)

    drift_summary: dict[str, Any] = {
        "total_drift_events": total_drift,
        "total_snapshots": total_snapshots,
        "drift_rate": (
            round(total_drift / total_snapshots, 6) if total_snapshots > 0 else 0.0
        ),
        "cycles_with_drift": sum(1 for c in cycles if c.get("drift_count", 0) > 0),
    }

    overall_continuity = "STABLE" if total_drift == 0 else "DRIFTED"
    flags: list[str] = sorted(advisory_flags or [])

    ledger_hash = canonical_hash(
        {
            "patch_id": PATCH_ID,
            "ledger_id": ledger_id,
            "cycle_count": len(cycles),
            "total_drift": total_drift,
            "overall_continuity": overall_continuity,
        }
    )

    return {
        "schema": "ProjectionRefreshLedger.v1",
        "patch_id": PATCH_ID,
        "ledger_id": ledger_id,
        "cycle_count": len(cycles),
        "total_snapshots": total_snapshots,
        "total_duration_ns": total_duration_ns,
        "projection_lineage": full_lineage,
        "drift_summary": drift_summary,
        "overall_continuity": overall_continuity,
        "refresh_cadence_status": refresh_cadence_status,
        "advisory_flags": flags,
        "ledger_hash": ledger_hash,
        **_AUTHORITY_BOUNDARY,
    }


# ---------------------------------------------------------------------------
# ProjectionContinuityReceipt.v1
# ---------------------------------------------------------------------------


def build_projection_continuity_receipt(
    *,
    receipt_id: str,
    ledger: dict[str, Any],
    source_packet_hash: str,
    final_packet_hash: str,
) -> dict[str, Any]:
    """Build a ProjectionContinuityReceipt.v1 sealing the refresh run.

    Records the full lineage from the first to the last projection hash and
    verifies that the lineage is internally consistent.
    """
    lineage = ledger.get("projection_lineage", [])
    overall_continuity = ledger.get("overall_continuity", NOT_COMPUTABLE)

    # Lineage validation: source must appear first, final must appear last
    lineage_valid = bool(
        lineage
        and lineage[0] == source_packet_hash
        and lineage[-1] == final_packet_hash
    )
    continuity_verified = lineage_valid and overall_continuity == "STABLE"

    receipt_hash = canonical_hash(
        {
            "patch_id": PATCH_ID,
            "receipt_id": receipt_id,
            "source_packet_hash": source_packet_hash,
            "final_packet_hash": final_packet_hash,
            "lineage_valid": lineage_valid,
            "overall_continuity": overall_continuity,
        }
    )

    return {
        "schema": "ProjectionContinuityReceipt.v1",
        "patch_id": PATCH_ID,
        "receipt_id": receipt_id,
        "source_packet_hash": source_packet_hash,
        "final_packet_hash": final_packet_hash,
        "projection_lineage": lineage,
        "lineage_valid": lineage_valid,
        "continuity_verified": continuity_verified,
        "overall_continuity": overall_continuity,
        "receipt_hash": receipt_hash,
        **_AUTHORITY_BOUNDARY,
    }


# ---------------------------------------------------------------------------
# Deterministic refresh scheduler
# ---------------------------------------------------------------------------


class ProjectionRefreshScheduler:
    """Governed, deterministic refresh scheduler for AAL-Viz projection packets.

    Scheduling is advisory-only.  The scheduler records refresh plan entries
    but does not mutate any runtime, replay, canon, or governance state.
    It fails closed: any exception during refresh invalidates that snapshot.

    No wall-clock nondeterminism: the caller supplies timestamps/durations
    so tests remain fully deterministic.
    """

    def __init__(
        self,
        *,
        max_cycles: int = 1,
        source_artifact_paths: dict[str, str | Path] | None = None,
    ) -> None:
        self._max_cycles = max(1, max_cycles)
        self._source_artifact_paths = source_artifact_paths
        self._cycles: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def plan_refresh(
        self,
        *,
        cycle_index: int,
        refresh_reasons: list[str] | None = None,
        timestamps: list[str] | None = None,
        durations_ns: list[int] | None = None,
        advisory_flags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Plan and execute a single advisory refresh cycle.

        Builds one or more refresh snapshots within the cycle.  Any failure
        during snapshot generation is caught; the snapshot is marked
        INVALIDATED and the cycle continues (fail-closed).

        Parameters
        ----------
        cycle_index:
            Zero-based cycle number.
        refresh_reasons:
            Advisory reason strings for each snapshot.  Defaults to a single
            ``["manual_trigger"]`` entry.
        timestamps:
            Deterministic timestamp strings for each snapshot.
        durations_ns:
            Deterministic refresh durations in nanoseconds for each snapshot.
        advisory_flags:
            Optional advisory flags to attach to the cycle.
        """
        reasons = refresh_reasons or ["manual_trigger"]
        tss = timestamps or [f"cycle_{cycle_index}_ts_0"]
        durs = durations_ns or [0]

        n = max(len(reasons), len(tss), len(durs))
        reasons = (reasons * n)[:n]
        tss = (tss * n)[:n]
        durs = (durs * n)[:n]

        cycle_id = canonical_hash(
            {"patch_id": PATCH_ID, "cycle_index": cycle_index, "reasons": reasons}
        )

        snapshots: list[dict[str, Any]] = []
        # Initial packet hash — build once before the snapshot loop
        initial_packet = self._safe_build_packet()
        source_hash = canonical_hash(initial_packet)

        for i, (reason, ts, dur) in enumerate(zip(reasons, tss, durs)):
            refresh_id = canonical_hash(
                {
                    "patch_id": PATCH_ID,
                    "cycle_id": cycle_id,
                    "snapshot_index": i,
                    "reason": reason,
                    "timestamp": ts,
                }
            )
            try:
                refreshed_packet = self._safe_build_packet()
                snapshot = build_projection_refresh_snapshot(
                    refresh_id=refresh_id,
                    cycle_id=cycle_id,
                    source_projection_hash=source_hash,
                    refreshed_packet=refreshed_packet,
                    refresh_reason=reason,
                    refresh_timestamp=ts,
                    refresh_duration_ns=dur,
                    advisory_flags=advisory_flags,
                )
            except Exception as exc:  # noqa: BLE001
                snapshot = self._invalidated_snapshot(
                    refresh_id=refresh_id,
                    cycle_id=cycle_id,
                    source_hash=source_hash,
                    reason=reason,
                    ts=ts,
                    dur=dur,
                    exc=exc,
                )

            snapshots.append(snapshot)

        cycle = build_projection_refresh_cycle(
            cycle_id=cycle_id,
            cycle_index=cycle_index,
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
        """Run the full advisory refresh loop for *max_cycles* cycles.

        Returns a ProjectionRefreshLedger.v1 covering all cycles.
        """
        self._cycles = []
        for i in range(self._max_cycles):
            self.plan_refresh(
                cycle_index=i,
                refresh_reasons=refresh_reasons,
                timestamps=timestamps,
                durations_ns=durations_ns,
                advisory_flags=advisory_flags,
            )

        return build_projection_refresh_ledger(
            ledger_id=canonical_hash(
                {
                    "patch_id": PATCH_ID,
                    "max_cycles": self._max_cycles,
                    "cycle_count": len(self._cycles),
                }
            ),
            cycles=self._cycles,
            advisory_flags=advisory_flags,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _safe_build_packet(self) -> dict[str, Any]:
        """Build a projection packet, returning a NOT_COMPUTABLE sentinel on failure."""
        try:
            return build_runtime_projection_packet(
                source_artifact_paths=self._source_artifact_paths
            )
        except Exception:  # noqa: BLE001
            return {
                "schema": "RuntimeProjectionPacket.v1",
                "patch_id": PATCH_ID,
                "status": NOT_COMPUTABLE,
                "reason": "packet build failed",
                **_AUTHORITY_BOUNDARY,
            }

    @staticmethod
    def _invalidated_snapshot(
        *,
        refresh_id: str,
        cycle_id: str,
        source_hash: str,
        reason: str,
        ts: str,
        dur: int,
        exc: Exception,
    ) -> dict[str, Any]:
        """Return a fail-closed INVALIDATED snapshot when refresh raises."""
        return {
            "schema": "ProjectionRefreshSnapshot.v1",
            "patch_id": PATCH_ID,
            "refresh_id": refresh_id,
            "cycle_id": cycle_id,
            "source_projection_hash": source_hash,
            "refreshed_projection_hash": NOT_COMPUTABLE,
            "refresh_reason": reason,
            "refresh_timestamp": ts,
            "projection_lineage": [source_hash, NOT_COMPUTABLE],
            "continuity_status": "INVALIDATED",
            "projection_equivalence": False,
            "refresh_duration_ns": dur,
            "advisory_flags": [f"error:{type(exc).__name__}"],
            "final_posture": {},
            "snapshot_hash": NOT_COMPUTABLE,
            **_AUTHORITY_BOUNDARY,
        }


# ---------------------------------------------------------------------------
# Projection continuity + drift checks
# ---------------------------------------------------------------------------


def verify_projection_continuity(
    ledger: dict[str, Any],
) -> dict[str, Any]:
    """Verify projection continuity across a complete refresh ledger.

    Checks:
    - Projection lineage is non-empty
    - All hashes in lineage are non-empty strings
    - No duplicate consecutive hashes (each refresh produced a distinct snapshot
      OR confirmed equivalence — both are valid; what is invalid is a missing hash)
    - Overall continuity posture is recorded

    Returns a verification report dict.
    """
    lineage: list[str] = ledger.get("projection_lineage", [])
    blockers: list[str] = []

    if not lineage:
        blockers.append("continuity:empty_lineage")

    for i, h in enumerate(lineage):
        if not h or h == NOT_COMPUTABLE:
            blockers.append(f"continuity:invalid_hash_at_index_{i}")

    overall_continuity = ledger.get("overall_continuity", NOT_COMPUTABLE)
    drift_summary = ledger.get("drift_summary", {})

    continuity_verified = not blockers and overall_continuity in ("STABLE", "DRIFTED")

    return {
        "schema": "ProjectionContinuityVerification.v1",
        "patch_id": PATCH_ID,
        "lineage_length": len(lineage),
        "continuity_verified": continuity_verified,
        "overall_continuity": overall_continuity,
        "drift_summary": drift_summary,
        "continuity_blockers": sorted(blockers),
        **_AUTHORITY_BOUNDARY,
    }


def check_refresh_drift(
    cycles: list[dict[str, Any]],
) -> dict[str, Any]:
    """Detect refresh drift across cycles.

    Drift is defined as any snapshot where ``projection_equivalence`` is False.
    Returns a drift report summarizing drift events per cycle.
    """
    drift_events: list[dict[str, Any]] = []

    for cycle in cycles:
        cycle_id = cycle.get("cycle_id", NOT_COMPUTABLE)
        cycle_index = cycle.get("cycle_index", -1)
        for snap in cycle.get("snapshots", []):
            if not snap.get("projection_equivalence", True):
                drift_events.append(
                    {
                        "cycle_id": cycle_id,
                        "cycle_index": cycle_index,
                        "refresh_id": snap.get("refresh_id", NOT_COMPUTABLE),
                        "continuity_status": snap.get("continuity_status", NOT_COMPUTABLE),
                        "source_hash": snap.get("source_projection_hash", NOT_COMPUTABLE),
                        "refreshed_hash": snap.get(
                            "refreshed_projection_hash", NOT_COMPUTABLE
                        ),
                    }
                )

    drift_detected = len(drift_events) > 0
    drift_rate = (
        round(
            len(drift_events)
            / sum(c.get("snapshot_count", 0) for c in cycles),
            6,
        )
        if any(c.get("snapshot_count", 0) > 0 for c in cycles)
        else 0.0
    )

    return {
        "schema": "ProjectionDriftReport.v1",
        "patch_id": PATCH_ID,
        "drift_detected": drift_detected,
        "drift_event_count": len(drift_events),
        "drift_rate": drift_rate,
        "drift_events": drift_events,
        **_AUTHORITY_BOUNDARY,
    }


# ---------------------------------------------------------------------------
# Snapshot lineage validation
# ---------------------------------------------------------------------------


def validate_snapshot_lineage(
    snapshots: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate that a sequence of refresh snapshots forms a stable lineage.

    Checks:
    - Each snapshot has schema ProjectionRefreshSnapshot.v1
    - projection_lineage is a 2-element list [source, refreshed]
    - refresh_id is non-empty
    - Hard invariants are all set correctly
    """
    violations: list[str] = []

    for i, snap in enumerate(snapshots):
        prefix = f"snapshot[{i}]"
        if snap.get("schema") != "ProjectionRefreshSnapshot.v1":
            violations.append(f"{prefix}:wrong_schema")
        lineage = snap.get("projection_lineage", [])
        if len(lineage) != 2:
            violations.append(f"{prefix}:lineage_length_not_2")
        if not snap.get("refresh_id"):
            violations.append(f"{prefix}:missing_refresh_id")
        # Hard invariants
        for flag, expected in [
            ("projection_only", True),
            ("advisory_only", True),
            ("authority_granted", False),
            ("mutation_allowed", False),
            ("promotion_allowed", False),
            ("inference_authority", False),
        ]:
            if snap.get(flag) != expected:
                violations.append(f"{prefix}:invariant_{flag}_violated")

    return {
        "schema": "SnapshotLineageValidation.v1",
        "patch_id": PATCH_ID,
        "snapshot_count": len(snapshots),
        "violations": sorted(violations),
        "lineage_valid": not violations,
        **_AUTHORITY_BOUNDARY,
    }


# ---------------------------------------------------------------------------
# Top-level refresh run builder
# ---------------------------------------------------------------------------


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
    """Build a complete LiveProjectionRefreshPacket.v1.

    Orchestrates the scheduler, ledger, continuity receipt, drift report,
    and snapshot lineage validation into a single top-level packet.

    Missing source artifacts produce NOT_COMPUTABLE; nothing is fabricated.
    """
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

    all_snapshots: list[dict[str, Any]] = []
    for cycle in scheduler._cycles:
        all_snapshots.extend(cycle.get("snapshots", []))

    # Drift report
    drift_report = check_refresh_drift(scheduler._cycles)

    # Continuity verification
    continuity_verification = verify_projection_continuity(ledger)

    # Snapshot lineage validation
    lineage_validation = validate_snapshot_lineage(all_snapshots)

    # Continuity receipt
    lineage = ledger.get("projection_lineage", [])
    source_hash = lineage[0] if lineage else NOT_COMPUTABLE
    final_hash = lineage[-1] if lineage else NOT_COMPUTABLE
    continuity_receipt = build_projection_continuity_receipt(
        receipt_id=canonical_hash(
            {
                "patch_id": PATCH_ID,
                "packet_id": packet_id,
                "source_hash": source_hash,
                "final_hash": final_hash,
            }
        ),
        ledger=ledger,
        source_packet_hash=source_hash,
        final_packet_hash=final_hash,
    )

    # Operator/AAL-Viz refresh cadence summary
    refresh_cadence_summary: dict[str, Any] = {
        "refresh_cadence_status": ledger.get("refresh_cadence_status", "ADVISORY"),
        "snapshot_freshness": "FRESH" if all_snapshots else NOT_COMPUTABLE,
        "continuity_posture": ledger.get("overall_continuity", NOT_COMPUTABLE),
        "projection_drift_posture": (
            "DRIFT_DETECTED" if drift_report.get("drift_detected") else "NO_DRIFT"
        ),
        "refresh_lineage_summary": {
            "cycle_count": ledger.get("cycle_count", 0),
            "total_snapshots": ledger.get("total_snapshots", 0),
            "lineage_length": len(lineage),
        },
    }

    # Final blockers
    remaining_blockers: list[str] = sorted(
        continuity_verification.get("continuity_blockers", [])
        + lineage_validation.get("violations", [])
    )
    final_status = "ADVISORY_ONLY" if not remaining_blockers else "BLOCKED"

    packet_hash = canonical_hash(
        {
            "patch_id": PATCH_ID,
            "packet_id": packet_id,
            "ledger_hash": ledger.get("ledger_hash", ""),
            "continuity_receipt_hash": continuity_receipt.get("receipt_hash", ""),
        }
    )

    return {
        "schema": "LiveProjectionRefreshPacket.v1",
        "patch_id": PATCH_ID,
        "packet_id": packet_id,
        "packet_hash": packet_hash,
        "refresh_cycles": scheduler._cycles,
        "ledger": ledger,
        "drift_report": drift_report,
        "continuity_verification": continuity_verification,
        "lineage_validation": lineage_validation,
        "continuity_receipt": continuity_receipt,
        "refresh_cadence_summary": refresh_cadence_summary,
        "projection_lineage": lineage,
        "continuity_status": ledger.get("overall_continuity", NOT_COMPUTABLE),
        "projection_equivalence": not drift_report.get("drift_detected", False),
        "refresh_drift_summary": drift_report,
        "refresh_cadence_status": refresh_cadence_summary["refresh_cadence_status"],
        "final_status": final_status,
        "remaining_blockers": remaining_blockers,
        **_AUTHORITY_BOUNDARY,
    }


def write_live_projection_refresh_packet(
    path: str | Path,
    packet: dict[str, Any],
) -> Path:
    """Write a live projection refresh packet to *path* as canonical JSON."""
    return write_runtime_projection_packet(path, packet)


def build_refresh_markdown(packet: dict[str, Any]) -> str:
    """Build a concise operator-readable Markdown summary of the refresh packet."""
    lines: list[str] = []
    lines.append(f"# Live Projection Refresh — {packet.get('packet_id', '')}")
    lines.append("")
    lines.append(f"**Patch:** `{packet.get('patch_id', '')}`")
    lines.append(f"**Final Status:** `{packet.get('final_status', '')}`")
    lines.append(f"**Projection Only:** `{packet.get('projection_only', True)}`")
    lines.append(f"**Advisory Only:** `{packet.get('advisory_only', True)}`")
    lines.append("")

    lines.append("## Authority Boundary")
    lines.append(
        "- authority_granted: `false`  mutation_allowed: `false`  "
        "promotion_allowed: `false`  inference_authority: `false`"
    )
    lines.append("")

    cadence = packet.get("refresh_cadence_summary", {})
    lines.append("## Refresh Cadence")
    lines.append(f"- Cadence status: `{cadence.get('refresh_cadence_status', '?')}`")
    lines.append(f"- Snapshot freshness: `{cadence.get('snapshot_freshness', '?')}`")
    lines.append(f"- Continuity posture: `{cadence.get('continuity_posture', '?')}`")
    lines.append(
        f"- Projection drift posture: `{cadence.get('projection_drift_posture', '?')}`"
    )
    summary = cadence.get("refresh_lineage_summary", {})
    lines.append(f"- Cycles: `{summary.get('cycle_count', 0)}`")
    lines.append(f"- Snapshots: `{summary.get('total_snapshots', 0)}`")
    lines.append(f"- Lineage length: `{summary.get('lineage_length', 0)}`")
    lines.append("")

    drift = packet.get("drift_report", {})
    lines.append("## Drift Report")
    lines.append(f"- Drift detected: `{drift.get('drift_detected', '?')}`")
    lines.append(f"- Drift events: `{drift.get('drift_event_count', 0)}`")
    lines.append(f"- Drift rate: `{drift.get('drift_rate', 0.0)}`")
    lines.append("")

    cv = packet.get("continuity_verification", {})
    lines.append("## Continuity Verification")
    lines.append(f"- Continuity verified: `{cv.get('continuity_verified', '?')}`")
    lines.append(f"- Overall continuity: `{cv.get('overall_continuity', '?')}`")
    lines.append("")

    receipt = packet.get("continuity_receipt", {})
    lines.append("## Continuity Receipt")
    lines.append(f"- Lineage valid: `{receipt.get('lineage_valid', '?')}`")
    lines.append(f"- Continuity verified: `{receipt.get('continuity_verified', '?')}`")
    lines.append("")

    blockers = packet.get("remaining_blockers", [])
    lines.append("## Remaining Blockers")
    if blockers:
        for b in blockers:
            lines.append(f"- `{b}`")
    else:
        lines.append("- None")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Refresh cadence integration for AAL-Viz runtime projection summaries
# ---------------------------------------------------------------------------


def build_aal_viz_refresh_cadence_extension(
    ledger: dict[str, Any] | None,
) -> dict[str, Any]:
    """Extend AAL-Viz runtime projection summaries with refresh cadence data.

    Returns a projection-only advisory summary of refresh cadence, freshness,
    continuity posture, drift posture, and lineage for the operator/AAL-Viz layer.
    This surface is advisory only; it does not mutate any projection state.
    """
    if ledger is None:
        return {
            "schema": "AALVizRefreshCadenceExtension.v1",
            "patch_id": PATCH_ID,
            "status": NOT_COMPUTABLE,
            "reason": "no refresh ledger available",
            **_AUTHORITY_BOUNDARY,
        }

    return {
        "schema": "AALVizRefreshCadenceExtension.v1",
        "patch_id": PATCH_ID,
        "status": "PRESENT",
        "refresh_cadence_status": ledger.get("refresh_cadence_status", NOT_COMPUTABLE),
        "snapshot_freshness": (
            "FRESH" if ledger.get("total_snapshots", 0) > 0 else NOT_COMPUTABLE
        ),
        "continuity_posture": ledger.get("overall_continuity", NOT_COMPUTABLE),
        "projection_drift_posture": (
            "DRIFT_DETECTED"
            if ledger.get("drift_summary", {}).get("total_drift_events", 0) > 0
            else "NO_DRIFT"
        ),
        "refresh_lineage_summaries": {
            "cycle_count": ledger.get("cycle_count", 0),
            "total_snapshots": ledger.get("total_snapshots", 0),
            "lineage_length": len(ledger.get("projection_lineage", [])),
            "ledger_hash": ledger.get("ledger_hash", NOT_COMPUTABLE),
        },
        **_AUTHORITY_BOUNDARY,
    }
