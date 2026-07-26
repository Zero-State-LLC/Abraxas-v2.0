#!/usr/bin/env python3
"""Generate AAL-Viz Batch 4 — motion, fields, responsive/PWA, marketing (Hallmark · Tier B).

Motion: deterministic CSS tokens + first-frame / reduced-motion SVG states.
Fields: subtle geometric spatial backgrounds (not scenic).
Responsive/PWA: header lockups, mobile chrome, maskable/app icons.
Marketing: honesty-labeled showcases only — no production availability claims.

Projection-only. No fake computation animation.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACK = REPO / "design-system" / "aal-viz"
BATCH = "4"
PRODUCER = "GROK+HALLMARK"

PAPER = "#0B1020"
PANEL = "#121A2A"
RULE = "#243049"
INK = "#E8EEF7"
MUTED = "#64748B"
CYAN = "#00D4F5"
VIOLET = "#A78BFA"
AMBER = "#F59E0B"
TEAL = "#2DD4BF"
GOLD = "#F2C14E"
OK = "#10B981"
ERR = "#EF4444"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


@dataclass
class AssetRecord:
    asset_id: str
    name: str
    category: str
    semantic_role: str
    authority_implication: str = "NONE"
    status: str = "CANDIDATE"
    source_format: str = "SVG"
    variants: list[str] = field(default_factory=lambda: ["default", "reduced_motion"])
    sizes: list[int] = field(default_factory=list)
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
    honesty_label: str = ""


def rec(
    records: list[AssetRecord],
    *,
    kind: str,
    name: str,
    category: str,
    role: str,
    alt: str,
    rel: str,
    honesty: str = "",
    sizes: list[int] | None = None,
    variants: list[str] | None = None,
    fmt: str = "SVG",
) -> None:
    records.append(
        AssetRecord(
            asset_id=f"AALVIZ-{kind}-{slug(role).upper()[:40]}",
            name=name,
            category=category,
            semantic_role=role,
            alt_text=alt,
            source_file=f"design-system/aal-viz/{rel}",
            export_files=[f"design-system/aal-viz/{rel}"],
            honesty_label=honesty,
            sizes=sizes or [],
            variants=variants or ["default", "reduced_motion"],
            source_format=fmt,
        )
    )


def icon_svg(body: str, label: str, view: int = 24) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view} {view}" '
        f'width="{view}" height="{view}" fill="none" stroke="currentColor" '
        f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
        f'role="img" aria-label="{label}">\n'
        f"  <title>{label}</title>\n"
        f"{body}</svg>\n"
    )


# ── Motion primitives (first-frame / reduced-motion static states) ──────────

MOTION: list[tuple[str, str, str, str, int]] = [
    # id, label, body, duration_ms, description role
    ("projection_arrival", "Projection arrival", "  <rect x=\"5\" y=\"7\" width=\"14\" height=\"10\" rx=\"1\" opacity=\"0.85\"/>\n  <path d=\"M5 14 L9 11 L12 13 L16 9\"/>\n", 200),
    ("artifact_detected", "New artifact detected", "  <path d=\"M8 4 H15 L20 9 V20 H8 Z\"/>\n  <circle cx=\"18\" cy=\"6\" r=\"3\" fill=\"currentColor\" stroke=\"none\" opacity=\"0.9\"/>\n", 180),
    ("source_refresh", "Source refresh", "  <path d=\"M19 12 A7 7 0 1 1 16 6\"/>\n  <path d=\"M19 4 V12 H11\"/>\n", 220),
    ("validation_pass", "Validation pass", "  <path d=\"M12 3 L20 7 V13 C20 17 12 21 12 21 S4 17 4 13 V7 Z\"/>\n  <path d=\"M9 12 L11 14 L15 10\"/>\n", 200),
    ("validation_failure", "Validation failure", "  <path d=\"M12 3 L20 7 V13 C20 17 12 21 12 21 S4 17 4 13 V7 Z\"/>\n  <path d=\"M9 9 L15 15 M15 9 L9 15\"/>\n", 200),
    ("fail_closed_transition", "Fail-closed transition", "  <rect x=\"5\" y=\"5\" width=\"14\" height=\"14\" rx=\"1\"/>\n  <path d=\"M8 12 H16\" stroke-width=\"2\"/>\n", 160),
    ("drift_detected", "Drift detected", "  <path d=\"M4 16 L8 10 L12 14 L16 6 L20 12\"/>\n  <path d=\"M4 18 H20\" stroke-dasharray=\"2 2\" opacity=\"0.5\"/>\n", 240),
    ("threshold_crossing", "Threshold crossing", "  <path d=\"M4 16 H20\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M5 14 L12 8 L19 4\"/>\n  <circle cx=\"16\" cy=\"16\" r=\"2\" fill=\"currentColor\" stroke=\"none\"/>\n", 200),
    ("operator_review_required", "Operator review required", "  <circle cx=\"12\" cy=\"8\" r=\"3\"/>\n  <path d=\"M6 20 C6 15 18 15 18 20\"/>\n  <path d=\"M12 11 V14\"/>\n", 180),
    ("route_blocked", "Route blocked", "  <path d=\"M4 12 H16\"/>\n  <path d=\"M10 9 L14 15 M14 9 L10 15\"/>\n  <path d=\"M14 9 L17 12 L14 15\" opacity=\"0.4\"/>\n", 160),
    ("route_restored", "Route restored", "  <path d=\"M4 12 H17\"/>\n  <path d=\"M14 9 L17 12 L14 15\"/>\n", 200),
    ("node_selected", "Node selected", "  <rect x=\"5\" y=\"5\" width=\"14\" height=\"14\" rx=\"2\" stroke-width=\"2\"/>\n  <rect x=\"8\" y=\"8\" width=\"8\" height=\"8\" rx=\"1\" opacity=\"0.35\"/>\n", 120),
    ("node_expanded", "Node expanded", "  <rect x=\"6\" y=\"6\" width=\"12\" height=\"12\" rx=\"1\"/>\n  <path d=\"M9 4 H4 V9 M15 4 H20 V9 M4 15 V20 H9 M20 15 V20 H15\"/>\n", 180),
    ("lineage_reveal", "Lineage reveal", "  <circle cx=\"6\" cy=\"8\" r=\"2\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"2\"/>\n  <circle cx=\"18\" cy=\"16\" r=\"2\"/>\n  <path d=\"M8 9 L10 11 M14 13 L16 15\"/>\n", 280),
    ("trace_traversal", "Trace traversal", "  <path d=\"M4 16 C8 16 8 8 12 8 S16 16 20 16\"/>\n  <circle cx=\"12\" cy=\"8\" r=\"2\" fill=\"currentColor\" stroke=\"none\"/>\n", 320),
    ("timeline_scrub", "Timeline scrub indicator", "  <path d=\"M4 12 H20\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"3\"/>\n  <path d=\"M12 7 V9 M12 15 V17\"/>\n", 100),
    ("cluster_formation", "Cluster formation", "  <circle cx=\"9\" cy=\"11\" r=\"3\"/>\n  <circle cx=\"15\" cy=\"11\" r=\"3\"/>\n  <circle cx=\"12\" cy=\"16\" r=\"3\"/>\n", 240),
    ("cluster_separation", "Cluster separation", "  <circle cx=\"7\" cy=\"10\" r=\"2.5\"/>\n  <circle cx=\"17\" cy=\"10\" r=\"2.5\"/>\n  <circle cx=\"12\" cy=\"17\" r=\"2.5\" opacity=\"0.4\"/>\n", 240),
    ("provider_conflict", "Provider conflict", "  <circle cx=\"8\" cy=\"10\" r=\"3\"/>\n  <circle cx=\"16\" cy=\"14\" r=\"3\"/>\n  <path d=\"M10 11 L14 13\" stroke-dasharray=\"1.5 1.5\"/>\n  <path d=\"M11 8 L13 16\" opacity=\"0.5\"/>\n", 200),
    ("evidence_attachment", "Evidence attachment", "  <path d=\"M8 4 H15 L20 9 V20 H8 Z\"/>\n  <path d=\"M11 14 L13 16 L17 12\"/>\n", 180),
    ("copy_confirmation", "Copy confirmation", "  <rect x=\"8\" y=\"7\" width=\"10\" height=\"12\" rx=\"1\"/>\n  <path d=\"M6 15 V5 H16\"/>\n  <path d=\"M11 12 L13 14 L16 10\"/>\n", 160),
    ("transport_reconnect", "Transport reconnect", "  <path d=\"M7 14 A5 5 0 1 0 12 8\"/>\n  <path d=\"M12 5 V8 H15\"/>\n", 220),
    ("polling_fallback", "Polling fallback transition", "  <circle cx=\"12\" cy=\"12\" r=\"7\" stroke-dasharray=\"3 2\"/>\n  <path d=\"M12 8 V12 H15\"/>\n", 200),
    ("replay_start", "Replay start", "  <path d=\"M8 7 V17 L16 12 Z\"/>\n", 160),
    ("replay_complete", "Replay complete", "  <path d=\"M8 7 V17 L16 12 Z\"/>\n  <path d=\"M17 7 V17\"/>\n  <path d=\"M6 19 H18\" opacity=\"0.4\"/>\n", 180),
    ("archived_transition", "Archived transition", "  <path d=\"M4 8 H20 V10 H4 Z\"/>\n  <path d=\"M6 10 V18 H18 V10\" opacity=\"0.7\"/>\n", 200),
    ("not_computable_reveal", "NOT_COMPUTABLE reveal", "  <rect x=\"5\" y=\"5\" width=\"14\" height=\"14\" rx=\"1\"/>\n  <path d=\"M8 8 L16 16 M16 8 L8 16\"/>\n", 160),
]


def motion_css(entries: list[tuple[str, str, str, int]]) -> str:
    lines = [
        "/* Hallmark · AAL-Viz motion primitives · batch 4",
        " * genre: atmospheric-technical · deterministic · no spectacle",
        " * Animate transform/opacity only. No layout thrash. No false computation.",
        " * prefers-reduced-motion → first-frame static (use .aalviz-motion--static).",
        " */",
        ":root {",
        "  --aalviz-dur-xs: 100ms;",
        "  --aalviz-dur-sm: 160ms;",
        "  --aalviz-dur-md: 200ms;",
        "  --aalviz-dur-lg: 280ms;",
        "  --aalviz-dur-xl: 320ms;",
        "  --aalviz-ease-out: cubic-bezier(0.22, 1, 0.36, 1);",
        "  --aalviz-ease-in-out: cubic-bezier(0.45, 0, 0.55, 1);",
        "}",
        "",
        "@keyframes aalviz-fade-in {",
        "  from { opacity: 0; }",
        "  to { opacity: 1; }",
        "}",
        "@keyframes aalviz-fade-rise {",
        "  from { opacity: 0; transform: translateY(4px); }",
        "  to { opacity: 1; transform: translateY(0); }",
        "}",
        "@keyframes aalviz-scale-in {",
        "  from { opacity: 0; transform: scale(0.96); }",
        "  to { opacity: 1; transform: scale(1); }",
        "}",
        "@keyframes aalviz-draw-line {",
        "  from { stroke-dashoffset: 24; }",
        "  to { stroke-dashoffset: 0; }",
        "}",
        "@keyframes aalviz-pulse-once {",
        "  0% { opacity: 1; }",
        "  50% { opacity: 0.55; }",
        "  100% { opacity: 1; }",
        "}",
        "",
        ".aalviz-motion {",
        "  animation-timing-function: var(--aalviz-ease-out);",
        "  animation-fill-mode: both;",
        "}",
        ".aalviz-motion--static,",
        ".aalviz-motion--reduced {",
        "  animation: none !important;",
        "}",
        "",
    ]
    # map each primitive to a named class
    anim_map = {
        "projection_arrival": ("aalviz-fade-rise", "var(--aalviz-dur-md)"),
        "artifact_detected": ("aalviz-scale-in", "var(--aalviz-dur-sm)"),
        "source_refresh": ("aalviz-fade-in", "var(--aalviz-dur-md)"),
        "validation_pass": ("aalviz-scale-in", "var(--aalviz-dur-md)"),
        "validation_failure": ("aalviz-fade-in", "var(--aalviz-dur-md)"),
        "fail_closed_transition": ("aalviz-fade-in", "var(--aalviz-dur-sm)"),
        "drift_detected": ("aalviz-fade-rise", "var(--aalviz-dur-lg)"),
        "threshold_crossing": ("aalviz-fade-in", "var(--aalviz-dur-md)"),
        "operator_review_required": ("aalviz-fade-in", "var(--aalviz-dur-sm)"),
        "route_blocked": ("aalviz-fade-in", "var(--aalviz-dur-sm)"),
        "route_restored": ("aalviz-fade-in", "var(--aalviz-dur-md)"),
        "node_selected": ("aalviz-scale-in", "var(--aalviz-dur-xs)"),
        "node_expanded": ("aalviz-scale-in", "var(--aalviz-dur-sm)"),
        "lineage_reveal": ("aalviz-fade-in", "var(--aalviz-dur-lg)"),
        "trace_traversal": ("aalviz-draw-line", "var(--aalviz-dur-xl)"),
        "timeline_scrub": ("aalviz-fade-in", "var(--aalviz-dur-xs)"),
        "cluster_formation": ("aalviz-scale-in", "var(--aalviz-dur-lg)"),
        "cluster_separation": ("aalviz-fade-in", "var(--aalviz-dur-lg)"),
        "provider_conflict": ("aalviz-fade-in", "var(--aalviz-dur-md)"),
        "evidence_attachment": ("aalviz-scale-in", "var(--aalviz-dur-sm)"),
        "copy_confirmation": ("aalviz-scale-in", "var(--aalviz-dur-sm)"),
        "transport_reconnect": ("aalviz-fade-in", "var(--aalviz-dur-md)"),
        "polling_fallback": ("aalviz-fade-in", "var(--aalviz-dur-md)"),
        "replay_start": ("aalviz-fade-in", "var(--aalviz-dur-sm)"),
        "replay_complete": ("aalviz-fade-in", "var(--aalviz-dur-sm)"),
        "archived_transition": ("aalviz-fade-in", "var(--aalviz-dur-md)"),
        "not_computable_reveal": ("aalviz-fade-in", "var(--aalviz-dur-sm)"),
    }
    for mid, label, _body, _dur in entries:
        anim, dur = anim_map.get(mid, ("aalviz-fade-in", "var(--aalviz-dur-md)"))
        lines.append(f".aalviz-motion--{mid} {{")
        lines.append(f"  animation-name: {anim};")
        lines.append(f"  animation-duration: {dur};")
        lines.append("}")
        lines.append("")
    lines += [
        "@media (prefers-reduced-motion: reduce) {",
        "  .aalviz-motion {",
        "    animation: none !important;",
        "    opacity: 1 !important;",
        "    transform: none !important;",
        "  }",
        "}",
        "",
    ]
    return "\n".join(lines)


# ── Spatial fields / backgrounds ────────────────────────────────────────────

def field_svg(name: str, label: str, body_paths: str, theme: str = "dark") -> str:
    bg = PAPER if theme == "dark" else "#F4F6FA"
    ink = INK if theme == "dark" else "#0F172A"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540" width="960" height="540" role="img" aria-label="{label}">
  <title>{label}</title>
  <desc>Subtle geometric spatial field. Interface chrome remains quiet. Projection only.</desc>
  <rect width="960" height="540" fill="{bg}"/>
{body_paths}  <text x="24" y="520" font-family="IBM Plex Mono, ui-monospace, monospace" font-size="10" letter-spacing="0.12em" fill="{MUTED}">{name.upper()} · FIELD · PROJECTION ONLY</text>
</svg>
"""


