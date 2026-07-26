#!/usr/bin/env python3
"""Generate AAL-Viz Batch 0 visual foundation assets (Hallmark · hand-built SVG).

Deterministic engineering glyphs — stroke grammar matches design-system icon family:
24×24 viewBox, stroke 1.5, round caps/joins, currentColor, no baked glow.

Authority: visual identity / projection-only. No production activation.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "design-system" / "aal-viz"
PRODUCER = "GROK+HALLMARK"
SCHEMA = "AALVizAssetManifest.v1"

# Canonical dark grammar (presentation only; monochrome uses currentColor)
CYAN = "#00D4F5"
VIOLET = "#A78BFA"
AMBER = "#F59E0B"
TEAL = "#2DD4BF"
INK = "#E8EEF7"
PAPER = "#0B1020"
MUTED = "#64748B"
ERROR = "#EF4444"
OK = "#10B981"


def _svg(
    body: str,
    *,
    view: int = 24,
    label: str,
    stroke: str = "currentColor",
    fill: str = "none",
    sw: float = 1.5,
) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view} {view}" '
        f'width="{view}" height="{view}" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" '
        f'role="img" aria-label="{label}">\n'
        f"  <title>{label}</title>\n"
        f"{body}"
        f"</svg>\n"
    )


def write_svg(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ── Brand identity ──────────────────────────────────────────────────────────

def brand_primary_symbol() -> str:
    """Projection-layer sigil: viewport plane + constellation nodes (≠ Abraxas lattice)."""
    body = f"""  <rect width="64" height="64" rx="12" fill="{PAPER}"/>
  <!-- projection plane -->
  <path d="M14 42 L32 18 L50 42 Z" fill="none" stroke="{MUTED}" stroke-width="1.25"/>
  <path d="M18 40 L32 22 L46 40 Z" fill="none" stroke="{CYAN}" stroke-width="1.75"/>
  <!-- observation aperture -->
  <circle cx="32" cy="34" r="5" fill="{PAPER}" stroke="{CYAN}" stroke-width="1.75"/>
  <circle cx="32" cy="34" r="1.8" fill="{CYAN}"/>
  <!-- constellation projection nodes (violet = projection register) -->
  <circle cx="22" cy="28" r="1.6" fill="{VIOLET}"/>
  <circle cx="42" cy="28" r="1.6" fill="{VIOLET}"/>
  <circle cx="32" cy="22" r="1.6" fill="{TEAL}"/>
  <!-- topology links (thin, advisory) -->
  <path d="M22 28 L32 34 M42 28 L32 34 M32 22 L32 34" stroke="{VIOLET}" stroke-width="1" opacity="0.85"/>
"""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" '
        f'aria-label="AAL-Viz primary symbol">\n'
        f"  <title>AAL-Viz</title>\n"
        f"  <desc>Projection-layer sigil: viewport plane and constellation nodes. "
        f"Observation only — no authority or execution.</desc>\n"
        f"{body}</svg>\n"
    )


def brand_favicon() -> str:
    body = f"""  <rect width="32" height="32" rx="6" fill="{PAPER}"/>
  <path d="M7 22 L16 8 L25 22 Z" fill="none" stroke="{CYAN}" stroke-width="1.75" stroke-linejoin="round"/>
  <circle cx="16" cy="17" r="2.5" fill="{PAPER}" stroke="{CYAN}" stroke-width="1.5"/>
  <circle cx="16" cy="17" r="1" fill="{CYAN}"/>
  <circle cx="11" cy="14" r="1" fill="{VIOLET}"/>
  <circle cx="21" cy="14" r="1" fill="{VIOLET}"/>
"""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" role="img" '
        f'aria-label="AAL-Viz favicon">\n  <title>AAL-Viz</title>\n{body}</svg>\n'
    )


def brand_horizontal(theme: str) -> str:
    if theme == "dark":
        bg, ink, accent = PAPER, INK, CYAN
    elif theme == "light":
        bg, ink, accent = "#F4F6FA", "#0F172A", "#0891B2"
    else:  # mono
        bg, ink, accent = "none", "#000000", "#000000"
    mark = f"""  <g transform="translate(8,8)" fill="none" stroke="{accent}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
    <path d="M2 28 L16 6 L30 28 Z"/>
    <circle cx="16" cy="20" r="4" fill="{bg if bg != 'none' else '#fff'}" stroke="{accent}"/>
    <circle cx="16" cy="20" r="1.5" fill="{accent}" stroke="none"/>
    <circle cx="9" cy="15" r="1.2" fill="{VIOLET if theme != 'mono' else accent}" stroke="none"/>
    <circle cx="23" cy="15" r="1.2" fill="{VIOLET if theme != 'mono' else accent}" stroke="none"/>
  </g>"""
    word = f"""  <text x="52" y="36" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="22" font-weight="600"
        letter-spacing="0.12em" fill="{ink}">AAL-VIZ</text>
  <text x="52" y="50" font-family="IBM Plex Mono, ui-monospace, monospace" font-size="8" font-weight="500"
        letter-spacing="0.18em" fill="{MUTED if theme != 'mono' else ink}" opacity="0.85">PROJECTION ONLY</text>"""
    bg_rect = f'  <rect width="220" height="64" rx="10" fill="{bg}"/>\n' if bg != "none" else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 64" role="img" '
        f'aria-label="AAL-Viz horizontal lockup {theme}">\n'
        f"  <title>AAL-Viz {theme}</title>\n{bg_rect}{mark}\n{word}\n</svg>\n"
    )


def brand_compact() -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 32" role="img" '
        f'aria-label="AAL-Viz compact lockup">\n'
        f"  <title>AAL-VIZ</title>\n"
        f'  <rect width="120" height="32" rx="6" fill="{PAPER}"/>\n'
        f'  <g transform="translate(6,4)" fill="none" stroke="{CYAN}" stroke-width="1.5" stroke-linejoin="round">\n'
        f'    <path d="M2 20 L12 4 L22 20 Z"/>\n'
        f'    <circle cx="12" cy="14" r="2.5" fill="{PAPER}"/>\n'
        f"  </g>\n"
        f'  <text x="36" y="21" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" '
        f'font-weight="600" letter-spacing="0.14em" fill="{INK}">AAL-VIZ</text>\n'
        f"</svg>\n"
    )


def brand_cobrand() -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 280 48" role="img" '
        f'aria-label="ABRAXAS / AAL-VIZ co-brand lockup">\n'
        f"  <title>ABRAXAS / AAL-VIZ</title>\n"
        f'  <rect width="280" height="48" rx="8" fill="{PAPER}"/>\n'
        f'  <text x="16" y="30" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="14" '
        f'font-weight="600" letter-spacing="0.16em" fill="{INK}">ABRAXAS</text>\n'
        f'  <text x="108" y="30" font-family="IBM Plex Mono, ui-monospace, monospace" font-size="12" '
        f'fill="{MUTED}">/</text>\n'
        f'  <text x="124" y="30" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="14" '
        f'font-weight="500" letter-spacing="0.12em" fill="{TEAL}">AAL-VIZ</text>\n'
        f'  <text x="200" y="30" font-family="IBM Plex Mono, ui-monospace, monospace" font-size="8" '
        f'letter-spacing="0.1em" fill="{VIOLET}">PROJECTION</text>\n'
        f"</svg>\n"
    )


def brand_watermark() -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 20" role="img" '
        f'aria-label="AAL-VIZ projection-only watermark">\n'
        f"  <title>AAL-VIZ · PROJECTION ONLY</title>\n"
        f'  <text x="0" y="14" font-family="IBM Plex Mono, ui-monospace, monospace" font-size="9" '
        f'font-weight="500" letter-spacing="0.14em" fill="currentColor">'
        f"AAL-VIZ · PROJECTION ONLY</text>\n"
        f"</svg>\n"
    )


def brand_splash() -> str:
    return brand_primary_symbol().replace(
        'aria-label="AAL-Viz primary symbol"',
        'aria-label="AAL-Viz loading splash"',
    )


def brand_social_card() -> str:
    """SVG social card 1200×630 — identity only, no fabricated screenshot."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630" role="img" aria-label="AAL-Viz social preview">
  <title>AAL-Viz · Projection Only</title>
  <rect width="1200" height="630" fill="{PAPER}"/>
  <rect x="0" y="0" width="1200" height="4" fill="{CYAN}"/>
  <!-- large sigil -->
  <g transform="translate(120,180)" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <path d="M40 220 L160 40 L280 220 Z" stroke="{MUTED}" stroke-width="2"/>
    <path d="M60 200 L160 60 L260 200 Z" stroke="{CYAN}" stroke-width="3"/>
    <circle cx="160" cy="150" r="28" fill="{PAPER}" stroke="{CYAN}" stroke-width="3"/>
    <circle cx="160" cy="150" r="10" fill="{CYAN}" stroke="none"/>
    <circle cx="100" cy="110" r="8" fill="{VIOLET}" stroke="none"/>
    <circle cx="220" cy="110" r="8" fill="{VIOLET}" stroke="none"/>
    <circle cx="160" cy="70" r="8" fill="{TEAL}" stroke="none"/>
    <path d="M100 110 L160 150 M220 110 L160 150 M160 70 L160 150" stroke="{VIOLET}" stroke-width="1.5"/>
  </g>
  <text x="480" y="280" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="72" font-weight="600" letter-spacing="0.08em" fill="{INK}">AAL-VIZ</text>
  <text x="480" y="340" font-family="IBM Plex Mono, ui-monospace, monospace" font-size="22" letter-spacing="0.2em" fill="{VIOLET}">PROJECTION ONLY</text>
  <text x="480" y="400" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="20" fill="{MUTED}">Observation · topology · evidence — no execution authority</text>
  <text x="48" y="590" font-family="IBM Plex Mono, ui-monospace, monospace" font-size="14" letter-spacing="0.12em" fill="{MUTED}">ABRAXAS / AAL-VIZ · VISUAL IDENTITY</text>
