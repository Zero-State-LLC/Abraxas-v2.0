#!/usr/bin/env python3
"""Generate AAL-Viz Batch 3 — docs, architecture, reports, banners (Hallmark · Tier B SVG).

Hand-built SVG diagrams and templates — not fake live data.
Labels: CONCEPT VISUAL | PRODUCT VISION | IMPLEMENTED SYSTEM MAP as appropriate.
Projection-only. No production availability claims.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACK = REPO / "design-system" / "aal-viz"
OUT = PACK
BATCH = "3"
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
    variants: list[str] = field(default_factory=lambda: ["diagram", "monochrome"])
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
        )
    )


# ── SVG helpers ─────────────────────────────────────────────────────────────

def svg_root(w: int, h: int, label: str, body: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{label}">
  <title>{label}</title>
  <desc>AAL-Viz documentation visual. Projection only. Not a live dashboard screenshot.</desc>
  <rect width="{w}" height="{h}" fill="{PAPER}"/>
{body}</svg>
"""


def label_bar(text: str, color: str = AMBER, y: int = 16) -> str:
    return (
        f'  <text x="24" y="{y}" font-family="IBM Plex Mono, ui-monospace, monospace" '
        f'font-size="11" letter-spacing="0.16em" fill="{color}">{text}</text>\n'
    )


def title_text(text: str, x: int = 24, y: int = 44, size: int = 22) -> str:
    return (
        f'  <text x="{x}" y="{y}" font-family="IBM Plex Sans, system-ui, sans-serif" '
        f'font-size="{size}" font-weight="600" fill="{INK}">{text}</text>\n'
    )


def node_box(x: int, y: int, w: int, h: int, text: str, stroke: str = CYAN, dash: bool = False) -> str:
    dash_attr = ' stroke-dasharray="4 3"' if dash else ""
    # simple text wrap: single line centered-ish
    tx = x + 10
    ty = y + h // 2 + 4
    return (
        f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{PANEL}" '
        f'stroke="{stroke}" stroke-width="1.5"{dash_attr}/>\n'
        f'  <text x="{tx}" y="{ty}" font-family="IBM Plex Sans, system-ui, sans-serif" '
        f'font-size="11" fill="{INK}">{text}</text>\n'
    )


def arrow(x1: int, y1: int, x2: int, y2: int, color: str = MUTED) -> str:
    # horizontal-ish arrow with chevron
    return (
        f'  <path d="M{x1} {y1} L{x2} {y2}" stroke="{color}" stroke-width="1.5" fill="none"/>\n'
        f'  <path d="M{x2 - 6} {y2 - 4} L{x2} {y2} L{x2 - 6} {y2 + 4}" stroke="{color}" '
        f'stroke-width="1.5" fill="none"/>\n'
    )


def v_arrow(x: int, y1: int, y2: int, color: str = MUTED) -> str:
    return (
        f'  <path d="M{x} {y1} L{x} {y2}" stroke="{color}" stroke-width="1.5" fill="none"/>\n'
        f'  <path d="M{x - 4} {y2 - 6} L{x} {y2} L{x + 4} {y2 - 6}" stroke="{color}" '
        f'stroke-width="1.5" fill="none"/>\n'
    )


def footer_disclaimer(w: int, h: int, text: str = "AAL-VIZ · PROJECTION ONLY · NO EXECUTION AUTHORITY") -> str:
    return (
        f'  <text x="24" y="{h - 16}" font-family="IBM Plex Mono, ui-monospace, monospace" '
        f'font-size="9" letter-spacing="0.1em" fill="{MUTED}">{text}</text>\n'
        f'  <rect x="0" y="0" width="{w}" height="3" fill="{CYAN}"/>\n'
    )


# ── Architecture diagrams (960×540) ─────────────────────────────────────────

W, H = 960, 540


def diagram_spine() -> str:
    body = label_bar("IMPLEMENTED SYSTEM MAP")
    body += title_text("Abraxas supported spine → AAL-Viz projection", 24, 48)
    steps = [
        (40, 200, "Input"),
        (170, 200, "Evidence"),
        (300, 200, "Belief Graph"),
        (450, 200, "Oracle"),
        (580, 200, "Projection"),
        (730, 200, "Operator"),
    ]
    strokes = [CYAN, TEAL, VIOLET, "#5B6CFF", TEAL, GOLD]
    for i, (x, y, t) in enumerate(steps):
        body += node_box(x, y, 110, 48, t, strokes[i % len(strokes)])
        if i < len(steps) - 1:
            body += arrow(x + 110, y + 24, steps[i + 1][0], y + 24)
    body += node_box(580, 300, 260, 56, "AAL-Viz (read + render only)", VIOLET, dash=True)
    body += v_arrow(640, 248, 300, VIOLET)
    body += (
        f'  <text x="40" y="400" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" fill="{MUTED}">'
        f"Projection layer does not mutate canon, credentials, or external production.</text>\n"
    )
    body += footer_disclaimer(W, H)
    return svg_root(W, H, "Abraxas end-to-end supported spine", body)


def diagram_authority_boundary() -> str:
    body = label_bar("IMPLEMENTED SYSTEM MAP")
    body += title_text("AAL-Viz authority boundary", 24, 48)
    body += node_box(40, 120, 260, 280, "", CYAN)
    body += f'  <text x="56" y="150" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="14" font-weight="600" fill="{CYAN}">MAY READ</text>\n'
    for i, t in enumerate(["Projection bundles", "Receipts / artifacts", "Topology maps", "Evidence refs", "Operator queues"]):
        body += f'  <text x="56" y="{180 + i * 28}" font-family="IBM Plex Mono, monospace" font-size="12" fill="{INK}">· {t}</text>\n'
    body += node_box(350, 120, 260, 280, "", TEAL)
    body += f'  <text x="366" y="150" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="14" font-weight="600" fill="{TEAL}">MAY RENDER</text>\n'
    for i, t in enumerate(["Status (non-color)", "Topology views", "Metrics chrome", "Empty/blocked", "Export templates"]):
        body += f'  <text x="366" y="{180 + i * 28}" font-family="IBM Plex Mono, monospace" font-size="12" fill="{INK}">· {t}</text>\n'
    body += node_box(660, 120, 260, 280, "", ERR)
    body += f'  <text x="676" y="150" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="14" font-weight="600" fill="{ERR}">NEVER MUTATE</text>\n'
    for i, t in enumerate(["Canon", "Activation", "Credentials", "External write", "Forecast routing"]):
        body += f'  <text x="676" y="{180 + i * 28}" font-family="IBM Plex Mono, monospace" font-size="12" fill="{INK}">· {t}</text>\n'
    body += footer_disclaimer(W, H)
    return svg_root(W, H, "AAL-Viz authority-boundary diagram", body)