def paths_grid(color: str = RULE, step: int = 48, opacity: float = 0.55) -> str:
    parts = [f'  <g stroke="{color}" stroke-width="1" opacity="{opacity}" fill="none">']
    for x in range(0, 961, step):
        parts.append(f'    <path d="M{x} 0 V540"/>')
    for y in range(0, 541, step):
        parts.append(f'    <path d="M0 {y} H960"/>')
    parts.append("  </g>")
    return "\n".join(parts) + "\n"


def paths_constellation(color: str = CYAN) -> str:
    pts = [(120, 140), (280, 200), (420, 120), (560, 220), (720, 160), (840, 280), (200, 360), (480, 340), (680, 400)]
    lines = ['  <g fill="none" stroke="{}" stroke-width="1" opacity="0.45">'.format(MUTED)]
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        lines.append(f'    <path d="M{x1} {y1} L{x2} {y2}"/>')
    lines.append("  </g>")
    lines.append(f'  <g fill="{color}">')
    for x, y in pts:
        lines.append(f'    <circle cx="{x}" cy="{y}" r="3"/>')
    lines.append("  </g>")
    return "\n".join(lines) + "\n"


def paths_spine(color: str = CYAN) -> str:
    return f"""  <path d="M80 270 H880" stroke="{color}" stroke-width="2" fill="none" opacity="0.7"/>
  <g fill="{PAPER}" stroke="{color}" stroke-width="1.5">
    <circle cx="160" cy="270" r="8"/>
    <circle cx="320" cy="270" r="8"/>
    <circle cx="480" cy="270" r="8"/>
    <circle cx="640" cy="270" r="8"/>
    <circle cx="800" cy="270" r="8"/>
  </g>
"""