</svg>
"""


def brand_hero_banner() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 320" width="1280" height="320" role="img" aria-label="AAL-Viz repository hero banner PRODUCT VISION">
  <title>AAL-Viz · PRODUCT VISION</title>
  <rect width="1280" height="320" fill="{PAPER}"/>
  <text x="40" y="36" font-family="IBM Plex Mono, ui-monospace, monospace" font-size="12" letter-spacing="0.2em" fill="{AMBER}">PRODUCT VISION</text>
  <!-- abstract topology field -->
  <g fill="none" stroke="{MUTED}" stroke-width="1" opacity="0.55">
    <path d="M40 200 C200 80, 400 280, 640 160 S1000 60, 1240 200"/>
    <path d="M40 240 C280 120, 520 260, 760 180 S1080 100, 1240 240"/>
  </g>
  <g fill="{CYAN}" opacity="0.9">
    <circle cx="200" cy="160" r="4"/><circle cx="420" cy="200" r="4"/>
    <circle cx="640" cy="140" r="5"/><circle cx="880" cy="180" r="4"/>
    <circle cx="1080" cy="150" r="4"/>
  </g>
  <g fill="{VIOLET}" opacity="0.85">
    <circle cx="320" cy="220" r="3"/><circle cx="760" cy="200" r="3"/><circle cx="980" cy="210" r="3"/>
  </g>
  <text x="40" y="120" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="48" font-weight="600" fill="{INK}">AAL-VIZ</text>
  <text x="40" y="160" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="20" fill="{TEAL}">Projection layer for Abraxas topology, evidence, and operator review</text>
  <text x="40" y="290" font-family="IBM Plex Mono, ui-monospace, monospace" font-size="11" letter-spacing="0.14em" fill="{MUTED}">NOT A LIVE SCREENSHOT · LABELED PRODUCT VISION · ACTIVATION DENIED</text>
</svg>
"""


# ── Authority glyphs — unique shapes independent of color ───────────────────

AuthorityDef = tuple[str, str, Callable[[], str]]  # id, alt, body_fn


def auth_observed() -> str:
    return "  <circle cx=\"12\" cy=\"12\" r=\"7\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"2.5\" fill=\"currentColor\" stroke=\"none\"/>\n"


def auth_inferred() -> str:
    return "  <path d=\"M12 4 L20 18 H4 Z\" fill=\"none\"/>\n  <circle cx=\"12\" cy=\"13\" r=\"1.5\" fill=\"currentColor\" stroke=\"none\"/>\n"


def auth_speculative() -> str:
    return "  <path d=\"M12 3 L14.5 9.5 L21 10 L16 14.5 L17.5 21 L12 17.5 L6.5 21 L8 14.5 L3 10 L9.5 9.5 Z\" fill=\"none\"/>\n"


def auth_shadow() -> str:
    return "  <circle cx=\"10\" cy=\"12\" r=\"6\"/>\n  <path d=\"M14 7 A6 6 0 0 1 14 17\" fill=\"none\"/>\n"


def auth_projection_only() -> str:
    return "  <rect x=\"4\" y=\"6\" width=\"16\" height=\"12\" rx=\"1\"/>\n  <path d=\"M4 15 L8 11 L11 13 L16 8\"/>\n  <path d=\"M8 19 H16\"/>\n"


def auth_not_computable() -> str:
    return "  <rect x=\"5\" y=\"5\" width=\"14\" height=\"14\" rx=\"1\"/>\n  <path d=\"M8 8 L16 16 M16 8 L8 16\"/>\n"


def auth_canary() -> str:
    return "  <path d=\"M12 4 L18 20 H6 Z\"/>\n  <path d=\"M12 10 V14\"/>\n  <circle cx=\"12\" cy=\"17\" r=\"0.8\" fill=\"currentColor\" stroke=\"none\"/>\n"


def auth_forecast() -> str:
    return "  <path d=\"M4 16 C8 16 8 8 12 8 S16 16 20 16\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M17 13 L20 16 L17 19\"/>\n"


def auth_canon_active() -> str:
    return "  <path d=\"M12 3 L19 7 V17 L12 21 L5 17 V7 Z\"/>\n  <path d=\"M9 12 L11 14 L15 10\"/>\n"


def auth_fail_closed() -> str:
    return "  <rect x=\"5\" y=\"5\" width=\"14\" height=\"14\" rx=\"1\"/>\n  <path d=\"M8 12 H16\" stroke-width=\"2\"/>\n"


def auth_blocked() -> str:
    return "  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n  <path d=\"M8 8 L16 16\" stroke-width=\"2\"/>\n"


def auth_verified() -> str:
    return "  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n  <path d=\"M8 12 L11 15 L16 9\"/>\n"


def auth_partial() -> str:
    return "  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n  <path d=\"M12 4 A8 8 0 0 1 12 20\" fill=\"none\"/>\n  <path d=\"M12 4 A8 8 0 0 0 12 20\" stroke-dasharray=\"2 2\"/>\n"


def auth_degraded() -> str:
    return "  <path d=\"M4 18 L12 4 L20 18 Z\"/>\n  <path d=\"M12 9 V13\"/>\n  <circle cx=\"12\" cy=\"15.5\" r=\"0.7\" fill=\"currentColor\" stroke=\"none\"/>\n"


def auth_unknown() -> str:
    return "  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n  <path d=\"M9.5 9.5 A2.5 2.5 0 1 1 12 12 V14\"/>\n  <circle cx=\"12\" cy=\"17\" r=\"0.7\" fill=\"currentColor\" stroke=\"none\"/>\n"


def auth_stale() -> str:
    return "  <circle cx=\"12\" cy=\"12\" r=\"7\"/>\n  <path d=\"M12 8 V12 L15 14\"/>\n  <path d=\"M17 5 L19 7 M5 17 L7 19\" opacity=\"0.7\"/>\n"


def auth_superseded() -> str:
    return "  <path d=\"M7 7 L17 7 L17 17\"/>\n  <path d=\"M7 7 L7 17 L17 17\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M10 14 L14 10\"/>\n"


def auth_archived() -> str:
    return "  <path d=\"M4 8 H20 V10 H4 Z\"/>\n  <path d=\"M6 10 V18 H18 V10\"/>\n  <path d=\"M10 13 H14\"/>\n"


def auth_held() -> str:
    return "  <rect x=\"7\" y=\"10\" width=\"10\" height=\"8\" rx=\"1\"/>\n  <path d=\"M9 10 V8 A3 3 0 0 1 15 8 V10\"/>\n  <circle cx=\"12\" cy=\"14\" r=\"1\" fill=\"currentColor\" stroke=\"none\"/>\n"


