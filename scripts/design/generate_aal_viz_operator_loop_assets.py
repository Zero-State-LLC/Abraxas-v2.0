#!/usr/bin/env python3
"""Generate AAL-Viz operator-loop visual assets (Hallmark · Tier B SVG).

Functional systems glyphs for the multi-agent operator loop — not mascots.
Producer identity is provenance only; does not grant authority.

Companion to: docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PACK = REPO / "design-system" / "aal-viz"
OUT = PACK / "operator_loop"
BATCH = "0.5"
PRODUCER = "GROK+HALLMARK"
PAPER = "#0B1020"
MUTED = "#64748B"
CYAN = "#00D4F5"
VIOLET = "#A78BFA"
AMBER = "#F59E0B"
TEAL = "#2DD4BF"
GOLD = "#F2C14E"
INK = "#E8EEF7"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def icon(body: str, label: str, view: int = 24) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view} {view}" '
        f'width="{view}" height="{view}" fill="none" stroke="currentColor" '
        f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
        f'role="img" aria-label="{label}">\n'
        f"  <title>{label}</title>\n"
        f"  <desc>Operator-loop systems glyph. Projection only. No authority grant.</desc>\n"
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


# ── Role glyphs (24×24) ─────────────────────────────────────────────────────

ROLE_GLYPHS: list[tuple[str, str, str]] = [
    (
        "human_operator",
        "Human operator",
        # person + decision diamond
        "  <circle cx=\"12\" cy=\"7\" r=\"3\"/>\n"
        "  <path d=\"M6 20 C6 14 18 14 18 20\"/>\n"
        "  <path d=\"M17 5 L20 8 L17 11 L14 8 Z\" opacity=\"0.85\"/>\n",
    ),
    (
        "hermes_orchestrator",
        "Hermes orchestrator",
        # hub with three routed rays (routing, not authority crown)
        "  <circle cx=\"12\" cy=\"12\" r=\"3\"/>\n"
        "  <path d=\"M12 5 V8 M5 12 H8 M16 12 H19\"/>\n"
        "  <path d=\"M7 7 L9.5 9.5 M17 7 L14.5 9.5 M7 17 L9.5 14.5 M17 17 L14.5 14.5\"/>\n"
        "  <circle cx=\"12\" cy=\"4\" r=\"1\" fill=\"currentColor\" stroke=\"none\"/>\n"
        "  <circle cx=\"4\" cy=\"12\" r=\"1\" fill=\"currentColor\" stroke=\"none\"/>\n"
        "  <circle cx=\"20\" cy=\"12\" r=\"1\" fill=\"currentColor\" stroke=\"none\"/>\n",
    ),
    (
        "grok_producer",
        "Grok producer",
        # divergent fan (exploration) + single output
        "  <path d=\"M12 18 V10\"/>\n"
        "  <path d=\"M12 10 L6 5 M12 10 L12 4 M12 10 L18 5\"/>\n"
        "  <circle cx=\"12\" cy=\"18\" r=\"2\"/>\n"
        "  <circle cx=\"6\" cy=\"5\" r=\"1.5\"/>\n"
        "  <circle cx=\"12\" cy=\"4\" r=\"1.5\"/>\n"
        "  <circle cx=\"18\" cy=\"5\" r=\"1.5\"/>\n",
    ),
    (
        "codex_cursor_producer",
        "Codex/Cursor producer",
        # precise bracket + check (repo-grounded implementation)
        "  <path d=\"M8 5 H6 V19 H8\"/>\n"
        "  <path d=\"M16 5 H18 V19 H16\"/>\n"
        "  <path d=\"M10 12 L12 14 L15 10\"/>\n",
    ),
    (
        "github_implementation_truth",
        "GitHub implementation truth",
        # branch graph (implementation source of truth)
        "  <circle cx=\"8\" cy=\"7\" r=\"2\"/>\n"
        "  <circle cx=\"8\" cy=\"17\" r=\"2\"/>\n"
        "  <circle cx=\"16\" cy=\"12\" r=\"2\"/>\n"
        "  <path d=\"M8 9 V15 M10 7 C14 7 14 12 14 12\"/>\n",
    ),
    (
        "notion_architecture_truth",
        "Notion architecture truth",
        # document + structure lines (architecture source of truth)
        "  <rect x=\"6\" y=\"4\" width=\"12\" height=\"16\" rx=\"1\"/>\n"
        "  <path d=\"M9 9 H15 M9 12 H15 M9 15 H13\"/>\n",
    ),
    (
        "ci_validator",
        "CI validator",
        # shield + check (deterministic technical evidence)
        "  <path d=\"M12 3 L19 6 V12 C19 16 15 19.5 12 20.5 C9 19.5 5 16 5 12 V6 Z\"/>\n"
        "  <path d=\"M9 12 L11 14 L15 10\"/>\n",
    ),
    (
        "aal_viz_projection",
        "AAL-Viz projection",
        # viewport plane + nodes (read-only projection)
        "  <path d=\"M5 17 L12 6 L19 17 Z\"/>\n"
        "  <circle cx=\"12\" cy=\"13\" r=\"2\"/>\n"
        "  <circle cx=\"9\" cy=\"11\" r=\"1\" fill=\"currentColor\" stroke=\"none\"/>\n"
        "  <circle cx=\"15\" cy=\"11\" r=\"1\" fill=\"currentColor\" stroke=\"none\"/>\n",
    ),
]


# ── Graph nodes ─────────────────────────────────────────────────────────────

LOOP_NODES: list[tuple[str, str, str]] = [
    (
        "work_packet",
        "Work packet node",
        "  <rect x=\"4\" y=\"5\" width=\"16\" height=\"14\" rx=\"2\"/>\n"
        "  <path d=\"M8 10 H16 M8 14 H13\"/>\n",
    ),
    (
        "handoff",
        "Handoff node",
        "  <circle cx=\"8\" cy=\"12\" r=\"3\"/>\n"
        "  <circle cx=\"16\" cy=\"12\" r=\"3\"/>\n"
        "  <path d=\"M11 12 H13\"/>\n"
        "  <path d=\"M13 10 L15 12 L13 14\"/>\n",
    ),
    (
        "integration",
        "Integration node",
        "  <path d=\"M5 8 L12 5 L19 8 V16 L12 19 L5 16 Z\"/>\n"
        "  <path d=\"M9 12 L11 14 L15 10\"/>\n",
    ),
    (
        "conflict",
        "Conflict node",
        "  <path d=\"M12 4 L20 18 H4 Z\"/>\n"
        "  <path d=\"M12 10 V13\"/>\n"
        "  <circle cx=\"12\" cy=\"15.5\" r=\"0.8\" fill=\"currentColor\" stroke=\"none\"/>\n",
    ),
    (
        "operator_decision",
        "Operator decision node",
        "  <path d=\"M12 3 L21 12 L12 21 L3 12 Z\"/>\n"
        "  <path d=\"M12 8 V13\"/>\n"
        "  <circle cx=\"12\" cy=\"15.5\" r=\"0.8\" fill=\"currentColor\" stroke=\"none\"/>\n",
    ),
]


# ── Edges ───────────────────────────────────────────────────────────────────

LOOP_EDGES: list[tuple[str, str, str]] = [
    (
        "assignment",
        "Assignment edge",
        "  <path d=\"M3 12 H17\"/>\n"
        "  <path d=\"M14 9 L17 12 L14 15\"/>\n"
        "  <circle cx=\"6\" cy=\"12\" r=\"1.5\" fill=\"currentColor\" stroke=\"none\"/>\n",
    ),
    (
        "peer_review",
        "Peer review edge",
        "  <path d=\"M4 10 H16\"/>\n"
        "  <path d=\"M16 10 L13 7\"/>\n"
        "  <path d=\"M20 14 H8\"/>\n"
        "  <path d=\"M8 14 L11 17\"/>\n",
    ),
    (
        "validation",
        "Validation edge",
        "  <path d=\"M3 12 H14\"/>\n"
        "  <path d=\"M11 9 L14 12 L11 15\"/>\n"
        "  <path d=\"M17 9 L19 11 L22 8\"/>\n",
    ),
    (
        "handoff_edge",
        "Handoff edge",
        "  <path d=\"M3 12 H10\" stroke-dasharray=\"2 2\"/>\n"
        "  <circle cx=\"12\" cy=\"12\" r=\"2\"/>\n"
        "  <path d=\"M14 12 H17\"/>\n"
        "  <path d=\"M14 9 L17 12 L14 15\"/>\n",
    ),
    (
        "merge",
        "Merge edge",
        "  <path d=\"M4 7 L11 12 L4 17\"/>\n"
        "  <path d=\"M11 12 H19\"/>\n"
        "  <path d=\"M16 9 L19 12 L16 15\"/>\n",
    ),
    (
        "blocked_dependency",
        "Blocked dependency edge",
        "  <path d=\"M3 12 H14\"/>\n"
        "  <path d=\"M10 9 L14 15 M14 9 L10 15\"/>\n"
        "  <path d=\"M16 12 H20\" opacity=\"0.4\" stroke-dasharray=\"2 2\"/>\n",
    ),
]


# ── Provenance badges ───────────────────────────────────────────────────────

def badge(label: str, color: str = "currentColor") -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 88 24" width="88" height="24" role="img" aria-label="Producer provenance {label}">
  <title>{label}</title>
  <desc>Producer identity is provenance only. Does not grant authority.</desc>
  <rect x="1" y="1" width="86" height="22" rx="4" fill="none" stroke="{color}" stroke-width="1.5"/>
  <text x="44" y="16" text-anchor="middle" font-family="IBM Plex Mono, ui-monospace, monospace" font-size="10" letter-spacing="0.12em" fill="{color}">{label}</text>
</svg>
"""