def paths_tree(color: str = TEAL) -> str:
    return f"""  <path d="M480 80 V420" stroke="{color}" stroke-width="2" fill="none"/>
  <path d="M480 160 L280 280 M480 160 L680 280 M480 280 L300 400 M480 280 L660 400" stroke="{MUTED}" stroke-width="1.5" fill="none"/>
  <g fill="{PAPER}" stroke="{color}" stroke-width="1.5">
    <circle cx="480" cy="80" r="7"/>
    <circle cx="280" cy="280" r="6"/>
    <circle cx="680" cy="280" r="6"/>
    <circle cx="300" cy="400" r="5"/>
    <circle cx="660" cy="400" r="5"/>
    <circle cx="480" cy="280" r="6"/>
  </g>
"""


def paths_hatch(color: str = VIOLET) -> str:
    parts = [f'  <g stroke="{color}" stroke-width="1" opacity="0.25" fill="none">']
    for i in range(-540, 960, 24):
        parts.append(f'    <path d="M{i} 0 L{i + 540} 540"/>')
    parts.append("  </g>")
    return "\n".join(parts) + "\n"


def paths_waves(color: str = VIOLET) -> str:
    return f"""  <path d="M0 200 C160 120, 320 280, 480 200 S800 120, 960 200" fill="none" stroke="{color}" stroke-width="1.5" stroke-dasharray="6 4" opacity="0.7"/>
  <path d="M0 280 C160 200, 320 360, 480 280 S800 200, 960 280" fill="none" stroke="{MUTED}" stroke-width="1" opacity="0.5"/>
  <path d="M0 360 C160 280, 320 440, 480 360 S800 280, 960 360" fill="none" stroke="{MUTED}" stroke-width="1" opacity="0.35"/>
"""


