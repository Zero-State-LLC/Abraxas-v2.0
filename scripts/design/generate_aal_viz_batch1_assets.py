#!/usr/bin/env python3
"""Generate AAL-Viz Batch 1 — runtime console completeness (Hallmark · Tier B SVG).

Families: empty/error, workflow, metrics, signal weather (multi-variant),
panel frames, accessibility patterns.

Projection-only. No live data baked in. No production activation.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "design-system" / "aal-viz"
PRODUCER = "GROK+HALLMARK"
BATCH = "1"
PAPER = "#0B1020"
CYAN = "#00D4F5"
VIOLET = "#A78BFA"
AMBER = "#F59E0B"
MUTED = "#64748B"
INK = "#E8EEF7"
ERROR = "#EF4444"
OK = "#10B981"
TEAL = "#2DD4BF"


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def icon_svg(body: str, label: str, view: int = 24, sw: float = 1.5) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view} {view}" '
        f'width="{view}" height="{view}" fill="none" stroke="currentColor" '
        f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" '
        f'role="img" aria-label="{label}">\n'
        f"  <title>{label}</title>\n"
        f"{body}</svg>\n"
    )


@dataclass
class AssetRecord:
    asset_id: str
    name: str
    category: str
    semantic_role: str
    authority_implication: str = "NONE"
    status: str = "CANDIDATE"
    source_format: str = "SVG"
    variants: list[str] = field(default_factory=lambda: ["outline", "monochrome"])
    sizes: list[int] = field(default_factory=lambda: [16, 24, 48])
    dark_theme: bool = True
    light_theme: bool = True
    reduced_motion: bool = True
    alt_text: str = ""
    source_file: str = ""
    export_files: list[str] = field(default_factory=list)
    producer_system: str = PRODUCER
    provenance: list[str] = field(default_factory=list)
    qa: dict = field(
        default_factory=lambda: {
            "contrast_verified": False,
            "small_size_verified": False,
            "semantic_reviewed": False,
            "authority_safe": True,
        }
    )
    batch: str = BATCH
    hallmark: str = "hand-built-svg-tier-B"


def rec(
    records: list[AssetRecord],
    *,
    kind: str,
    name: str,
    category: str,
    role: str,
    alt: str,
    rel: str,
    variants: list[str] | None = None,
    sizes: list[int] | None = None,
) -> None:
    records.append(
        AssetRecord(
            asset_id=f"AALVIZ-{kind}-{role.upper().replace('.', '_')[:48]}",
            name=name,
            category=category,
            semantic_role=role,
            alt_text=alt,
            source_file=f"design-system/aal-viz/{rel}",
            export_files=[f"design-system/aal-viz/{rel}"],
            variants=variants or ["outline", "monochrome"],
            sizes=sizes or [16, 24, 48],
        )
    )


# ── Workflow (24×24) ────────────────────────────────────────────────────────

WORKFLOW: list[tuple[str, str, str]] = [
    ("available", "AVAILABLE", "  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"2\" fill=\"currentColor\" stroke=\"none\"/>\n"),
    ("copied", "COPIED", "  <rect x=\"8\" y=\"7\" width=\"10\" height=\"12\" rx=\"1\"/>\n  <path d=\"M6 15 V5 H16\"/>\n  <path d=\"M11 12 L13 14 L16 10\"/>\n"),
    ("review_required", "REVIEW_REQUIRED", "  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n  <path d=\"M12 8 V13\"/>\n  <circle cx=\"12\" cy=\"16\" r=\"0.8\" fill=\"currentColor\" stroke=\"none\"/>\n"),
    ("blocked", "BLOCKED", "  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n  <path d=\"M8 8 L16 16\" stroke-width=\"2\"/>\n"),
    ("completed_manually", "COMPLETED_MANUALLY", "  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n  <path d=\"M8 12 L11 15 L16 9\"/>\n  <path d=\"M18 6 L20 8\" opacity=\"0.6\"/>\n"),
    ("checklist_incomplete", "CHECKLIST_INCOMPLETE", "  <rect x=\"5\" y=\"4\" width=\"14\" height=\"16\" rx=\"1\"/>\n  <path d=\"M8 9 H16 M8 13 H14 M8 17 H12\"/>\n"),
    ("checklist_complete", "CHECKLIST_COMPLETE", "  <rect x=\"5\" y=\"4\" width=\"14\" height=\"16\" rx=\"1\"/>\n  <path d=\"M8 10 L10 12 L14 8\"/>\n  <path d=\"M8 16 H16\"/>\n"),
    ("evidence_attached", "EVIDENCE_ATTACHED", "  <path d=\"M8 4 H15 L20 9 V20 H8 Z\"/>\n  <path d=\"M15 4 V9 H20\"/>\n  <path d=\"M11 14 L13 16 L17 12\"/>\n"),
    ("evidence_missing", "EVIDENCE_MISSING", "  <path d=\"M8 4 H15 L20 9 V20 H8 Z\"/>\n  <path d=\"M15 4 V9 H20\"/>\n  <path d=\"M11 12 L17 18 M17 12 L11 18\"/>\n"),
    ("decision_pending", "DECISION_PENDING", "  <path d=\"M12 3 L21 12 L12 21 L3 12 Z\"/>\n  <path d=\"M12 9 V13\"/>\n  <circle cx=\"12\" cy=\"16\" r=\"0.7\" fill=\"currentColor\" stroke=\"none\"/>\n"),
    ("decision_accepted", "DECISION_ACCEPTED", "  <path d=\"M12 3 L21 12 L12 21 L3 12 Z\"/>\n  <path d=\"M9 12 L11 14 L15 10\"/>\n"),
    ("decision_rejected", "DECISION_REJECTED", "  <path d=\"M12 3 L21 12 L12 21 L3 12 Z\"/>\n  <path d=\"M9 9 L15 15 M15 9 L9 15\"/>\n"),
    ("decision_deferred", "DECISION_DEFERRED", "  <path d=\"M12 3 L21 12 L12 21 L3 12 Z\"/>\n  <path d=\"M9 12 H15\" stroke-dasharray=\"2 2\"/>\n"),
    ("correction_proposed", "CORRECTION_PROPOSED", "  <path d=\"M14 4 L20 10 L10 20 H4 V14 Z\"/>\n  <path d=\"M12 8 L16 12\"/>\n"),
    ("correction_accepted", "CORRECTION_ACCEPTED", "  <path d=\"M14 4 L20 10 L10 20 H4 V14 Z\"/>\n  <path d=\"M8 14 L10 16 L14 11\"/>\n"),
    ("correction_rejected", "CORRECTION_REJECTED", "  <path d=\"M14 4 L20 10 L10 20 H4 V14 Z\"/>\n  <path d=\"M9 11 L15 17 M15 11 L9 17\"/>\n"),
    ("escalation_required", "ESCALATION_REQUIRED", "  <path d=\"M12 4 L20 18 H4 Z\"/>\n  <path d=\"M12 10 V13\"/>\n  <circle cx=\"12\" cy=\"15.5\" r=\"0.7\" fill=\"currentColor\" stroke=\"none\"/>\n  <path d=\"M12 4 V2\"/>\n"),
    ("operator_note", "OPERATOR_NOTE", "  <path d=\"M6 5 H18 V19 H6 Z\"/>\n  <path d=\"M9 9 H15 M9 12 H15 M9 15 H12\"/>\n"),
    ("manual_handoff", "MANUAL_HANDOFF", "  <circle cx=\"7\" cy=\"10\" r=\"3\"/>\n  <circle cx=\"17\" cy=\"14\" r=\"3\"/>\n  <path d=\"M10 11 L14 13\"/>\n"),
    ("copy_prompt", "COPY_PROMPT", "  <rect x=\"5\" y=\"6\" width=\"14\" height=\"12\" rx=\"1\"/>\n  <path d=\"M8 10 H16 M8 13 H13\"/>\n  <path d=\"M16 4 H20 V8\"/>\n"),
    ("copy_checklist", "COPY_CHECKLIST", "  <rect x=\"7\" y=\"5\" width=\"11\" height=\"14\" rx=\"1\"/>\n  <path d=\"M5 15 V3 H16\"/>\n  <path d=\"M10 10 L12 12 L15 8\"/>\n"),
    ("copy_json", "COPY_JSON", "  <path d=\"M8 6 C6 6 6 8 6 10 V14 C6 16 6 18 8 18\"/>\n  <path d=\"M16 6 C18 6 18 8 18 10 V14 C18 16 18 18 16 18\"/>\n  <path d=\"M11 8 H13 M11 12 H13 M11 16 H13\"/>\n"),
    ("open_source", "OPEN_SOURCE", "  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n  <path d=\"M12 8 V16 M8 12 H16\"/>\n"),
    ("open_artifact", "OPEN_ARTIFACT", "  <rect x=\"6\" y=\"4\" width=\"12\" height=\"16\" rx=\"1\"/>\n  <path d=\"M9 9 H15 M9 13 H15\"/>\n  <path d=\"M16 16 L20 20\"/>\n"),
    ("open_receipt", "OPEN_RECEIPT", "  <rect x=\"6\" y=\"4\" width=\"12\" height=\"16\" rx=\"1\"/>\n  <path d=\"M9 9 H15 M9 13 H13\"/>\n  <path d=\"M9 17 L11 18 L15 15\"/>\n"),
    ("open_notion", "OPEN_NOTION", "  <rect x=\"5\" y=\"4\" width=\"14\" height=\"16\" rx=\"1\"/>\n  <path d=\"M9 8 V16 M9 8 H12 C14 8 14 12 12 12 H9\"/>\n"),
    ("open_github", "OPEN_GITHUB", "  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n  <path d=\"M9 18 C9 15 10 14 11 13 C9 13 8 11 8 10 C8 9 8.5 8 9.5 8 C9 7 9 6 9.5 5.5 C11 6 12 6.5 12 6.5 S13 6 14.5 5.5 C15 6 15 7 14.5 8 C15.5 8 16 9 16 10 C16 11 15 13 13 13 C14 14 14 15 14 18\"/>\n"),
    ("compare_versions", "COMPARE_VERSIONS", "  <rect x=\"3\" y=\"6\" width=\"8\" height=\"12\" rx=\"1\"/>\n  <rect x=\"13\" y=\"6\" width=\"8\" height=\"12\" rx=\"1\"/>\n  <path d=\"M11 12 H13\"/>\n"),
    ("view_lineage", "VIEW_LINEAGE", "  <circle cx=\"6\" cy=\"8\" r=\"2\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"2\"/>\n  <circle cx=\"18\" cy=\"16\" r=\"2\"/>\n  <path d=\"M8 9 L10 11 M14 13 L16 15\"/>\n"),
    ("view_audit_trail", "VIEW_AUDIT_TRAIL", "  <path d=\"M5 5 H19 V19 H5 Z\"/>\n  <path d=\"M5 9 H19 M5 13 H19 M5 17 H19 M9 5 V19\"/>\n"),
]


# ── Metrics (24×24) ─────────────────────────────────────────────────────────

METRICS: list[tuple[str, str, str]] = [
    ("metric_rising", "Metric rising", "  <path d=\"M5 16 L10 11 L14 14 L19 7\"/>\n  <path d=\"M15 7 H19 V11\"/>\n"),
    ("metric_falling", "Metric falling", "  <path d=\"M5 8 L10 13 L14 10 L19 17\"/>\n  <path d=\"M15 17 H19 V13\"/>\n"),
    ("metric_unchanged", "Metric unchanged", "  <path d=\"M5 12 H19\"/>\n  <path d=\"M8 9 L5 12 L8 15 M16 9 L19 12 L16 15\"/>\n"),
    ("metric_volatile", "Metric volatile", "  <path d=\"M4 12 L7 6 L10 16 L13 8 L16 14 L20 10\"/>\n"),
    ("metric_unavailable", "Metric unavailable", "  <path d=\"M5 16 L10 11 L14 14 L17 10\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M8 8 L16 16 M16 8 L8 16\"/>\n"),
    ("metric_stale", "Metric stale", "  <path d=\"M5 16 L10 11 L14 14 L19 8\" opacity=\"0.55\"/>\n  <circle cx=\"18\" cy=\"6\" r=\"3\"/>\n  <path d=\"M18 5 V6.5 L19 7\"/>\n"),
    ("metric_partial", "Metric partial", "  <path d=\"M5 16 L10 11 L12 13\"/>\n  <path d=\"M12 13 L19 8\" stroke-dasharray=\"2 2\"/>\n"),
    ("delta_positive", "Positive delta", "  <path d=\"M12 18 V6 M8 10 L12 6 L16 10\"/>\n"),
    ("delta_negative", "Negative delta", "  <path d=\"M12 6 V18 M8 14 L12 18 L16 14\"/>\n"),
    ("delta_neutral", "Neutral delta", "  <path d=\"M6 12 H18\"/>\n"),
    ("confidence_high", "Confidence high", "  <path d=\"M6 16 V10 H9 V16 Z\" fill=\"currentColor\" stroke=\"none\" opacity=\"0.9\"/>\n  <path d=\"M11 16 V8 H14 V16 Z\" fill=\"currentColor\" stroke=\"none\" opacity=\"0.9\"/>\n  <path d=\"M16 16 V6 H19 V16 Z\" fill=\"currentColor\" stroke=\"none\" opacity=\"0.9\"/>\n"),
    ("confidence_medium", "Confidence medium", "  <path d=\"M6 16 V10 H9 V16 Z\" fill=\"currentColor\" stroke=\"none\"/>\n  <path d=\"M11 16 V8 H14 V16 Z\" fill=\"currentColor\" stroke=\"none\"/>\n  <path d=\"M16 16 V6 H19 V16 Z\" opacity=\"0.35\"/>\n"),
    ("confidence_low", "Confidence low", "  <path d=\"M6 16 V10 H9 V16 Z\" fill=\"currentColor\" stroke=\"none\"/>\n  <path d=\"M11 16 V8 H14 V16 Z\" opacity=\"0.35\"/>\n  <path d=\"M16 16 V6 H19 V16 Z\" opacity=\"0.35\"/>\n"),
    ("confidence_unavailable", "Confidence unavailable", "  <path d=\"M6 16 V10 H9 V16 M11 16 V8 H14 V16 M16 16 V6 H19 V16\" stroke-dasharray=\"1.5 1.5\"/>\n  <path d=\"M7 7 L17 17\"/>\n"),
    ("calibration_good", "Calibration good", "  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"3\"/>\n  <path d=\"M12 4 V7 M12 17 V20\"/>\n"),
    ("calibration_weak", "Calibration weak", "  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"3\" stroke-dasharray=\"2 2\"/>\n"),
    ("calibration_unresolved", "Calibration unresolved", "  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n  <path d=\"M9 9 L15 15 M15 9 L9 15\"/>\n"),
    ("threshold_crossed", "Threshold crossed", "  <path d=\"M4 16 H20\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M5 14 L10 8 L14 11 L19 4\"/>\n  <circle cx=\"16\" cy=\"16\" r=\"2\" fill=\"currentColor\" stroke=\"none\"/>\n"),
    ("threshold_approaching", "Threshold approaching", "  <path d=\"M4 16 H20\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M5 14 L12 9 L17 12\"/>\n  <path d=\"M17 16 V13\"/>\n"),
    ("outlier", "Outlier", "  <path d=\"M4 14 H20\"/>\n  <circle cx=\"8\" cy=\"14\" r=\"1.5\" fill=\"currentColor\" stroke=\"none\"/>\n  <circle cx=\"12\" cy=\"14\" r=\"1.5\" fill=\"currentColor\" stroke=\"none\"/>\n  <circle cx=\"18\" cy=\"7\" r=\"2\"/>\n"),
    ("missing_sample", "Missing sample", "  <circle cx=\"8\" cy=\"14\" r=\"2\"/>\n  <circle cx=\"16\" cy=\"14\" r=\"2\" stroke-dasharray=\"1.5 1.5\"/>\n  <path d=\"M14 12 L18 16 M18 12 L14 16\" opacity=\"0.7\"/>\n"),
    ("insufficient_sample", "Insufficient sample", "  <path d=\"M5 18 V14 M9 18 V12 M13 18 V16 M17 18 V15\"/>\n  <path d=\"M4 8 H20\" stroke-dasharray=\"2 2\" opacity=\"0.5\"/>\n"),
    ("distribution_shift", "Distribution shift", "  <path d=\"M4 16 C7 16 7 8 10 8 S13 16 16 16 S19 10 20 10\"/>\n  <path d=\"M4 16 C7 16 8 12 11 12 S14 18 17 14 S20 12 20 12\" stroke-dasharray=\"2 2\" opacity=\"0.7\"/>\n"),
    ("trend_break", "Trend break", "  <path d=\"M4 14 L10 8 L14 11\"/>\n  <path d=\"M14 11 L20 6\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M13 10 L15 12\"/>\n"),
    ("regime_transition", "Regime transition", "  <path d=\"M4 16 H10 V8 H4 Z\" opacity=\"0.5\"/>\n  <path d=\"M14 16 H20 V8 H14 Z\"/>\n  <path d=\"M10 12 H14\"/>\n"),
    ("data_gap", "Data gap", "  <path d=\"M4 12 H9 M15 12 H20\"/>\n  <path d=\"M9 12 H15\" stroke-dasharray=\"2 2\"/>\n"),
    ("temporal_gap", "Temporal gap", "  <circle cx=\"6\" cy=\"12\" r=\"2\"/>\n  <circle cx=\"18\" cy=\"12\" r=\"2\"/>\n  <path d=\"M9 12 H15\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M12 8 V16\" opacity=\"0.4\"/>\n"),
    ("contradiction", "Contradiction", "  <path d=\"M8 8 L16 16 M16 8 L8 16\" stroke-width=\"2\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n"),
    ("consensus", "Consensus", "  <circle cx=\"9\" cy=\"12\" r=\"4\"/>\n  <circle cx=\"15\" cy=\"12\" r=\"4\"/>\n  <path d=\"M11 12 H13\"/>\n"),
    ("provider_disagreement", "Provider disagreement", "  <circle cx=\"8\" cy=\"10\" r=\"3\"/>\n  <circle cx=\"16\" cy=\"14\" r=\"3\"/>\n  <path d=\"M10 11 L14 13\" stroke-dasharray=\"1.5 1.5\"/>\n  <path d=\"M11 8 L13 16\" opacity=\"0.5\"/>\n"),
    # chart annotations
    ("point_observed", "Observed point", "  <circle cx=\"12\" cy=\"12\" r=\"4\" fill=\"currentColor\" stroke=\"none\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"7\"/>\n"),
    ("point_inferred", "Inferred point", "  <circle cx=\"12\" cy=\"12\" r=\"4\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"7\" stroke-dasharray=\"2 2\"/>\n"),
    ("point_forecast", "Forecast point", "  <path d=\"M12 6 L18 12 L12 18 L6 12 Z\" stroke-dasharray=\"2 2\"/>\n"),
    ("point_intervention", "Intervention point", "  <path d=\"M12 5 V19 M5 12 H19\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"3\"/>\n"),
    ("point_review", "Review point", "  <circle cx=\"12\" cy=\"12\" r=\"6\"/>\n  <path d=\"M12 9 V12\"/>\n  <circle cx=\"12\" cy=\"14.5\" r=\"0.7\" fill=\"currentColor\" stroke=\"none\"/>\n"),
    ("point_correction", "Correction point", "  <path d=\"M14 6 L18 10 L10 18 H6 V14 Z\"/>\n"),
    ("point_outcome", "Outcome point", "  <path d=\"M8 16 L12 8 L16 16 Z\" fill=\"currentColor\" stroke=\"none\" opacity=\"0.85\"/>\n"),
    ("marker_baseline", "Baseline marker", "  <path d=\"M4 16 H20\"/>\n  <path d=\"M4 16 V18 M20 16 V18\"/>\n"),
    ("marker_threshold", "Threshold marker", "  <path d=\"M4 12 H20\" stroke-dasharray=\"3 2\"/>\n  <path d=\"M12 8 V16\"/>\n"),
    ("ci_cap", "Confidence interval cap", "  <path d=\"M8 8 V16 M16 8 V16 M8 8 H16 M8 16 H16\"/>\n  <path d=\"M12 10 V14\"/>\n"),
    ("missing_interval", "Missing interval marker", "  <path d=\"M6 12 H10 M14 12 H18\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M10 9 V15 M14 9 V15\" opacity=\"0.5\"/>\n"),
    ("event_flag", "Event flag", "  <path d=\"M8 20 V5 H16 L14 9 L16 13 H8\"/>\n"),
    ("flag_artifact_citation", "Artifact citation flag", "  <path d=\"M8 20 V5 H15 L18 8 V13 H8\"/>\n  <path d=\"M15 5 V8 H18\"/>\n"),
    ("flag_provenance_citation", "Provenance citation flag", "  <path d=\"M8 20 V5 H16 L14 9 L16 13 H8\"/>\n  <path d=\"M10 8 H14 M10 11 H13\"/>\n"),
]


# ── Signal weather compact bodies ───────────────────────────────────────────

def weather_body(kind: str) -> str:
    """Abstract instrumentation — not cartoon weather."""
    bodies = {
        "clear_stable": "  <circle cx=\"12\" cy=\"12\" r=\"6\"/>\n  <path d=\"M12 4 V6 M12 18 V20 M4 12 H6 M18 12 H20\" opacity=\"0.5\"/>\n",
        "emerging": "  <path d=\"M6 16 C8 12 10 10 12 10 S16 12 18 16\"/>\n  <path d=\"M8 16 H16\" opacity=\"0.4\"/>\n",
        "increasing_pressure": "  <path d=\"M6 18 C8 14 10 10 12 8 S16 10 18 14\"/>\n  <path d=\"M12 8 V4\"/>\n  <path d=\"M10 6 L12 4 L14 6\"/>\n",
        "high_pressure": "  <path d=\"M5 18 C8 10 10 6 12 6 S16 10 19 18\" stroke-width=\"2\"/>\n  <path d=\"M12 6 V3\"/>\n",
        "turbulent": "  <path d=\"M4 14 L7 8 L10 16 L13 7 L16 15 L20 9\"/>\n",
        "drift_front": "  <path d=\"M4 16 L10 10 L14 13 L20 6\"/>\n  <path d=\"M4 18 H20\" stroke-dasharray=\"2 2\" opacity=\"0.5\"/>\n",
        "conflict_front": "  <path d=\"M6 8 L12 14 L18 8\"/>\n  <path d=\"M6 16 L12 10 L18 16\"/>\n",
        "evidence_drought": "  <rect x=\"6\" y=\"6\" width=\"12\" height=\"12\" rx=\"1\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M9 12 H15\" opacity=\"0.4\"/>\n",
        "provider_fog": "  <path d=\"M5 14 H19\" opacity=\"0.35\"/>\n  <path d=\"M6 11 H18\" opacity=\"0.5\"/>\n  <path d=\"M7 8 H17\" opacity=\"0.7\"/>\n  <circle cx=\"12\" cy=\"16\" r=\"2\"/>\n",
        "temporal_fog": "  <circle cx=\"12\" cy=\"12\" r=\"7\" stroke-dasharray=\"2 3\" opacity=\"0.6\"/>\n  <path d=\"M12 8 V12 L15 14\" opacity=\"0.7\"/>\n",
        "forecast_unavailable": "  <path d=\"M4 16 C8 16 8 8 12 8 S16 16 20 16\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M9 9 L15 15 M15 9 L9 15\"/>\n",
        "partial_visibility": "  <circle cx=\"12\" cy=\"12\" r=\"7\"/>\n  <path d=\"M12 5 A7 7 0 0 1 12 19\" fill=\"currentColor\" stroke=\"none\" opacity=\"0.2\"/>\n  <path d=\"M5 12 H12\"/>\n",
        "fail_closed_storm": "  <rect x=\"5\" y=\"5\" width=\"14\" height=\"14\" rx=\"1\"/>\n  <path d=\"M8 12 H16\" stroke-width=\"2\"/>\n  <path d=\"M7 8 L10 11 M17 8 L14 11\" opacity=\"0.6\"/>\n",
        "recovery": "  <path d=\"M7 14 A5 5 0 1 0 12 8\"/>\n  <path d=\"M12 5 V8 H15\"/>\n",
        "stable_undersampled": "  <circle cx=\"12\" cy=\"12\" r=\"6\"/>\n  <path d=\"M12 4 V6 M4 12 H6\" opacity=\"0.4\"/>\n  <circle cx=\"18\" cy=\"6\" r=\"2\" stroke-dasharray=\"1 1\"/>\n",
        "mixed_regime": "  <path d=\"M4 16 H11 V8 H4 Z\" opacity=\"0.55\"/>\n  <path d=\"M13 16 H20 V8 H13 Z\" stroke-dasharray=\"2 2\"/>\n",
        "regime_transition_wx": "  <path d=\"M4 16 H10 V9 H4 Z\"/>\n  <path d=\"M14 16 H20 V9 H14 Z\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M10 12 H14\"/>\n  <path d=\"M12 10 V14\"/>\n",
    }
    return bodies[kind]


WEATHER_STATES: list[tuple[str, str, str]] = [
    ("clear_stable", "Clear / stable", "CLEAR_STABLE"),
    ("emerging", "Emerging", "EMERGING"),
    ("increasing_pressure", "Increasing pressure", "INCREASING_PRESSURE"),
    ("high_pressure", "High pressure", "HIGH_PRESSURE"),
    ("turbulent", "Turbulent", "TURBULENT"),
    ("drift_front", "Drift front", "DRIFT_FRONT"),
    ("conflict_front", "Conflict front", "CONFLICT_FRONT"),
    ("evidence_drought", "Evidence drought", "EVIDENCE_DROUGHT"),
    ("provider_fog", "Provider fog", "PROVIDER_FOG"),
    ("temporal_fog", "Temporal fog", "TEMPORAL_FOG"),
    ("forecast_unavailable", "Forecast unavailable", "FORECAST_UNAVAILABLE"),
    ("partial_visibility", "Partial visibility", "PARTIAL_VISIBILITY"),
    ("fail_closed_storm", "Fail-closed storm", "FAIL_CLOSED_STORM"),
    ("recovery", "Recovery", "RECOVERY"),
    ("stable_undersampled", "Stable but under-sampled", "STABLE_UNDERSAMPLED"),
    ("mixed_regime", "Mixed regime", "MIXED_REGIME"),
    ("regime_transition_wx", "Regime transition", "REGIME_TRANSITION"),
]


def weather_panel(kind: str, label: str) -> str:
    body = weather_body(kind).replace('cx="12"', 'cx="32"').replace('cy="12"', 'cy="28"')
    # crude scale: wrap compact geometry in transform
    inner = weather_body(kind)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 64" width="96" height="64" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" role="img" aria-label="{label} panel">
  <title>{label}</title>
  <rect x="1" y="1" width="94" height="62" rx="6" stroke="{MUTED}" fill="{PAPER}"/>
  <g transform="translate(12,8) scale(1.6)">{inner}  </g>
  <text x="48" y="56" text-anchor="middle" font-family="IBM Plex Mono, ui-monospace, monospace" font-size="7" letter-spacing="0.06em" fill="currentColor" stroke="none">{label.upper()[:22]}</text>
</svg>
"""