def diagram_shadow_forecast() -> str:
    body = label_bar("CONCEPT VISUAL")
    body += title_text("SHADOW versus FORECAST — separate lanes", 24, 48)
    body += node_box(80, 160, 320, 200, "", MUTED)
    body += f'  <text x="100" y="200" font-size="16" font-weight="600" fill="{MUTED}" font-family="IBM Plex Sans, system-ui, sans-serif">SHADOW</text>\n'
    body += f'  <text x="100" y="240" font-size="12" fill="{INK}" font-family="IBM Plex Mono, monospace">advisory · fail-open</text>\n'
    body += f'  <text x="100" y="270" font-size="12" fill="{INK}" font-family="IBM Plex Mono, monospace">no canon blend</text>\n'
    body += node_box(520, 160, 320, 200, "", VIOLET, dash=True)
    body += f'  <text x="540" y="200" font-size="16" font-weight="600" fill="{VIOLET}" font-family="IBM Plex Sans, system-ui, sans-serif">FORECAST</text>\n'
    body += f'  <text x="540" y="240" font-size="12" fill="{INK}" font-family="IBM Plex Mono, monospace">dashed · non-canonical</text>\n'
    body += f'  <text x="540" y="270" font-size="12" fill="{INK}" font-family="IBM Plex Mono, monospace">never solid cyan</text>\n'
    body += f'  <text x="420" y="260" font-size="20" fill="{ERR}" font-family="IBM Plex Sans, system-ui, sans-serif">≠</text>\n'
    body += footer_disclaimer(W, H, "NO VISUAL BLENDING · PROJECTION ONLY")
    return svg_root(W, H, "SHADOW versus FORECAST diagram", body)


def diagram_envelope() -> str:
    body = label_bar("CONCEPT VISUAL")
    body += title_text("Projection Envelope lifecycle", 24, 48)
    steps = [
        (40, 220, "Source", CYAN),
        (190, 220, "Envelope", TEAL),
        (340, 220, "Adapter", VIOLET),
        (490, 220, "Projection", TEAL),
        (640, 220, "A11y variant", GOLD),
    ]
    for i, (x, y, t, c) in enumerate(steps):
        body += node_box(x, y, 120, 50, t, c, dash=(t == "Envelope"))
        if i < len(steps) - 1:
            body += arrow(x + 120, y + 25, steps[i + 1][0], y + 25)
    body += footer_disclaimer(W, H)
    return svg_root(W, H, "Projection Envelope lifecycle", body)


def diagram_lineage() -> str:
    body = label_bar("IMPLEMENTED SYSTEM MAP")
    body += title_text("Artifact lineage", 24, 48)
    steps = ["Source", "Transform", "Validate", "Receipt", "Projection"]
    for i, t in enumerate(steps):
        x = 60 + i * 170
        body += node_box(x, 220, 130, 48, t, CYAN if i < 4 else TEAL)
        if i < len(steps) - 1:
            body += arrow(x + 130, 244, x + 170, 244)
    body += footer_disclaimer(W, H)
    return svg_root(W, H, "Artifact lineage diagram", body)


def diagram_activation_lanes() -> str:
    body = label_bar("IMPLEMENTED SYSTEM MAP")
    body += title_text("Governance activation lanes", 24, 48)
    lanes = [
        (60, "LOCAL_DEV", CYAN),
        (250, "SANDBOX", TEAL),
        (440, "INTERNAL_CANARY", AMBER),
        (630, "EXTERNAL_PRODUCTION", ERR),
    ]
    for x, t, c in lanes:
        body += node_box(x, 200, 160, 80, t, c, dash=(t != "LOCAL_DEV"))
    body += f'  <text x="630" y="320" font-size="11" fill="{ERR}" font-family="IBM Plex Mono, monospace">LOCKED without dual-control</text>\n'
    body += footer_disclaimer(W, H)
    return svg_root(W, H, "Governance activation lanes", body)