def paths_fail(color: str = ERR) -> str:
    return f"""  <rect x="80" y="80" width="800" height="380" rx="12" fill="none" stroke="{color}" stroke-width="1.5" opacity="0.5"/>
  <path d="M200 200 H760 M200 270 H760 M200 340 H760" stroke="{MUTED}" stroke-width="1" opacity="0.35"/>
  <path d="M400 180 L560 360 M560 180 L400 360" stroke="{color}" stroke-width="2" opacity="0.55"/>
"""


FIELDS: list[tuple[str, str, str, object]] = [
    ("console_bg_dark", "Primary console background", "dark", lambda: paths_grid(RULE, 64, 0.35)),
    ("console_bg_light", "Light-theme console background", "light", lambda: paths_grid("#CBD5E1", 64, 0.5)),
    ("report_neutral", "Neutral report background", "dark", lambda: paths_grid(RULE, 80, 0.25)),
    ("canon_spine_field", "Canon Spine field", "dark", paths_spine),
    ("projection_field", "Projection field", "dark", lambda: paths_constellation(TEAL)),
    ("shadow_field", "Shadow field", "dark", lambda: paths_hatch(MUTED) + paths_grid(RULE, 96, 0.2)),
    ("forecast_field", "Forecast-reserved field", "dark", paths_waves),
    ("yggdrasil_field", "YGGDRASIL topology field", "dark", paths_tree),
    ("belief_graph_field", "Belief Graph field", "dark", lambda: paths_constellation(VIOLET)),
    ("evidence_memory_field", "Evidence-memory field", "dark", lambda: paths_grid(TEAL, 56, 0.2) + paths_constellation(TEAL)),
    ("temporal_field", "Temporal field", "dark", paths_waves),
    ("cluster_field", "Cluster field", "dark", lambda: paths_constellation(GOLD)),
    (
        "drift_field",
        "Drift field",
        "dark",
        lambda: paths_hatch(AMBER)
        + f'  <path d="M80 400 L240 200 L400 320 L560 140 L880 300" fill="none" stroke="{AMBER}" stroke-width="1.5" opacity="0.6"/>\n',
    ),
    (
        "operator_review_field",
        "Operator-review field",
        "dark",
        lambda: paths_grid(GOLD, 72, 0.25)
        + f'  <rect x="320" y="160" width="320" height="200" rx="8" fill="none" stroke="{GOLD}" stroke-width="1.5" opacity="0.5"/>\n',
    ),
    ("fail_closed_field", "Fail-closed field", "dark", paths_fail),
    ("archive_field", "Archive/historical field", "dark", lambda: paths_grid(MUTED, 48, 0.2) + paths_hatch(MUTED)),
    ("presentation_wallpaper", "Presentation wallpaper", "dark", lambda: paths_constellation(CYAN) + paths_grid(RULE, 96, 0.15)),
    (
        "docs_banner_bg",
        "Documentation banner background",
        "dark",
        lambda: paths_grid(RULE, 64, 0.3)
        + f'  <path d="M0 400 C240 280, 480 480, 960 320" fill="none" stroke="{CYAN}" stroke-width="1" opacity="0.4"/>\n',
    ),
    (
        "social_preview_bg",
        "Social-preview background",
        "dark",
        lambda: paths_constellation(VIOLET) + f'  <rect x="0" y="0" width="960" height="4" fill="{CYAN}"/>\n',
    ),
    ("print_safe_bg", "Print-safe background", "light", lambda: paths_grid("#94A3B8", 64, 0.4)),
]


