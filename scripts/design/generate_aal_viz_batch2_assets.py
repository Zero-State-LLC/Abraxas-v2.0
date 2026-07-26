#!/usr/bin/env python3
"""Generate AAL-Viz Batch 2 — ABX-Rune visual system (Hallmark · Tier B SVG).

Engineering operators — not occult. Shared construction grid:
  24×24 viewBox, outer frame 22×22 @ (1,1) rx=2, stroke 1.5, round caps.
Variants: outline · solid · engrave · motion (segmented paths).

Projection-only. Does not authorize activation or canon mutation.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "design-system" / "aal-viz" / "runes"
ROOT_PACK = REPO / "design-system" / "aal-viz"
BATCH = "2"
PRODUCER = "GROK+HALLMARK"
MUTED = "#64748B"
CYAN = "#00D4F5"
PAPER = "#0B1020"


def slug_rune(rune_id: str) -> str:
    # RUNE.VIZ.ENCODE -> viz_encode
    s = rune_id.replace("RUNE.", "").lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def frame(color: str = MUTED) -> str:
    return f'  <rect x="1" y="1" width="22" height="22" rx="2" stroke="{color}" stroke-width="1" fill="none"/>\n'


def svg_wrap(body: str, label: str, *, stroke: str = "currentColor", title: str | None = None) -> str:
    t = title or label
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" '
        f'fill="none" stroke="{stroke}" stroke-width="1.5" stroke-linecap="round" '
        f'stroke-linejoin="round" role="img" aria-label="{label}" data-rune="{label}">\n'
        f"  <title>{t}</title>\n"
        f"  <desc>Engineering operator glyph. Not occult. Projection-layer visual only.</desc>\n"
        f"{body}</svg>\n"
    )


def outline(inner: str, rune_id: str) -> str:
    return svg_wrap(frame() + inner, rune_id, stroke="currentColor")


def solid(inner: str, rune_id: str) -> str:
    plate = (
        f'  <rect x="1" y="1" width="22" height="22" rx="2" fill="currentColor" opacity="0.12" stroke="{MUTED}" stroke-width="1"/>\n'
    )
    return svg_wrap(plate + inner, f"{rune_id} solid", stroke="currentColor")


def engrave(inner: str, rune_id: str) -> str:
    """One-color engravable — no dual-tone frame."""
    body = frame("currentColor") + inner
    return svg_wrap(body, f"{rune_id} engrave", stroke="currentColor")


def motion(segments: list[str], rune_id: str) -> str:
    """Motion-ready: each path is a segment for stroke-dash animation."""
    parts = [frame()]
    for i, seg in enumerate(segments):
        parts.append(f'  <g class="rune-segment" data-segment="{i}">\n{seg}  </g>\n')
    return svg_wrap("".join(parts), f"{rune_id} motion", stroke="currentColor")


# Inner geometry only (no frame). Prefer multi-path for motion variants.

def g_encode() -> tuple[str, list[str]]:
    a = '  <rect x="5" y="7" width="8" height="10" rx="1"/>\n'
    b = '  <path d="M14 9 H19 M14 12 H18 M14 15 H19"/>\n'
    c = '  <path d="M17 7 V17"/>\n'
    return a + b + c, [a, b, c]


def g_decode() -> tuple[str, list[str]]:
    a = '  <path d="M5 9 H10 M5 12 H11 M5 15 H10"/>\n'
    b = '  <path d="M8 7 V17"/>\n'
    c = '  <rect x="11" y="7" width="8" height="10" rx="1"/>\n'
    return a + b + c, [a, b, c]


def g_interpreter() -> tuple[str, list[str]]:
    a = '  <rect x="4" y="6" width="16" height="12" rx="1"/>\n'
    b = '  <path d="M7 10 L10 13 L14 9"/>\n'
    c = '  <path d="M16 14 H18"/>\n'
    return a + b + c, [a, b, c]


def g_story_bind() -> tuple[str, list[str]]:
    a = '  <path d="M6 7 H14 V11 H6 Z"/>\n'
    b = '  <path d="M10 11 V14 H18 V18 H10 Z"/>\n'
    c = '  <path d="M10 11 H14"/>\n'
    return a + b + c, [a, b, c]


def g_diagramize() -> tuple[str, list[str]]:
    a = '  <rect x="5" y="5" width="6" height="5" rx="0.5"/>\n  <rect x="13" y="5" width="6" height="5" rx="0.5"/>\n'
    b = '  <rect x="9" y="14" width="6" height="5" rx="0.5"/>\n'
    c = '  <path d="M8 10 V12 H11 M16 10 V12 H13 M12 12 V14"/>\n'
    return a + b + c, [a, b, c]


def g_infograph() -> tuple[str, list[str]]:
    a = '  <path d="M6 17 V11 M10 17 V8 M14 17 V12 M18 17 V6"/>\n'
    b = '  <path d="M5 17 H19"/>\n'
    return a + b, [a, b]


def g_cardify() -> tuple[str, list[str]]:
    a = '  <rect x="5" y="6" width="14" height="12" rx="1"/>\n'
    b = '  <path d="M8 10 H16 M8 13 H13"/>\n'
    return a + b, [a, b]


def g_access_render() -> tuple[str, list[str]]:
    a = '  <circle cx="12" cy="12" r="3"/>\n'
    b = '  <path d="M4 12 C6 7 9 5 12 5 S18 7 20 12 C18 17 15 19 12 19 S6 17 4 12 Z"/>\n'
    c = '  <path d="M12 5 V3 M12 19 V21"/>\n'
    return a + b + c, [a, b, c]


def g_flowchart() -> tuple[str, list[str]]:
    a = '  <rect x="8" y="4" width="8" height="4" rx="0.5"/>\n'
    b = '  <path d="M12 8 V11"/>\n  <path d="M12 11 L7 15 H17 L12 11 Z"/>\n'
    c = '  <path d="M12 15 V17"/>\n  <rect x="8" y="17" width="8" height="3" rx="0.5"/>\n'
    return a + b + c, [a, b, c]


def g_cognitive_load() -> tuple[str, list[str]]:
    a = '  <circle cx="12" cy="10" r="5"/>\n'
    b = '  <path d="M9 10 H15 M12 7 V13"/>\n'
    c = '  <path d="M8 17 H16 M10 19 H14"/>\n'
    return a + b + c, [a, b, c]


def g_memetic_compress() -> tuple[str, list[str]]:
    a = '  <path d="M6 8 H18 L15 12 H9 Z"/>\n'
    b = '  <path d="M9 12 H15 L13 16 H11 Z"/>\n'
    c = '  <path d="M11 16 H13 V19 H11 Z"/>\n'
    return a + b + c, [a, b, c]


def g_ingest() -> tuple[str, list[str]]:
    a = '  <path d="M12 5 V14"/>\n  <path d="M9 11 L12 14 L15 11"/>\n'
    b = '  <path d="M6 17 H18"/>\n'
    return a + b, [a, b]


def g_lineage() -> tuple[str, list[str]]:
    a = '  <circle cx="7" cy="7" r="2"/>\n  <circle cx="12" cy="12" r="2"/>\n  <circle cx="17" cy="17" r="2"/>\n'
    b = '  <path d="M8.5 8.5 L10.5 10.5 M13.5 13.5 L15.5 15.5"/>\n'
    return a + b, [a, b]


def g_belief() -> tuple[str, list[str]]:
    a = '  <circle cx="8" cy="10" r="3"/>\n  <circle cx="16" cy="10" r="3"/>\n'
    b = '  <circle cx="12" cy="16" r="3"/>\n'
    c = '  <path d="M10.5 12 L11 14 M13.5 12 L13 14"/>\n'
    return a + b + c, [a, b, c]


def g_oracle() -> tuple[str, list[str]]:
    a = '  <circle cx="12" cy="12" r="7"/>\n'
    b = '  <circle cx="12" cy="12" r="2.5"/>\n'
    c = '  <path d="M12 5 V7 M12 17 V19 M5 12 H7 M17 12 H19"/>\n'
    return a + b + c, [a, b, c]


def g_validate() -> tuple[str, list[str]]:
    a = '  <path d="M12 4 L19 7 V13 C19 16.5 15.5 19.5 12 20.5 C8.5 19.5 5 16.5 5 13 V7 Z"/>\n'
    b = '  <path d="M9 12 L11 14 L15 10"/>\n'
    return a + b, [a, b]


def g_route() -> tuple[str, list[str]]:
    a = '  <circle cx="6" cy="8" r="2"/>\n  <circle cx="18" cy="8" r="2"/>\n  <circle cx="12" cy="17" r="2"/>\n'
    b = '  <path d="M8 8 H16 M7.5 9.5 L11 15.5 M16.5 9.5 L13 15.5"/>\n'
    return a + b, [a, b]


def g_bind() -> tuple[str, list[str]]:
    a = '  <rect x="4" y="8" width="6" height="8" rx="1"/>\n  <rect x="14" y="8" width="6" height="8" rx="1"/>\n'
    b = '  <path d="M10 12 H14"/>\n'
    return a + b, [a, b]


def g_merge() -> tuple[str, list[str]]:
    a = '  <path d="M5 6 L12 12 L5 18"/>\n'
    b = '  <path d="M12 12 H19"/>\n'
    return a + b, [a, b]


def g_replay() -> tuple[str, list[str]]:
    a = '  <path d="M8 7 V17 L16 12 Z"/>\n'
    b = '  <path d="M17 7 V17"/>\n'
    return a + b, [a, b]


def g_archive() -> tuple[str, list[str]]:
    a = '  <path d="M5 8 H19 V10 H5 Z"/>\n'
    b = '  <path d="M7 10 V17 H17 V10"/>\n'
    c = '  <path d="M10 13 H14"/>\n'
    return a + b + c, [a, b, c]


def g_drift() -> tuple[str, list[str]]:
    a = '  <path d="M5 16 L9 10 L13 14 L19 6"/>\n'
    b = '  <path d="M5 18 H19" stroke-dasharray="2 2" opacity="0.6"/>\n'
    return a + b, [a, b]


def g_forecast() -> tuple[str, list[str]]:
    a = '  <path d="M5 16 C9 16 9 8 13 8 S17 16 19 16" stroke-dasharray="2 2"/>\n'
    b = '  <path d="M16 13 L19 16 L16 19"/>\n'
    return a + b, [a, b]


def g_provenance() -> tuple[str, list[str]]:
    a = '  <path d="M8 18 V8 L12 5 L16 8 V18"/>\n'
    b = '  <path d="M10 18 V13 H14 V18"/>\n'
    return a + b, [a, b]


def g_operator() -> tuple[str, list[str]]:
    a = '  <circle cx="12" cy="8" r="3"/>\n'
    b = '  <path d="M7 19 C7 14 17 14 17 19"/>\n'
    c = '  <path d="M16 6 L19 6 L19 9"/>\n'
    return a + b + c, [a, b, c]


def g_gate() -> tuple[str, list[str]]:
    a = '  <path d="M12 4 L19 8 V16 L12 20 L5 16 V8 Z"/>\n'
    b = '  <path d="M9 12 H15"/>\n'
    return a + b, [a, b]


def g_receipt() -> tuple[str, list[str]]:
    a = '  <rect x="7" y="4" width="10" height="16" rx="1"/>\n'
    b = '  <path d="M10 9 H14 M10 12 H14 M10 15 L12 16 L14 14"/>\n'
    return a + b, [a, b]


def g_ledger() -> tuple[str, list[str]]:
    a = '  <rect x="5" y="5" width="14" height="14" rx="1"/>\n'
    b = '  <path d="M5 9 H19 M5 13 H19 M5 17 H19 M9 5 V19"/>\n'
    return a + b, [a, b]


def g_canon() -> tuple[str, list[str]]:
    a = '  <path d="M12 4 L19 8 V16 L12 20 L5 16 V8 Z"/>\n'
    b = '  <path d="M12 8 V16 M9 11 H15"/>\n'
    return a + b, [a, b]


def g_shadow() -> tuple[str, list[str]]:
    a = '  <circle cx="10" cy="12" r="5"/>\n'
    b = '  <path d="M14 8 A5 5 0 0 1 14 16" opacity="0.85"/>\n'
    return a + b, [a, b]


# (rune_id, family, purpose, geometry_fn)
RUNES: list[tuple[str, str, str, callable]] = [
    # P0 AAL-Viz-specific
    ("RUNE.VIZ.ENCODE", "aal_viz", "Encode projection payload for viz surface", g_encode),
    ("RUNE.VIZ.DECODE", "aal_viz", "Decode projection payload for inspection", g_decode),
    ("RUNE.VIZ.INTERPRETER", "aal_viz", "Interpret structured projection for operator view", g_interpreter),
    ("RUNE.VIZ.STORY_BIND", "aal_viz", "Bind narrative segments to evidence packets", g_story_bind),
    ("RUNE.DIAGRAMIZE", "aal_viz", "Render relational structure as diagram primitives", g_diagramize),
    ("RUNE.INFOGRAPH", "aal_viz", "Compose metric blocks into infographic layout", g_infograph),
    ("RUNE.CARDIFY", "aal_viz", "Package projection slice as operator card", g_cardify),
    ("RUNE.ACCESS_RENDER", "aal_viz", "Render access-safe projection (read/copy constraints)", g_access_render),
    ("RUNE.FLOWCHART", "aal_viz", "Emit flowchart topology from declared routes", g_flowchart),
    ("RUNE.COGNITIVE_LOAD.SCORE", "aal_viz", "Score cognitive load of a projection surface", g_cognitive_load),
    ("RUNE.MEMETIC.COMPRESS", "aal_viz", "Compress memetic payload for short projection", g_memetic_compress),
    # P1 shared system runes (AAL-Viz visible)
    ("RUNE.INGEST", "shared", "Ingest source into evidence lane", g_ingest),
    ("RUNE.LINEAGE", "shared", "Trace artifact lineage", g_lineage),
    ("RUNE.BELIEF", "shared", "Belief-graph operator", g_belief),
    ("RUNE.ORACLE", "shared", "Oracle signal operator", g_oracle),
    ("RUNE.VALIDATE", "shared", "Validation gate operator", g_validate),
    ("RUNE.ROUTE", "shared", "Route through topology", g_route),
    ("RUNE.BIND", "shared", "Bind two surfaces", g_bind),
    ("RUNE.MERGE", "shared", "Merge streams", g_merge),
    ("RUNE.REPLAY", "shared", "Replay historical run", g_replay),
    ("RUNE.ARCHIVE", "shared", "Archive artifact", g_archive),
    ("RUNE.DRIFT", "shared", "Detect drift", g_drift),
    ("RUNE.FORECAST", "shared", "Forecast lane (non-canonical)", g_forecast),
    ("RUNE.PROVENANCE", "shared", "Provenance enforce/view", g_provenance),
    ("RUNE.OPERATOR", "shared", "Operator intervention", g_operator),
    ("RUNE.GATE", "shared", "Authority/doctrine gate", g_gate),
    ("RUNE.RECEIPT", "shared", "Execution receipt", g_receipt),
    ("RUNE.LEDGER", "shared", "Ledger entry surface", g_ledger),
    ("RUNE.CANON", "shared", "Canon spine marker", g_canon),
    ("RUNE.SHADOW", "shared", "Shadow lane marker", g_shadow),
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
    variants: list[str] = field(default_factory=lambda: ["outline", "solid", "engrave", "motion"])
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
    purpose: str = ""
    rune_family: str = ""


def main() -> None:
    records: list[AssetRecord] = []
    registry_entries: list[dict] = []
    files = 0

    for rune_id, family, purpose, geo_fn in RUNES:
        stem = slug_rune(rune_id)
        sub = "aal_viz" if family == "aal_viz" else "shared"
        base = OUT / sub
        inner, segs = geo_fn()

        paths = {
            "outline": base / f"{stem}.svg",
            "solid": base / f"{stem}.solid.svg",
            "engrave": base / f"{stem}.engrave.svg",
            "motion": base / f"{stem}.motion.svg",
        }
        write(paths["outline"], outline(inner, rune_id))
        write(paths["solid"], solid(inner, rune_id))
        write(paths["engrave"], engrave(inner, rune_id))
        write(paths["motion"], motion(segs, rune_id))
        files += 4

        rels = [f"runes/{sub}/{p.name}" for p in paths.values()]
        export = [f"design-system/aal-viz/{r}" for r in rels]
        records.append(
            AssetRecord(
                asset_id=f"AALVIZ-RUNE-{stem.upper()}",
                name=stem,
                category="rune",
                semantic_role=rune_id,
                alt_text=f"{rune_id}: {purpose}",
                source_file=export[0],
                export_files=export,
                purpose=purpose,
                rune_family=family,
            )
        )
        registry_entries.append(
            {
                "rune_id": rune_id,
                "semantic_role": purpose,
                "family": family,
                "stem": stem,
                "lane_hint": "PROJECTION" if family == "aal_viz" else "SHARED",
                "authority_implication": "NONE",
                "construction": {
                    "grid": "24x24",
                    "frame": "22x22@1,1 rx=2",
                    "stroke": 1.5,
                    "sizes_px": [16, 24, 48],
                },
                "variants": {
                    "outline": f"design-system/aal-viz/runes/{sub}/{stem}.svg",
                    "solid": f"design-system/aal-viz/runes/{sub}/{stem}.solid.svg",
                    "engrave": f"design-system/aal-viz/runes/{sub}/{stem}.engrave.svg",
                    "motion": f"design-system/aal-viz/runes/{sub}/{stem}.motion.svg",
                },
                "motion_segments": len(segs),
                "legacy_glyph_map_ref": "design-system/runes/glyph_map.v1.json",
                "notes": "AAL-Viz authored pack; does not replace contract catalog unless mapped EXACT",
            }
        )

    rune_registry = {
        "schema_version": "AALVizRuneRegistry.v1",
        "batch": BATCH,
        "status": "SHIPPED_CANDIDATE",
        "construction_grid": {
            "viewBox": "0 0 24 24",
            "frame": {"x": 1, "y": 1, "w": 22, "h": 22, "rx": 2},
            "stroke_width": 1.5,
            "stroke_linecap": "round",
            "stroke_linejoin": "round",
            "optical_sizes_px": [16, 24, 48],
            "variants": ["outline", "solid", "engrave", "motion"],
            "forbidden": ["occult motifs", "unique decorative language per rune", "baked glow"],
        },
        "count": len(registry_entries),
        "aal_viz_count": sum(1 for e in registry_entries if e["family"] == "aal_viz"),
        "shared_count": sum(1 for e in registry_entries if e["family"] == "shared"),
        "entries": registry_entries,
        "existing_system_runes": "design-system/runes/glyphs/",
        "contract_catalog": "contracts/runes/catalog.v1.json",
    }
    write(ROOT_PACK / "AAL_VIZ_RUNE_REGISTRY.json", json.dumps(rune_registry, indent=2) + "\n")

    manifest = {
        "schema_version": "AALVizAssetManifest.v1",
        "name": "aal-viz-batch2-runes",
        "batch": BATCH,
        "version": "0.1.0",
        "updated": "2026-07-19",
        "hallmark": {
            "genre": "atmospheric-technical",
            "theme": "custom (Abraxas projection grammar)",
            "enrichment": "Tier B hand-built SVG · engineering rune alphabet",
        },
        "producer_system": PRODUCER,
        "asset_count": len(records),
        "file_count_approx": files,
        "assets": [asdict(r) for r in records],
    }
    write(ROOT_PACK / "aal_viz_asset_manifest.batch2.v1.json", json.dumps(manifest, indent=2) + "\n")

    # Gap ledger update
    gap_path = ROOT_PACK / "docs" / "AAL_VIZ_ASSET_GAP_LEDGER.csv"
    rows = [
        ("class", "planned", "shipped", "batch", "status", "notes"),
        ("identity", "10", "11", "0", "PARTIAL", "SVG masters"),
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
        ("runes", "30", str(len(RUNES)), "2", "SHIPPED", "4 variants each; aal_viz+shared"),
        ("motion", "27", "0", "4", "DEFERRED", "rune.motion segments ready for wiring"),
        ("marketing", "23", "0", "3", "DEFERRED", ""),
        ("architecture_diagrams", "25", "0", "3", "DEFERRED", ""),
    ]
    with gap_path.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

    # Icon registry merge
    reg_path = ROOT_PACK / "AAL_VIZ_ICON_REGISTRY.json"
    reg = json.loads(reg_path.read_text(encoding="utf-8")) if reg_path.exists() else {}
    reg["runes_aal_viz"] = [slug_rune(r[0]) for r in RUNES if r[1] == "aal_viz"]
    reg["runes_shared"] = [slug_rune(r[0]) for r in RUNES if r[1] == "shared"]
    write(reg_path, json.dumps(reg, indent=2) + "\n")

    print(f"Batch 2: {files} SVG files, {len(RUNES)} runes → {OUT}")


if __name__ == "__main__":
    main()