def auth_operator_review() -> str:
    return "  <circle cx=\"12\" cy=\"8\" r=\"3\"/>\n  <path d=\"M6 20 C6 15 18 15 18 20\"/>\n  <path d=\"M16 6 L20 6 L20 10\"/>\n"


def auth_manual_only() -> str:
    return "  <path d=\"M8 20 C8 12 10 8 12 4 C14 8 16 12 16 20\"/>\n  <path d=\"M8 16 H16\"/>\n"


def auth_read_only() -> str:
    return "  <path d=\"M2 12 C5 7 9 5 12 5 S19 7 22 12 C19 17 15 19 12 19 S5 17 2 12 Z\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"2.5\"/>\n  <path d=\"M4 20 L20 4\" opacity=\"0.5\"/>\n"


def auth_copy_only() -> str:
    return "  <rect x=\"8\" y=\"8\" width=\"10\" height=\"12\" rx=\"1\"/>\n  <path d=\"M6 16 V6 H16\"/>\n"


def auth_no_authority() -> str:
    return "  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n  <path d=\"M12 7 V13\"/>\n  <circle cx=\"12\" cy=\"16\" r=\"0.8\" fill=\"currentColor\" stroke=\"none\"/>\n  <path d=\"M5 5 L19 19\" opacity=\"0.4\"/>\n"


def auth_source_missing() -> str:
    return "  <ellipse cx=\"12\" cy=\"12\" rx=\"8\" ry=\"5\"/>\n  <path d=\"M12 7 V17\"/>\n  <path d=\"M9 12 H15\" stroke-dasharray=\"2 2\"/>\n"


def auth_provenance_missing() -> str:
    return "  <path d=\"M8 6 H16 V18 H8 Z\"/>\n  <path d=\"M10 10 H14 M10 13 H14\"/>\n  <path d=\"M18 8 L21 11 L18 14\" stroke-dasharray=\"1.5 1.5\"/>\n"


def auth_validator_missing() -> str:
    return "  <path d=\"M12 3 L20 7 V13 C20 17 16 20 12 21 C8 20 4 17 4 13 V7 Z\"/>\n  <path d=\"M9 12 H15\" stroke-dasharray=\"2 2\"/>\n"


def auth_schema_invalid() -> str:
    return "  <path d=\"M5 6 H19 V10 H5 Z\"/>\n  <path d=\"M5 12 H19 V18 H5 Z\"/>\n  <path d=\"M8 8 L16 16\"/>\n"


def auth_conflict() -> str:
    return "  <path d=\"M8 8 L16 16 M16 8 L8 16\" stroke-width=\"2\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n"


def auth_drift_detected() -> str:
    return "  <path d=\"M4 16 L8 10 L12 14 L16 6 L20 12\"/>\n  <path d=\"M4 18 H20\" stroke-dasharray=\"2 2\" opacity=\"0.6\"/>\n"


AUTHORITY: list[AuthorityDef] = [
    ("OBSERVED", "Observed evidence status", auth_observed),
    ("INFERRED", "Inferred status", auth_inferred),
    ("SPECULATIVE", "Speculative status", auth_speculative),
    ("SHADOW", "Shadow lane status", auth_shadow),
    ("PROJECTION_ONLY", "Projection-only status", auth_projection_only),
    ("NOT_COMPUTABLE", "Not computable status", auth_not_computable),
    ("CANARY", "Canary status", auth_canary),
    ("FORECAST", "Forecast status", auth_forecast),
    ("CANON_ACTIVE", "Canon active status", auth_canon_active),
    ("FAIL_CLOSED", "Fail-closed status", auth_fail_closed),
    ("BLOCKED", "Blocked status", auth_blocked),
    ("VERIFIED", "Verified status", auth_verified),
    ("PARTIAL", "Partial status", auth_partial),
    ("DEGRADED", "Degraded status", auth_degraded),
    ("UNKNOWN", "Unknown status", auth_unknown),
    ("STALE", "Stale status", auth_stale),
    ("SUPERSEDED", "Superseded status", auth_superseded),
    ("ARCHIVED", "Archived status", auth_archived),
    ("HELD", "Held status", auth_held),
    ("OPERATOR_REVIEW", "Operator review status", auth_operator_review),
    ("MANUAL_ONLY", "Manual-only status", auth_manual_only),
    ("READ_ONLY", "Read-only status", auth_read_only),
    ("COPY_ONLY", "Copy-only status", auth_copy_only),
    ("NO_AUTHORITY", "No authority status", auth_no_authority),
    ("SOURCE_MISSING", "Source missing status", auth_source_missing),
    ("PROVENANCE_MISSING", "Provenance missing status", auth_provenance_missing),
    ("VALIDATOR_MISSING", "Validator missing status", auth_validator_missing),
    ("SCHEMA_INVALID", "Schema invalid status", auth_schema_invalid),
    ("CONFLICT", "Conflict status", auth_conflict),
    ("DRIFT_DETECTED", "Drift detected status", auth_drift_detected),
]


# ── Activation lanes ────────────────────────────────────────────────────────

def act_local_dev() -> str:
    return "  <rect x=\"4\" y=\"6\" width=\"16\" height=\"12\" rx=\"1\"/>\n  <path d=\"M8 10 H16 M8 14 H12\"/>\n  <circle cx=\"18\" cy=\"6\" r=\"2\" fill=\"currentColor\" stroke=\"none\"/>\n"


def act_sandbox() -> str:
    return "  <rect x=\"5\" y=\"5\" width=\"14\" height=\"14\" rx=\"2\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M9 12 H15 M12 9 V15\"/>\n"


def act_internal_canary() -> str:
    return "  <path d=\"M12 4 L18 20 H6 Z\"/>\n  <path d=\"M12 10 V13\"/>\n  <path d=\"M4 20 H20\" opacity=\"0.4\"/>\n"


def act_external_production() -> str:
    return "  <path d=\"M4 18 V10 L12 4 L20 10 V18\"/>\n  <path d=\"M9 18 V13 H15 V18\"/>\n"


def act_external_production_locked() -> str:
    return act_external_production() + "  <path d=\"M14 8 V6 A2 2 0 0 1 18 6 V8 H14 Z\" transform=\"translate(-2,6)\"/>\n  <rect x=\"12\" y=\"14\" width=\"6\" height=\"4\" rx=\"0.5\"/>\n"


def act_reversible() -> str:
    return "  <path d=\"M7 8 A6 6 0 1 1 7 16\"/>\n  <path d=\"M7 5 V8 H10\"/>\n  <path d=\"M17 16 A6 6 0 1 1 17 8\"/>\n  <path d=\"M17 19 V16 H14\"/>\n"


def act_rollback_available() -> str:
    return "  <path d=\"M8 12 H18\"/>\n  <path d=\"M11 9 L8 12 L11 15\"/>\n  <path d=\"M18 8 V16\"/>\n"


def act_rollback_missing() -> str:
    return "  <path d=\"M8 12 H16\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M11 9 L8 12 L11 15\" opacity=\"0.5\"/>\n  <path d=\"M17 9 L19 15 M19 9 L17 15\"/>\n"


def act_bounded_credentials() -> str:
    return "  <rect x=\"5\" y=\"10\" width=\"14\" height=\"8\" rx=\"1\"/>\n  <path d=\"M8 10 V8 A4 4 0 0 1 16 8 V10\"/>\n  <path d=\"M9 14 H15\"/>\n"


def act_production_credentials() -> str:
    return "  <rect x=\"5\" y=\"10\" width=\"14\" height=\"8\" rx=\"1\"/>\n  <path d=\"M8 10 V8 A4 4 0 0 1 16 8 V10\"/>\n  <path d=\"M12 13 V15\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"0.8\" fill=\"currentColor\" stroke=\"none\"/>\n"


def act_isolated() -> str:
    return "  <circle cx=\"12\" cy=\"12\" r=\"5\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"9\" stroke-dasharray=\"2 2\"/>\n"


def act_network_disabled() -> str:
    return "  <path d=\"M4 12 H20\"/>\n  <path d=\"M7 8 A6 6 0 0 1 17 8\"/>\n  <path d=\"M7 16 A6 6 0 0 0 17 16\"/>\n  <path d=\"M6 6 L18 18\"/>\n"