def weather_timeline(kind: str, label: str) -> str:
    inner = weather_body(kind)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 24" width="16" height="24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" role="img" aria-label="{label} timeline marker">
  <title>{label}</title>
  <path d="M8 2 V22" opacity="0.35"/>
  <g transform="translate(-4,0) scale(0.65) translate(6,6)">{inner}  </g>
</svg>
"""


# ── Empty / error illustrations (96×72) ─────────────────────────────────────

EMPTY: list[tuple[str, str, str, str]] = [
    # id, title, badge label, extra geometry key
    ("no_projection_bundle", "No projection bundle", "NOT_COMPUTABLE", "bundle"),
    ("sample_fallback_active", "Sample fallback active", "PARTIAL", "fallback"),
    ("authority_validation_failed", "Authority validation failed", "FAIL_CLOSED", "auth_fail"),
    ("source_artifact_absent", "Source artifact absent", "SOURCE_MISSING", "missing_file"),
    ("provenance_unavailable", "Provenance unavailable", "PROVENANCE_MISSING", "prov"),
    ("validator_artifact_unavailable", "Validator artifact unavailable", "VALIDATOR_MISSING", "validator"),
    ("no_selected_system", "No selected system", "EMPTY", "select"),
    ("no_packets_available", "No packets available", "EMPTY", "packets"),
    ("no_receipts_available", "No receipts available", "EMPTY", "receipts"),
    ("no_evidence_available", "No evidence available", "EMPTY", "evidence"),
    ("no_forecast_outcome_join", "No forecast/outcome join", "NOT_COMPUTABLE", "join"),
    ("no_provider_observations", "No provider observations", "EMPTY", "providers"),
    ("no_review_suggestions", "No review suggestions", "EMPTY", "review"),
    ("no_workflow_items", "No workflow items", "EMPTY", "workflow"),
    ("no_timeline_data", "No timeline data", "EMPTY", "timeline"),
    ("no_comparison_baseline", "No comparison baseline", "EMPTY", "compare"),
    ("insufficient_sample", "Insufficient sample", "PARTIAL", "sample"),
    ("schema_mismatch", "Schema mismatch", "SCHEMA_INVALID", "schema"),
    ("corrupt_artifact", "Corrupt artifact", "FAIL_CLOSED", "corrupt"),
    ("stale_projection", "Stale projection", "STALE", "stale"),
    ("transport_disconnected", "Transport disconnected", "DEGRADED", "transport"),
    ("websocket_retry", "WebSocket retry", "DEGRADED", "retry"),
    ("polling_fallback", "Polling fallback", "PARTIAL", "poll"),
    ("read_only_mode", "Read-only mode", "READ_ONLY", "readonly"),
    ("external_production_locked", "External production locked", "HELD", "locked"),
    ("operator_decision_required", "Operator decision required", "OPERATOR_REVIEW", "decision"),
]


def empty_geometry(key: str) -> str:
    g = {
        "bundle": "  <rect x=\"28\" y=\"18\" width=\"40\" height=\"28\" rx=\"2\" stroke-dasharray=\"3 2\"/>\n  <path d=\"M36 32 L44 26 L52 34 L60 24\" opacity=\"0.5\"/>\n",
        "fallback": "  <rect x=\"30\" y=\"20\" width=\"36\" height=\"24\" rx=\"2\"/>\n  <text x=\"48\" y=\"35\" text-anchor=\"middle\" font-size=\"7\" font-family=\"IBM Plex Mono, monospace\" fill=\"currentColor\" stroke=\"none\">SAMPLE</text>\n",
        "auth_fail": "  <path d=\"M48 16 L64 48 H32 Z\"/>\n  <path d=\"M48 28 V36\"/>\n  <circle cx=\"48\" cy=\"40\" r=\"1.2\" fill=\"currentColor\" stroke=\"none\"/>\n",
        "missing_file": "  <path d=\"M34 18 H52 L62 28 V50 H34 Z\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M40 34 L56 34 M48 28 V40\" opacity=\"0.5\"/>\n",
        "prov": "  <path d=\"M36 48 V28 L48 18 L60 28 V48\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M42 48 V36 H54 V48\"/>\n",
        "validator": "  <path d=\"M48 16 L64 24 V36 C64 44 48 52 48 52 S32 44 32 36 V24 Z\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M40 34 H56\"/>\n",
        "select": "  <rect x=\"28\" y=\"20\" width=\"40\" height=\"28\" rx=\"2\"/>\n  <path d=\"M36 28 H60 M36 36 H52\" opacity=\"0.4\"/>\n  <circle cx=\"48\" cy=\"42\" r=\"2\" stroke-dasharray=\"1 1\"/>\n",
        "packets": "  <rect x=\"32\" y=\"22\" width=\"14\" height=\"10\" rx=\"1\" opacity=\"0.4\"/>\n  <rect x=\"50\" y=\"34\" width=\"14\" height=\"10\" rx=\"1\" opacity=\"0.4\"/>\n",
        "receipts": "  <rect x=\"36\" y=\"18\" width=\"24\" height=\"32\" rx=\"1\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M42 28 H54 M42 36 H50\" opacity=\"0.4\"/>\n",
        "evidence": "  <path d=\"M36 18 H54 L62 26 V50 H36 Z\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M42 34 H54\" opacity=\"0.4\"/>\n",
        "join": "  <circle cx=\"36\" cy=\"34\" r=\"8\" stroke-dasharray=\"2 2\"/>\n  <circle cx=\"60\" cy=\"34\" r=\"8\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M44 34 H52\" stroke-dasharray=\"2 2\"/>\n",
        "providers": "  <rect x=\"28\" y=\"26\" width=\"16\" height=\"16\" rx=\"2\" opacity=\"0.45\"/>\n  <rect x=\"52\" y=\"26\" width=\"16\" height=\"16\" rx=\"2\" opacity=\"0.45\"/>\n",
        "review": "  <path d=\"M34 20 H54 L62 28 V50 H34 Z\"/>\n  <path d=\"M42 34 L46 38 L54 30\" opacity=\"0.35\" stroke-dasharray=\"2 2\"/>\n",
        "workflow": "  <path d=\"M30 28 H66 M30 36 H50 M30 44 H42\" opacity=\"0.4\"/>\n",
        "timeline": "  <path d=\"M28 36 H68\"/>\n  <circle cx=\"36\" cy=\"36\" r=\"3\" opacity=\"0.35\"/>\n  <circle cx=\"48\" cy=\"36\" r=\"3\" stroke-dasharray=\"1 1\"/>\n  <circle cx=\"60\" cy=\"36\" r=\"3\" opacity=\"0.35\"/>\n",
        "compare": "  <rect x=\"28\" y=\"22\" width=\"16\" height=\"28\" rx=\"1\" opacity=\"0.5\"/>\n  <rect x=\"52\" y=\"22\" width=\"16\" height=\"28\" rx=\"1\" stroke-dasharray=\"2 2\"/>\n",
        "sample": "  <path d=\"M32 48 V36 M40 48 V30 M48 48 V42 M56 48 V38 M64 48 V40\"/>\n  <path d=\"M28 24 H68\" stroke-dasharray=\"2 2\" opacity=\"0.4\"/>\n",
        "schema": "  <path d=\"M30 22 H66 V32 H30 Z\"/>\n  <path d=\"M30 36 H66 V48 H30 Z\"/>\n  <path d=\"M36 26 L60 44\"/>\n",
        "corrupt": "  <path d=\"M36 18 H54 L62 26 V50 H36 Z\"/>\n  <path d=\"M40 30 L56 46 M56 30 L40 46\"/>\n",
        "stale": "  <rect x=\"30\" y=\"20\" width=\"36\" height=\"26\" rx=\"2\" opacity=\"0.55\"/>\n  <circle cx=\"62\" cy=\"18\" r=\"5\"/>\n  <path d=\"M62 16 V18.5 L63.5 19\"/>\n",
        "transport": "  <path d=\"M28 36 H42 M54 36 H68\"/>\n  <path d=\"M42 36 H54\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M48 28 L48 44\" opacity=\"0.4\"/>\n",
        "retry": "  <path d=\"M58 36 A12 12 0 1 0 48 24\"/>\n  <path d=\"M48 20 V24 H52\"/>\n",
        "poll": "  <circle cx=\"48\" cy=\"34\" r=\"10\" stroke-dasharray=\"3 2\"/>\n  <path d=\"M48 28 V34 H53\"/>\n",
        "readonly": "  <path d=\"M30 34 C36 24 42 22 48 22 S60 24 66 34 C60 44 54 46 48 46 S36 44 30 34 Z\"/>\n  <circle cx=\"48\" cy=\"34\" r=\"4\"/>\n  <path d=\"M34 48 L62 20\" opacity=\"0.5\"/>\n",
        "locked": "  <path d=\"M34 48 V34 L48 24 L62 34 V48\"/>\n  <rect x=\"42\" y=\"36\" width=\"12\" height=\"10\" rx=\"1\"/>\n  <path d=\"M45 36 V33 A3 3 0 0 1 51 33 V36\"/>\n",
        "decision": "  <path d=\"M48 16 L66 34 L48 52 L30 34 Z\"/>\n  <path d=\"M48 28 V36\"/>\n  <circle cx=\"48\" cy=\"40\" r=\"1.2\" fill=\"currentColor\" stroke=\"none\"/>\n",
    }
    return g.get(key, "  <rect x=\"32\" y=\"22\" width=\"32\" height=\"24\" rx=\"2\" stroke-dasharray=\"2 2\"/>\n")


def empty_illustration(eid: str, title: str, badge: str, key: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 72" width="96" height="72" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" role="img" aria-label="{title}">
  <title>{title}</title>
  <desc>{badge}. Informative empty or blocked state. Projection only.</desc>
  <rect x="1" y="1" width="94" height="70" rx="6" stroke="{MUTED}" fill="{PAPER}"/>
{empty_geometry(key)}  <rect x="8" y="56" width="80" height="10" rx="2" fill="{PAPER}" stroke="{MUTED}"/>
  <text x="48" y="63.5" text-anchor="middle" font-family="IBM Plex Mono, ui-monospace, monospace" font-size="6.5" letter-spacing="0.08em" fill="currentColor" stroke="none">{badge}</text>
</svg>
"""