PROVENANCE = [
    ("HERMES", CYAN),
    ("GROK", VIOLET),
    ("CODEX", TEAL),
    ("MIXED", GOLD),
    ("HUMAN", AMBER),
]


# ── Work states ─────────────────────────────────────────────────────────────

WORK_STATES: list[tuple[str, str, str]] = [
    ("active", "ACTIVE", "  <circle cx=\"12\" cy=\"12\" r=\"7\"/>\n  <circle cx=\"12\" cy=\"12\" r=\"2.5\" fill=\"currentColor\" stroke=\"none\"/>\n"),
    ("waiting", "WAITING", "  <circle cx=\"12\" cy=\"12\" r=\"7\"/>\n  <path d=\"M12 8 V12 L15 14\"/>\n"),
    ("blocked", "BLOCKED", "  <circle cx=\"12\" cy=\"12\" r=\"7\"/>\n  <path d=\"M8 8 L16 16\" stroke-width=\"2\"/>\n"),
    ("review", "REVIEW", "  <circle cx=\"12\" cy=\"12\" r=\"7\"/>\n  <path d=\"M12 8 V13\"/>\n  <circle cx=\"12\" cy=\"16\" r=\"0.8\" fill=\"currentColor\" stroke=\"none\"/>\n"),
    ("integrated", "INTEGRATED", "  <circle cx=\"12\" cy=\"12\" r=\"7\"/>\n  <path d=\"M8 12 L11 15 L16 9\"/>\n"),
    ("superseded", "SUPERSEDED", "  <circle cx=\"12\" cy=\"12\" r=\"7\" opacity=\"0.55\"/>\n  <path d=\"M8 8 L16 16 M16 8 L8 16\" opacity=\"0.7\"/>\n"),
]