def act_external_write_disabled() -> str:
    return "  <path d=\"M4 12 H12\"/>\n  <path d=\"M9 9 L12 12 L9 15\"/>\n  <rect x=\"14\" y=\"8\" width=\"6\" height=\"8\" rx=\"1\"/>\n  <path d=\"M15 10 L19 14 M19 10 L15 14\"/>\n"


def act_mutation_disabled() -> str:
    return "  <path d=\"M12 4 V20 M4 12 H20\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n  <path d=\"M7 7 L17 17\"/>\n"


def act_canon_mutation_disabled() -> str:
    return "  <path d=\"M12 3 L19 7 V17 L12 21 L5 17 V7 Z\"/>\n  <path d=\"M8 12 H16\"/>\n  <path d=\"M9 9 L15 15\" opacity=\"0.7\"/>\n"


def act_forecast_routing_disabled() -> str:
    return "  <path d=\"M4 16 C8 16 8 8 12 8 S16 16 20 16\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M8 8 L16 16\"/>\n"


ACTIVATION: list[AuthorityDef] = [
    ("LOCAL_DEV", "Local development lane", act_local_dev),
    ("SANDBOX", "Sandbox lane", act_sandbox),
    ("INTERNAL_CANARY", "Internal canary lane", act_internal_canary),
    ("EXTERNAL_PRODUCTION", "External production lane", act_external_production),
    ("EXTERNAL_PRODUCTION_LOCKED", "External production locked", act_external_production_locked),
    ("REVERSIBLE", "Reversible operation", act_reversible),
    ("ROLLBACK_AVAILABLE", "Rollback available", act_rollback_available),
    ("ROLLBACK_MISSING", "Rollback missing", act_rollback_missing),
    ("BOUNDED_CREDENTIALS", "Bounded credentials", act_bounded_credentials),
    ("PRODUCTION_CREDENTIALS", "Production credentials", act_production_credentials),
    ("ISOLATED", "Isolated environment", act_isolated),
    ("NETWORK_DISABLED", "Network disabled", act_network_disabled),
    ("EXTERNAL_WRITE_DISABLED", "External write disabled", act_external_write_disabled),
    ("MUTATION_DISABLED", "Mutation disabled", act_mutation_disabled),
    ("CANON_MUTATION_DISABLED", "Canon mutation disabled", act_canon_mutation_disabled),
    ("FORECAST_ROUTING_DISABLED", "Forecast routing disabled", act_forecast_routing_disabled),
]


# ── Navigation ──────────────────────────────────────────────────────────────