# ── Panel frames (vector chrome) ────────────────────────────────────────────

def panel_frame(name: str, label: str, *, dash: bool = False, corner: str = "mark", badge: str = "") -> str:
    stroke_extra = ' stroke-dasharray="4 3"' if dash else ""
    marks = {
        "mark": "  <path d=\"M8 8 H16 M8 8 V16\" opacity=\"0.7\"/>\n  <path d=\"M88 8 H80 M88 8 V16\" opacity=\"0.7\"/>\n  <path d=\"M8 56 H16 M8 56 V48\" opacity=\"0.7\"/>\n  <path d=\"M88 56 H80 M88 56 V48\" opacity=\"0.7\"/>\n",
        "raised": "  <rect x=\"6\" y=\"6\" width=\"84\" height=\"52\" rx=\"5\" opacity=\"0.25\"/>\n",
        "rail": "  <path d=\"M10 8 V56\" stroke-width=\"3\" opacity=\"0.5\"/>\n",
        "footer": "  <path d=\"M12 48 H84\" opacity=\"0.5\"/>\n  <text x=\"14\" y=\"54\" font-family=\"IBM Plex Mono, monospace\" font-size=\"5\" fill=\"currentColor\" stroke=\"none\" opacity=\"0.7\">SOURCE · PROVENANCE</text>\n",
        "divider": "  <path d=\"M12 18 H84\"/>\n  <text x=\"12\" y=\"14\" font-family=\"IBM Plex Mono, monospace\" font-size=\"6\" fill=\"currentColor\" stroke=\"none\" letter-spacing=\"0.1em\">TITLE</text>\n",
        "none": "",
    }
    badge_el = ""
    if badge:
        badge_el = (
            f'  <rect x="64" y="8" width="24" height="8" rx="2" stroke="{MUTED}"/>\n'
            f'  <text x="76" y="14" text-anchor="middle" font-family="IBM Plex Mono, monospace" '
            f'font-size="4.5" fill="currentColor" stroke="none">{badge}</text>\n'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 64" width="96" height="64" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" role="img" aria-label="{label}">
  <title>{label}</title>
  <rect x="4" y="4" width="88" height="56" rx="6"{stroke_extra}/>
{marks.get(corner, marks['mark'])}{badge_el}</svg>
"""


PANELS: list[tuple[str, str, dict]] = [
    ("base_panel", "Base panel corner treatment", {"corner": "mark"}),
    ("raised_panel", "Raised panel treatment", {"corner": "raised"}),
    ("evidence_panel", "Evidence panel treatment", {"badge": "EVID"}),
    ("warning_panel", "Warning panel treatment", {"badge": "WARN"}),
    ("fail_closed_panel", "Fail-closed panel treatment", {"badge": "FAIL"}),
    ("projection_only_panel", "Projection-only panel", {"badge": "PROJ", "dash": True}),
    ("forecast_reserved_panel", "Forecast-reserved panel", {"badge": "FCST", "dash": True}),
    ("operator_review_panel", "Operator-review panel", {"badge": "OPS"}),
    ("modal_frame", "Modal frame", {"corner": "raised"}),
    ("drawer_frame", "Drawer frame", {"corner": "rail"}),
    ("inspector_frame", "Inspector frame", {"corner": "rail", "badge": "INS"}),
    ("command_palette_frame", "Command palette frame", {"corner": "raised"}),
    ("timeline_rail", "Timeline rail", {"corner": "rail"}),
    ("evidence_rail", "Evidence rail", {"corner": "rail", "badge": "EV"}),
    ("authority_rail", "Authority rail", {"corner": "rail", "badge": "AUTH"}),
    ("source_provenance_footer", "Source/provenance footer", {"corner": "footer"}),
    ("panel_title_divider", "Panel title divider", {"corner": "divider"}),
    ("compact_card_frame", "Compact card frame", {"corner": "mark"}),
    ("data_table_header_frame", "Data-table header frame", {"corner": "divider"}),
    ("empty_state_container", "Empty-state container", {"dash": True, "corner": "mark"}),
    ("error_state_container", "Error-state container", {"badge": "ERR"}),
    ("loading_state_container", "Loading-state container", {"dash": True, "corner": "none"}),
]


# ── A11y patterns ───────────────────────────────────────────────────────────

def pattern_svg(name: str, label: str, body: str, view: int = 24) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view} {view}" width="{view}" height="{view}" role="img" aria-label="{label}">
  <title>{label}</title>
  <defs>
{body}  </defs>
  <rect width="{view}" height="{view}" fill="url(#{name})" stroke="currentColor" stroke-width="1"/>
</svg>
"""


A11Y_PATTERNS = [
    ("hatch_diagonal", "Diagonal hatch pattern", '    <pattern id="hatch_diagonal" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">\n      <line x1="0" y1="0" x2="0" y2="6" stroke="currentColor" stroke-width="1.2"/>\n    </pattern>\n'),
    ("hatch_cross", "Cross hatch pattern", '    <pattern id="hatch_cross" width="8" height="8" patternUnits="userSpaceOnUse">\n      <path d="M0 0 L8 8 M8 0 L0 8" stroke="currentColor" stroke-width="1"/>\n    </pattern>\n'),
    ("dots_sparse", "Sparse dots pattern", '    <pattern id="dots_sparse" width="8" height="8" patternUnits="userSpaceOnUse">\n      <circle cx="2" cy="2" r="1.2" fill="currentColor"/>\n    </pattern>\n'),
    ("dots_dense", "Dense dots pattern", '    <pattern id="dots_dense" width="4" height="4" patternUnits="userSpaceOnUse">\n      <circle cx="1" cy="1" r="0.8" fill="currentColor"/>\n    </pattern>\n'),
    ("stripes_horizontal", "Horizontal stripes", '    <pattern id="stripes_horizontal" width="4" height="4" patternUnits="userSpaceOnUse">\n      <line x1="0" y1="1" x2="4" y2="1" stroke="currentColor" stroke-width="1.5"/>\n    </pattern>\n'),
    ("stripes_vertical", "Vertical stripes", '    <pattern id="stripes_vertical" width="4" height="4" patternUnits="userSpaceOnUse">\n      <line x1="1" y1="0" x2="1" y2="4" stroke="currentColor" stroke-width="1.5"/>\n    </pattern>\n'),
    ("checker", "Checker pattern", '    <pattern id="checker" width="8" height="8" patternUnits="userSpaceOnUse">\n      <rect width="4" height="4" fill="currentColor" opacity="0.55"/>\n      <rect x="4" y="4" width="4" height="4" fill="currentColor" opacity="0.55"/>\n    </pattern>\n'),
    ("observed_fill", "Observed register fill pattern", '    <pattern id="observed_fill" width="6" height="6" patternUnits="userSpaceOnUse">\n      <rect width="6" height="6" fill="none"/>\n      <circle cx="3" cy="3" r="1.5" fill="currentColor"/>\n    </pattern>\n'),
    ("inferred_fill", "Inferred register fill pattern", '    <pattern id="inferred_fill" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">\n      <line x1="0" y1="0" x2="0" y2="6" stroke="currentColor" stroke-width="2"/>\n    </pattern>\n'),
    ("speculative_fill", "Speculative register fill pattern", '    <pattern id="speculative_fill" width="8" height="8" patternUnits="userSpaceOnUse">\n      <path d="M0 4 H8 M4 0 V8" stroke="currentColor" stroke-width="1" stroke-dasharray="2 2"/>\n    </pattern>\n'),
    ("shadow_fill", "Shadow register fill pattern", '    <pattern id="shadow_fill" width="4" height="4" patternUnits="userSpaceOnUse">\n      <line x1="0" y1="0" x2="4" y2="4" stroke="currentColor" stroke-width="1" opacity="0.7"/>\n    </pattern>\n'),
    ("not_computable_fill", "Not-computable fill pattern", '    <pattern id="not_computable_fill" width="8" height="8" patternUnits="userSpaceOnUse">\n      <path d="M1 1 L7 7 M7 1 L1 7" stroke="currentColor" stroke-width="1.2"/>\n    </pattern>\n'),
]

A11Y_LINES = [
    ("line_solid_verified", "Verified solid line", "  <path d=\"M2 12 H22\" stroke-width=\"2\"/>\n"),
    ("line_dashed_inferred", "Inferred dashed line", "  <path d=\"M2 12 H22\" stroke-dasharray=\"4 3\"/>\n"),
    ("line_dotted_speculative", "Speculative dotted line", "  <path d=\"M2 12 H22\" stroke-dasharray=\"1.5 3\"/>\n"),
    ("line_double_authority", "Authority double line", "  <path d=\"M2 10 H22 M2 14 H22\"/>\n"),
    ("line_rail_evidence", "Evidence rail line", "  <path d=\"M2 12 H22\" stroke-width=\"3\" opacity=\"0.35\"/>\n  <path d=\"M2 12 H22\"/>\n"),
    ("line_blocked", "Blocked line", "  <path d=\"M2 12 H22\"/>\n  <path d=\"M10 8 L14 16 M14 8 L10 16\"/>\n"),
]

FOCUS_ASSETS = [
    ("focus_ring", "Focus-state ring", "  <rect x=\"3\" y=\"3\" width=\"18\" height=\"18\" rx=\"3\" stroke-width=\"2\"/>\n  <rect x=\"6\" y=\"6\" width=\"12\" height=\"12\" rx=\"2\" opacity=\"0.35\"/>\n"),
    ("keyboard_focus_indicator", "Keyboard focus indicator", "  <rect x=\"2\" y=\"2\" width=\"20\" height=\"20\" rx=\"2\" stroke-width=\"2\" stroke-dasharray=\"3 2\"/>\n"),
    ("large_target_hit", "Large-target control chrome", "  <rect x=\"2\" y=\"2\" width=\"20\" height=\"20\" rx=\"4\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"3\" fill=\"currentColor\" stroke=\"none\"/>\n"),
]


def main() -> None:
    records: list[AssetRecord] = []
    files = 0

    # Workflow
    for name, role, body in WORKFLOW:
        rel = f"workflow/{name}.svg"
        write(OUT / rel, icon_svg(body, role.replace("_", " ")))
        rec(records, kind="ICON-WF", name=name, category="workflow_icon", role=role, alt=role, rel=rel)
        files += 1

    # Metrics
    for name, alt, body in METRICS:
        rel = f"metrics/{name}.svg"
        write(OUT / rel, icon_svg(body, alt))
        rec(records, kind="ICON-MET", name=name, category="metric_icon", role=name.upper(), alt=alt, rel=rel)
        files += 1

    # Weather variants
    for name, label, role in WEATHER_STATES:
        # compact
        rel_c = f"weather/compact/{name}.svg"
        write(OUT / rel_c, icon_svg(weather_body(name), label))
        rec(
            records,
            kind="WX-COMPACT",
            name=f"{name}_compact",
            category="weather_compact",
            role=role,
            alt=label,
            rel=rel_c,
            variants=["outline", "monochrome", "reduced_motion"],
        )
        files += 1
        # panel (also serves reduced-animation — static, no SMIL)
        rel_p = f"weather/panel/{name}.svg"
        write(OUT / rel_p, weather_panel(name, label))
        rec(
            records,
            kind="WX-PANEL",
            name=f"{name}_panel",
            category="weather_panel",
            role=role,
            alt=f"{label} panel",
            rel=rel_p,
            sizes=[64, 96],
            variants=["panel", "monochrome", "reduced_motion"],
        )
        files += 1
        # timeline
        rel_t = f"weather/timeline/{name}.svg"
        write(OUT / rel_t, weather_timeline(name, label))
        rec(
            records,
            kind="WX-TL",
            name=f"{name}_timeline",
            category="weather_timeline",
            role=role,
            alt=f"{label} timeline marker",
            rel=rel_t,
            sizes=[16, 24],
        )
        files += 1

    # Empty / error
    for eid, title, badge, key in EMPTY:
        rel = f"empty/{eid}.svg"
        write(OUT / rel, empty_illustration(eid, title, badge, key))
        rec(
            records,
            kind="EMPTY",
            name=eid,
            category="empty_error_state",
            role=badge,
            alt=f"{title} ({badge})",
            rel=rel,
            sizes=[96, 192],
            variants=["illustration", "monochrome"],
        )
        files += 1

    # Panels
    for name, label, opts in PANELS:
        rel = f"panels/{name}.svg"
        write(OUT / rel, panel_frame(name, label, **opts))
        rec(
            records,
            kind="PANEL",
            name=name,
            category="panel_frame",
            role=name.upper(),
            alt=label,
            rel=rel,
            sizes=[96, 192],
            variants=["frame", "monochrome"],
        )
        files += 1

    # A11y patterns
    for name, label, body in A11Y_PATTERNS:
        rel = f"a11y/patterns/{name}.svg"
        write(OUT / rel, pattern_svg(name, label, body))
        rec(
            records,
            kind="A11Y-PAT",
            name=name,
            category="a11y_pattern",
            role=name.upper(),
            alt=label,
            rel=rel,
            variants=["pattern", "monochrome", "high_contrast"],
        )
        files += 1

    for name, label, body in A11Y_LINES:
        rel = f"a11y/lines/{name}.svg"
        write(OUT / rel, icon_svg(body, label))
        rec(records, kind="A11Y-LINE", name=name, category="a11y_line", role=name.upper(), alt=label, rel=rel)
        files += 1

    for name, label, body in FOCUS_ASSETS:
        rel = f"a11y/focus/{name}.svg"
        write(OUT / rel, icon_svg(body, label))
        rec(records, kind="A11Y-FOCUS", name=name, category="a11y_focus", role=name.upper(), alt=label, rel=rel)
        files += 1

    # A11y templates (JSON/md — not images)
    alt_templates = {
        "schema_version": "AALVizAltTextTemplates.v1",
        "batch": BATCH,
        "templates": {
            "authority": "{status} status",
            "weather": "Signal weather: {state}",
            "empty": "{title}. {badge}. No data rendered.",
            "workflow": "Workflow state: {state}",
            "metric": "Metric mark: {name}",
            "decorative": "",  # use aria-hidden
        },
        "sr_decorative_suppression": {
            "rule": "Mark purely ornamental SVG with aria-hidden=true and empty alt; pair with visible text label.",
            "map": [
                "weather decorative bloom behind panel",
                "panel corner marks when title is present",
                "brand mark next to visible AAL-VIZ wordmark",
            ],
        },
    }
    write(
        OUT / "a11y/templates/alt_text_templates.v1.json",
        json.dumps(alt_templates, indent=2) + "\n",
    )
    write(
        OUT / "a11y/templates/plain_language_infographic.md",
        "# Plain-language infographic template\n\n"
        "1. **What this shows** — one sentence, projection-only.\n"
        "2. **What is observed** — bullets from source artifacts only.\n"
        "3. **What is inferred** — explicitly labeled INFERRED.\n"
        "4. **What is blocked** — NOT_COMPUTABLE / FAIL_CLOSED with reason code.\n"
        "5. **What to do next** — operator action or “no action; held”.\n"
        "6. **Sources** — artifact ids / paths.\n",
    )
    write(
        OUT / "a11y/templates/copy_paste_projection.md",
        "# Copy/paste projection template\n\n"
        "```\nAAL-VIZ · PROJECTION ONLY\nStatus: {STATUS}\nObserved: …\nInferred: …\nBlocked: …\nSources: …\n```\n",
    )
    write(
        OUT / "a11y/templates/short_text_projection.md",
        "# Short-text projection template\n\n"
        "`{ENTITY} · {STATUS} · projection only · sources: {N}`\n",
    )
    write(
        OUT / "a11y/templates/print_safe_diagram.md",
        "# Print-safe diagram template\n\n"
        "- Black stroke on white; no reliance on cyan/violet alone.\n"
        "- Use a11y/patterns for node fills.\n"
        "- Include watermark `AAL-VIZ · PROJECTION ONLY`.\n"
        "- Disable glow; 1.5–2pt strokes minimum.\n",
    )
    write(
        OUT / "a11y/templates/grayscale_report.md",
        "# Grayscale report template\n\n"
        "- Map registers to pattern fills (observed=dots, inferred=hatch, speculative=dash-cross).\n"
        "- Keep textual badges for every status chip.\n",
    )
    write(
        OUT / "a11y/templates/sr_decorative_suppression_map.json",
        json.dumps(alt_templates["sr_decorative_suppression"], indent=2) + "\n",
    )

    for tname in (
        "alt_text_templates.v1.json",
        "plain_language_infographic.md",
        "copy_paste_projection.md",
        "short_text_projection.md",
        "print_safe_diagram.md",
        "grayscale_report.md",
        "sr_decorative_suppression_map.json",
    ):
        rel = f"a11y/templates/{tname}"
        rec(
            records,
            kind="A11Y-TPL",
            name=slug(tname),
            category="a11y_template",
            role=tname.upper(),
            alt=f"Accessibility template {tname}",
            rel=rel,
            variants=["document"],
            sizes=[],
        )

    # Batch 1 manifest fragment
    b1_manifest = {
        "schema_version": "AALVizAssetManifest.v1",
        "name": "aal-viz-batch1-runtime-console",
        "batch": BATCH,
        "version": "0.1.0",
        "updated": "2026-07-19",
        "hallmark": {
            "genre": "atmospheric-technical",
            "theme": "custom (Abraxas projection grammar)",
            "enrichment": "Tier B hand-built SVG",
            "macrostructure": "Workbench",
        },
        "producer_system": PRODUCER,
        "asset_count": len(records),
        "file_count_approx": files,
        "assets": [asdict(r) for r in records],
    }
    write(OUT / "aal_viz_asset_manifest.batch1.v1.json", json.dumps(b1_manifest, indent=2) + "\n")

    # Merge indexes into icon registry
    reg_path = OUT / "AAL_VIZ_ICON_REGISTRY.json"
    reg = json.loads(reg_path.read_text(encoding="utf-8")) if reg_path.exists() else {}
    reg["schema_version"] = "AALVizIconRegistry.v1"
    reg["workflow"] = [n for n, _, _ in WORKFLOW]
    reg["metrics"] = [n for n, _, _ in METRICS]
    reg["weather"] = [n for n, _, _ in WEATHER_STATES]
    reg["empty_error"] = [e[0] for e in EMPTY]
    reg["panels"] = [p[0] for p in PANELS]
    reg["a11y_patterns"] = [p[0] for p in A11Y_PATTERNS]
    reg["a11y_lines"] = [p[0] for p in A11Y_LINES]
    reg["a11y_focus"] = [p[0] for p in FOCUS_ASSETS]
    write(reg_path, json.dumps(reg, indent=2) + "\n")

    # Gap ledger refresh (full picture)
    gap_path = OUT / "docs" / "AAL_VIZ_ASSET_GAP_LEDGER.csv"
    rows = [
        ("class", "planned", "shipped", "batch", "status", "notes"),
        ("identity", "10", "11", "0", "PARTIAL", "SVG masters"),
        ("authority", "30", "30", "0", "SHIPPED", "outline+solid"),
        ("activation", "16", "16", "0", "SHIPPED", ""),
        ("navigation", "44", "44", "0", "SHIPPED", ""),
        ("subsystem_p0", "24", "24", "0", "SHIPPED", ""),
        ("graph_primitives", "51", "51", "0", "SHIPPED", ""),
        ("workflow", "30", str(len(WORKFLOW)), "1", "SHIPPED", ""),
        ("metrics", "44", str(len(METRICS)), "1", "SHIPPED", "P0+annotations"),
        ("weather", "17", str(len(WEATHER_STATES) * 3), "1", "SHIPPED", "compact+panel+timeline ×17"),
        ("empty_error", "26", str(len(EMPTY)), "1", "SHIPPED", "badge-labeled"),
        ("panels", "22", str(len(PANELS)), "1", "SHIPPED", "SVG frames"),
        ("a11y_patterns", "19", str(len(A11Y_PATTERNS) + len(A11Y_LINES) + len(FOCUS_ASSETS) + 7), "1", "SHIPPED", "patterns+lines+focus+templates"),
        ("runes", "30", "0", "2", "DEFERRED", ""),
        ("motion", "27", "0", "4", "DEFERRED", ""),
        ("marketing", "23", "0", "3", "DEFERRED", "partial brand in batch0"),
    ]
    with gap_path.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

    print(f"Batch 1: {files} SVG files, {len(records)} records → {OUT}")


if __name__ == "__main__":
    main()