# ── Responsive / PWA ────────────────────────────────────────────────────────

def header_lockup(width: int, label: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 40" width="{width}" height="40" role="img" aria-label="{label}">
  <title>{label}</title>
  <rect width="{width}" height="40" fill="{PAPER}"/>
  <g transform="translate(8,6)" fill="none" stroke="{CYAN}" stroke-width="1.5" stroke-linejoin="round">
    <path d="M2 22 L14 4 L26 22 Z"/>
    <circle cx="14" cy="15" r="3" fill="{PAPER}"/>
  </g>
  <text x="48" y="25" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="14" font-weight="600" letter-spacing="0.12em" fill="{INK}">AAL-VIZ</text>
  <text x="{width - 12}" y="25" text-anchor="end" font-family="IBM Plex Mono, monospace" font-size="9" letter-spacing="0.1em" fill="{VIOLET}">PROJECTION</text>
</svg>
"""


def mobile_mark() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32" role="img" aria-label="AAL-Viz mobile header mark">
  <title>AAL-Viz</title>
  <rect width="32" height="32" rx="6" fill="{PAPER}"/>
  <path d="M7 22 L16 8 L25 22 Z" fill="none" stroke="{CYAN}" stroke-width="1.75" stroke-linejoin="round"/>
  <circle cx="16" cy="17" r="2.5" fill="{PAPER}" stroke="{CYAN}" stroke-width="1.5"/>
  <circle cx="11" cy="14" r="1" fill="{VIOLET}"/>
  <circle cx="21" cy="14" r="1" fill="{VIOLET}"/>
</svg>
"""


def pwa_icon(size: int, maskable: bool = False) -> str:
    pad = int(size * 0.1) if maskable else int(size * 0.12)
    # scale triangle into view
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}" role="img" aria-label="AAL-Viz app icon {size}px{' maskable' if maskable else ''}">
  <title>AAL-Viz {size}px</title>
  <rect width="{size}" height="{size}" rx="{size * 0.18:.0f}" fill="{PAPER}"/>
  <g transform="translate({pad},{pad}) scale({(size - 2 * pad) / 48:.4f})" fill="none" stroke="{CYAN}" stroke-width="2" stroke-linejoin="round">
    <path d="M4 40 L24 6 L44 40 Z"/>
    <circle cx="24" cy="28" r="5" fill="{PAPER}"/>
    <circle cx="24" cy="28" r="2" fill="{CYAN}" stroke="none"/>
    <circle cx="14" cy="20" r="2" fill="{VIOLET}" stroke="none"/>
    <circle cx="34" cy="20" r="2" fill="{VIOLET}" stroke="none"/>
  </g>