NAV: list[AuthorityDef] = [
    ("overview", "Overview", lambda: "  <rect x=\"4\" y=\"4\" width=\"7\" height=\"7\" rx=\"1\"/>\n  <rect x=\"13\" y=\"4\" width=\"7\" height=\"7\" rx=\"1\"/>\n  <rect x=\"4\" y=\"13\" width=\"7\" height=\"7\" rx=\"1\"/>\n  <rect x=\"13\" y=\"13\" width=\"7\" height=\"7\" rx=\"1\"/>\n"),
    ("system_spine", "System spine", lambda: "  <path d=\"M12 3 V21\"/>\n  <circle cx=\"12\" cy=\"6\" r=\"2\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"2\"/>\n  <circle cx=\"12\" cy=\"18\" r=\"2\"/>\n  <path d=\"M12 8 H16 M12 14 H8\"/>\n"),
    ("topology", "Topology", lambda: "  <circle cx=\"7\" cy=\"8\" r=\"2.5\"/>\n  <circle cx=\"17\" cy=\"8\" r=\"2.5\"/>\n  <circle cx=\"12\" cy=\"17\" r=\"2.5\"/>\n  <path d=\"M9 9 L15 9 M8.5 10 L11 15 M15.5 10 L13 15\"/>\n"),
    ("constellation", "Constellation", lambda: "  <circle cx=\"6\" cy=\"8\" r=\"1.5\" fill=\"currentColor\" stroke=\"none\"/>\n  <circle cx=\"14\" cy=\"6\" r=\"1.5\" fill=\"currentColor\" stroke=\"none\"/>\n  <circle cx=\"18\" cy=\"14\" r=\"1.5\" fill=\"currentColor\" stroke=\"none\"/>\n  <circle cx=\"8\" cy=\"16\" r=\"1.5\" fill=\"currentColor\" stroke=\"none\"/>\n  <path d=\"M6 8 L14 6 L18 14 L8 16 Z\" opacity=\"0.7\"/>\n"),
    ("trace", "Trace", lambda: "  <path d=\"M4 18 C8 18 8 6 12 6 S16 18 20 18\"/>\n  <circle cx=\"12\" cy=\"6\" r=\"1.5\" fill=\"currentColor\" stroke=\"none\"/>\n"),
    ("timeline", "Timeline", lambda: "  <path d=\"M4 12 H20\"/>\n  <circle cx=\"7\" cy=\"12\" r=\"2\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"2\"/>\n  <circle cx=\"17\" cy=\"12\" r=\"2\"/>\n"),
    ("weather", "Signal weather", lambda: "  <path d=\"M8 14 A4 4 0 1 1 14 10 A3 3 0 1 1 16 16 H8 Z\"/>\n"),
    ("evidence", "Evidence", lambda: "  <path d=\"M8 4 H16 L20 8 V20 H8 Z\"/>\n  <path d=\"M16 4 V8 H20\"/>\n  <path d=\"M11 12 H17 M11 15 H15\"/>\n"),
    ("provenance", "Provenance", lambda: "  <path d=\"M6 18 V8 L12 4 L18 8 V18\"/>\n  <path d=\"M9 18 V12 H15 V18\"/>\n  <path d=\"M12 8 V12\"/>\n"),
    ("receipts", "Receipts", lambda: "  <rect x=\"6\" y=\"4\" width=\"12\" height=\"16\" rx=\"1\"/>\n  <path d=\"M9 9 H15 M9 12 H15 M9 15 H13\"/>\n"),
    ("ledger", "Ledger", lambda: "  <path d=\"M5 5 H19 V19 H5 Z\"/>\n  <path d=\"M5 9 H19 M5 13 H19 M5 17 H19 M9 5 V19\"/>\n"),
    ("artifact_registry", "Artifact registry", lambda: "  <rect x=\"4\" y=\"6\" width=\"16\" height=\"12\" rx=\"1\"/>\n  <path d=\"M8 6 V18 M12 6 V18 M16 6 V18\"/>\n"),
    ("belief_graph", "Belief graph", lambda: "  <circle cx=\"8\" cy=\"10\" r=\"3\"/>\n  <circle cx=\"16\" cy=\"10\" r=\"3\"/>\n  <circle cx=\"12\" cy=\"17\" r=\"3\"/>\n  <path d=\"M10.5 11.5 L10.5 15 M13.5 11.5 L13.5 15\"/>\n"),
    ("oracle", "Oracle", lambda: "  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"3\"/>\n  <path d=\"M12 4 V7 M12 17 V20 M4 12 H7 M17 12 H20\"/>\n"),
    ("yggdrasil", "YGGDRASIL router", lambda: "  <path d=\"M12 3 V21\"/>\n  <path d=\"M12 8 L6 14 M12 8 L18 14 M12 14 L7 20 M12 14 L17 20\"/>\n  <circle cx=\"12\" cy=\"8\" r=\"1.5\" fill=\"currentColor\" stroke=\"none\"/>\n"),
    ("runtime", "Runtime", lambda: "  <rect x=\"4\" y=\"5\" width=\"16\" height=\"14\" rx=\"1\"/>\n  <path d=\"M8 9 L11 12 L8 15\"/>\n  <path d=\"M13 15 H17\"/>\n"),
    ("validation", "Validation", lambda: "  <path d=\"M12 3 L20 7 V13 C20 17 12 21 12 21 S4 17 4 13 V7 Z\"/>\n  <path d=\"M9 12 L11 14 L15 10\"/>\n"),
    ("governance", "Governance", lambda: "  <path d=\"M4 10 L12 4 L20 10 V20 H4 Z\"/>\n  <path d=\"M10 20 V14 H14 V20\"/>\n"),
    ("operator_queue", "Operator queue", lambda: "  <path d=\"M6 7 H18 M6 12 H18 M6 17 H14\"/>\n  <circle cx=\"18\" cy=\"17\" r=\"2\"/>\n"),
    ("review", "Review", lambda: "  <path d=\"M5 5 H15 L19 9 V19 H5 Z\"/>\n  <path d=\"M15 5 V9 H19\"/>\n  <path d=\"M9 13 L11 15 L15 11\"/>\n"),
    ("decisions", "Decisions", lambda: "  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n  <path d=\"M12 8 V12 L15 14\"/>\n  <path d=\"M8 8 L10 10 M16 8 L14 10\" opacity=\"0.5\"/>\n"),
    ("outcomes", "Outcomes", lambda: "  <path d=\"M5 16 L10 10 L14 13 L19 6\"/>\n  <path d=\"M16 6 H19 V9\"/>\n"),
    ("providers", "Providers", lambda: "  <rect x=\"4\" y=\"8\" width=\"6\" height=\"8\" rx=\"1\"/>\n  <rect x=\"14\" y=\"8\" width=\"6\" height=\"8\" rx=\"1\"/>\n  <path d=\"M10 12 H14\"/>\n"),
    ("reliability", "Reliability", lambda: "  <path d=\"M4 16 L8 10 L12 14 L16 6 L20 10\"/>\n  <path d=\"M4 18 H20\" opacity=\"0.4\"/>\n"),
    ("analytics", "Analytics", lambda: "  <path d=\"M5 19 V11 M10 19 V7 M15 19 V13 M20 19 V9\"/>\n"),
    ("narrative", "Narrative", lambda: "  <path d=\"M6 6 H18 V18 H6 Z\"/>\n  <path d=\"M9 10 H15 M9 13 H13\"/>\n"),
    ("settings", "Settings", lambda: "  <circle cx=\"12\" cy=\"12\" r=\"3\"/>\n  <path d=\"M12 3 V6 M12 18 V21 M3 12 H6 M18 12 H21 M5.5 5.5 L7.5 7.5 M16.5 16.5 L18.5 18.5 M18.5 5.5 L16.5 7.5 M7.5 16.5 L5.5 18.5\"/>\n"),
    ("accessibility", "Accessibility", lambda: "  <circle cx=\"12\" cy=\"5\" r=\"2\"/>\n  <path d=\"M8 10 H16 M12 10 V16 M9 20 L12 16 L15 20\"/>\n"),
    ("export", "Export", lambda: "  <path d=\"M12 4 V14 M9 11 L12 14 L15 11\"/>\n  <path d=\"M5 17 V20 H19 V17\"/>\n"),
    ("copy_packet", "Copy packet", lambda: "  <rect x=\"8\" y=\"6\" width=\"10\" height=\"14\" rx=\"1\"/>\n  <path d=\"M6 16 V4 H16\"/>\n  <path d=\"M11 11 H15 M11 14 H14\"/>\n"),
    ("search", "Search", lambda: "  <circle cx=\"11\" cy=\"11\" r=\"6\"/>\n  <path d=\"M16 16 L20 20\"/>\n"),
    ("filter", "Filter", lambda: "  <path d=\"M4 6 H20 L14 12 V18 L10 20 V12 Z\"/>\n"),
    ("compare", "Compare", lambda: "  <rect x=\"3\" y=\"6\" width=\"8\" height=\"12\" rx=\"1\"/>\n  <rect x=\"13\" y=\"6\" width=\"8\" height=\"12\" rx=\"1\"/>\n  <path d=\"M11 12 H13\"/>\n"),
    ("inspect", "Inspect", lambda: "  <circle cx=\"10\" cy=\"10\" r=\"5\"/>\n  <path d=\"M14 14 L19 19\"/>\n  <path d=\"M8 10 H12 M10 8 V12\"/>\n"),
    ("expand", "Expand", lambda: "  <path d=\"M9 4 H4 V9 M15 4 H20 V9 M4 15 V20 H9 M20 15 V20 H15\"/>\n"),
    ("collapse", "Collapse", lambda: "  <path d=\"M4 9 H9 V4 M15 4 V9 H20 M20 15 H15 V20 M9 20 V15 H4\"/>\n"),
    ("refresh", "Refresh", lambda: "  <path d=\"M20 12 A8 8 0 1 1 16 5\"/>\n  <path d=\"M20 5 V12 H13\"/>\n"),
    ("replay", "Replay", lambda: "  <path d=\"M7 7 V17 L16 12 Z\"/>\n  <path d=\"M17 7 V17\"/>\n"),
    ("archive", "Archive", lambda: "  <path d=\"M4 7 H20 V9 H4 Z\"/>\n  <path d=\"M6 9 V18 H18 V9\"/>\n"),
    ("source_link", "Source link", lambda: "  <path d=\"M10 14 L8 16 A3 3 0 0 1 4 12 L6 10\"/>\n  <path d=\"M14 10 L16 8 A3 3 0 0 1 20 12 L18 14\"/>\n  <path d=\"M9 12 H15\"/>\n"),
    ("notion_reference", "Notion reference", lambda: "  <rect x=\"5\" y=\"4\" width=\"14\" height=\"16\" rx=\"1\"/>\n  <path d=\"M9 8 V16 M9 8 H12 C14 8 14 12 12 12 H9\"/>\n"),
    ("github_reference", "GitHub reference", lambda: "  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n  <path d=\"M9 18 C9 15 9 14 10 13 C8 13 7 11 7 10 C7 9 7.5 8 8.5 8 C8 7 8 6 8.5 5.5 C10 6 11 6.5 12 6.5 S14 6 15.5 5.5 C16 6 16 7 15.5 8 C16.5 8 17 9 17 10 C17 11 16 13 14 13 C15 14 15 15 15 18\"/>\n"),
    ("documentation", "Documentation", lambda: "  <path d=\"M6 4 H14 L18 8 V20 H6 Z\"/>\n  <path d=\"M14 4 V8 H18\"/>\n  <path d=\"M9 12 H15 M9 15 H13\"/>\n"),
    ("help", "Help", lambda: "  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n  <path d=\"M9.5 9.5 A2.5 2.5 0 1 1 12 12 V14\"/>\n  <circle cx=\"12\" cy=\"17\" r=\"0.7\" fill=\"currentColor\" stroke=\"none\"/>\n"),
]


# ── Subsystem glyphs ────────────────────────────────────────────────────────