def loop_diagram() -> str:
    w, h = 960, 420
    stages = [
        "INTAKE", "CONTEXT", "CLASSIFY", "DECOMPOSE", "ROUTE", "PRODUCE",
        "VALIDATE", "RECONCILE", "OP REVIEW", "INTEGRATE", "SEAL", "CONTINUE",
    ]
    body = f'  <rect width="{w}" height="{h}" fill="{PAPER}"/>\n'
    body += f'  <rect x="0" y="0" width="{w}" height="3" fill="{CYAN}"/>\n'
    body += f'  <text x="24" y="28" font-family="IBM Plex Mono, monospace" font-size="11" letter-spacing="0.16em" fill="{AMBER}">IMPLEMENTED SYSTEM MAP · PROJECTION ONLY</text>\n'
    body += f'  <text x="24" y="56" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="20" font-weight="600" fill="{INK}">Canonical multi-agent operator loop</text>\n'
    body += f'  <text x="24" y="80" font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" fill="{MUTED}">Producer identity = provenance only · Operator retains merge/deploy authority</text>\n'
    # two rows of 6
    for i, name in enumerate(stages):
        row, col = divmod(i, 6)
        x = 28 + col * 155
        y = 120 + row * 110
        body += f'  <rect x="{x}" y="{y}" width="140" height="44" rx="6" fill="#121A2A" stroke="{CYAN if row == 0 else TEAL}" stroke-width="1.5"/>\n'
        body += f'  <text x="{x + 12}" y="{y + 27}" font-family="IBM Plex Mono, monospace" font-size="11" fill="{INK}">{name}</text>\n'
        if col < 5:
            body += f'  <path d="M{x + 140} {y + 22} H{x + 155}" stroke="{MUTED}" stroke-width="1.5"/>\n'
            body += f'  <path d="M{x + 150} {y + 18} L{x + 155} {y + 22} L{x + 150} {y + 26}" stroke="{MUTED}" stroke-width="1.5" fill="none"/>\n'
        elif row == 0:
            # wrap to next row
            body += f'  <path d="M{x + 70} {y + 44} V{y + 66}" stroke="{MUTED}" stroke-width="1.5"/>\n'
    body += f'  <text x="24" y="{h - 24}" font-family="IBM Plex Mono, monospace" font-size="10" letter-spacing="0.1em" fill="{MUTED}">AAL-VIZ · OPERATOR LOOP · NO EXECUTION AUTHORITY</text>\n'
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Canonical multi-agent operator loop">
  <title>Canonical multi-agent operator loop</title>
{body}</svg>
"""


def main() -> None:
    records: list[AssetRecord] = []
    files = 0

    def rec(name: str, category: str, role: str, alt: str, rel: str, sizes: list[int] | None = None) -> None:
        records.append(
            AssetRecord(
                asset_id=f"AALVIZ-OPLOOP-{name.upper()}",
                name=name,
                category=category,
                semantic_role=role,
                alt_text=alt,
                source_file=f"design-system/aal-viz/{rel}",
                export_files=[f"design-system/aal-viz/{rel}"],
                sizes=sizes or [16, 24, 48],
            )
        )

    # Roles
    for name, alt, body in ROLE_GLYPHS:
        rel = f"operator_loop/roles/{name}.svg"
        write(PACK / rel, icon(body, alt))
        solid = (
            f'  <rect x="1" y="1" width="22" height="22" rx="4" fill="currentColor" opacity="0.12" stroke="none"/>\n'
            + body
        )
        write(PACK / f"operator_loop/roles/{name}.solid.svg", icon(solid, f"{alt} (solid)"))
        rec(name, "operator_loop_role", name.upper(), alt, rel)
        files += 2

    # Nodes
    for name, alt, body in LOOP_NODES:
        rel = f"operator_loop/nodes/{name}.svg"
        write(PACK / rel, icon(body, alt))
        rec(name, "operator_loop_node", name.upper(), alt, rel)
        files += 1

    # Edges
    for name, alt, body in LOOP_EDGES:
        rel = f"operator_loop/edges/{name}.svg"
        write(PACK / rel, icon(body, alt))
        rec(name, "operator_loop_edge", name.upper(), alt, rel)
        files += 1

    # Provenance badges
    for label, color in PROVENANCE:
        name = f"badge_{label.lower()}"
        rel = f"operator_loop/badges/{name}.svg"
        write(PACK / rel, badge(label, color))
        rec(name, "operator_loop_badge", label, f"Producer provenance {label}", rel, sizes=[88, 24])
        files += 1

    # Work states
    for name, role, body in WORK_STATES:
        rel = f"operator_loop/work_states/{name}.svg"
        write(PACK / rel, icon(body, f"Work state {role}"))
        rec(name, "operator_loop_work_state", role, f"Work state {role}", rel)
        files += 1

    # Diagram
    rel = "operator_loop/diagrams/canonical_operator_loop.svg"
    write(PACK / rel, loop_diagram())
    rec("canonical_operator_loop", "operator_loop_diagram", "OPERATOR_LOOP", "Canonical multi-agent operator loop", rel, sizes=[960, 420])
    files += 1

    # Manifest
    manifest = {
        "schema_version": "AALVizAssetManifest.v1",
        "name": "aal-viz-operator-loop",
        "batch": BATCH,
        "version": "0.1.0",
        "updated": "2026-07-26",
        "companion_spec": "docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md",
        "hallmark": {
            "genre": "atmospheric-technical",
            "enrichment": "Tier B systems glyphs (not mascots)",
            "rule": "Producer identity records provenance; it does not grant authority.",
        },
        "producer_system": PRODUCER,
        "asset_count": len(records),
        "file_count_approx": files,
        "assets": [asdict(r) for r in records],
    }
    write(PACK / "aal_viz_asset_manifest.operator_loop.v1.json", json.dumps(manifest, indent=2) + "\n")

    # Registry merge
    reg_path = PACK / "AAL_VIZ_ICON_REGISTRY.json"
    reg = json.loads(reg_path.read_text(encoding="utf-8")) if reg_path.exists() else {}
    reg["operator_loop_roles"] = [r[0] for r in ROLE_GLYPHS]
    reg["operator_loop_nodes"] = [n[0] for n in LOOP_NODES]
    reg["operator_loop_edges"] = [e[0] for e in LOOP_EDGES]
    reg["operator_loop_badges"] = [f"badge_{p[0].lower()}" for p in PROVENANCE]
    reg["operator_loop_work_states"] = [w[0] for w in WORK_STATES]
    write(reg_path, json.dumps(reg, indent=2) + "\n")

    # Gap ledger append note
    gap = PACK / "docs" / "AAL_VIZ_ASSET_GAP_LEDGER.csv"
    if gap.exists():
        text = gap.read_text(encoding="utf-8").rstrip() + "\n"
        if "operator_loop" not in text:
            text += f"operator_loop,{len(records)},{files},{BATCH},SHIPPED,roles+nodes+edges+badges+states+diagram\n"
            gap.write_text(text, encoding="utf-8")

    # Inventory snippet file
    write(
        PACK / "operator_loop/README.md",
        """# Operator-loop visual set

Companion to [`docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md`](../../../docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md).

**Rule:** Producer identity records provenance. It does **not** grant authority.

## Layout

| Path | Contents |
|------|----------|
| `roles/` | Human, Hermes, Grok, Codex/Cursor, GitHub, Notion, CI, AAL-Viz |
| `nodes/` | Work packet, handoff, integration, conflict, operator decision |
| `edges/` | Assignment, peer review, validation, handoff, merge, blocked dependency |
| `badges/` | HERMES · GROK · CODEX · MIXED · HUMAN |
| `work_states/` | ACTIVE · WAITING · BLOCKED · REVIEW · INTEGRATED · SUPERSEDED |
| `diagrams/` | Canonical loop map |

Regenerate: `python scripts/design/generate_aal_viz_operator_loop_assets.py`
""",
    )

    print(f"Operator loop assets: {files} files, {len(records)} records → {OUT}")


if __name__ == "__main__":
    main()
