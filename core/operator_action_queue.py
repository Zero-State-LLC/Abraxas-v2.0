"""Deterministic advisory-only operator action queue and review spine.

PATCH-P18-OPERATOR-ACTION-QUEUE-AND-REVIEW-SPINE-001

Transforms runtime/projection/replay/chronoscope/render observations into
review-only operator action items, approval checkpoints, escalation paths, and
lineage receipts. No execution authority is ever granted.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths
from core.temporal_persistence_memory import summarize_temporal_persistence_memory
from core.temporal_resonance_coherence import summarize_temporal_resonance_coherence
from core.temporal_stability_pressure import summarize_temporal_stability_pressure

from core.status_result import (
    STATUS_BLOCKED as BLOCKED,
    STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE,
)

PATCH_ID = "PATCH-P18-OPERATOR-ACTION-QUEUE-AND-REVIEW-SPINE-001"

_DRIFT_ESCALATION_THRESHOLD_PCT = 5.0
_SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
_ALLOWED_DECISIONS = ["approve", "reject", "defer", "request_more_evidence"]
_QUEUE_ADVISORY_FLAGS = sorted(
    [
        "advisory_only",
        "review_only",
        "no_execution_authority",
        "no_mutation_authority",
        "no_auto_execute",
        "no_auto_approve",
        "deterministic_ordering",
        "fail_closed",
    ]
)
_FORBIDDEN_TRUE_FLAGS = {
    "authority_granted",
    "execution_authority",
    "execution_unlocked",
    "mutation_allowed",
    "promotion_allowed",
    "auto_execute",
    "auto_approve",
    "inference_authority",
}


def _invariants() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "review_only": True,
        "execution_authority": False,
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
        "auto_execute": False,
        "auto_approve": False,
    }


def _load_artifact(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))  # type: ignore[no-any-return]
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _read_status(payload: dict[str, Any] | None) -> str:
    if payload is None:
        return NOT_COMPUTABLE
    for key in ("final_status", "status", "freeze_status"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return "PRESENT"


def _source_marker(payload: dict[str, Any]) -> str:
    for key in ("packet_hash", "projection_id", "artifact_id", "report_hash", "patch_id"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    ledger = payload.get("ledger")
    if isinstance(ledger, dict):
        ledger_hash = ledger.get("ledger_hash")
        if isinstance(ledger_hash, str) and ledger_hash:
            return ledger_hash
    return canonical_hash(
        {
            "schema": payload.get("schema"),
            "patch_id": payload.get("patch_id"),
            "status": _read_status(payload),
        }
    )


def _build_source_entries(
    paths: dict[str, str | Path],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any] | None]]:
    payloads: dict[str, dict[str, Any] | None] = {}
    entries: list[dict[str, Any]] = []
    for source_key, source_path in sorted(paths.items(), key=lambda item: item[0]):
        payload = _load_artifact(source_path)
        payloads[source_key] = payload
        if payload is None:
            entries.append(
                {
                    "schema": "OperatorActionQueueSourceEntry.v1",
                    "source_key": source_key,
                    "source_path": str(source_path),
                    "source_status": NOT_COMPUTABLE,
                    "source_reason": "source artifact missing or unreadable",
                    **_invariants(),
                }
            )
            continue
        entries.append(
            {
                "schema": "OperatorActionQueueSourceEntry.v1",
                "source_key": source_key,
                "source_path": str(source_path),
                "source_status": "PRESENT",
                "source_schema": payload.get("schema", NOT_COMPUTABLE),
                "source_marker": _source_marker(payload),
                "source_final_status": _read_status(payload),
                **_invariants(),
            }
        )
    return entries, payloads


def _stable_strings(values: list[Any]) -> list[str]:
    return sorted({str(value) for value in values if str(value)})


def _build_item(
    *,
    category: str,
    severity: str,
    source_key: str,
    source_artifact: str,
    title: str,
    advisory_text: str,
    recommended_operator_action: str,
    evidence: dict[str, Any],
    related_blockers: list[str] | None = None,
) -> dict[str, Any]:
    item_id = canonical_hash(
        {
            "category": category,
            "source_key": source_key,
            "source_artifact": source_artifact,
            "evidence": evidence,
        }
    )
    return {
        "schema": "OperatorActionItem.v1",
        "item_id": item_id,
        "category": category,
        "severity": severity,
        "source_key": source_key,
        "source_artifact": source_artifact,
        "title": title,
        "advisory_text": advisory_text,
        "recommended_operator_action": recommended_operator_action,
        "evidence": evidence,
        "related_blockers": sorted(related_blockers or []),
        "requires_human_decision": True,
        **_invariants(),
    }


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


def _derive_missing_artifact_items(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for entry in entries:
        if entry.get("source_status") != NOT_COMPUTABLE:
            continue
        source_path = str(entry.get("source_path", ""))
        items.append(
            _build_item(
                category="missing_artifact_review",
                severity="HIGH",
                source_key=str(entry.get("source_key", "")),
                source_artifact=source_path,
                title="Missing source artifact requires operator review",
                advisory_text=f"Source artifact is missing or unreadable: {source_path}",
                recommended_operator_action=(
                    f"Review missing artifact evidence and rerun upstream generation for {source_path}."
                ),
                evidence={
                    "source_status": NOT_COMPUTABLE,
                    "source_reason": entry.get("source_reason", ""),
                },
            )
        )
    return items


def _derive_blocked_projection_items(
    entries_by_key: dict[str, dict[str, Any]], payloads: dict[str, dict[str, Any] | None]
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for source_key in ("projection_bus", "runtime_projection", "projection_chronoscope"):
        payload = payloads.get(source_key)
        entry = entries_by_key.get(source_key)
        if payload is None or entry is None:
            continue
        status = _read_status(payload)
        blockers = _stable_strings(payload.get("remaining_blockers", []))
        if status != BLOCKED:
            continue
        items.append(
            _build_item(
                category="blocked_projection_review",
                severity="HIGH",
                source_key=source_key,
                source_artifact=str(entry.get("source_path", "")),
                title="Blocked projection surface requires operator review",
                advisory_text=(
                    f"{source_key} reported BLOCKED with blockers: {', '.join(blockers) or 'none recorded'}"
                ),
                recommended_operator_action=(
                    f"Review blocked projection evidence for {source_key} before relying on downstream advisory summaries."
                ),
                evidence={"status": status, "blocked_count": len(blockers)},
                related_blockers=blockers,
            )
        )
    return items


def _derive_drift_items(
    entries_by_key: dict[str, dict[str, Any]], payloads: dict[str, dict[str, Any] | None]
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    benchmark = payloads.get("runtime_benchmark")
    benchmark_entry = entries_by_key.get("runtime_benchmark")
    if isinstance(benchmark, dict) and benchmark_entry is not None:
        drift_report = benchmark.get("drift_report", {})
        if isinstance(drift_report, dict):
            detections = _stable_strings(drift_report.get("detections", []))
            if drift_report.get("drift_detected") is True or detections:
                items.append(
                    _build_item(
                        category="drift_review",
                        severity="MEDIUM",
                        source_key="runtime_benchmark",
                        source_artifact=str(benchmark_entry.get("source_path", "")),
                        title="Runtime drift signals require operator review",
                        advisory_text=(
                            "Benchmark drift signals observed: "
                            + (", ".join(detections) if detections else "drift_detected=true")
                        ),
                        recommended_operator_action=(
                            "Review benchmark drift evidence before trusting optimization or replay posture."
                        ),
                        evidence={
                            "drift_detected": drift_report.get("drift_detected", False),
                            "detections": detections,
                        },
                    )
                )
    chronoscope = payloads.get("projection_chronoscope")
    chronoscope_entry = entries_by_key.get("projection_chronoscope")
    if isinstance(chronoscope, dict) and chronoscope_entry is not None:
        drift_timeline = chronoscope.get("drift_timeline", {})
        if isinstance(drift_timeline, dict):
            drift_events = _stable_strings(drift_timeline.get("drift_events", []))
            if drift_events:
                items.append(
                    _build_item(
                        category="drift_review",
                        severity="MEDIUM",
                        source_key="projection_chronoscope",
                        source_artifact=str(chronoscope_entry.get("source_path", "")),
                        title="Chronoscope drift timeline requires operator review",
                        advisory_text=(
                            "Chronoscope drift events observed: " + ", ".join(drift_events)
                        ),
                        recommended_operator_action=(
                            "Review chronoscope drift events before treating timeline posture as stable."
                        ),
                        evidence={
                            "drift_event_count": len(drift_events),
                            "drift_events": drift_events,
                        },
                    )
                )
    return items


def _derive_lineage_items(
    entries_by_key: dict[str, dict[str, Any]], payloads: dict[str, dict[str, Any] | None]
) -> list[dict[str, Any]]:
    chronoscope = payloads.get("projection_chronoscope")
    entry = entries_by_key.get("projection_chronoscope")
    if not isinstance(chronoscope, dict) or entry is None:
        return []
    lineage = chronoscope.get("lineage_evolution", {})
    if not isinstance(lineage, dict):
        return []
    lineage_gap_count = int(lineage.get("lineage_gap_count", 0))
    corrupt_lineage_count = int(lineage.get("corrupt_lineage_count", 0))
    blockers = [
        blocker
        for blocker in _stable_strings(chronoscope.get("remaining_blockers", []))
        if blocker.startswith("corrupt_lineage:")
    ]
    if lineage_gap_count <= 0 and corrupt_lineage_count <= 0 and not blockers:
        return []
    severity = "HIGH" if corrupt_lineage_count > 0 else "MEDIUM"
    return [
        _build_item(
            category="lineage_gap_review",
            severity=severity,
            source_key="projection_chronoscope",
            source_artifact=str(entry.get("source_path", "")),
            title="Lineage continuity requires operator review",
            advisory_text=(
                "Chronoscope lineage reported gaps or corruption "
                f"(lineage_gap_count={lineage_gap_count}, corrupt_lineage_count={corrupt_lineage_count})."
            ),
            recommended_operator_action=(
                "Review lineage evidence before treating projection chronology as continuous."
            ),
            evidence={
                "lineage_gap_count": lineage_gap_count,
                "corrupt_lineage_count": corrupt_lineage_count,
            },
            related_blockers=blockers,
        )
    ]


def _derive_replay_equivalence_items(
    entries_by_key: dict[str, dict[str, Any]], payloads: dict[str, dict[str, Any] | None]
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    incremental = payloads.get("incremental_replay")
    inc_entry = entries_by_key.get("incremental_replay")
    if isinstance(incremental, dict) and inc_entry is not None:
        verified = incremental.get("replay_equivalence_verified")
        if verified is False:
            items.append(
                _build_item(
                    category="replay_equivalence_review",
                    severity="HIGH",
                    source_key="incremental_replay",
                    source_artifact=str(inc_entry.get("source_path", "")),
                    title="Replay equivalence failure requires operator review",
                    advisory_text="Incremental replay reported replay_equivalence_verified=false.",
                    recommended_operator_action=(
                        "Review replay equivalence evidence before relying on incremental replay outcomes."
                    ),
                    evidence={
                        "replay_equivalence_verified": False,
                        "final_status": incremental.get("final_status", NOT_COMPUTABLE),
                    },
                    related_blockers=_stable_strings(incremental.get("remaining_blockers", [])),
                )
            )
    runtime_projection = payloads.get("runtime_projection")
    projection_entry = entries_by_key.get("runtime_projection")
    if isinstance(runtime_projection, dict) and projection_entry is not None:
        replay_topology = runtime_projection.get("replay_topology", {})
        if isinstance(replay_topology, dict):
            equivalence = replay_topology.get("replay_equivalence_status", {})
            if isinstance(equivalence, dict) and equivalence.get("equivalence_verified") is False:
                items.append(
                    _build_item(
                        category="replay_equivalence_review",
                        severity="HIGH",
                        source_key="runtime_projection",
                        source_artifact=str(projection_entry.get("source_path", "")),
                        title="Projection replay equivalence review required",
                        advisory_text="Runtime projection surfaced replay equivalence failure.",
                        recommended_operator_action=(
                            "Review runtime projection replay equivalence evidence before trusting advisory projection state."
                        ),
                        evidence={
                            "equivalence_verified": False,
                            "final_status": equivalence.get("final_status", NOT_COMPUTABLE),
                        },
                        related_blockers=_stable_strings(runtime_projection.get("remaining_blockers", [])),
                    )
                )
    return items


def _derive_benchmark_regression_items(
    entries_by_key: dict[str, dict[str, Any]], payloads: dict[str, dict[str, Any] | None]
) -> list[dict[str, Any]]:
    benchmark = payloads.get("runtime_benchmark")
    entry = entries_by_key.get("runtime_benchmark")
    if not isinstance(benchmark, dict) or entry is None:
        return []
    drift_report = benchmark.get("drift_report", {})
    if not isinstance(drift_report, dict):
        return []
    performance_delta = drift_report.get("performance_delta", {})
    if not isinstance(performance_delta, dict):
        return []
    delta_ns = performance_delta.get("delta_ns")
    delta_pct = performance_delta.get("delta_pct")
    if not isinstance(delta_ns, int | float) or not isinstance(delta_pct, int | float):
        return []
    if float(delta_ns) <= 0 and float(delta_pct) <= 0:
        return []
    severity = "HIGH" if float(delta_pct) >= _DRIFT_ESCALATION_THRESHOLD_PCT else "MEDIUM"
    return [
        _build_item(
            category="benchmark_regression_review",
            severity=severity,
            source_key="runtime_benchmark",
            source_artifact=str(entry.get("source_path", "")),
            title="Benchmark regression requires operator review",
            advisory_text=(
                f"Benchmark performance regression observed (delta_ns={int(delta_ns)}, delta_pct={float(delta_pct):.6f})."
            ),
            recommended_operator_action=(
                "Review benchmark regression evidence before adopting optimization conclusions."
            ),
            evidence={"delta_ns": int(delta_ns), "delta_pct": float(delta_pct)},
        )
    ]


def _derive_render_items(
    entries_by_key: dict[str, dict[str, Any]], payloads: dict[str, dict[str, Any] | None]
) -> list[dict[str, Any]]:
    render_packet = payloads.get("graph_render_packet")
    entry = entries_by_key.get("graph_render_packet")
    if not isinstance(render_packet, dict) or entry is None:
        return []
    blockers = _stable_strings(render_packet.get("remaining_blockers", []))
    blocker_count = int(render_packet.get("render_blocker_count", len(blockers)))
    if blocker_count <= 0 and _read_status(render_packet) != BLOCKED:
        return []
    return [
        _build_item(
            category="render_blocker_review",
            severity="HIGH",
            source_key="graph_render_packet",
            source_artifact=str(entry.get("source_path", "")),
            title="Render blockers require operator review",
            advisory_text=(
                f"Graph render packet reported {blocker_count} blocker(s) with final_status={_read_status(render_packet)}."
            ),
            recommended_operator_action=(
                "Review render blocker evidence before treating graph render surfaces as reliable."
            ),
            evidence={
                "render_blocker_count": blocker_count,
                "final_status": _read_status(render_packet),
            },
            related_blockers=blockers,
        )
    ]


def _derive_authority_boundary_items(
    entries_by_key: dict[str, dict[str, Any]], payloads: dict[str, dict[str, Any] | None]
) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    items: list[dict[str, Any]] = []
    violations_by_source: dict[str, list[str]] = {}
    for source_key, payload in sorted(payloads.items(), key=lambda item: item[0]):
        entry = entries_by_key.get(source_key)
        if payload is None or entry is None:
            continue
        violations = _scan_forbidden_true_flags(payload)
        if not violations:
            continue
        violations_by_source[source_key] = violations
        items.append(
            _build_item(
                category="authority_boundary_review",
                severity="CRITICAL",
                source_key=source_key,
                source_artifact=str(entry.get("source_path", "")),
                title="Authority boundary violation requires operator review",
                advisory_text=(
                    f"Forbidden authority or mutation flags were observed in {source_key}: {', '.join(violations)}"
                ),
                recommended_operator_action=(
                    f"Escalate authority boundary review for {source_key}; do not execute or mutate anything."
                ),
                evidence={"violations": violations},
            )
        )
    return items, violations_by_source


def _derive_release_readiness_items(
    entries_by_key: dict[str, dict[str, Any]], payloads: dict[str, dict[str, Any] | None]
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    stabilization = payloads.get("stabilization_release_readiness")
    stabilization_entry = entries_by_key.get("stabilization_release_readiness")
    if isinstance(stabilization, dict) and stabilization_entry is not None:
        release_readiness = stabilization.get("release_readiness", {})
        final_posture = stabilization.get("final_posture", {})
        release_status = (
            release_readiness.get("status", NOT_COMPUTABLE)
            if isinstance(release_readiness, dict)
            else NOT_COMPUTABLE
        )
        final_status = (
            final_posture.get("status", NOT_COMPUTABLE)
            if isinstance(final_posture, dict)
            else NOT_COMPUTABLE
        )
        if release_status != "ready_for_manual_release_review" or final_status != "STABILIZED_RELEASE_READINESS_RECORDED":
            items.append(
                _build_item(
                    category="release_readiness_review",
                    severity="MEDIUM",
                    source_key="stabilization_release_readiness",
                    source_artifact=str(stabilization_entry.get("source_path", "")),
                    title="Release readiness posture requires operator review",
                    advisory_text=(
                        "Stabilization release posture is not fully ready for manual release review "
                        f"(release_status={release_status}, final_posture={final_status})."
                    ),
                    recommended_operator_action=(
                        "Review release readiness evidence before treating stabilization posture as ready."
                    ),
                    evidence={
                        "release_readiness_status": release_status,
                        "final_posture_status": final_status,
                    },
                )
            )
    governance = payloads.get("governance_freeze_baseline")
    governance_entry = entries_by_key.get("governance_freeze_baseline")
    if isinstance(governance, dict) and governance_entry is not None:
        freeze_status = governance.get("freeze_status", NOT_COMPUTABLE)
        if freeze_status != "FROZEN":
            items.append(
                _build_item(
                    category="release_readiness_review",
                    severity="MEDIUM",
                    source_key="governance_freeze_baseline",
                    source_artifact=str(governance_entry.get("source_path", "")),
                    title="Governance freeze posture requires operator review",
                    advisory_text=(
                        f"Governance freeze artifact reported freeze_status={freeze_status}."
                    ),
                    recommended_operator_action=(
                        "Review governance freeze evidence before treating release posture as constrained."
                    ),
                    evidence={"freeze_status": freeze_status},
                )
            )
    return items


def _sort_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        items,
        key=lambda item: (
            _SEVERITY_ORDER.get(str(item.get("severity", "LOW")), 999),
            str(item.get("category", "")),
            str(item.get("source_artifact", "")),
            str(item.get("item_id", "")),
        ),
    )


def _related_item_ids(items: list[dict[str, Any]], *, categories: set[str]) -> list[str]:
    return [
        str(item.get("item_id", ""))
        for item in items
        if str(item.get("category", "")) in categories
    ]


def _build_checkpoints(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checkpoints: list[dict[str, Any]] = []
    for item in items:
        checkpoint_id = canonical_hash(
            {"item_id": item.get("item_id"), "category": item.get("category")}
        )
        checkpoints.append(
            {
                "schema": "OperatorApprovalCheckpoint.v1",
                "checkpoint_id": checkpoint_id,
                "related_action_item_ids": [str(item.get("item_id", ""))],
                "required_operator_decision": "Select an operator review disposition for this advisory item.",
                "allowed_decisions": list(_ALLOWED_DECISIONS),
                "decision_status": "PENDING",
                "execution_unlocked": False,
                **_invariants(),
            }
        )
    return checkpoints


def _build_escalations(
    *,
    items: list[dict[str, Any]],
    entries: list[dict[str, Any]],
    payloads: dict[str, dict[str, Any] | None],
    authority_violations: dict[str, list[str]],
) -> list[dict[str, Any]]:
    escalations: list[dict[str, Any]] = []
    blocked_sources = sorted(
        source_key
        for source_key, payload in payloads.items()
        if isinstance(payload, dict) and _read_status(payload) == BLOCKED
    )
    if len(blocked_sources) >= 2:
        escalations.append(
            {
                "schema": "OperatorEscalationPath.v1",
                "escalation_id": canonical_hash({"reason": "repeated_blocked_status", "sources": blocked_sources}),
                "reason_code": "repeated_blocked_status",
                "severity": "HIGH",
                "related_action_item_ids": _related_item_ids(
                    items,
                    categories={"blocked_projection_review", "render_blocker_review"},
                ),
                "source_keys": blocked_sources,
                "advisory_text": (
                    f"Multiple advisory surfaces remain BLOCKED: {', '.join(blocked_sources)}"
                ),
                "recommended_operator_action": "Escalate blocked advisory surfaces for manual operator review.",
                **_invariants(),
            }
        )

    not_computable_sources = sorted(
        str(entry.get("source_key", ""))
        for entry in entries
        if entry.get("source_status") == NOT_COMPUTABLE
    )
    if len(not_computable_sources) >= 2:
        escalations.append(
            {
                "schema": "OperatorEscalationPath.v1",
                "escalation_id": canonical_hash(
                    {"reason": "repeated_not_computable_source", "sources": not_computable_sources}
                ),
                "reason_code": "repeated_not_computable_source",
                "severity": "HIGH",
                "related_action_item_ids": _related_item_ids(
                    items,
                    categories={"missing_artifact_review"},
                ),
                "source_keys": not_computable_sources,
                "advisory_text": (
                    "Multiple source artifacts are NOT_COMPUTABLE: "
                    + ", ".join(not_computable_sources)
                ),
                "recommended_operator_action": "Escalate missing-source posture for manual evidence collection.",
                **_invariants(),
            }
        )

    benchmark = payloads.get("runtime_benchmark")
    if isinstance(benchmark, dict):
        drift_report = benchmark.get("drift_report", {})
        performance_delta = drift_report.get("performance_delta", {}) if isinstance(drift_report, dict) else {}
        delta_pct = performance_delta.get("delta_pct") if isinstance(performance_delta, dict) else None
        if isinstance(delta_pct, int | float) and float(delta_pct) >= _DRIFT_ESCALATION_THRESHOLD_PCT:
            escalations.append(
                {
                    "schema": "OperatorEscalationPath.v1",
                    "escalation_id": canonical_hash(
                        {"reason": "drift_above_threshold", "delta_pct": float(delta_pct)}
                    ),
                    "reason_code": "drift_above_threshold",
                    "severity": "HIGH",
                    "related_action_item_ids": _related_item_ids(
                        items,
                        categories={"benchmark_regression_review", "drift_review"},
                    ),
                    "source_keys": ["runtime_benchmark"],
                    "advisory_text": (
                        f"Observed benchmark drift above threshold (delta_pct={float(delta_pct):.6f})."
                    ),
                    "recommended_operator_action": "Escalate benchmark drift evidence for manual operator review.",
                    **_invariants(),
                }
            )

    chronoscope = payloads.get("projection_chronoscope")
    if isinstance(chronoscope, dict):
        lineage = chronoscope.get("lineage_evolution", {})
        corrupt_lineage_count = (
            int(lineage.get("corrupt_lineage_count", 0))
            if isinstance(lineage, dict)
            else 0
        )
        if corrupt_lineage_count > 0:
            escalations.append(
                {
                    "schema": "OperatorEscalationPath.v1",
                    "escalation_id": canonical_hash(
                        {"reason": "corrupt_lineage", "count": corrupt_lineage_count}
                    ),
                    "reason_code": "corrupt_lineage",
                    "severity": "HIGH",
                    "related_action_item_ids": _related_item_ids(
                        items,
                        categories={"lineage_gap_review"},
                    ),
                    "source_keys": ["projection_chronoscope"],
                    "advisory_text": (
                        f"Chronoscope reported corrupt lineage evidence (count={corrupt_lineage_count})."
                    ),
                    "recommended_operator_action": "Escalate corrupt lineage evidence for manual chronology review.",
                    **_invariants(),
                }
            )

    if authority_violations:
        invalid_sources = sorted(authority_violations)
        escalations.append(
            {
                "schema": "OperatorEscalationPath.v1",
                "escalation_id": canonical_hash(
                    {"reason": "invalid_authority_boundary", "sources": invalid_sources}
                ),
                "reason_code": "invalid_authority_boundary",
                "severity": "CRITICAL",
                "related_action_item_ids": _related_item_ids(
                    items,
                    categories={"authority_boundary_review"},
                ),
                "source_keys": invalid_sources,
                "advisory_text": (
                    "Authority boundary violations were observed in advisory sources: "
                    + ", ".join(invalid_sources)
                ),
                "recommended_operator_action": "Escalate authority boundary evidence immediately for manual review.",
                **_invariants(),
            }
        )

    if _related_item_ids(items, categories={"replay_equivalence_review"}):
        escalations.append(
            {
                "schema": "OperatorEscalationPath.v1",
                "escalation_id": canonical_hash({"reason": "failed_replay_equivalence"}),
                "reason_code": "failed_replay_equivalence",
                "severity": "HIGH",
                "related_action_item_ids": _related_item_ids(
                    items,
                    categories={"replay_equivalence_review"},
                ),
                "source_keys": ["incremental_replay", "runtime_projection"],
                "advisory_text": "Replay equivalence failure evidence requires escalated operator review.",
                "recommended_operator_action": "Escalate replay equivalence evidence for manual operator adjudication.",
                **_invariants(),
            }
        )

    return sorted(escalations, key=lambda item: str(item.get("escalation_id", "")))


def _build_lineage_receipts(
    items: list[dict[str, Any]], checkpoints: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    checkpoint_by_item = {
        str(checkpoint.get("related_action_item_ids", [""])[0]): checkpoint
        for checkpoint in checkpoints
    }
    receipts: list[dict[str, Any]] = []
    for item in items:
        item_id = str(item.get("item_id", ""))
        checkpoint = checkpoint_by_item[item_id]
        evidence_hash = canonical_hash(item.get("evidence", {}))
        receipts.append(
            {
                "schema": "OperatorActionLineageReceipt.v1",
                "receipt_id": canonical_hash(
                    {
                        "item_id": item_id,
                        "checkpoint_id": checkpoint.get("checkpoint_id"),
                        "evidence_hash": evidence_hash,
                    }
                ),
                "action_item_id": item_id,
                "checkpoint_id": checkpoint.get("checkpoint_id"),
                "source_artifact": item.get("source_artifact"),
                "evidence_hash": evidence_hash,
                "lineage_status": "PENDING_OPERATOR_REVIEW",
                **_invariants(),
            }
        )
    return receipts


def _count_by(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        label = str(item.get(key, ""))
        counts[label] = counts.get(label, 0) + 1
    return {label: counts[label] for label in sorted(counts)}


def _top_action_categories(items: list[dict[str, Any]]) -> list[str]:
    counts = _count_by(items, "category")
    return [
        category
        for category, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def _recommended_actions(
    items: list[dict[str, Any]], payloads: dict[str, dict[str, Any] | None]
) -> list[str]:
    recommended: list[str] = []
    operator_console = payloads.get("operator_console")
    if isinstance(operator_console, dict):
        recommended.extend(
            str(action)
            for action in operator_console.get("operator_next_actions", [])
            if str(action)
        )
    recommended.extend(
        str(item.get("recommended_operator_action", ""))
        for item in items
        if str(item.get("recommended_operator_action", ""))
    )
    unique: list[str] = []
    for action in recommended:
        if action not in unique:
            unique.append(action)
    return unique


def summarize_operator_action_queue(queue_data: dict[str, Any] | None) -> dict[str, Any]:
    if queue_data is None:
        return {
            "operator_action_queue_status": NOT_COMPUTABLE,
            "operator_action_item_count": 0,
            "pending_approval_count": 0,
            "escalation_count": 0,
            "top_action_categories": [],
            "queue_advisory_flags": list(_QUEUE_ADVISORY_FLAGS),
            "temporal_state_diff_status": NOT_COMPUTABLE,
            "total_change_count": 0,
            "topology_change_count": 0,
            "lineage_shift_count": 0,
            "drift_acceleration_status": NOT_COMPUTABLE,
            "replay_equivalence_change_status": NOT_COMPUTABLE,
            "queue_delta_count": 0,
            "transport_delta_count": 0,
            "diff_advisory_flags": [],
            "multi_run_convergence_status": NOT_COMPUTABLE,
            "regime_classification": NOT_COMPUTABLE,
            "convergence_evidence_count": 0,
            "topology_persistence_ratio": 0.0,
            "drift_persistence_ratio": 0.0,
            "lineage_persistence_ratio": 0.0,
            "replay_stability_status": NOT_COMPUTABLE,
            "transport_stability_status": NOT_COMPUTABLE,
            "queue_stability_status": NOT_COMPUTABLE,
            "blocker_persistence_status": NOT_COMPUTABLE,
            "convergence_advisory_flags": [],
            "cross_run_topology_fusion_status": NOT_COMPUTABLE,
            "fusion_node_count": 0,
            "fusion_edge_count": 0,
            "persistent_cluster_count": 0,
            "lineage_corridor_count": 0,
            "replay_continuity_status": NOT_COMPUTABLE,
            "transport_continuity_status": NOT_COMPUTABLE,
            "topology_stability_score": 0.0,
            "fusion_advisory_flags": [],
            "temporal_topology_cartography_status": NOT_COMPUTABLE,
            "atlas_region_count": 0,
            "atlas_corridor_count": 0,
            "stable_region_count": 0,
            "volatile_region_count": 0,
            "drift_zone_count": 0,
            "replay_corridor_count": 0,
            "continuity_corridor_count": 0,
            "topology_density_score": 0.0,
            "cartography_advisory_flags": [],
            "temporal_stability_pressure_status": NOT_COMPUTABLE,
            "aggregate_stress_score": 0.0,
            "resilience_score": 0.0,
            "dominant_pressure_component": NOT_COMPUTABLE,
            "pressure_zone_count": 0,
            "critical_pressure_count": 0,
            "strain_zone_count": 0,
            "collapse_pressure_zone_count": 0,
            "drift_load_zone_count": 0,
            "transition_pressure_gradient": 0.0,
            "pressure_advisory_flags": [],
            "temporal_persistence_memory_status": NOT_COMPUTABLE,
            "aggregate_memory_score": 0.0,
            "decay_score": 0.0,
            "hysteresis_score": 0.0,
            "dominant_memory_component": NOT_COMPUTABLE,
            "persistence_half_life_bucket": NOT_COMPUTABLE,
            "memory_zone_count": 0,
            "persistent_memory_count": 0,
            "rapid_decay_zone_count": 0,
            "hysteresis_zone_count": 0,
            "replay_memory_zone_count": 0,
            "topology_memory_zone_count": 0,
            "drift_memory_zone_count": 0,
            "memory_advisory_flags": [],
            "temporal_resonance_coherence_status": NOT_COMPUTABLE,
            "aggregate_coherence_score": 0.0,
            "resonance_score": 0.0,
            "dissonance_score": 0.0,
            "dominant_coherence_component": NOT_COMPUTABLE,
            "phase_alignment_bucket": NOT_COMPUTABLE,
            "coherence_zone_count": 0,
            "locked_coherence_count": 0,
            "resonance_zone_count": 0,
            "dissonance_zone_count": 0,
            "replay_resonance_zone_count": 0,
            "topology_alignment_zone_count": 0,
            "phase_alignment_zone_count": 0,
            "coherence_advisory_flags": [],
        }
    pressure_summary = summarize_temporal_stability_pressure(queue_data)
    memory_summary = summarize_temporal_persistence_memory(queue_data)
    resonance_summary = summarize_temporal_resonance_coherence(queue_data)
    return {
        "operator_action_queue_status": queue_data.get(
            "operator_action_queue_status", queue_data.get("final_status", NOT_COMPUTABLE)
        ),
        "operator_action_item_count": int(queue_data.get("operator_action_item_count", 0)),
        "pending_approval_count": int(queue_data.get("pending_approval_count", 0)),
        "escalation_count": int(queue_data.get("escalation_count", 0)),
        "top_action_categories": [
            str(item) for item in queue_data.get("top_action_categories", [])
        ],
        "queue_advisory_flags": [
            str(item) for item in queue_data.get("queue_advisory_flags", _QUEUE_ADVISORY_FLAGS)
        ],
        "temporal_state_diff_status": str(
            queue_data.get("temporal_state_diff_status", NOT_COMPUTABLE)
        ),
        "total_change_count": int(queue_data.get("total_change_count", 0)),
        "topology_change_count": int(queue_data.get("topology_change_count", 0)),
        "lineage_shift_count": int(queue_data.get("lineage_shift_count", 0)),
        "drift_acceleration_status": str(
            queue_data.get("drift_acceleration_status", NOT_COMPUTABLE)
        ),
        "replay_equivalence_change_status": str(
            queue_data.get("replay_equivalence_change_status", NOT_COMPUTABLE)
        ),
        "queue_delta_count": int(queue_data.get("queue_delta_count", 0)),
        "transport_delta_count": int(queue_data.get("transport_delta_count", 0)),
        "diff_advisory_flags": [
            str(item) for item in queue_data.get("diff_advisory_flags", [])
        ],
        "multi_run_convergence_status": str(
            queue_data.get("multi_run_convergence_status", NOT_COMPUTABLE)
        ),
        "regime_classification": str(
            queue_data.get("regime_classification", NOT_COMPUTABLE)
        ),
        "convergence_evidence_count": int(
            queue_data.get("convergence_evidence_count", 0)
        ),
        "topology_persistence_ratio": float(
            queue_data.get("topology_persistence_ratio", 0.0)
        ),
        "drift_persistence_ratio": float(
            queue_data.get("drift_persistence_ratio", 0.0)
        ),
        "lineage_persistence_ratio": float(
            queue_data.get("lineage_persistence_ratio", 0.0)
        ),
        "replay_stability_status": str(
            queue_data.get("replay_stability_status", NOT_COMPUTABLE)
        ),
        "transport_stability_status": str(
            queue_data.get("transport_stability_status", NOT_COMPUTABLE)
        ),
        "queue_stability_status": str(
            queue_data.get("queue_stability_status", NOT_COMPUTABLE)
        ),
        "blocker_persistence_status": str(
            queue_data.get("blocker_persistence_status", NOT_COMPUTABLE)
        ),
        "convergence_advisory_flags": [
            str(item) for item in queue_data.get("convergence_advisory_flags", [])
        ],
        "cross_run_topology_fusion_status": str(
            queue_data.get("cross_run_topology_fusion_status", NOT_COMPUTABLE)
        ),
        "fusion_node_count": int(queue_data.get("fusion_node_count", 0)),
        "fusion_edge_count": int(queue_data.get("fusion_edge_count", 0)),
        "persistent_cluster_count": int(queue_data.get("persistent_cluster_count", 0)),
        "lineage_corridor_count": int(queue_data.get("lineage_corridor_count", 0)),
        "replay_continuity_status": str(
            queue_data.get("replay_continuity_status", NOT_COMPUTABLE)
        ),
        "transport_continuity_status": str(
            queue_data.get("transport_continuity_status", NOT_COMPUTABLE)
        ),
        "topology_stability_score": float(
            queue_data.get("topology_stability_score", 0.0)
        ),
        "fusion_advisory_flags": [
            str(item) for item in queue_data.get("fusion_advisory_flags", [])
        ],
        "temporal_topology_cartography_status": str(
            queue_data.get("temporal_topology_cartography_status", NOT_COMPUTABLE)
        ),
        "atlas_region_count": int(queue_data.get("atlas_region_count", 0)),
        "atlas_corridor_count": int(queue_data.get("atlas_corridor_count", 0)),
        "stable_region_count": int(queue_data.get("stable_region_count", 0)),
        "volatile_region_count": int(queue_data.get("volatile_region_count", 0)),
        "drift_zone_count": int(queue_data.get("drift_zone_count", 0)),
        "replay_corridor_count": int(queue_data.get("replay_corridor_count", 0)),
        "continuity_corridor_count": int(queue_data.get("continuity_corridor_count", 0)),
        "topology_density_score": float(queue_data.get("topology_density_score", 0.0)),
        "cartography_advisory_flags": [
            str(item) for item in queue_data.get("cartography_advisory_flags", [])
        ],
        "temporal_stability_pressure_status": str(
            queue_data.get(
                "temporal_stability_pressure_status",
                pressure_summary["temporal_stability_pressure_status"],
            )
        ),
        "aggregate_stress_score": float(
            queue_data.get("aggregate_stress_score", pressure_summary["aggregate_stress_score"])
        ),
        "resilience_score": float(
            queue_data.get("resilience_score", pressure_summary["resilience_score"])
        ),
        "dominant_pressure_component": str(
            queue_data.get(
                "dominant_pressure_component",
                pressure_summary["dominant_pressure_component"],
            )
        ),
        "pressure_zone_count": int(
            queue_data.get("pressure_zone_count", pressure_summary["pressure_zone_count"])
        ),
        "critical_pressure_count": int(
            queue_data.get(
                "critical_pressure_count", pressure_summary["critical_pressure_count"]
            )
        ),
        "strain_zone_count": int(
            queue_data.get("strain_zone_count", pressure_summary["strain_zone_count"])
        ),
        "collapse_pressure_zone_count": int(
            queue_data.get(
                "collapse_pressure_zone_count",
                pressure_summary["collapse_pressure_zone_count"],
            )
        ),
        "drift_load_zone_count": int(
            queue_data.get("drift_load_zone_count", pressure_summary["drift_load_zone_count"])
        ),
        "transition_pressure_gradient": float(
            queue_data.get(
                "transition_pressure_gradient",
                pressure_summary["transition_pressure_gradient"],
            )
        ),
        "pressure_advisory_flags": [
            str(item) for item in queue_data.get("pressure_advisory_flags", [])
        ]
        or pressure_summary["pressure_advisory_flags"],
        "temporal_persistence_memory_status": str(
            queue_data.get(
                "temporal_persistence_memory_status",
                memory_summary["temporal_persistence_memory_status"],
            )
        ),
        "aggregate_memory_score": float(
            queue_data.get("aggregate_memory_score", memory_summary["aggregate_memory_score"])
        ),
        "decay_score": float(queue_data.get("decay_score", memory_summary["decay_score"])),
        "hysteresis_score": float(
            queue_data.get("hysteresis_score", memory_summary["hysteresis_score"])
        ),
        "dominant_memory_component": str(
            queue_data.get(
                "dominant_memory_component",
                memory_summary["dominant_memory_component"],
            )
        ),
        "persistence_half_life_bucket": str(
            queue_data.get(
                "persistence_half_life_bucket",
                memory_summary["persistence_half_life_bucket"],
            )
        ),
        "memory_zone_count": int(
            queue_data.get("memory_zone_count", memory_summary["memory_zone_count"])
        ),
        "persistent_memory_count": int(
            queue_data.get("persistent_memory_count", memory_summary["persistent_memory_count"])
        ),
        "rapid_decay_zone_count": int(
            queue_data.get("rapid_decay_zone_count", memory_summary["rapid_decay_zone_count"])
        ),
        "hysteresis_zone_count": int(
            queue_data.get("hysteresis_zone_count", memory_summary["hysteresis_zone_count"])
        ),
        "replay_memory_zone_count": int(
            queue_data.get("replay_memory_zone_count", memory_summary["replay_memory_zone_count"])
        ),
        "topology_memory_zone_count": int(
            queue_data.get(
                "topology_memory_zone_count",
                memory_summary["topology_memory_zone_count"],
            )
        ),
        "drift_memory_zone_count": int(
            queue_data.get("drift_memory_zone_count", memory_summary["drift_memory_zone_count"])
        ),
        "memory_advisory_flags": [
            str(item) for item in queue_data.get("memory_advisory_flags", [])
        ]
        or memory_summary["memory_advisory_flags"],
        "temporal_resonance_coherence_status": str(
            queue_data.get(
                "temporal_resonance_coherence_status",
                resonance_summary["temporal_resonance_coherence_status"],
            )
        ),
        "aggregate_coherence_score": float(
            queue_data.get(
                "aggregate_coherence_score",
                resonance_summary["aggregate_coherence_score"],
            )
        ),
        "resonance_score": float(
            queue_data.get("resonance_score", resonance_summary["resonance_score"])
        ),
        "dissonance_score": float(
            queue_data.get("dissonance_score", resonance_summary["dissonance_score"])
        ),
        "dominant_coherence_component": str(
            queue_data.get(
                "dominant_coherence_component",
                resonance_summary["dominant_coherence_component"],
            )
        ),
        "phase_alignment_bucket": str(
            queue_data.get(
                "phase_alignment_bucket", resonance_summary["phase_alignment_bucket"]
            )
        ),
        "coherence_zone_count": int(
            queue_data.get("coherence_zone_count", resonance_summary["coherence_zone_count"])
        ),
        "locked_coherence_count": int(
            queue_data.get(
                "locked_coherence_count", resonance_summary["locked_coherence_count"]
            )
        ),
        "resonance_zone_count": int(
            queue_data.get("resonance_zone_count", resonance_summary["resonance_zone_count"])
        ),
        "dissonance_zone_count": int(
            queue_data.get(
                "dissonance_zone_count", resonance_summary["dissonance_zone_count"]
            )
        ),
        "replay_resonance_zone_count": int(
            queue_data.get(
                "replay_resonance_zone_count",
                resonance_summary["replay_resonance_zone_count"],
            )
        ),
        "topology_alignment_zone_count": int(
            queue_data.get(
                "topology_alignment_zone_count",
                resonance_summary["topology_alignment_zone_count"],
            )
        ),
        "phase_alignment_zone_count": int(
            queue_data.get(
                "phase_alignment_zone_count",
                resonance_summary["phase_alignment_zone_count"],
            )
        ),
        "coherence_advisory_flags": [
            str(item) for item in queue_data.get("coherence_advisory_flags", [])
        ]
        or resonance_summary["coherence_advisory_flags"],
    }


def build_operator_action_queue_packet(
    *,
    queue_id: str = "operator_action_queue_001",
    source_artifact_paths: dict[str, str | Path] | None = None,
) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    defaults: dict[str, str | Path] = {
        "runtime_performance_profile": paths.runtime_performance_profile_latest,
        "runtime_benchmark": paths.runtime_benchmark_latest,
        "stabilization_release_readiness": paths.stabilization_release_readiness_latest,
        "governance_freeze_baseline": paths.governance_freeze_baseline_latest,
        "incremental_replay": paths.incremental_replay_latest,
        "operator_console": paths.operator_runtime_console_latest,
        "projection_bus": paths.projection_bus_latest,
        "runtime_projection": paths.aal_viz_runtime_projection_latest,
        "projection_chronoscope": paths.projection_chronoscope_latest,
        "graph_render_packet": paths.aal_viz_graph_render_packet_latest,
        "temporal_state_diff": paths.temporal_state_diff_latest,
        "temporal_topology_cartography": paths.temporal_topology_cartography_latest,
        "temporal_stability_pressure": paths.temporal_stability_pressure_latest,
    }
    if source_artifact_paths is None:
        merged_paths = dict(defaults)
    else:
        missing_root = Path("__missing_source_artifacts__")
        merged_paths = {
            key: source_artifact_paths.get(key, missing_root / f"{key}.json")
            for key in defaults
        }
        for key, value in source_artifact_paths.items():
            if key not in merged_paths:
                merged_paths[key] = value
    if source_artifact_paths is None:
        multi_run_convergence_path = paths.multi_run_convergence_latest
        cross_run_topology_fusion_path = paths.cross_run_topology_fusion_latest
        temporal_topology_cartography_path = paths.temporal_topology_cartography_latest
        temporal_stability_pressure_path = paths.temporal_stability_pressure_latest
        temporal_persistence_memory_path = paths.temporal_persistence_memory_latest
        temporal_resonance_coherence_path = paths.temporal_resonance_coherence_latest
    else:
        missing_root = Path("__missing_source_artifacts__")
        multi_run_convergence_path = source_artifact_paths.get(
            "multi_run_convergence",
            missing_root / "multi_run_convergence.json",
        )
        cross_run_topology_fusion_path = source_artifact_paths.get(
            "cross_run_topology_fusion",
            missing_root / "cross_run_topology_fusion.json",
        )
        temporal_topology_cartography_path = source_artifact_paths.get(
            "temporal_topology_cartography",
            missing_root / "temporal_topology_cartography.json",
        )
        temporal_stability_pressure_path = source_artifact_paths.get(
            "temporal_stability_pressure",
            missing_root / "temporal_stability_pressure.json",
        )
        temporal_persistence_memory_path = source_artifact_paths.get(
            "temporal_persistence_memory",
            missing_root / "temporal_persistence_memory.json",
        )
        temporal_resonance_coherence_path = source_artifact_paths.get(
            "temporal_resonance_coherence",
            missing_root / "temporal_resonance_coherence.json",
        )
    multi_run_convergence_payload = _load_artifact(multi_run_convergence_path)
    cross_run_topology_fusion_payload = _load_artifact(cross_run_topology_fusion_path)
    temporal_topology_cartography_payload = _load_artifact(
        temporal_topology_cartography_path
    )
    temporal_stability_pressure_payload = _load_artifact(temporal_stability_pressure_path)
    temporal_stability_pressure_summary = summarize_temporal_stability_pressure(
        temporal_stability_pressure_payload
    )
    temporal_persistence_memory_payload = _load_artifact(temporal_persistence_memory_path)
    temporal_persistence_memory_summary = summarize_temporal_persistence_memory(
        temporal_persistence_memory_payload
    )
    temporal_resonance_coherence_payload = _load_artifact(temporal_resonance_coherence_path)
    temporal_resonance_coherence_summary = summarize_temporal_resonance_coherence(
        temporal_resonance_coherence_payload
    )
    source_entries, payloads = _build_source_entries(merged_paths)
    entries_by_key = {
        str(entry.get("source_key", "")): entry for entry in source_entries
    }

    authority_items, authority_violations = _derive_authority_boundary_items(
        entries_by_key, payloads
    )
    items = _sort_items(
        _derive_missing_artifact_items(source_entries)
        + _derive_blocked_projection_items(entries_by_key, payloads)
        + _derive_drift_items(entries_by_key, payloads)
        + _derive_lineage_items(entries_by_key, payloads)
        + _derive_replay_equivalence_items(entries_by_key, payloads)
        + _derive_benchmark_regression_items(entries_by_key, payloads)
        + _derive_render_items(entries_by_key, payloads)
        + authority_items
        + _derive_release_readiness_items(entries_by_key, payloads)
    )
    checkpoints = _build_checkpoints(items)
    escalations = _build_escalations(
        items=items,
        entries=source_entries,
        payloads=payloads,
        authority_violations=authority_violations,
    )
    lineage_receipts = _build_lineage_receipts(items, checkpoints)

    severity_counts = _count_by(items, "severity")
    category_counts = _count_by(items, "category")
    blocked_sources = sorted(
        {
            str(entry.get("source_path", ""))
            for entry in source_entries
            if entry.get("source_status") == NOT_COMPUTABLE
        }
        | {
            str(entry.get("source_path", ""))
            for entry in source_entries
            if isinstance(payloads.get(str(entry.get("source_key", ""))), dict)
            and _read_status(payloads.get(str(entry.get("source_key", "")))) == BLOCKED
        }
    )

    if not items and all(entry.get("source_status") == NOT_COMPUTABLE for entry in source_entries):
        final_status = NOT_COMPUTABLE
    elif items:
        final_status = "ADVISORY_ONLY"
    else:
        final_status = "PASS"

    queue_hash = canonical_hash(
        {
            "queue_id": queue_id,
            "item_ids": [item["item_id"] for item in items],
            "checkpoint_ids": [checkpoint["checkpoint_id"] for checkpoint in checkpoints],
            "escalation_ids": [escalation["escalation_id"] for escalation in escalations],
            "source_status": {
                str(entry.get("source_key", "")): {
                    "source_status": entry.get("source_status"),
                    "source_marker": entry.get("source_marker", NOT_COMPUTABLE),
                    "source_final_status": entry.get("source_final_status", NOT_COMPUTABLE),
                }
                for entry in source_entries
            },
        }
    )

    return {
        "schema": "OperatorReviewQueue.v1",
        "patch_id": PATCH_ID,
        "queue_id": queue_id,
        "source_artifacts": {key: str(value) for key, value in merged_paths.items()},
        "source_entries": source_entries,
        "operator_action_items": items,
        "approval_checkpoints": checkpoints,
        "escalation_paths": escalations,
        "action_lineage_receipts": lineage_receipts,
        "severity_counts": severity_counts,
        "category_counts": category_counts,
        "operator_action_queue_status": final_status,
        "operator_action_item_count": len(items),
        "pending_approval_count": len(checkpoints),
        "escalation_count": len(escalations),
        "blocked_sources": blocked_sources,
        "top_action_categories": _top_action_categories(items),
        "recommended_operator_next_actions": _recommended_actions(items, payloads),
        "queue_advisory_flags": list(_QUEUE_ADVISORY_FLAGS),
        "temporal_state_diff_status": str(
            (payloads.get("temporal_state_diff") or {}).get("temporal_state_diff_status", NOT_COMPUTABLE)
            if isinstance(payloads.get("temporal_state_diff"), dict)
            else NOT_COMPUTABLE
        ),
        "total_change_count": int(
            (payloads.get("temporal_state_diff") or {}).get("total_change_count", 0)
            if isinstance(payloads.get("temporal_state_diff"), dict)
            else 0
        ),
        "topology_change_count": int(
            (payloads.get("temporal_state_diff") or {}).get("topology_change_count", 0)
            if isinstance(payloads.get("temporal_state_diff"), dict)
            else 0
        ),
        "lineage_shift_count": int(
            (payloads.get("temporal_state_diff") or {}).get("lineage_shift_count", 0)
            if isinstance(payloads.get("temporal_state_diff"), dict)
            else 0
        ),
        "drift_acceleration_status": str(
            (payloads.get("temporal_state_diff") or {}).get(
                "drift_acceleration_status", NOT_COMPUTABLE
            )
            if isinstance(payloads.get("temporal_state_diff"), dict)
            else NOT_COMPUTABLE
        ),
        "replay_equivalence_change_status": str(
            (payloads.get("temporal_state_diff") or {}).get(
                "replay_equivalence_change_status", NOT_COMPUTABLE
            )
            if isinstance(payloads.get("temporal_state_diff"), dict)
            else NOT_COMPUTABLE
        ),
        "queue_delta_count": int(
            (payloads.get("temporal_state_diff") or {}).get("queue_delta_count", 0)
            if isinstance(payloads.get("temporal_state_diff"), dict)
            else 0
        ),
        "transport_delta_count": int(
            (payloads.get("temporal_state_diff") or {}).get("transport_delta_count", 0)
            if isinstance(payloads.get("temporal_state_diff"), dict)
            else 0
        ),
        "diff_advisory_flags": [
            str(item)
            for item in (
                (payloads.get("temporal_state_diff") or {}).get("diff_advisory_flags", [])
                if isinstance(payloads.get("temporal_state_diff"), dict)
                else []
            )
        ],
        "multi_run_convergence_status": str(
            (multi_run_convergence_payload or {}).get(
                "multi_run_convergence_status", NOT_COMPUTABLE
            )
            if isinstance(multi_run_convergence_payload, dict)
            else NOT_COMPUTABLE
        ),
        "regime_classification": str(
            (multi_run_convergence_payload or {}).get(
                "regime_classification", NOT_COMPUTABLE
            )
            if isinstance(multi_run_convergence_payload, dict)
            else NOT_COMPUTABLE
        ),
        "convergence_evidence_count": int(
            (multi_run_convergence_payload or {}).get(
                "convergence_evidence_count", 0
            )
            if isinstance(multi_run_convergence_payload, dict)
            else 0
        ),
        "topology_persistence_ratio": float(
            (multi_run_convergence_payload or {}).get(
                "topology_persistence_ratio", 0.0
            )
            if isinstance(multi_run_convergence_payload, dict)
            else 0.0
        ),
        "drift_persistence_ratio": float(
            (multi_run_convergence_payload or {}).get(
                "drift_persistence_ratio", 0.0
            )
            if isinstance(multi_run_convergence_payload, dict)
            else 0.0
        ),
        "lineage_persistence_ratio": float(
            (multi_run_convergence_payload or {}).get(
                "lineage_persistence_ratio", 0.0
            )
            if isinstance(multi_run_convergence_payload, dict)
            else 0.0
        ),
        "replay_stability_status": str(
            (multi_run_convergence_payload or {}).get(
                "replay_stability_status", NOT_COMPUTABLE
            )
            if isinstance(multi_run_convergence_payload, dict)
            else NOT_COMPUTABLE
        ),
        "transport_stability_status": str(
            (multi_run_convergence_payload or {}).get(
                "transport_stability_status", NOT_COMPUTABLE
            )
            if isinstance(multi_run_convergence_payload, dict)
            else NOT_COMPUTABLE
        ),
        "queue_stability_status": str(
            (multi_run_convergence_payload or {}).get(
                "queue_stability_status", NOT_COMPUTABLE
            )
            if isinstance(multi_run_convergence_payload, dict)
            else NOT_COMPUTABLE
        ),
        "blocker_persistence_status": str(
            (multi_run_convergence_payload or {}).get(
                "blocker_persistence_status", NOT_COMPUTABLE
            )
            if isinstance(multi_run_convergence_payload, dict)
            else NOT_COMPUTABLE
        ),
        "convergence_advisory_flags": [
            str(item)
            for item in (
                (multi_run_convergence_payload or {}).get(
                    "convergence_advisory_flags", []
                )
                if isinstance(multi_run_convergence_payload, dict)
                else []
            )
        ],
        "cross_run_topology_fusion_status": str(
            (cross_run_topology_fusion_payload or {}).get(
                "cross_run_topology_fusion_status", NOT_COMPUTABLE
            )
            if isinstance(cross_run_topology_fusion_payload, dict)
            else NOT_COMPUTABLE
        ),
        "fusion_node_count": int(
            (cross_run_topology_fusion_payload or {}).get("fusion_node_count", 0)
            if isinstance(cross_run_topology_fusion_payload, dict)
            else 0
        ),
        "fusion_edge_count": int(
            (cross_run_topology_fusion_payload or {}).get("fusion_edge_count", 0)
            if isinstance(cross_run_topology_fusion_payload, dict)
            else 0
        ),
        "persistent_cluster_count": int(
            (cross_run_topology_fusion_payload or {}).get("persistent_cluster_count", 0)
            if isinstance(cross_run_topology_fusion_payload, dict)
            else 0
        ),
        "lineage_corridor_count": int(
            (cross_run_topology_fusion_payload or {}).get("lineage_corridor_count", 0)
            if isinstance(cross_run_topology_fusion_payload, dict)
            else 0
        ),
        "replay_continuity_status": str(
            (cross_run_topology_fusion_payload or {}).get(
                "replay_continuity_status", NOT_COMPUTABLE
            )
            if isinstance(cross_run_topology_fusion_payload, dict)
            else NOT_COMPUTABLE
        ),
        "transport_continuity_status": str(
            (cross_run_topology_fusion_payload or {}).get(
                "transport_continuity_status", NOT_COMPUTABLE
            )
            if isinstance(cross_run_topology_fusion_payload, dict)
            else NOT_COMPUTABLE
        ),
        "topology_stability_score": float(
            (cross_run_topology_fusion_payload or {}).get(
                "topology_stability_score", 0.0
            )
            if isinstance(cross_run_topology_fusion_payload, dict)
            else 0.0
        ),
        "fusion_advisory_flags": [
            str(item)
            for item in (
                (cross_run_topology_fusion_payload or {}).get(
                    "fusion_advisory_flags", []
                )
                if isinstance(cross_run_topology_fusion_payload, dict)
                else []
            )
        ],
        "temporal_topology_cartography_status": str(
            (temporal_topology_cartography_payload or {}).get(
                "temporal_topology_cartography_status", NOT_COMPUTABLE
            )
            if isinstance(temporal_topology_cartography_payload, dict)
            else NOT_COMPUTABLE
        ),
        "atlas_region_count": int(
            (temporal_topology_cartography_payload or {}).get("atlas_region_count", 0)
            if isinstance(temporal_topology_cartography_payload, dict)
            else 0
        ),
        "atlas_corridor_count": int(
            (temporal_topology_cartography_payload or {}).get("atlas_corridor_count", 0)
            if isinstance(temporal_topology_cartography_payload, dict)
            else 0
        ),
        "stable_region_count": int(
            (temporal_topology_cartography_payload or {}).get("stable_region_count", 0)
            if isinstance(temporal_topology_cartography_payload, dict)
            else 0
        ),
        "volatile_region_count": int(
            (temporal_topology_cartography_payload or {}).get("volatile_region_count", 0)
            if isinstance(temporal_topology_cartography_payload, dict)
            else 0
        ),
        "drift_zone_count": int(
            (temporal_topology_cartography_payload or {}).get("drift_zone_count", 0)
            if isinstance(temporal_topology_cartography_payload, dict)
            else 0
        ),
        "replay_corridor_count": int(
            (temporal_topology_cartography_payload or {}).get(
                "replay_corridor_count", 0
            )
            if isinstance(temporal_topology_cartography_payload, dict)
            else 0
        ),
        "continuity_corridor_count": int(
            (temporal_topology_cartography_payload or {}).get(
                "continuity_corridor_count", 0
            )
            if isinstance(temporal_topology_cartography_payload, dict)
            else 0
        ),
        "topology_density_score": float(
            (temporal_topology_cartography_payload or {}).get(
                "topology_density_score", 0.0
            )
            if isinstance(temporal_topology_cartography_payload, dict)
            else 0.0
        ),
        "cartography_advisory_flags": [
            str(item)
            for item in (
                (temporal_topology_cartography_payload or {}).get(
                    "cartography_advisory_flags", []
                )
                if isinstance(temporal_topology_cartography_payload, dict)
                else []
            )
        ],
        "temporal_stability_pressure_status": temporal_stability_pressure_summary[
            "temporal_stability_pressure_status"
        ],
        "aggregate_stress_score": temporal_stability_pressure_summary[
            "aggregate_stress_score"
        ],
        "resilience_score": temporal_stability_pressure_summary["resilience_score"],
        "dominant_pressure_component": temporal_stability_pressure_summary[
            "dominant_pressure_component"
        ],
        "pressure_zone_count": temporal_stability_pressure_summary[
            "pressure_zone_count"
        ],
        "critical_pressure_count": temporal_stability_pressure_summary[
            "critical_pressure_count"
        ],
        "strain_zone_count": temporal_stability_pressure_summary["strain_zone_count"],
        "collapse_pressure_zone_count": temporal_stability_pressure_summary[
            "collapse_pressure_zone_count"
        ],
        "drift_load_zone_count": temporal_stability_pressure_summary[
            "drift_load_zone_count"
        ],
        "transition_pressure_gradient": temporal_stability_pressure_summary[
            "transition_pressure_gradient"
        ],
        "pressure_advisory_flags": temporal_stability_pressure_summary[
            "pressure_advisory_flags"
        ],
        "temporal_persistence_memory_status": temporal_persistence_memory_summary[
            "temporal_persistence_memory_status"
        ],
        "aggregate_memory_score": temporal_persistence_memory_summary[
            "aggregate_memory_score"
        ],
        "decay_score": temporal_persistence_memory_summary["decay_score"],
        "hysteresis_score": temporal_persistence_memory_summary["hysteresis_score"],
        "dominant_memory_component": temporal_persistence_memory_summary[
            "dominant_memory_component"
        ],
        "persistence_half_life_bucket": temporal_persistence_memory_summary[
            "persistence_half_life_bucket"
        ],
        "memory_zone_count": temporal_persistence_memory_summary["memory_zone_count"],
        "persistent_memory_count": temporal_persistence_memory_summary[
            "persistent_memory_count"
        ],
        "rapid_decay_zone_count": temporal_persistence_memory_summary[
            "rapid_decay_zone_count"
        ],
        "hysteresis_zone_count": temporal_persistence_memory_summary[
            "hysteresis_zone_count"
        ],
        "replay_memory_zone_count": temporal_persistence_memory_summary[
            "replay_memory_zone_count"
        ],
        "topology_memory_zone_count": temporal_persistence_memory_summary[
            "topology_memory_zone_count"
        ],
        "drift_memory_zone_count": temporal_persistence_memory_summary[
            "drift_memory_zone_count"
        ],
        "memory_advisory_flags": temporal_persistence_memory_summary[
            "memory_advisory_flags"
        ],
        "temporal_resonance_coherence_status": temporal_resonance_coherence_summary[
            "temporal_resonance_coherence_status"
        ],
        "aggregate_coherence_score": temporal_resonance_coherence_summary[
            "aggregate_coherence_score"
        ],
        "resonance_score": temporal_resonance_coherence_summary["resonance_score"],
        "dissonance_score": temporal_resonance_coherence_summary["dissonance_score"],
        "dominant_coherence_component": temporal_resonance_coherence_summary[
            "dominant_coherence_component"
        ],
        "phase_alignment_bucket": temporal_resonance_coherence_summary[
            "phase_alignment_bucket"
        ],
        "coherence_zone_count": temporal_resonance_coherence_summary[
            "coherence_zone_count"
        ],
        "locked_coherence_count": temporal_resonance_coherence_summary[
            "locked_coherence_count"
        ],
        "resonance_zone_count": temporal_resonance_coherence_summary[
            "resonance_zone_count"
        ],
        "dissonance_zone_count": temporal_resonance_coherence_summary[
            "dissonance_zone_count"
        ],
        "replay_resonance_zone_count": temporal_resonance_coherence_summary[
            "replay_resonance_zone_count"
        ],
        "topology_alignment_zone_count": temporal_resonance_coherence_summary[
            "topology_alignment_zone_count"
        ],
        "phase_alignment_zone_count": temporal_resonance_coherence_summary[
            "phase_alignment_zone_count"
        ],
        "coherence_advisory_flags": temporal_resonance_coherence_summary[
            "coherence_advisory_flags"
        ],
        "queue_hash": queue_hash,
        "final_status": final_status,
        **_invariants(),
    }


def write_operator_action_queue_packet(path: str | Path, packet: dict[str, Any]) -> Path:
    target = Path(path)
    write_canonical_json(target, packet)
    return target


def build_operator_action_queue_markdown(packet: dict[str, Any]) -> str:
    severity_counts = packet.get("severity_counts", {})
    lines = [
        f"# Operator Action Queue — {packet.get('queue_id', '')}",
        "",
        f"**Patch:** `{packet.get('patch_id', '')}`",
        f"**Final Status:** `{packet.get('final_status', '')}`",
        f"**Queue Item Count:** `{packet.get('operator_action_item_count', 0)}`",
        f"**Pending Approvals:** `{packet.get('pending_approval_count', 0)}`",
        f"**Escalation Count:** `{packet.get('escalation_count', 0)}`",
        f"**Temporal State Diff Status:** `{packet.get('temporal_state_diff_status', NOT_COMPUTABLE)}`",
        f"**Total Changes:** `{packet.get('total_change_count', 0)}`",
        f"**Topology Changes:** `{packet.get('topology_change_count', 0)}`",
        f"**Lineage Shifts:** `{packet.get('lineage_shift_count', 0)}`",
        (
            f"**Drift Acceleration:** "
            f"`{packet.get('drift_acceleration_status', NOT_COMPUTABLE)}`"
        ),
        (
            f"**Replay Equivalence Changes:** "
            f"`{packet.get('replay_equivalence_change_status', NOT_COMPUTABLE)}`"
        ),
        f"**Queue Deltas:** `{packet.get('queue_delta_count', 0)}`",
        f"**Transport Deltas:** `{packet.get('transport_delta_count', 0)}`",
        "",
        "## Severity Counts",
    ]
    if isinstance(severity_counts, dict) and severity_counts:
        for severity in sorted(severity_counts, key=lambda item: (_SEVERITY_ORDER.get(item, 999), item)):
            lines.append(f"- `{severity}`: `{severity_counts[severity]}`")
    else:
        lines.append("- None")

    lines.extend(["", "## Blocked Sources"])
    blocked_sources = [str(item) for item in packet.get("blocked_sources", [])]
    if blocked_sources:
        for source in blocked_sources:
            lines.append(f"- `{source}`")
    else:
        lines.append("- None")

    lines.extend(["", "## Recommended Operator Next Actions"])
    actions = [str(item) for item in packet.get("recommended_operator_next_actions", [])]
    if actions:
        for action in actions:
            lines.append(f"- {action}")
    else:
        lines.append("- No advisory review items generated.")

    lines.append("")
    return "\n".join(lines)