SUBSYSTEM: list[AuthorityDef] = [
    ("abraxas_kernel", "Abraxas kernel", lambda: "  <path d=\"M12 3 L19 7 V17 L12 21 L5 17 V7 Z\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"2.5\"/>\n"),
    ("aal_viz_projection_layer", "AAL-Viz projection layer", lambda: "  <path d=\"M5 18 L12 5 L19 18 Z\"/>\n  <circle cx=\"12\" cy=\"13\" r=\"2\"/>\n  <circle cx=\"9\" cy=\"11\" r=\"1\" fill=\"currentColor\" stroke=\"none\"/>\n  <circle cx=\"15\" cy=\"11\" r=\"1\" fill=\"currentColor\" stroke=\"none\"/>\n"),
    ("oracle_signal_layer", "Oracle signal layer", lambda: "  <path d=\"M4 12 H8 M16 12 H20\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"4\"/>\n  <path d=\"M12 4 V7 M12 17 V20\"/>\n"),
    ("belief_graph", "Belief graph subsystem", lambda: "  <circle cx=\"7\" cy=\"9\" r=\"2.5\"/>\n  <circle cx=\"17\" cy=\"9\" r=\"2.5\"/>\n  <circle cx=\"12\" cy=\"17\" r=\"2.5\"/>\n  <path d=\"M9 10 L11 15 M15 10 L13 15 M9.5 9 H14.5\"/>\n"),
    ("evidence_memory", "Evidence memory", lambda: "  <ellipse cx=\"12\" cy=\"12\" rx=\"8\" ry=\"5\"/>\n  <path d=\"M8 12 H16\"/>\n"),
    ("compositional_memory_connector", "Compositional memory connector", lambda: "  <rect x=\"3\" y=\"8\" width=\"6\" height=\"8\" rx=\"1\"/>\n  <rect x=\"15\" y=\"8\" width=\"6\" height=\"8\" rx=\"1\"/>\n  <path d=\"M9 12 H15\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"1.5\"/>\n"),
    ("yggdrasil_router", "YGGDRASIL router", lambda: "  <path d=\"M12 2 V22\"/>\n  <path d=\"M12 6 L5 12 M12 6 L19 12 M12 12 L6 20 M12 12 L18 20\"/>\n"),
    ("canon_spine", "Canon spine", lambda: "  <path d=\"M12 3 V21\" stroke-width=\"2\"/>\n  <path d=\"M8 7 H16 M8 12 H16 M8 17 H16\"/>\n"),
    ("continuity_spine", "Continuity spine", lambda: "  <path d=\"M4 12 C8 6 16 18 20 12\"/>\n  <path d=\"M4 16 C8 10 16 22 20 16\" opacity=\"0.5\"/>\n"),
    ("artifact_registry", "Artifact registry subsystem", lambda: "  <rect x=\"5\" y=\"4\" width=\"14\" height=\"16\" rx=\"1\"/>\n  <path d=\"M8 8 H16 M8 12 H16 M8 16 H12\"/>\n"),
    ("validation_service", "Validation service", lambda: "  <path d=\"M12 3 L20 7 V13 C20 17 12 21 12 21 S4 17 4 13 V7 Z\"/>\n  <path d=\"M9 12 L11 14 L15 10\"/>\n"),
    ("governance_service", "Governance service", lambda: "  <circle cx=\"12\" cy=\"8\" r=\"3\"/>\n  <path d=\"M6 20 C6 14 18 14 18 20\"/>\n  <path d=\"M4 10 H8 M16 10 H20\"/>\n"),
    ("operator_surface", "Operator surface", lambda: "  <rect x=\"3\" y=\"5\" width=\"18\" height=\"14\" rx=\"1\"/>\n  <path d=\"M7 10 H17 M7 14 H13\"/>\n"),
    ("runtime", "Runtime subsystem", lambda: "  <rect x=\"4\" y=\"6\" width=\"16\" height=\"12\" rx=\"1\"/>\n  <path d=\"M8 12 L11 9 L14 14 L16 11\"/>\n"),
    ("ingest", "Ingest", lambda: "  <path d=\"M12 4 V14 M9 11 L12 14 L15 11\"/>\n  <path d=\"M5 18 H19\"/>\n"),
    ("provider_adapter", "Provider adapter", lambda: "  <rect x=\"3\" y=\"9\" width=\"7\" height=\"6\" rx=\"1\"/>\n  <rect x=\"14\" y=\"9\" width=\"7\" height=\"6\" rx=\"1\"/>\n  <path d=\"M10 12 H14\"/>\n"),
    ("storage", "Storage", lambda: "  <ellipse cx=\"12\" cy=\"7\" rx=\"7\" ry=\"3\"/>\n  <path d=\"M5 7 V17 C5 19 19 19 19 17 V7\"/>\n"),
    ("observability", "Observability", lambda: "  <circle cx=\"12\" cy=\"12\" r=\"3\"/>\n  <path d=\"M12 3 V7 M12 17 V21 M3 12 H7 M17 12 H21\"/>\n"),
    ("replay", "Replay subsystem", lambda: "  <path d=\"M6 6 V18 L15 12 Z\"/>\n  <path d=\"M17 6 V18\"/>\n"),
    ("audit", "Audit", lambda: "  <path d=\"M8 4 H16 L20 8 V20 H8 Z\"/>\n  <path d=\"M11 12 L13 14 L17 10\"/>\n"),
    ("forecast_lane", "Forecast lane", lambda: "  <path d=\"M4 16 C9 16 9 8 14 8\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M14 5 V11 M11 8 H17\"/>\n"),
    ("shadow_lane", "Shadow lane", lambda: "  <path d=\"M6 6 H14 V18 H6 Z\"/>\n  <path d=\"M14 8 H18 V18 H10\" opacity=\"0.5\"/>\n"),
    ("projection_lane", "Projection lane", lambda: "  <rect x=\"4\" y=\"7\" width=\"16\" height=\"10\" rx=\"1\"/>\n  <path d=\"M7 14 L10 10 L13 12 L17 8\"/>\n"),
    ("authority_lane", "Authority lane", lambda: "  <path d=\"M12 3 L19 20 H5 Z\"/>\n  <path d=\"M12 10 V14\"/>\n  <circle cx=\"12\" cy=\"16.5\" r=\"0.7\" fill=\"currentColor\" stroke=\"none\"/>\n"),
]


# ── Graph primitives ────────────────────────────────────────────────────────

NODE_SHAPES: list[tuple[str, str, str]] = [
    # id, alt, body
    ("canonical_state", "Canonical-state node", "  <rect x=\"4\" y=\"4\" width=\"16\" height=\"16\" rx=\"2\"/>\n"),
    ("advisory", "Advisory node", "  <rect x=\"4\" y=\"4\" width=\"16\" height=\"16\" rx=\"2\" stroke-dasharray=\"3 2\"/>\n"),
    ("shadow", "Shadow node", "  <rect x=\"5\" y=\"5\" width=\"14\" height=\"14\" rx=\"2\" opacity=\"0.85\"/>\n  <rect x=\"7\" y=\"7\" width=\"14\" height=\"14\" rx=\"2\" opacity=\"0.35\"/>\n"),
    ("projection", "Projection node", "  <path d=\"M4 18 L12 4 L20 18 Z\"/>\n"),
    ("forecast", "Forecast node", "  <path d=\"M12 4 L20 12 L12 20 L4 12 Z\" stroke-dasharray=\"2 2\"/>\n"),
    ("operator", "Operator node", "  <rect x=\"4\" y=\"4\" width=\"16\" height=\"16\" rx=\"1\"/>\n  <path d=\"M8 12 H16 M12 8 V16\"/>\n"),
    ("external_source", "External-source node", "  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n  <path d=\"M12 6 V12 H17\"/>\n"),
    ("provider", "Provider node", "  <rect x=\"5\" y=\"7\" width=\"14\" height=\"10\" rx=\"3\"/>\n"),
    ("evidence", "Evidence node", "  <path d=\"M8 4 H15 L20 9 V20 H8 Z\"/>\n"),
    ("artifact", "Artifact node", "  <rect x=\"6\" y=\"5\" width=\"12\" height=\"14\" rx=\"1\"/>\n  <path d=\"M9 9 H15 M9 12 H15\"/>\n"),
    ("receipt", "Receipt node", "  <rect x=\"6\" y=\"4\" width=\"12\" height=\"16\" rx=\"1\"/>\n  <path d=\"M9 9 H15 M9 13 H13\"/>\n  <path d=\"M9 17 L11 18 L15 15\"/>\n"),
    ("decision", "Decision node", "  <path d=\"M12 3 L21 12 L12 21 L3 12 Z\"/>\n"),
    ("gate", "Gate node", "  <path d=\"M12 3 L20 7 V17 L12 21 L4 17 V7 Z\"/>\n"),
    ("blocker", "Blocker node", "  <circle cx=\"12\" cy=\"12\" r=\"8\"/>\n  <path d=\"M8 8 L16 16\" stroke-width=\"2\"/>\n"),
    ("missing", "Missing node", "  <rect x=\"4\" y=\"4\" width=\"16\" height=\"16\" rx=\"2\" stroke-dasharray=\"2 3\"/>\n  <path d=\"M9 9 L15 15 M15 9 L9 15\" opacity=\"0.6\"/>\n"),
    ("conflict", "Conflict node", "  <path d=\"M12 3 L20 20 H4 Z\"/>\n  <path d=\"M12 9 V13\"/>\n  <circle cx=\"12\" cy=\"16\" r=\"0.8\" fill=\"currentColor\" stroke=\"none\"/>\n"),
    ("archived", "Archived node", "  <rect x=\"4\" y=\"6\" width=\"16\" height=\"12\" rx=\"1\" opacity=\"0.7\"/>\n  <path d=\"M8 12 H16\"/>\n"),
    ("cluster", "Cluster node", "  <circle cx=\"9\" cy=\"10\" r=\"3\"/>\n  <circle cx=\"15\" cy=\"10\" r=\"3\"/>\n  <circle cx=\"12\" cy=\"15\" r=\"3\"/>\n"),
    ("aggregate", "Aggregate node", "  <rect x=\"4\" y=\"6\" width=\"16\" height=\"12\" rx=\"2\"/>\n  <path d=\"M8 10 H16 M8 14 H12\"/>\n"),
    ("synthetic_demo", "Synthetic demo node", "  <rect x=\"4\" y=\"4\" width=\"16\" height=\"16\" rx=\"2\" stroke-dasharray=\"1 2\"/>\n  <text x=\"8\" y=\"15\" font-size=\"6\" font-family=\"monospace\" fill=\"currentColor\" stroke=\"none\">DEMO</text>\n"),
]