</svg>
"""


def control_icon(name: str, body: str, label: str) -> str:
    return icon_svg(body, label)


MOBILE_CONTROLS: list[tuple[str, str, str]] = [
    ("graph_pan", "Touch graph pan", "  <path d=\"M12 5 V19 M5 12 H19\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"3\"/>\n"),
    ("graph_zoom_in", "Touch graph zoom in", "  <circle cx=\"11\" cy=\"11\" r=\"6\"/>\n  <path d=\"M11 8 V14 M8 11 H14 M16 16 L20 20\"/>\n"),
    ("graph_zoom_out", "Touch graph zoom out", "  <circle cx=\"11\" cy=\"11\" r=\"6\"/>\n  <path d=\"M8 11 H14 M16 16 L20 20\"/>\n"),
    ("inspector_open", "Mobile inspector open", "  <rect x=\"4\" y=\"5\" width=\"10\" height=\"14\" rx=\"1\"/>\n  <path d=\"M16 8 H20 M16 12 H20 M16 16 H18\"/>\n"),
    ("inspector_close", "Mobile inspector close", "  <rect x=\"4\" y=\"5\" width=\"16\" height=\"14\" rx=\"1\"/>\n  <path d=\"M9 9 L15 15 M15 9 L9 15\"/>\n"),
    ("filter_open", "Mobile filter", "  <path d=\"M4 6 H20 L14 12 V18 L10 20 V12 Z\"/>\n"),
    ("timeline_scrub_mobile", "Mobile timeline scrub", "  <path d=\"M4 12 H20\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"4\"/>\n"),
    ("source_drawer", "Mobile source drawer", "  <path d=\"M6 4 H18 V20 H6 Z\"/>\n  <path d=\"M9 8 H15 M9 12 H15 M9 16 H13\"/>\n"),
    ("authority_legend", "Mobile authority legend", "  <circle cx=\"7\" cy=\"8\" r=\"2\" fill=\"currentColor\" stroke=\"none\"/>\n  <path d=\"M12 8 H20\"/>\n  <path d=\"M7 12 L10 16 L4 16 Z\"/>\n  <path d=\"M12 14 H20\"/>\n  <rect x=\"5\" y=\"18\" width=\"4\" height=\"3\"/>\n  <path d=\"M12 20 H20\"/>\n"),
    ("nav_bottom_overview", "Bottom nav overview", "  <rect x=\"4\" y=\"4\" width=\"7\" height=\"7\" rx=\"1\"/>\n  <rect x=\"13\" y=\"4\" width=\"7\" height=\"7\" rx=\"1\"/>\n  <rect x=\"4\" y=\"13\" width=\"7\" height=\"7\" rx=\"1\"/>\n  <rect x=\"13\" y=\"13\" width=\"7\" height=\"7\" rx=\"1\"/>\n"),
    ("nav_bottom_topology", "Bottom nav topology", "  <circle cx=\"7\" cy=\"8\" r=\"2.5\"/>\n  <circle cx=\"17\" cy=\"8\" r=\"2.5\"/>\n  <circle cx=\"12\" cy=\"17\" r=\"2.5\"/>\n  <path d=\"M9 9 L15 9 M8.5 10 L11 15 M15.5 10 L13 15\"/>\n"),
    ("nav_bottom_review", "Bottom nav review", "  <path d=\"M5 5 H15 L19 9 V19 H5 Z\"/>\n  <path d=\"M9 13 L11 15 L15 11\"/>\n"),
    ("nav_bottom_settings", "Bottom nav settings", "  <circle cx=\"12\" cy=\"12\" r=\"3\"/>\n  <path d=\"M12 3 V6 M12 18 V21 M3 12 H6 M18 12 H21\"/>\n"),
    ("collapsed_nav", "Collapsed navigation", "  <path d=\"M5 7 H19 M5 12 H19 M5 17 H19\"/>\n"),
    ("empty_mobile", "Mobile empty state mark", "  <rect x=\"5\" y=\"6\" width=\"14\" height=\"12\" rx=\"1\" stroke-dasharray=\"2 2\"/>\n  <path d=\"M9 12 H15\" opacity=\"0.4\"/>\n"),
    ("narrow_report_card", "Narrow-width report card", "  <rect x=\"4\" y=\"3\" width=\"16\" height=\"18\" rx=\"2\"/>\n  <path d=\"M7 8 H17 M7 12 H14 M7 16 H12\"/>\n"),
    ("pinned_tab", "Browser pinned-tab mark", "  <path d=\"M6 18 L12 6 L18 18 Z\"/>\n  <circle cx=\"12\" cy=\"14\" r=\"1.5\" fill=\"currentColor\" stroke=\"none\"/>\n"),
]


# ── Marketing showcases (honesty-labeled) ───────────────────────────────────

def showcase_card(w: int, h: int, title: str, honesty: str, subtitle: str, motif: str = "constellation") -> str:
    if motif == "constellation":
        field = paths_constellation(TEAL)
    elif motif == "tree":
        field = paths_tree(CYAN)
    elif motif == "spine":
        field = paths_spine(CYAN)
    elif motif == "waves":
        field = paths_waves()
    else:
        field = paths_grid(RULE, 64, 0.3)
    # scale field conceptually inside - field is 960x540, we use full canvas
    body = f'  <rect width="{w}" height="{h}" fill="{PAPER}"/>\n'
    body += f'  <rect x="0" y="0" width="{w}" height="4" fill="{CYAN}"/>\n'
    # simple scaled motif for non-960 sizes
    if w != 960 or h != 540:
        body += f'  <g transform="scale({w/960:.4f} {h/540:.4f})" opacity="0.85">\n'
        body += field
        body += "  </g>\n"
    else:
        body += field
    body += (
        f'  <text x="32" y="36" font-family="IBM Plex Mono, ui-monospace, monospace" '
        f'font-size="12" letter-spacing="0.16em" fill="{AMBER}">{honesty}</text>\n'
        f'  <text x="32" y="{int(h * 0.45)}" font-family="IBM Plex Sans, system-ui, sans-serif" '
        f'font-size="{28 if h > 400 else 22}" font-weight="600" fill="{INK}">{title}</text>\n'
        f'  <text x="32" y="{int(h * 0.45) + 36}" font-family="IBM Plex Sans, system-ui, sans-serif" '
        f'font-size="14" fill="{MUTED}">{subtitle}</text>\n'
        f'  <text x="32" y="{h - 24}" font-family="IBM Plex Mono, monospace" font-size="10" '
        f'letter-spacing="0.1em" fill="{MUTED}">AAL-VIZ · PROJECTION ONLY · NO PRODUCTION CLAIM</text>\n'
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{title}">
  <title>{title}</title>
  <desc>{honesty}. Marketing visual without production availability claims.</desc>
{body}</svg>
"""


SHOWCASES: list[tuple[str, str, str, str, str, int, int]] = [
    ("product_overview", "AAL-Viz overview", "PRODUCT VISION", "Projection layer for topology, evidence, and operator review", "constellation", 1280, 720),
    ("projection_explainer", "Projection only", "PRODUCT VISION", "Read and render — never mutate canon or credentials", "spine", 1280, 720),
    ("feature_card_topology", "Topology", "PRODUCT VISION", "Deterministic graph chrome, procedural layouts", "tree", 640, 400),
    ("feature_card_evidence", "Evidence & provenance", "PRODUCT VISION", "Source-backed status with non-color glyphs", "constellation", 640, 400),
    ("feature_card_a11y", "Accessibility", "PRODUCT VISION", "Shape, pattern, and text — not hue alone", "grid", 640, 400),
    ("feature_card_governance", "Governance", "PRODUCT VISION", "Activation lanes stay held without dual-control", "spine", 640, 400),
    ("operator_console_overview", "Operator console", "PRODUCT VISION", "Workbench density without execution authority", "grid", 1280, 720),
    ("topology_showcase", "Topology visualization", "PRODUCT VISION", "YGGDRASIL-style routing field", "tree", 1280, 720),
    ("evidence_showcase", "Evidence and provenance", "PRODUCT VISION", "Lineage-first presentation", "constellation", 1280, 720),
    ("a11y_showcase", "Accessibility showcase", "PRODUCT VISION", "Patterns, mono, and honest empty states", "grid", 1280, 720),
    ("governance_showcase", "Governance showcase", "PRODUCT VISION", "Lanes, holds, fail-closed", "spine", 1280, 720),
    ("drift_showcase", "Drift detection", "PRODUCT VISION", "Baseline vs observed — advisory until gated", "waves", 1280, 720),
    ("belief_showcase", "Belief Graph", "CONCEPT VISUAL", "Architecture presentation — not live belief state", "constellation", 1280, 720),
    ("oracle_showcase", "Oracle integration", "CONCEPT VISUAL", "Signal → score → advise → project", "waves", 1280, 720),
    ("yggdrasil_showcase", "YGGDRASIL", "CONCEPT VISUAL", "Routing topology presentation", "tree", 1280, 720),
    ("readiness_showcase", "Production readiness", "PRODUCT VISION", "Gates remain DENIED / NO_GO until dual-control", "spine", 1280, 720),
    ("case_study_cover", "Case study", "PRODUCT VISION", "Projection-layer visual system", "constellation", 1200, 1600),
]