def diagram_simple_flow(title: str, honesty: str, nodes: list[tuple[str, str]], subtitle: str = "") -> str:
    body = label_bar(honesty)
    body += title_text(title, 24, 48)
    if subtitle:
        body += f'  <text x="24" y="72" font-size="12" fill="{MUTED}" font-family="IBM Plex Sans, system-ui, sans-serif">{subtitle}</text>\n'
    n = len(nodes)
    gap = min(160, (W - 80) // max(n, 1))
    for i, (t, c) in enumerate(nodes):
        x = 40 + i * gap
        body += node_box(x, 220, gap - 30, 56, t, c)
        if i < n - 1:
            body += arrow(x + gap - 30, 248, x + gap, 248)
    body += footer_disclaimer(W, H)
    return svg_root(W, H, title, body)


def diagram_loop(title: str, honesty: str, nodes: list[str], color: str = CYAN) -> str:
    body = label_bar(honesty)
    body += title_text(title, 24, 48)
    # square loop of 4
    positions = [(200, 160), (520, 160), (520, 320), (200, 320)]
    for i, t in enumerate(nodes[:4]):
        x, y = positions[i]
        body += node_box(x, y, 160, 48, t, color)
    # arrows around
    body += arrow(360, 184, 520, 184, color)
    body += v_arrow(600, 208, 320, color)
    body += f'  <path d="M520 344 L360 344" stroke="{color}" stroke-width="1.5" fill="none"/>\n'
    body += f'  <path d="M366 340 L360 344 L366 348" stroke="{color}" stroke-width="1.5" fill="none"/>\n'
    body += v_arrow(280, 320, 208, color)
    body += footer_disclaimer(W, H)
    return svg_root(W, H, title, body)


def diagram_yggdrasil() -> str:
    body = label_bar("CONCEPT VISUAL")
    body += title_text("YGGDRASIL routing map", 24, 48)
    body += f'  <path d="M480 100 V400" stroke="{CYAN}" stroke-width="2" fill="none"/>\n'
    body += f'  <path d="M480 160 L300 260 M480 160 L660 260 M480 260 L320 360 M480 260 L640 360" stroke="{MUTED}" stroke-width="1.5" fill="none"/>\n'
    for cx, cy, lab in [(480, 100, "root"), (300, 260, "route"), (660, 260, "route"), (320, 360, "leaf"), (640, 360, "leaf"), (480, 260, "join")]:
        body += f'  <circle cx="{cx}" cy="{cy}" r="8" fill="{PAPER}" stroke="{CYAN}" stroke-width="1.5"/>\n'
        body += f'  <text x="{cx + 14}" y="{cy + 4}" font-size="11" fill="{INK}" font-family="IBM Plex Mono, monospace">{lab}</text>\n'
    body += footer_disclaimer(W, H)
    return svg_root(W, H, "YGGDRASIL routing map", body)


def diagram_canon_spine() -> str:
    body = label_bar("CONCEPT VISUAL")
    body += title_text("Canon Spine map", 24, 48)
    body += f'  <path d="M120 280 H840" stroke="{CYAN}" stroke-width="3" fill="none"/>\n'
    for i, t in enumerate(["Identity", "Contracts", "Runtime", "Governance", "Evidence", "Projection"]):
        x = 140 + i * 120
        body += f'  <circle cx="{x}" cy="280" r="10" fill="{PAPER}" stroke="{CYAN}" stroke-width="1.5"/>\n'
        body += f'  <text x="{x}" y="320" text-anchor="middle" font-size="11" fill="{INK}" font-family="IBM Plex Sans, system-ui, sans-serif">{t}</text>\n'
    body += footer_disclaimer(W, H)
    return svg_root(W, H, "Canon Spine map", body)


def diagram_taxonomy() -> str:
    body = label_bar("IMPLEMENTED SYSTEM MAP")
    body += title_text("Canonical visual taxonomy", 24, 48)
    cats = [
        (40, "Identity", CYAN),
        (180, "Authority", TEAL),
        (320, "Runes", GOLD),
        (460, "Nav", VIOLET),
        (600, "Graph", CYAN),
        (740, "Weather", AMBER),
    ]
    for x, t, c in cats:
        body += node_box(x, 180, 120, 160, t, c)
    body += footer_disclaimer(W, H)
    return svg_root(W, H, "Canonical visual taxonomy sheet", body)


def diagram_folder_map() -> str:
    body = label_bar("IMPLEMENTED SYSTEM MAP")
    body += title_text("AAL-Viz asset folder map", 24, 48)
    lines = [
        "design-system/aal-viz/",
        "  brand/ authority/ activation/ navigation/",
        "  subsystem/ graph/ workflow/ metrics/",
        "  weather/ empty/ panels/ a11y/ runes/",
        "  diagrams/ infographics/ reports/ banners/",
        "  docs/ showcase/",
    ]
    for i, line in enumerate(lines):
        body += (
            f'  <text x="48" y="{140 + i * 36}" font-family="IBM Plex Mono, monospace" '
            f'font-size="14" fill="{CYAN if i == 0 else INK}">{line}</text>\n'
        )
    body += footer_disclaimer(W, H)
    return svg_root(W, H, "Asset folder map", body)


def diagram_qa_pipeline() -> str:
    return diagram_simple_flow(
        "Visual QA pipeline",
        "IMPLEMENTED SYSTEM MAP",
        [
            ("Author", CYAN),
            ("Squint 16px", TEAL),
            ("Mono pass", VIOLET),
            ("Manifest", GOLD),
            ("CANDIDATE", AMBER),
        ],
    )


def diagram_a11y_pipeline() -> str:
    return diagram_simple_flow(
        "Accessibility rendering pipeline",
        "IMPLEMENTED SYSTEM MAP",
        [
            ("Source", CYAN),
            ("Shape status", TEAL),
            ("Pattern fill", VIOLET),
            ("Alt text", GOLD),
            ("Export", AMBER),
        ],
    )


def diagram_frontend() -> str:
    return diagram_simple_flow(
        "AAL-Viz frontend architecture",
        "CONCEPT VISUAL",
        [
            ("Console", CYAN),
            ("Bundle", TEAL),
            ("Transport", VIOLET),
            ("Panels", GOLD),
            ("Export", AMBER),
        ],
        "Live layout remains procedural; assets are chrome only.",
    )


def diagram_bundle() -> str:
    return diagram_simple_flow(
        "Projection bundle construction",
        "CONCEPT VISUAL",
        [
            ("Receipts", CYAN),
            ("Stabilization", TEAL),
            ("Yggdrasil", VIOLET),
            ("Bundle JSON", GOLD),
            ("Console", TEAL),
        ],
    )


def diagram_transport() -> str:
    body = label_bar("IMPLEMENTED SYSTEM MAP")
    body += title_text("WebSocket / polling / sample fallback", 24, 48)
    body += node_box(80, 180, 200, 60, "WebSocket", CYAN)
    body += node_box(380, 180, 200, 60, "Polling fallback", AMBER, dash=True)
    body += node_box(680, 180, 200, 60, "Sample fixture", MUTED, dash=True)
    body += arrow(280, 210, 380, 210, AMBER)
    body += arrow(580, 210, 680, 210, MUTED)
    body += f'  <text x="80" y="300" font-size="12" fill="{MUTED}" font-family="IBM Plex Mono, monospace">Degrade honestly — never invent live packets</text>\n'
    body += footer_disclaimer(W, H)
    return svg_root(W, H, "Transport fallback diagram", body)


def diagram_fail_closed() -> str:
    body = label_bar("IMPLEMENTED SYSTEM MAP")
    body += title_text("Fail-closed behavior", 24, 48)
    body += node_box(100, 200, 200, 60, "Validate", CYAN)
    body += arrow(300, 230, 380, 230, ERR)
    body += node_box(380, 200, 220, 60, "FAIL_CLOSED", ERR)
    body += arrow(600, 230, 680, 230, MUTED)
    body += node_box(680, 200, 200, 60, "No mutation", MUTED)
    body += footer_disclaimer(W, H)
    return svg_root(W, H, "Fail-closed behavior", body)


def diagram_asset_lifecycle() -> str:
    return diagram_simple_flow(
        "Asset lifecycle",
        "IMPLEMENTED SYSTEM MAP",
        [
            ("Draft", MUTED),
            ("CANDIDATE", AMBER),
            ("QA", TEAL),
            ("APPROVED", OK),
            ("Superseded", MUTED),
        ],
    )


DIAGRAMS: list[tuple[str, str, str, callable]] = [
    ("spine_e2e", "Abraxas end-to-end supported spine", "IMPLEMENTED SYSTEM MAP", diagram_spine),
    ("authority_boundary", "AAL-Viz authority-boundary diagram", "IMPLEMENTED SYSTEM MAP", diagram_authority_boundary),
    ("shadow_vs_forecast", "SHADOW versus FORECAST diagram", "CONCEPT VISUAL", diagram_shadow_forecast),
    ("projection_envelope", "Projection Envelope lifecycle", "CONCEPT VISUAL", diagram_envelope),
    ("artifact_lineage", "Artifact lineage diagram", "IMPLEMENTED SYSTEM MAP", diagram_lineage),
    ("activation_lanes", "Governance activation lanes", "IMPLEMENTED SYSTEM MAP", diagram_activation_lanes),
    ("canon_spine", "Canon Spine map", "CONCEPT VISUAL", diagram_canon_spine),
    ("yggdrasil", "YGGDRASIL routing map", "CONCEPT VISUAL", diagram_yggdrasil),
    (
        "belief_graph",
        "Belief Graph architecture",
        "CONCEPT VISUAL",
        lambda: diagram_simple_flow(
            "Belief Graph architecture",
            "CONCEPT VISUAL",
            [("Nodes", VIOLET), ("Edges", CYAN), ("Confidence", TEAL), ("Projection", GOLD)],
        ),
    ),
    (
        "evidence_memory",
        "Compositional evidence memory flow",
        "CONCEPT VISUAL",
        lambda: diagram_simple_flow(
            "Compositional evidence memory",
            "CONCEPT VISUAL",
            [("Ingest", CYAN), ("Compose", TEAL), ("Store", VIOLET), ("Retrieve", GOLD)],
        ),
    ),
    (
        "oracle_pipeline",
        "Oracle analysis pipeline",
        "CONCEPT VISUAL",
        lambda: diagram_simple_flow(
            "Oracle analysis pipeline",
            "CONCEPT VISUAL",
            [("Signal", "#5B6CFF"), ("Score", TEAL), ("Advise", VIOLET), ("Project", GOLD)],
        ),
    ),
    (
        "brier_loop",
        "Brier feedback loop",
        "CONCEPT VISUAL",
        lambda: diagram_loop("Brier feedback loop", "CONCEPT VISUAL", ["Forecast", "Outcome", "Score", "Calibrate"], VIOLET),
    ),
    (
        "drift_loop",
        "Drift detection loop",
        "CONCEPT VISUAL",
        lambda: diagram_loop("Drift detection loop", "CONCEPT VISUAL", ["Baseline", "Observe", "Diff", "Flag"], AMBER),
    ),
    (
        "operator_review_loop",
        "Operator review loop",
        "IMPLEMENTED SYSTEM MAP",
        lambda: diagram_loop("Operator review loop", "IMPLEMENTED SYSTEM MAP", ["Queue", "Inspect", "Decide", "Record"], GOLD),
    ),
    ("fail_closed", "Fail-closed behavior", "IMPLEMENTED SYSTEM MAP", diagram_fail_closed),
    (
        "provider_reliability",
        "Provider reliability flow",
        "CONCEPT VISUAL",
        lambda: diagram_simple_flow(
            "Provider reliability flow",
            "CONCEPT VISUAL",
            [("Observe", CYAN), ("Score", TEAL), ("Compare", VIOLET), ("Report", GOLD)],
        ),
    ),
    (
        "replay_recovery",
        "Replay and recovery flow",
        "CONCEPT VISUAL",
        lambda: diagram_simple_flow(
            "Replay and recovery",
            "CONCEPT VISUAL",
            [("Archive", MUTED), ("Replay", CYAN), ("Validate", TEAL), ("Recover", OK)],
        ),
    ),
    ("frontend_arch", "AAL-Viz frontend architecture", "CONCEPT VISUAL", diagram_frontend),
    ("bundle_construction", "Projection bundle construction", "CONCEPT VISUAL", diagram_bundle),
    ("transport_fallback", "WebSocket/polling/sample-fallback", "IMPLEMENTED SYSTEM MAP", diagram_transport),
    ("visual_taxonomy", "Canonical visual taxonomy sheet", "IMPLEMENTED SYSTEM MAP", diagram_taxonomy),
    ("asset_lifecycle", "Asset lifecycle diagram", "IMPLEMENTED SYSTEM MAP", diagram_asset_lifecycle),
    ("folder_map", "Asset folder map", "IMPLEMENTED SYSTEM MAP", diagram_folder_map),
    ("visual_qa", "Visual QA pipeline", "IMPLEMENTED SYSTEM MAP", diagram_qa_pipeline),
    ("a11y_pipeline", "Accessibility rendering pipeline", "IMPLEMENTED SYSTEM MAP", diagram_a11y_pipeline),
]


# ── Infographic templates (800×1000 portrait frames) ────────────────────────

def infographic_template(name: str, title: str, zones: list[str]) -> str:
    w, h = 800, 1000
    body = f'  <rect width="{w}" height="{h}" fill="{PAPER}"/>\n'
    body += f'  <rect x="0" y="0" width="{w}" height="4" fill="{CYAN}"/>\n'
    body += label_bar("TEMPLATE · PROJECTION ONLY", AMBER, 28)
    body += title_text(title, 32, 64, 26)
    body += (
        f'  <rect x="32" y="80" width="200" height="22" rx="4" fill="none" stroke="{VIOLET}"/>\n'
        f'  <text x="42" y="95" font-size="10" fill="{VIOLET}" font-family="IBM Plex Mono, monospace" letter-spacing="0.12em">AUTHORITY: NONE</text>\n'
    )
    y = 130
    for z in zones:
        body += (
            f'  <rect x="32" y="{y}" width="736" height="70" rx="6" fill="{PANEL}" stroke="{RULE}"/>\n'
            f'  <text x="48" y="{y + 28}" font-size="11" fill="{MUTED}" font-family="IBM Plex Mono, monospace" letter-spacing="0.1em">{z}</text>\n'
            f'  <text x="48" y="{y + 50}" font-size="12" fill="{INK}" font-family="IBM Plex Sans, system-ui, sans-serif">…</text>\n'
        )
        y += 86
    # required zones footer
    for i, z in enumerate(["PROVENANCE", "SOURCES", "BLOCKED CLAIMS", "NOT_COMPUTABLE", "DISCLAIMER"]):
        body += (
            f'  <rect x="{32 + i * 148}" y="{h - 120}" width="140" height="48" rx="4" fill="none" stroke="{MUTED}" stroke-dasharray="3 2"/>\n'
            f'  <text x="{40 + i * 148}" y="{h - 92}" font-size="9" fill="{MUTED}" font-family="IBM Plex Mono, monospace">{z}</text>\n'
        )
    body += (
        f'  <text x="32" y="{h - 40}" font-size="10" fill="{MUTED}" font-family="IBM Plex Mono, monospace">'
        f"Accessible text companion required · AAL-VIZ · PROJECTION ONLY</text>\n"
    )
    return svg_root(w, h, f"Infographic template: {title}", body)


INFOGRAPHICS = [
    ("process", "Process infographic", ["STEP 1", "STEP 2", "STEP 3", "OUTCOME"]),
    ("timeline", "Timeline infographic", ["T0", "T1", "T2", "TN"]),
    ("comparison", "Comparison infographic", ["OPTION A", "OPTION B", "DELTA", "DECISION"]),
    ("status_board", "Status-board infographic", ["OBSERVED", "INFERRED", "BLOCKED", "HELD"]),
    ("cluster_card", "Cluster-card infographic", ["CLUSTER ID", "MEMBERS", "COHERENCE", "RISK"]),
    ("proof_chain", "Proof-chain infographic", ["CLAIM", "EVIDENCE", "VALIDATOR", "RECEIPT"]),
    ("incident_summary", "Incident summary", ["SYMPTOM", "IMPACT", "RESPONSE", "STATUS"]),
    ("production_readiness", "Production-readiness summary", ["GATES", "RISKS", "HOLD", "NEXT"]),
    ("validation_report", "Validation report", ["SCHEMA", "PROOFS", "RESULT", "GAPS"]),
    ("threat_model", "Threat-model summary", ["ASSETS", "THREATS", "CONTROLS", "RESIDUAL"]),
    ("benchmark", "Benchmark summary", ["METRIC", "BASELINE", "RESULT", "NOTES"]),
    ("release_summary", "Release summary", ["VERSION", "CHANGES", "GATES", "HOLD"]),
    ("operator_decision", "Operator decision summary", ["CONTEXT", "OPTIONS", "DECISION", "RECEIPT"]),
    ("research_finding", "Research finding summary", ["QUESTION", "METHOD", "FINDING", "LIMITS"]),
    ("provider_comparison", "Provider comparison", ["PROVIDER A", "PROVIDER B", "SCORE", "CAVEATS"]),
    ("drift_report", "Drift report", ["BASELINE", "OBSERVED", "DRIFT", "ACTION"]),
    ("forecast_calibration", "Forecast calibration report", ["FORECAST", "OUTCOME", "BRIER", "NOTE"]),
    ("evidence_gap", "Evidence-gap report", ["REQUIRED", "PRESENT", "MISSING", "BLOCKED"]),
    ("canon_change", "Canon-change summary", ["BEFORE", "AFTER", "AUTHORITY", "HOLD"]),
    ("notion_reconciliation", "Repository/Notion reconciliation", ["REPO", "NOTION", "DELTA", "STATUS"]),
]


# ── Report / export assets ──────────────────────────────────────────────────

def report_cover() -> str:
    w, h = 800, 1100
    body = f'  <rect width="{w}" height="{h}" fill="{PAPER}"/>\n'
    body += f'  <rect x="0" y="0" width="{w}" height="6" fill="{CYAN}"/>\n'
    body += label_bar("PROJECTION ONLY", VIOLET, 80)
    body += title_text("AAL-Viz Report", 48, 200, 40)
    body += f'  <text x="48" y="250" font-size="16" fill="{MUTED}" font-family="IBM Plex Sans, system-ui, sans-serif">Observation · topology · evidence</text>\n'
    body += node_box(48, 320, 280, 40, "STATUS: CANDIDATE", AMBER)
    body += f'  <text x="48" y="{h - 80}" font-size="12" fill="{MUTED}" font-family="IBM Plex Mono, monospace">No production availability claim</text>\n'
    body += f'  <text x="48" y="{h - 50}" font-size="12" fill="{MUTED}" font-family="IBM Plex Mono, monospace">AAL-VIZ · PROJECTION ONLY</text>\n'
    return svg_root(w, h, "PDF report cover", body)


def report_divider(title: str = "Section") -> str:
    w, h = 800, 200
    body = f'  <rect width="{w}" height="{h}" fill="{PAPER}"/>\n'
    body += f'  <path d="M48 100 H752" stroke="{CYAN}" stroke-width="1.5"/>\n'
    body += title_text(title, 48, 90, 28)
    body += f'  <text x="48" y="140" font-size="11" fill="{MUTED}" font-family="IBM Plex Mono, monospace">PROJECTION ONLY</text>\n'
    return svg_root(w, h, f"PDF section divider: {title}", body)


def marker_chip(label: str, color: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 28" width="160" height="28" role="img" aria-label="{label}">
  <title>{label}</title>
  <rect x="1" y="1" width="158" height="26" rx="4" fill="{PAPER}" stroke="{color}" stroke-width="1.5"/>
  <text x="80" y="18" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="10" letter-spacing="0.12em" fill="{color}">{label}</text>
</svg>
"""


def report_footer() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 40" width="800" height="40" role="img" aria-label="Report footer">
  <title>Report footer</title>
  <rect width="800" height="40" fill="{PAPER}"/>
  <path d="M0 1 H800" stroke="{RULE}"/>
  <text x="16" y="24" font-family="IBM Plex Mono, monospace" font-size="10" fill="{MUTED}">AAL-VIZ · PROJECTION ONLY</text>
  <text x="784" y="24" text-anchor="end" font-family="IBM Plex Mono, monospace" font-size="10" fill="{MUTED}">page · sources required</text>
</svg>
"""


def provenance_footer() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 48" width="800" height="48" role="img" aria-label="Provenance footer">
  <title>Provenance footer</title>
  <rect width="800" height="48" fill="{PANEL}"/>
  <text x="16" y="20" font-family="IBM Plex Mono, monospace" font-size="10" fill="{MUTED}">PROVENANCE</text>
  <text x="16" y="36" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="11" fill="{INK}">source · artifact · validator · receipt</text>
</svg>
"""


def page_number() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 24" width="80" height="24" role="img" aria-label="Page number">
  <title>Page number</title>
  <text x="40" y="16" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="11" fill="{MUTED}">— n —</text>
</svg>
"""


def source_chip() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 24" width="120" height="24" role="img" aria-label="Source reference chip">
  <title>Source reference</title>
  <rect x="1" y="1" width="118" height="22" rx="11" fill="none" stroke="{TEAL}"/>
  <text x="60" y="16" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="9" fill="{TEAL}">SRC · ref</text>
</svg>
"""


def hash_chip() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 24" width="160" height="24" role="img" aria-label="Artifact hash chip">
  <title>Artifact hash</title>
  <rect x="1" y="1" width="158" height="22" rx="4" fill="none" stroke="{MUTED}"/>
  <text x="80" y="16" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="9" fill="{MUTED}">sha256:…</text>
</svg>
"""


def qr_container() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" width="96" height="96" role="img" aria-label="QR reference container">
  <title>QR / reference link container</title>
  <rect x="2" y="2" width="92" height="92" rx="4" fill="{PAPER}" stroke="{MUTED}"/>
  <rect x="16" y="16" width="24" height="24" fill="none" stroke="{INK}"/>
  <rect x="56" y="16" width="24" height="24" fill="none" stroke="{INK}"/>
  <rect x="16" y="56" width="24" height="24" fill="none" stroke="{INK}"/>
  <rect x="56" y="56" width="24" height="24" fill="none" stroke="{MUTED}" stroke-dasharray="2 2"/>
  <text x="48" y="90" text-anchor="middle" font-size="7" fill="{MUTED}" font-family="IBM Plex Mono, monospace">REF</text>
</svg>
"""


def caption_style() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 40" width="400" height="40" role="img" aria-label="Diagram caption style">
  <title>Diagram caption</title>
  <text x="0" y="16" font-family="IBM Plex Mono, monospace" font-size="10" fill="{MUTED}">FIG · caption — sources in footer</text>
  <text x="0" y="32" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="11" fill="{INK}">Short descriptive caption (projection only).</text>
</svg>
"""


def table_header() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 36" width="600" height="36" role="img" aria-label="Table header style">
  <title>Table header</title>
  <rect width="600" height="36" fill="{PANEL}"/>
  <path d="M0 35 H600" stroke="{CYAN}" stroke-width="1"/>
  <text x="12" y="22" font-family="IBM Plex Mono, monospace" font-size="10" letter-spacing="0.1em" fill="{MUTED}">COL · COL · COL · STATUS</text>
</svg>
"""


def code_excerpt() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 120" width="480" height="120" role="img" aria-label="Code JSON excerpt style">
  <title>Code/JSON excerpt</title>
  <rect width="480" height="120" rx="6" fill="{PANEL}" stroke="{RULE}"/>
  <text x="16" y="28" font-family="IBM Plex Mono, monospace" font-size="11" fill="{TEAL}">{{</text>
  <text x="28" y="48" font-family="IBM Plex Mono, monospace" font-size="11" fill="{INK}">"status": "PROJECTION_ONLY",</text>
  <text x="28" y="68" font-family="IBM Plex Mono, monospace" font-size="11" fill="{INK}">"authority": "NONE"</text>
  <text x="16" y="88" font-family="IBM Plex Mono, monospace" font-size="11" fill="{TEAL}">}}</text>
</svg>
"""


def callout(kind: str, color: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 64" width="480" height="64" role="img" aria-label="Callout {kind}">
  <title>Callout {kind}</title>
  <rect width="480" height="64" rx="4" fill="{PANEL}" stroke="{RULE}"/>
  <rect x="0" y="0" width="4" height="64" fill="{color}"/>
  <text x="20" y="28" font-family="IBM Plex Mono, monospace" font-size="10" letter-spacing="0.12em" fill="{color}">{kind.upper()}</text>
  <text x="20" y="48" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" fill="{INK}">Callout body — honest, sourced, projection-only.</text>
</svg>
"""


def summary_card(title: str, color: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 280 160" width="280" height="160" role="img" aria-label="{title} card">
  <title>{title}</title>
  <rect width="280" height="160" rx="8" fill="{PANEL}" stroke="{color}"/>
  <text x="16" y="32" font-family="IBM Plex Mono, monospace" font-size="10" letter-spacing="0.12em" fill="{color}">{title.upper()}</text>
  <text x="16" y="64" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="14" fill="{INK}">Summary slot</text>
  <text x="16" y="140" font-family="IBM Plex Mono, monospace" font-size="9" fill="{MUTED}">sources · blocked · NOT_COMPUTABLE</text>
</svg>
"""


# ── Banners ─────────────────────────────────────────────────────────────────

def banner(w: int, h: int, title: str, honesty: str, subtitle: str) -> str:
    body = f'  <rect width="{w}" height="{h}" fill="{PAPER}"/>\n'
    body += f'  <rect x="0" y="0" width="{w}" height="4" fill="{CYAN}"/>\n'
    # topology field
    body += f'  <path d="M0 {h * 0.65} C{w * 0.25} {h * 0.3}, {w * 0.5} {h * 0.8}, {w} {h * 0.45}" fill="none" stroke="{RULE}" stroke-width="1"/>\n'
    body += f'  <path d="M0 {h * 0.75} C{w * 0.3} {h * 0.5}, {w * 0.6} {h * 0.9}, {w} {h * 0.55}" fill="none" stroke="{MUTED}" stroke-width="1" opacity="0.5"/>\n'
    for i in range(5):
        cx = int(w * (0.15 + i * 0.18))
        cy = int(h * (0.45 + (i % 2) * 0.12))
        body += f'  <circle cx="{cx}" cy="{cy}" r="3" fill="{CYAN if i % 2 == 0 else VIOLET}"/>\n'
    body += label_bar(honesty, AMBER, 28)
    body += title_text(title, 32, int(h * 0.42), 36 if h > 200 else 24)
    body += f'  <text x="32" y="{int(h * 0.42) + 36}" font-size="14" fill="{MUTED}" font-family="IBM Plex Sans, system-ui, sans-serif">{subtitle}</text>\n'
    body += f'  <text x="32" y="{h - 24}" font-size="10" fill="{MUTED}" font-family="IBM Plex Mono, monospace">AAL-VIZ · PROJECTION ONLY · NO PRODUCTION CLAIM</text>\n'
    return svg_root(w, h, title, body)


def main() -> None:
    records: list[AssetRecord] = []
    diagram_reg: list[dict] = []
    files = 0

    # Diagrams
    for name, title, honesty, fn in DIAGRAMS:
        rel = f"diagrams/{name}.svg"
        write(OUT / rel, fn())
        rec(
            records,
            kind="DIAG",
            name=name,
            category="architecture_diagram",
            role=name.upper(),
            alt=title,
            rel=rel,
            honesty=honesty,
            sizes=[960, 540],
        )
        diagram_reg.append(
            {
                "id": name,
                "title": title,
                "honesty_label": honesty,
                "path": f"design-system/aal-viz/{rel}",
                "batch": BATCH,
            }
        )
        files += 1

    # Infographics
    for name, title, zones in INFOGRAPHICS:
        rel = f"infographics/{name}.svg"
        write(OUT / rel, infographic_template(name, title, zones))
        rec(
            records,
            kind="INFO",
            name=name,
            category="infographic_template",
            role=name.upper(),
            alt=title,
            rel=rel,
            honesty="TEMPLATE · PROJECTION ONLY",
            sizes=[800, 1000],
        )
        files += 1

    # Reports
    report_assets = [
        ("cover", report_cover(), "PDF report cover"),
        ("section_divider", report_divider("Section"), "PDF section divider"),
        ("footer", report_footer(), "Report footer"),
        ("provenance_footer", provenance_footer(), "Provenance footer"),
        ("page_number", page_number(), "Page number treatment"),
        ("source_chip", source_chip(), "Source-reference chip"),
        ("artifact_hash_chip", hash_chip(), "Artifact-hash chip"),
        ("qr_container", qr_container(), "QR/reference-link container"),
        ("diagram_caption", caption_style(), "Diagram caption style"),
        ("table_header", table_header(), "Table header style"),
        ("code_excerpt", code_excerpt(), "Code/JSON excerpt style"),
        ("callout_info", callout("info", CYAN), "Callout info"),
        ("callout_warning", callout("warning", AMBER), "Callout warning"),
        ("callout_fail_closed", callout("fail_closed", ERR), "Callout fail-closed"),
        ("callout_projection", callout("projection_only", VIOLET), "Callout projection-only"),
        ("card_executive", summary_card("Executive summary", CYAN), "Executive-summary card"),
        ("card_risk", summary_card("Risk summary", AMBER), "Risk-summary card"),
        ("card_decision", summary_card("Decision summary", GOLD), "Decision-summary card"),
        ("card_evidence", summary_card("Evidence summary", TEAL), "Evidence-summary card"),
    ]
    for name, content, alt in report_assets:
        rel = f"reports/{name}.svg"
        write(OUT / rel, content)
        rec(records, kind="RPT", name=name, category="report_asset", role=name.upper(), alt=alt, rel=rel)
        files += 1

    markers = [
        ("confidential", "CONFIDENTIAL / INTERNAL", ERR),
        ("projection_only", "PROJECTION ONLY", VIOLET),
        ("draft", "DRAFT", AMBER),
        ("superseded", "SUPERSEDED", MUTED),
        ("canon_active", "CANON ACTIVE", CYAN),
        ("review_required", "REVIEW REQUIRED", GOLD),
    ]
    for name, label, color in markers:
        rel = f"reports/marker_{name}.svg"
        write(OUT / rel, marker_chip(label, color))
        rec(records, kind="RPT-MARK", name=f"marker_{name}", category="report_marker", role=label, alt=label, rel=rel)
        files += 1

    # Banners / communication
    banners = [
        ("readme_header", 1280, 320, "AAL-Viz", "PRODUCT VISION", "Projection layer for topology, evidence, and operator review"),
        ("notion_cover", 1500, 600, "AAL-Viz", "PRODUCT VISION", "Abraxas projection-layer visual system"),
        ("docs_portal_hero", 1440, 480, "Documentation", "PRODUCT VISION", "Visual language · runes · diagrams · reports"),
        ("github_repo_card", 1280, 640, "AAL-Viz visual pack", "PRODUCT VISION", "Hallmark Tier-B asset foundation · batches 0–3"),
        ("social_square", 1080, 1080, "AAL-VIZ", "PRODUCT VISION", "Projection only"),
        ("social_portrait", 1080, 1350, "AAL-VIZ", "PRODUCT VISION", "Observation · topology · evidence"),
        ("social_landscape", 1200, 630, "AAL-VIZ", "PRODUCT VISION", "Projection-only visual language"),
        ("og_default", 1200, 630, "AAL-Viz", "PRODUCT VISION", "No fabricated product screenshot"),
        ("slide_title_bg", 1920, 1080, "AAL-Viz", "PRODUCT VISION", "Presentation title field"),
        ("slide_section_bg", 1920, 1080, "Section", "PRODUCT VISION", "Presentation section field"),
    ]
    for name, w, h, title, honesty, sub in banners:
        rel = f"banners/{name}.svg"
        write(OUT / rel, banner(w, h, title, honesty, sub))
        rec(
            records,
            kind="BANNER",
            name=name,
            category="banner",
            role=name.upper(),
            alt=f"{title} — {honesty}",
            rel=rel,
            honesty=honesty,
            sizes=[w, h],
        )
        files += 1

    # Manifest
    manifest = {
        "schema_version": "AALVizAssetManifest.v1",
        "name": "aal-viz-batch3-docs-comms",
        "batch": BATCH,
        "version": "0.1.0",
        "updated": "2026-07-19",
        "hallmark": {
            "genre": "atmospheric-technical",
            "theme": "custom (Abraxas projection grammar)",
            "enrichment": "Tier B hand-built SVG diagrams/templates",
        },
        "producer_system": PRODUCER,
        "asset_count": len(records),
        "file_count_approx": files,
        "assets": [asdict(r) for r in records],
    }
    write(PACK / "aal_viz_asset_manifest.batch3.v1.json", json.dumps(manifest, indent=2) + "\n")

    # Diagram registry
    diag_reg = {
        "schema_version": "AALVizDiagramRegistry.v1",
        "status": "SHIPPED_CANDIDATE",
        "batch": BATCH,
        "count": len(diagram_reg),
        "entries": diagram_reg,
        "primitives": {
            "nodes": "graph/nodes/",
            "edges": "graph/edges/",
            "ports": "graph/ports/",
        },
        "honesty_labels": ["IMPLEMENTED SYSTEM MAP", "CONCEPT VISUAL", "PRODUCT VISION", "TEMPLATE · PROJECTION ONLY"],
    }
    write(PACK / "AAL_VIZ_DIAGRAM_REGISTRY.json", json.dumps(diag_reg, indent=2) + "\n")

    # Export presets update
    export_reg = {
        "schema_version": "AALVizExportPresetRegistry.v1",
        "batch": BATCH,
        "presets": [
            {"id": "diagram-960", "format": "SVG", "size_px": [960, 540], "use": "docs architecture"},
            {"id": "infographic-portrait", "format": "SVG", "size_px": [800, 1000], "use": "report templates"},
            {"id": "report-cover", "format": "SVG", "source": "reports/cover.svg"},
            {"id": "readme-banner", "format": "SVG", "source": "banners/readme_header.svg", "label_required": "PRODUCT VISION"},
            {"id": "notion-cover", "format": "SVG", "source": "banners/notion_cover.svg", "label_required": "PRODUCT VISION"},
            {"id": "og-default", "format": "SVG", "source": "banners/og_default.svg"},
            {"id": "social-square", "format": "SVG", "source": "banners/social_square.svg"},
            {"id": "watermark", "format": "SVG", "source": "brand/wordmark-watermark.svg"},
        ],
    }
    write(PACK / "AAL_VIZ_EXPORT_PRESET_REGISTRY.json", json.dumps(export_reg, indent=2) + "\n")

    # Gap ledger
    gap_path = PACK / "docs" / "AAL_VIZ_ASSET_GAP_LEDGER.csv"
    rows = [
        ("class", "planned", "shipped", "batch", "status", "notes"),
        ("identity", "10", "11", "0", "PARTIAL", ""),
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
        ("architecture_diagrams", "25", str(len(DIAGRAMS)), "3", "SHIPPED", "honesty labels"),
        ("infographics", "20", str(len(INFOGRAPHICS)), "3", "SHIPPED", "templates"),
        ("report_assets", "22", str(len(report_assets) + len(markers)), "3", "SHIPPED", ""),
        ("banners_comms", "10", "10", "3", "SHIPPED", "readme/notion/social/slides"),
        ("motion", "27", "0", "4", "DEFERRED", ""),
        ("backgrounds", "20", "0", "4", "DEFERRED", ""),
        ("responsive_pwa", "17", "0", "4", "DEFERRED", ""),
        ("marketing_showcases", "13", "0", "4", "DEFERRED", "partial via banners"),
    ]
    with gap_path.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

    # Icon registry merge
    reg_path = PACK / "AAL_VIZ_ICON_REGISTRY.json"
    reg = json.loads(reg_path.read_text(encoding="utf-8")) if reg_path.exists() else {}
    reg["diagrams"] = [d[0] for d in DIAGRAMS]
    reg["infographics"] = [i[0] for i in INFOGRAPHICS]
    reg["reports"] = [r[0] for r in report_assets] + [f"marker_{m[0]}" for m in markers]
    reg["banners"] = [b[0] for b in banners]
    write(reg_path, json.dumps(reg, indent=2) + "\n")

    print(f"Batch 3: {files} SVG files, {len(records)} records → {OUT}")


if __name__ == "__main__":
    main()