EDGE_STYLES: list[tuple[str, str, str]] = [
    ("verified_dependency", "Verified dependency edge", "  <path d=\"M3 12 H17\"/>\n  <path d=\"M14 9 L17 12 L14 15\"/>\n  <path d=\"M3 12 H17\" stroke-width=\"2.5\" opacity=\"0.15\"/>\n"),
    ("declared_lineage", "Declared lineage edge", "  <path d=\"M3 12 H17\"/>\n  <path d=\"M14 9 L17 12 L14 15\"/>\n"),
    ("inferred_relationship", "Inferred relationship edge", "  <path d=\"M3 12 H17\" stroke-dasharray=\"3 2\"/>\n  <path d=\"M14 9 L17 12 L14 15\"/>\n"),
    ("projection_relationship", "Projection relationship edge", "  <path d=\"M3 12 H17\" stroke-dasharray=\"1 2\"/>\n  <path d=\"M14 9 L17 12 L14 15\"/>\n"),
    ("candidate_relationship", "Candidate relationship edge", "  <path d=\"M3 12 H17\" stroke-dasharray=\"4 3\" opacity=\"0.7\"/>\n  <path d=\"M14 9 L17 12 L14 15\" opacity=\"0.7\"/>\n"),
    ("blocked_route", "Blocked route edge", "  <path d=\"M3 12 H17\"/>\n  <path d=\"M10 9 L14 15 M14 9 L10 15\"/>\n"),
    ("missing_endpoint", "Missing endpoint edge", "  <path d=\"M3 12 H12\" stroke-dasharray=\"2 2\"/>\n  <circle cx=\"17\" cy=\"12\" r=\"3\" stroke-dasharray=\"1.5 1.5\"/>\n"),
    ("stale_connection", "Stale connection edge", "  <path d=\"M3 12 H17\" opacity=\"0.45\"/>\n  <path d=\"M14 9 L17 12 L14 15\" opacity=\"0.45\"/>\n"),
    ("conflict_connection", "Conflict connection edge", "  <path d=\"M3 9 H17\"/>\n  <path d=\"M3 15 H17\"/>\n  <path d=\"M10 7 L14 17\"/>\n"),
    ("one_way_authority_flow", "One-way authority flow", "  <path d=\"M3 12 H17\" stroke-width=\"2\"/>\n  <path d=\"M14 8 L17 12 L14 16\"/>\n"),
    ("read_only_flow", "Read-only flow", "  <path d=\"M3 12 H17\"/>\n  <path d=\"M14 9 L17 12 L14 15\"/>\n  <circle cx=\"8\" cy=\"12\" r=\"1.5\"/>\n"),
    ("data_flow", "Data flow", "  <path d=\"M3 12 H17\"/>\n  <path d=\"M6 12 H8 M11 12 H13\" stroke-width=\"2.5\"/>\n  <path d=\"M14 9 L17 12 L14 15\"/>\n"),
    ("validation_flow", "Validation flow", "  <path d=\"M3 12 H17\"/>\n  <path d=\"M7 10 L9 12 L7 14\"/>\n  <path d=\"M14 9 L17 12 L14 15\"/>\n"),
    ("provenance_flow", "Provenance flow", "  <path d=\"M3 12 H17\"/>\n  <path d=\"M6 10 V14 M10 10 V14\"/>\n  <path d=\"M14 9 L17 12 L14 15\"/>\n"),
    ("operator_review_route", "Operator-review route", "  <path d=\"M3 12 H17\" stroke-dasharray=\"2 2\"/>\n  <circle cx=\"10\" cy=\"12\" r=\"2\"/>\n  <path d=\"M14 9 L17 12 L14 15\"/>\n"),
    ("forecast_gated_route", "Forecast-gated route", "  <path d=\"M3 12 H10\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M12 3 L20 7 V17 L12 21 L4 17\" transform=\"scale(0.35) translate(22,18)\"/>\n  <path d=\"M14 12 H17\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M14 9 L17 12 L14 15\"/>\n"),
    ("dashed_advisory_link", "Dashed advisory link", "  <path d=\"M3 12 H17\" stroke-dasharray=\"2 3\"/>\n"),
    ("temporal_continuation", "Temporal continuation", "  <path d=\"M3 12 C8 6 12 18 17 12\"/>\n  <path d=\"M14 10 L17 12 L14 14\"/>\n"),
    ("cross_modal_connector", "Cross-modal connector", "  <path d=\"M3 8 H10 V16 H17\"/>\n  <path d=\"M14 13 L17 16 L14 19\"/>\n"),
    ("archived_historical_relation", "Archived historical relation", "  <path d=\"M3 12 H17\" opacity=\"0.4\" stroke-dasharray=\"1 2\"/>\n  <path d=\"M14 9 L17 12 L14 15\" opacity=\"0.4\"/>\n"),
]

PORTS: list[tuple[str, str, str]] = [
    ("input_port", "Input port", "  <circle cx=\"12\" cy=\"12\" r=\"5\"/>\n  <path d=\"M7 12 H2 M9 9 L7 12 L9 15\"/>\n"),
    ("output_port", "Output port", "  <circle cx=\"12\" cy=\"12\" r=\"5\"/>\n  <path d=\"M17 12 H22 M15 9 L17 12 L15 15\"/>\n"),
    ("read_only_port", "Read-only port", "  <circle cx=\"12\" cy=\"12\" r=\"5\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"1.5\"/>\n"),
    ("validation_port", "Validation port", "  <circle cx=\"12\" cy=\"12\" r=\"5\"/>\n  <path d=\"M10 12 L11.5 13.5 L14.5 10\"/>\n"),
    ("blocked_port", "Blocked port", "  <circle cx=\"12\" cy=\"12\" r=\"5\"/>\n  <path d=\"M9 9 L15 15\"/>\n"),
    ("optional_port", "Optional port", "  <circle cx=\"12\" cy=\"12\" r=\"5\" stroke-dasharray=\"2 2\"/>\n"),
    ("multiplex_junction", "Multiplex junction", "  <circle cx=\"12\" cy=\"12\" r=\"3\" fill=\"currentColor\" stroke=\"none\"/>\n  <path d=\"M12 3 V7 M12 17 V21 M3 12 H7 M17 12 H21\"/>\n"),
    ("merge_junction", "Merge junction", "  <path d=\"M4 6 L12 12 L4 18\"/>\n  <path d=\"M12 12 H20\"/>\n"),
    ("split_junction", "Split junction", "  <path d=\"M4 12 H12\"/>\n  <path d=\"M12 12 L20 6 M12 12 L20 18\"/>\n"),
    ("feedback_loop_junction", "Feedback-loop junction", "  <path d=\"M8 12 A4 4 0 1 0 12 8\"/>\n  <path d=\"M12 5 V8 H15\"/>\n  <path d=\"M4 12 H8\"/>\n"),
    ("operator_intervention_junction", "Operator-intervention junction", "  <circle cx=\"12\" cy=\"12\" r=\"4\"/>\n  <path d=\"M12 3 V6 M12 18 V21 M3 12 H6 M18 12 H21\"/>\n  <path d=\"M10 12 H14 M12 10 V14\"/>\n"),
]


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
    batch: str = "0"
    hall_mark: str = "hand-built-svg-tier-B"


def slug(s: str) -> str:
    """snake_case file stems (stable across authority IDs and nav keys)."""
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def emit_icon_family(
    records: list[AssetRecord],
    items: list[AuthorityDef],
    category: str,
    id_prefix: str,
    rel_dir: str,
) -> int:
    n = 0
    for i, (sid, alt, body_fn) in enumerate(items, start=1):
        body = body_fn()
        name = slug(sid)
        rel = f"{rel_dir}/{name}.svg"
        path = OUT / rel
        write_svg(path, _svg(body, label=alt))
        # solid variant (fill-friendly for badges — clone with filled badge plate)
        solid_rel = f"{rel_dir}/{name}.solid.svg"
        solid_body = (
            f'  <rect x="1" y="1" width="22" height="22" rx="4" fill="currentColor" opacity="0.12" stroke="none"/>\n'
            + body
        )
        write_svg(OUT / solid_rel, _svg(solid_body, label=f"{alt} (solid badge)"))
        aid = f"{id_prefix}-{sid.replace('.', '-').upper()}-{i:03d}"
        records.append(
            AssetRecord(
                asset_id=aid,
                name=name,
                category=category,
                semantic_role=sid,
                alt_text=alt,
                source_file=f"design-system/aal-viz/{rel}",
                export_files=[
                    f"design-system/aal-viz/{rel}",
                    f"design-system/aal-viz/{solid_rel}",
                ],
                variants=["outline", "solid", "monochrome"],
            )
        )
        n += 2
    return n