def main() -> None:
    records: list[AssetRecord] = []
    files = 0
    motion_entries_reg: list[dict] = []

    # Motion SVGs + CSS
    motion_meta = [(m[0], m[1], m[2], m[3]) for m in MOTION]
    write(PACK / "motion" / "aal_viz_motion.primitives.css", motion_css(motion_meta))
    rec(
        records,
        kind="MOTION-CSS",
        name="aal_viz_motion_primitives_css",
        category="motion_css",
        role="MOTION_CSS",
        alt="AAL-Viz motion primitives CSS",
        rel="motion/aal_viz_motion.primitives.css",
        variants=["css", "reduced_motion"],
        fmt="CSS",
    )

    for mid, label, body, dur in MOTION:
        rel = f"motion/states/{mid}.svg"
        write(PACK / rel, icon_svg(body, label))
        # reduced-motion twin is same file (static by design)
        rel_rm = f"motion/states/{mid}.reduced.svg"
        write(PACK / rel_rm, icon_svg(body, f"{label} (reduced motion)"))
        files += 2
        rec(
            records,
            kind="MOTION",
            name=mid,
            category="motion_primitive",
            role=mid.upper(),
            alt=label,
            rel=rel,
            sizes=[16, 24, 48],
            variants=["state_icon", "reduced_motion", "css_class"],
        )
        motion_entries_reg.append(
            {
                "id": mid,
                "label": label,
                "duration_ms": dur,
                "css_class": f"aalviz-motion--{mid}",
                "first_frame_svg": f"design-system/aal-viz/{rel}",
                "reduced_motion_svg": f"design-system/aal-viz/{rel_rm}",
                "animates": ["opacity", "transform"],
                "forbidden": ["random particles", "perpetual thinking loop", "layout thrash"],
            }
        )

    # Fields
    for name, label, theme, path_fn in FIELDS:
        rel = f"fields/{name}.svg"
        write(PACK / rel, field_svg(name, label, path_fn(), theme))
        files += 1
        rec(
            records,
            kind="FIELD",
            name=name,
            category="spatial_field",
            role=name.upper(),
            alt=label,
            rel=rel,
            sizes=[960, 540],
            variants=["field", "monochrome_via_currentColor_recolor"],
        )

    # Responsive headers
    for name, w, lab in [
        ("header_desktop", 360, "Desktop header lockup"),
        ("header_tablet", 280, "Tablet header lockup"),
        ("header_mobile_bar", 200, "Mobile header lockup"),
    ]:
        rel = f"responsive/{name}.svg"
        write(PACK / rel, header_lockup(w, lab))
        files += 1
        rec(records, kind="RESP", name=name, category="responsive_header", role=name.upper(), alt=lab, rel=rel, sizes=[w, 40])

    rel = "responsive/mobile_header_mark.svg"
    write(PACK / rel, mobile_mark())
    files += 1
    rec(records, kind="RESP", name="mobile_header_mark", category="responsive_header", role="MOBILE_MARK", alt="Mobile header mark", rel=rel, sizes=[32])

    for name, label, body in MOBILE_CONTROLS:
        rel = f"responsive/controls/{name}.svg"
        write(PACK / rel, control_icon(name, body, label))
        files += 1
        rec(records, kind="RESP-CTL", name=name, category="responsive_control", role=name.upper(), alt=label, rel=rel, sizes=[24, 44])

    # PWA icons
    for size in (180, 192, 512):
        rel = f"pwa/icon_{size}.svg"
        write(PACK / rel, pwa_icon(size, maskable=False))
        files += 1
        rec(records, kind="PWA", name=f"icon_{size}", category="pwa_icon", role=f"ICON_{size}", alt=f"App icon {size}px", rel=rel, sizes=[size])

    rel = "pwa/icon_maskable_512.svg"
    write(PACK / rel, pwa_icon(512, maskable=True))
    files += 1
    rec(records, kind="PWA", name="icon_maskable_512", category="pwa_icon", role="MASKABLE_512", alt="Maskable app icon 512", rel=rel, sizes=[512], variants=["maskable"])

    rel = "pwa/pinned_tab.svg"
    write(PACK / rel, control_icon("pinned", MOBILE_CONTROLS[-1][2], "Browser pinned-tab SVG"))
    files += 1
    rec(records, kind="PWA", name="pinned_tab", category="pwa_icon", role="PINNED_TAB", alt="Pinned tab mark", rel=rel, sizes=[16, 32])

    # Marketing showcases
    for name, title, honesty, sub, motif, w, h in SHOWCASES:
        rel = f"marketing/{name}.svg"
        write(PACK / rel, showcase_card(w, h, title, honesty, sub, motif))
        files += 1
        rec(
            records,
            kind="MKT",
            name=name,
            category="marketing_showcase",
            role=name.upper(),
            alt=f"{title} ({honesty})",
            rel=rel,
            honesty=honesty,
            sizes=[w, h],
            variants=["showcase", "product_vision_labeled"],
        )

    # Manifest
    manifest = {
        "schema_version": "AALVizAssetManifest.v1",
        "name": "aal-viz-batch4-motion-fields-pwa",
        "batch": BATCH,
        "version": "0.1.0",
        "updated": "2026-07-26",
        "hallmark": {
            "genre": "atmospheric-technical",
            "theme": "custom (Abraxas projection grammar)",
            "enrichment": "Tier B SVG + deterministic CSS motion",
        },
        "producer_system": PRODUCER,
        "asset_count": len(records),
        "file_count_approx": files + 1,
        "assets": [asdict(r) for r in records],
    }
    write(PACK / "aal_viz_asset_manifest.batch4.v1.json", json.dumps(manifest, indent=2) + "\n")

    # Motion registry
    motion_reg = {
        "schema_version": "AALVizMotionRegistry.v1",
        "status": "SHIPPED_CANDIDATE",
        "batch": BATCH,
        "css": "design-system/aal-viz/motion/aal_viz_motion.primitives.css",
        "principles": "design-system/motion/principles.md",
        "rules": [
            "Informational motion only",
            "No simulated computation or false progress",
            "prefers-reduced-motion → static first frame",
            "Animate transform/opacity only",
            "No random particles",
            "No perpetual AI-thinking loops",
            "State understandable on frame 0",
        ],
        "tokens": {
            "dur_xs": "100ms",
            "dur_sm": "160ms",
            "dur_md": "200ms",
            "dur_lg": "280ms",
            "dur_xl": "320ms",
            "ease_out": "cubic-bezier(0.22, 1, 0.36, 1)",
        },
        "count": len(motion_entries_reg),
        "entries": motion_entries_reg,
    }
    write(PACK / "AAL_VIZ_MOTION_REGISTRY.json", json.dumps(motion_reg, indent=2) + "\n")

    # Gap ledger — all complete except optional residuals
    gap_path = PACK / "docs" / "AAL_VIZ_ASSET_GAP_LEDGER.csv"
    rows = [
        ("class", "planned", "shipped", "batch", "status", "notes"),
        ("identity", "10", "11", "0", "SHIPPED", ""),
        ("authority", "30", "30", "0", "SHIPPED", ""),
        ("activation", "16", "16", "0", "SHIPPED", ""),
        ("navigation", "44", "44", "0", "SHIPPED", ""),
        ("subsystem_p0", "24", "24", "0", "SHIPPED", ""),
        ("graph_primitives", "51", "51", "0", "SHIPPED", ""),
        ("workflow", "30", "30", "1", "SHIPPED", ""),
        ("metrics", "44", "44", "1", "SHIPPED", ""),
        ("weather", "17", "51", "1", "SHIPPED", "×3 variants"),
        ("empty_error", "26", "26", "1", "SHIPPED", ""),
        ("panels", "22", "22", "1", "SHIPPED", ""),
        ("a11y_patterns", "19", "28", "1", "SHIPPED", ""),
        ("runes", "30", "30", "2", "SHIPPED", "×4 variants"),
        ("architecture_diagrams", "25", "25", "3", "SHIPPED", ""),
        ("infographics", "20", "20", "3", "SHIPPED", ""),
        ("report_assets", "22", "25", "3", "SHIPPED", ""),
        ("banners_comms", "10", "10", "3", "SHIPPED", ""),
        ("motion", "27", str(len(MOTION)), "4", "SHIPPED", "CSS + first-frame SVG"),
        ("backgrounds", "20", str(len(FIELDS)), "4", "SHIPPED", "geometric fields"),
        ("responsive_pwa", "17", str(3 + 1 + len(MOBILE_CONTROLS) + 5), "4", "SHIPPED", "headers+controls+pwa"),
        ("marketing_showcases", "17", str(len(SHOWCASES)), "4", "SHIPPED", "honesty-labeled"),
        ("inventory_status", "—", "COMPLETE", "0-4", "COMPLETE", "authored pack closed"),
    ]
    with gap_path.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

    # Icon registry merge
    reg_path = PACK / "AAL_VIZ_ICON_REGISTRY.json"
    reg = json.loads(reg_path.read_text(encoding="utf-8")) if reg_path.exists() else {}
    reg["motion"] = [m[0] for m in MOTION]
    reg["fields"] = [f[0] for f in FIELDS]
    reg["responsive"] = [c[0] for c in MOBILE_CONTROLS]
    reg["pwa"] = ["icon_180", "icon_192", "icon_512", "icon_maskable_512", "pinned_tab"]
    reg["marketing"] = [s[0] for s in SHOWCASES]
    write(reg_path, json.dumps(reg, indent=2) + "\n")

    # Export presets append
    exp_path = PACK / "AAL_VIZ_EXPORT_PRESET_REGISTRY.json"
    exp = json.loads(exp_path.read_text(encoding="utf-8")) if exp_path.exists() else {"presets": []}
    exp["batch4"] = [
        {"id": "field-960", "source": "fields/console_bg_dark.svg"},
        {"id": "pwa-512", "source": "pwa/icon_512.svg"},
        {"id": "pwa-maskable", "source": "pwa/icon_maskable_512.svg"},
        {"id": "motion-css", "source": "motion/aal_viz_motion.primitives.css"},
        {"id": "marketing-overview", "source": "marketing/product_overview.svg", "label_required": "PRODUCT VISION"},
    ]
    write(exp_path, json.dumps(exp, indent=2) + "\n")

    print(f"Batch 4: ~{files} SVG + CSS, {len(records)} records, {len(MOTION)} motion, {len(FIELDS)} fields")


if __name__ == "__main__":
    main()
