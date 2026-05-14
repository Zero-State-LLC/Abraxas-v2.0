from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import (
    TemporalGovernanceWeatherReportPacket,
    TemporalWeatherValidationFinding,
    TemporalWeatherValidationReport,
)


def _canonical_json(d: object) -> str:
    return json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()


def validate_temporal_governance_weather_report_packet(
    report: TemporalGovernanceWeatherReportPacket | Mapping[str, Any],
) -> TemporalWeatherValidationReport:
    r = (
        report
        if isinstance(report, TemporalGovernanceWeatherReportPacket)
        else TemporalGovernanceWeatherReportPacket(**dict(report))
    )

    findings: list[TemporalWeatherValidationFinding] = []
    status = "PASS"

    if (
        (not r.projection_only)
        or r.report_authoritative
        or r.inference_authority_allowed
        or r.action_authorization_allowed
        or r.execution_allowed
        or r.mutation_allowed
        or r.rollback_allowed
        or r.promotion_allowed
        or r.routing_change_allowed
        or r.timeline_collapse_allowed
        or r.canonical_selection_allowed
        or r.replay_normalization_allowed
        or r.adapter_activation_allowed
        or r.auto_transition_allowed
    ):
        findings.append(
            TemporalWeatherValidationFinding(
                "FLAGS_FORBIDDEN",
                "error",
                "top-level flags violate projection-only policy.",
            )
        )
        status = "BLOCKED"

    if not r.weather_summary.projection_only:
        findings.append(
            TemporalWeatherValidationFinding(
                "SUMMARY_PROJECTION_REQUIRED",
                "error",
                "weather_summary.projection_only must be true.",
            )
        )
        status = "BLOCKED"

    if any((not s.projection_only) or s.inference_authority_allowed for s in r.sections):
        findings.append(
            TemporalWeatherValidationFinding(
                "SECTION_FLAGS_FORBIDDEN",
                "error",
                "section flags invalid.",
            )
        )
        status = "BLOCKED"

    if any(a.action_authorization_allowed for a in r.alerts):
        findings.append(
            TemporalWeatherValidationFinding(
                "ALERT_ACTION_FORBIDDEN",
                "error",
                "alerts may not authorize action.",
            )
        )
        status = "BLOCKED"

    if any(
        (not f.lineage_preserved) or f.replay_normalization_allowed or f.routing_change_allowed
        for f in r.pressure_fronts
    ):
        findings.append(
            TemporalWeatherValidationFinding(
                "FRONT_FLAGS_FORBIDDEN",
                "error",
                "pressure front flags invalid.",
            )
        )
        status = "BLOCKED"

    if any(
        p.action_authorization_allowed or p.execution_allowed or p.mutation_allowed or p.routing_change_allowed
        for p in r.review_prompts
    ):
        findings.append(
            TemporalWeatherValidationFinding(
                "PROMPT_FLAGS_FORBIDDEN",
                "error",
                "review prompt flags invalid.",
            )
        )
        status = "BLOCKED"

    receipt_hash = _sha256_text(
        _canonical_json(
            {
                "status": status,
                "findings": [asdict(f) for f in findings],
                "report_id": r.report_id,
            }
        )
    )
    return TemporalWeatherValidationReport(status, tuple(findings), receipt_hash)
