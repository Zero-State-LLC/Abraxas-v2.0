#!/usr/bin/env python3
"""Inventory ghost ``scripts/**/run_*.py`` path strings (advisory).

Classifies references in core/, scripts/, and tests/:
  - RELOCATABLE: basename exists under a domain package
  - MISSING_PLAN_ONLY: no runner on disk (historical/planned)
  - TEST_FIXTURE_PLACEHOLDER: synthetic names used only in tests

Does not invent runners. Safe to re-run anytime.
"""
from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.canonical.json import canonical_hash, write_canonical_json  # noqa: E402

OUT_JSON = ROOT / "out/production_readiness/scripts_ghost_path_inventory.v1.json"
OUT_MD = ROOT / "out/production_readiness/scripts_ghost_path_inventory.v1.md"

PATH_RE = re.compile(r"\bscripts/(?:[a-z0-9_]+/)?run_[a-zA-Z0-9_]+\.py\b")
FIXTURE_ALLOW = re.compile(
    r"run_(foo|bar|a|b|target|example|shared|missing_surface|surface)\.py$"
)


def _existing_runners(repo: Path) -> dict[str, list[str]]:
    by_name: dict[str, list[str]] = {}
    scripts = repo / "scripts"
    if not scripts.is_dir():
        return by_name
    for path in scripts.rglob("run_*.py"):
        rel = path.relative_to(repo).as_posix()
        by_name.setdefault(path.name, []).append(rel)
    return by_name


def _scan(
    repo: Path, roots: list[str], existing: dict[str, list[str]]
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for root_name in roots:
        root = repo / root_name
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            rel = path.relative_to(repo).as_posix()
            for match in PATH_RE.finditer(text):
                ref = match.group(0)
                if (repo / ref).exists():
                    continue
                base = Path(ref).name
                if base in existing:
                    kind = "RELOCATABLE"
                    locations = sorted(existing[base])
                elif FIXTURE_ALLOW.search(base):
                    kind = "TEST_FIXTURE_PLACEHOLDER"
                    locations = []
                else:
                    kind = "MISSING_PLAN_ONLY"
                    locations = []
                findings.append(
                    {
                        "source_file": rel,
                        "referenced_path": ref,
                        "basename": base,
                        "kind": kind,
                        "existing_locations": locations,
                    }
                )
    return findings


def build_inventory(repo: Path | None = None) -> dict[str, Any]:
    root = Path(repo) if repo is not None else ROOT
    existing = _existing_runners(root)
    core_findings = _scan(root, ["core", "scripts"], existing)
    test_findings = _scan(root, ["tests"], existing)

    def _by_kind(rows: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for row in rows:
            counts[row["kind"]] = counts.get(row["kind"], 0) + 1
        return dict(sorted(counts.items()))

    core_missing = [f for f in core_findings if f["kind"] == "MISSING_PLAN_ONLY"]
    packet: dict[str, Any] = {
        "schema_version": "ScriptsGhostPathInventory.v1",
        "inventory_id": "SCRIPTS_GHOST_PATH_INVENTORY_001",
        "produced_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "producer": "scripts/tools/run_scripts_ghost_path_inventory.py",
        "advisory_only": True,
        "projection_only": True,
        "authority_granted": False,
        "mutation_allowed": False,
        "summary": {
            "core_scripts_hits": len(core_findings),
            "tests_hits": len(test_findings),
            "by_kind_core_scripts": _by_kind(core_findings),
            "by_kind_tests": _by_kind(test_findings),
            "unique_missing_basenames_core": sorted(
                {f["basename"] for f in core_missing}
            ),
            "relocatable_count_core": sum(
                1 for f in core_findings if f["kind"] == "RELOCATABLE"
            ),
        },
        "policy": {
            "do_not_invent_runners": True,
            "historical_plan_strings_allowed": True,
            "action": (
                "MISSING_PLAN_ONLY: leave or annotate as planned/not landed. "
                "RELOCATABLE: rewrite to existing domain path. "
                "TEST_FIXTURE_PLACEHOLDER: ignore."
            ),
        },
        "core_and_scripts_findings": core_findings,
        "test_findings_count": len(test_findings),
        "test_findings_sample": test_findings[:40],
    }
    packet["inventory_hash"] = canonical_hash(
        {k: v for k, v in packet.items() if k != "inventory_hash"}
    )
    return packet


def render_markdown(packet: dict[str, Any]) -> str:
    findings = packet["core_and_scripts_findings"]
    lines = [
        "# Scripts Ghost Path Inventory v1",
        "",
        f"- inventory_id: `{packet['inventory_id']}`",
        f"- produced_at: `{packet['produced_at']}`",
        f"- core/scripts hits: **{packet['summary']['core_scripts_hits']}**",
        f"- tests hits: **{packet['summary']['tests_hits']}**",
        (
            "- unique missing basenames (core/scripts): "
            f"**{len(packet['summary']['unique_missing_basenames_core'])}**"
        ),
        f"- relocatable (core/scripts): **{packet['summary']['relocatable_count_core']}**",
        "",
        "## Policy",
        "",
        "- Do **not** invent stub runners to silence strings.",
        "- `MISSING_PLAN_ONLY`: historical/planned path; leave or annotate.",
        "- `RELOCATABLE`: basename exists under a domain — rewrite reference.",
        "- `TEST_FIXTURE_PLACEHOLDER`: synthetic names in tests — ignore.",
        "",
        "## Core / scripts findings",
        "",
    ]
    if not findings:
        lines.append("_None._")
    else:
        lines.append("| Kind | Source | Referenced path |")
        lines.append("|------|--------|-----------------|")
        for row in findings:
            lines.append(
                f"| {row['kind']} | `{row['source_file']}` | `{row['referenced_path']}` |"
            )
    lines.extend(["", "## Unique missing basenames (core/scripts)", ""])
    for name in packet["summary"]["unique_missing_basenames_core"]:
        lines.append(f"- `{name}`")
    lines.extend(
        [
            "",
            "## Regenerate",
            "",
            "```bash",
            "python scripts/tools/run_scripts_ghost_path_inventory.py",
            "```",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    packet = build_inventory(ROOT)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    write_canonical_json(OUT_JSON, packet)
    OUT_MD.write_text(render_markdown(packet), encoding="utf-8")
    summary = packet["summary"]
    print(
        {
            "status": "OK",
            "core_scripts_hits": summary["core_scripts_hits"],
            "tests_hits": summary["tests_hits"],
            "unique_missing_basenames_core": len(
                summary["unique_missing_basenames_core"]
            ),
            "relocatable_count_core": summary["relocatable_count_core"],
            "output_json": str(OUT_JSON.relative_to(ROOT)),
            "output_md": str(OUT_MD.relative_to(ROOT)),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