def main() -> None:
    records: list[AssetRecord] = []
    count = 0

    # Brand
    brand_files = {
        "primary-symbol.svg": brand_primary_symbol(),
        "favicon.svg": brand_favicon(),
        "lockup-horizontal-dark.svg": brand_horizontal("dark"),
        "lockup-horizontal-light.svg": brand_horizontal("light"),
        "lockup-horizontal-mono.svg": brand_horizontal("mono"),
        "lockup-compact.svg": brand_compact(),
        "lockup-cobrand.svg": brand_cobrand(),
        "wordmark-watermark.svg": brand_watermark(),
        "splash.svg": brand_splash(),
        "social-preview-1200x630.svg": brand_social_card(),
        "hero-banner-product-vision.svg": brand_hero_banner(),
    }
    for fname, content in brand_files.items():
        rel = f"brand/{fname}"
        write_svg(OUT / rel, content)
        count += 1
        name = fname.replace(".svg", "")
        records.append(
            AssetRecord(
                asset_id=f"AALVIZ-BRAND-{name.upper().replace('-', '_')[:40]}",
                name=name,
                category="identity",
                semantic_role="BRAND",
                authority_implication="NONE",
                alt_text=f"AAL-Viz brand asset {name}",
                source_file=f"design-system/aal-viz/{rel}",
                export_files=[f"design-system/aal-viz/{rel}"],
                sizes=[16, 32, 48, 64, 180, 192, 512] if "favicon" in name or "primary" in name else [24, 64, 256],
                variants=["color", "monochrome"] if "horizontal" in name else ["default"],
            )
        )

    count += emit_icon_family(records, AUTHORITY, "authority_icon", "AALVIZ-ICON-AUTH", "authority")
    count += emit_icon_family(records, ACTIVATION, "activation_icon", "AALVIZ-ICON-ACT", "activation")
    count += emit_icon_family(records, NAV, "navigation_icon", "AALVIZ-ICON-NAV", "navigation")
    count += emit_icon_family(records, SUBSYSTEM, "subsystem_glyph", "AALVIZ-ICON-SYS", "subsystem")

    for i, (sid, alt, body) in enumerate(NODE_SHAPES, start=1):
        rel = f"graph/nodes/{sid}.svg"
        write_svg(OUT / rel, _svg(body, label=alt))
        count += 1
        records.append(
            AssetRecord(
                asset_id=f"AALVIZ-GRAPH-NODE-{sid.upper()}-{i:03d}",
                name=sid,
                category="graph_node",
                semantic_role=sid.upper(),
                alt_text=alt,
                source_file=f"design-system/aal-viz/{rel}",
                export_files=[f"design-system/aal-viz/{rel}"],
            )
        )

    for i, (sid, alt, body) in enumerate(EDGE_STYLES, start=1):
        rel = f"graph/edges/{sid}.svg"
        write_svg(OUT / rel, _svg(body, label=alt))
        count += 1
        records.append(
            AssetRecord(
                asset_id=f"AALVIZ-GRAPH-EDGE-{sid.upper()}-{i:03d}",
                name=sid,
                category="graph_edge",
                semantic_role=sid.upper(),
                alt_text=alt,
                source_file=f"design-system/aal-viz/{rel}",
                export_files=[f"design-system/aal-viz/{rel}"],
            )
        )

    for i, (sid, alt, body) in enumerate(PORTS, start=1):
        rel = f"graph/ports/{sid}.svg"
        write_svg(OUT / rel, _svg(body, label=alt))
        count += 1
        records.append(
            AssetRecord(
                asset_id=f"AALVIZ-GRAPH-PORT-{sid.upper()}-{i:03d}",
                name=sid,
                category="graph_port",
                semantic_role=sid.upper(),
                alt_text=alt,
                source_file=f"design-system/aal-viz/{rel}",
                export_files=[f"design-system/aal-viz/{rel}"],
            )
        )

    # Manifest
    manifest = {
        "schema_version": SCHEMA,
        "name": "aal-viz-visual-foundation",
        "batch": "0",
        "version": "0.1.0",
        "updated": "2026-07-19",
        "hallmark": {
            "genre": "atmospheric-technical",
            "theme": "custom (Abraxas cyan/violet/amber projection grammar)",
            "enrichment": "Tier B hand-built SVG",
            "authority": "projection-only visual identity — no activation",
        },
        "producer_system": PRODUCER,
        "stroke_grammar": {
            "viewBox": "0 0 24 24",
            "stroke_width": 1.5,
            "stroke_linecap": "round",
            "stroke_linejoin": "round",
            "default_stroke": "currentColor",
            "no_baked_glow": True,
        },
        "asset_count": len(records),
        "file_count_approx": count,
        "assets": [asdict(r) for r in records],
    }
    (OUT / "aal_viz_asset_manifest.v1.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    # Icon registry (subset indexes)
    icon_reg = {
        "schema_version": "AALVizIconRegistry.v1",
        "authority": [r.name for r in records if r.category == "authority_icon"],
        "activation": [r.name for r in records if r.category == "activation_icon"],
        "navigation": [r.name for r in records if r.category == "navigation_icon"],
        "subsystem": [r.name for r in records if r.category == "subsystem_glyph"],
        "graph_nodes": [r.name for r in records if r.category == "graph_node"],
        "graph_edges": [r.name for r in records if r.category == "graph_edge"],
        "graph_ports": [r.name for r in records if r.category == "graph_port"],
        "identity": [r.name for r in records if r.category == "identity"],
    }
    (OUT / "AAL_VIZ_ICON_REGISTRY.json").write_text(
        json.dumps(icon_reg, indent=2) + "\n", encoding="utf-8"
    )

    # Gap ledger CSV (Batch 0 closed vs full inventory classes)
    gap_path = OUT / "docs" / "AAL_VIZ_ASSET_GAP_LEDGER.csv"
    gap_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        ("class", "planned", "batch0_shipped", "status", "notes"),
        ("identity", "10", str(len(brand_files)), "PARTIAL", "SVG masters; raster favicon sizes deferred"),
        ("authority", "30", str(len(AUTHORITY)), "SHIPPED_OUTLINE", "outline+solid; lockups deferred"),
        ("activation", "16", str(len(ACTIVATION)), "SHIPPED_OUTLINE", "outline+solid"),
        ("navigation", "44", str(len(NAV)), "SHIPPED_OUTLINE", "core nav complete"),
        ("subsystem_p0", "24", str(len(SUBSYSTEM)), "SHIPPED_OUTLINE", "P0 core; P1 analytical deferred"),
        ("graph_nodes", "20", str(len(NODE_SHAPES)), "SHIPPED", "primitives"),
        ("graph_edges", "20", str(len(EDGE_STYLES)), "SHIPPED", "style tokens as SVG samples"),
        ("graph_ports", "11", str(len(PORTS)), "SHIPPED", ""),
        ("runes", "30", "0", "DEFERRED_BATCH_2", "use existing design-system/runes + new VIZ runes"),
        ("panels", "22", "0", "DEFERRED_BATCH_1", "CSS-first"),
        ("metrics", "44", "0", "DEFERRED_BATCH_1", ""),
        ("weather", "17", "0", "DEFERRED_BATCH_1", ""),
        ("empty_error", "26", "0", "DEFERRED_BATCH_1", ""),
        ("workflow", "30", "0", "DEFERRED_BATCH_1", ""),
        ("a11y_patterns", "19", "0", "DEFERRED_BATCH_1", "currentColor enables mono path"),
        ("motion", "27", "0", "DEFERRED_BATCH_4", ""),
        ("marketing", "23", "0", "DEFERRED_BATCH_3", "hero+social SVG shipped in brand"),
    ]
    with gap_path.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

    print(f"Generated {count} SVG files, {len(records)} manifest records → {OUT}")


if __name__ == "__main__":
    main()
