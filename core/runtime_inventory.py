from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "RuntimeInventoryPacket.v1"
INVENTORY_ID = "RUNTIME_INVENTORY_001"
OUT_JSON = "out/audit/runtime_inventory_001.latest.json"
OUT_MD = "out/audit/runtime_inventory_001.latest.md"

_EXCLUDED_DIRS = frozenset({".git", ".mypy_cache", ".pytest_cache", "__pycache__"})
_EXCLUDED_GENERATED_OUTPUTS = frozenset(
    {
        OUT_JSON,
        OUT_MD,
        "out/audit/repo_notion_diff_001.latest.json",
        "out/audit/repo_notion_diff_001.latest.md",
        "out/yggdrasil/yggdrasil_route_namespace_mapping_001.latest.json",
        "out/yggdrasil/yggdrasil_route_namespace_mapping_001.latest.md",
        "out/audit/rune_equivalent_surface_audit_001.latest.json",
        "out/audit/rune_equivalent_surface_audit_001.latest.md",
        "out/audit/belief_graph_gap_verification_001.latest.json",
        "out/audit/belief_graph_gap_verification_001.latest.md",
        "out/audit/rune_registry_formalization_plan_001.latest.json",
        "out/audit/rune_registry_formalization_plan_001.latest.md",
    }
)
_ANCHOR_PATHS: tuple[str, ...] = (
    "README.md",
    "PLANS.md",
    "AGENTS.md",
    "core/generated_artifact_registry.py",
    "docs/status/continuity-spine.json",
    "docs/status/badges.json",
)
_INVENTORY_ROOTS: tuple[str, ...] = (
    "contracts",
    "core",
    "scripts",
    "Scripts",
    "tests",
    "out",
    "input",
    "docs/status",
    "docs/audits",
    "docs/atlas",
)
_SURFACE_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("yggdrasil_routes", ("contracts/yggdrasil/routes/",)),
    ("runtime_paths", ("core/config.py",)),
    ("generated_registry", ("core/generated_artifact_registry.py",)),
    ("research_canary", ("out/research_canary_", "core/research_canary_", "Scripts/run_research_canary_")),
    ("temporal_continuity", ("out/temporal_continuity_", "core/temporal_continuity_", "Scripts/run_temporal_continuity_")),
    ("metric_operator", ("out/metric_operator/", "core/metric_operator_", "Scripts/run_metric_operator_")),
    ("projection", ("out/projections/", "core/projection", "Scripts/run_projection")),
)


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _iter_files(repo_root: Path, rel_root: str) -> list[Path]:
    root = repo_root / rel_root
    if not root.exists():
        return []
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(repo_root).parts
        rel_path = path.relative_to(repo_root).as_posix()
        if rel_path in _EXCLUDED_GENERATED_OUTPUTS:
            continue
        if any(part in _EXCLUDED_DIRS for part in rel_parts):
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(repo_root).as_posix())


def _classify(rel_path: str) -> str:
    if rel_path.startswith("contracts/"):
        return "contract"
    if rel_path.startswith("core/"):
        return "core_module"
    if rel_path.startswith(("scripts/", "Scripts/")):
        return "runner_script"
    if rel_path.startswith("tests/"):
        return "test"
    if rel_path.startswith("out/"):
        return "generated_artifact"
    if rel_path.startswith("input/"):
        return "operator_input"
    if rel_path.startswith("docs/status/"):
        return "status_doc"
    if rel_path.startswith("docs/audits/"):
        return "audit_doc"
    if rel_path.startswith("docs/atlas/"):
        return "atlas_doc"
    return "other"


def _record(repo_root: Path, path: Path) -> dict[str, Any]:
    rel_path = path.relative_to(repo_root).as_posix()
    return {
        "path": rel_path,
        "surface_class": _classify(rel_path),
        "suffix": path.suffix,
        "sha256": _sha256(path),
        "bytes": path.stat().st_size,
    }


def _counts(records: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        surface_class = str(record["surface_class"])
        counts[surface_class] = counts.get(surface_class, 0) + 1
    return dict(sorted(counts.items()))


def _anchor_hashes(repo_root: Path) -> list[dict[str, Any]]:
    anchors: list[dict[str, Any]] = []
    for rel_path in _ANCHOR_PATHS:
        path = repo_root / rel_path
        anchors.append(
            {
                "path": rel_path,
                "observed": path.is_file(),
                "sha256": _sha256(path) if path.is_file() else "NOT_COMPUTABLE",
            }
        )
    return anchors


def _surface_categories(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    categories: dict[str, dict[str, Any]] = {}
    paths = [str(record["path"]) for record in records]
    for name, prefixes in _SURFACE_PATTERNS:
        matches = sorted(path for path in paths if path.startswith(prefixes))
        categories[name] = {
            "count": len(matches),
            "paths": matches,
        }
    return dict(sorted(categories.items()))


def _root_presence(repo_root: Path) -> list[dict[str, Any]]:
    return [
        {
            "path": rel_root,
            "observed": (repo_root / rel_root).exists(),
        }
        for rel_root in _INVENTORY_ROOTS
    ]


def build_runtime_inventory(*, repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root)
    files: list[Path] = []
    for rel_root in _INVENTORY_ROOTS:
        files.extend(_iter_files(root, rel_root))
    records = [_record(root, path) for path in sorted(set(files), key=lambda item: item.relative_to(root).as_posix())]
    missing_roots = [row["path"] for row in _root_presence(root) if row["observed"] is False]

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "inventory_id": INVENTORY_ID,
        "inventory_status": "EMITTED_ADVISORY_ONLY" if records else "NOT_COMPUTABLE",
        "notion_source": "ABRAXAS_PATCH_QUEUE_REVISED_001",
        "patch_id": "PATCH-ABX-RUNTIME-INVENTORY-001",
        "inventory_roots": list(_INVENTORY_ROOTS),
        "root_presence": _root_presence(root),
        "missing_roots": missing_roots,
        "anchor_hashes": _anchor_hashes(root),
        "surface_categories": _surface_categories(records),
        "surface_counts": _counts(records),
        "total_files": len(records),
        "records": records,
        "filesystem_read_only": True,
        "artifact_regeneration": False,
        "runtime_activation": False,
        "forecast_routing": False,
        "canon_mutation": False,
        "repo_mutation": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "valid_for_execution": False,
        "recommended_next_patch": "PATCH-ABX-REPO-NOTION-DIFF-001",
        "authority_locks": {
            "canon_mutation": False,
            "execution_authority": False,
            "forecast_routing": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "token_minting": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_runtime_inventory(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)


def write_runtime_inventory_markdown(path: str | Path, packet: dict[str, Any]) -> None:
    lines = [
        "# Runtime Inventory",
        "",
        f"- inventory_id: {packet['inventory_id']}",
        f"- inventory_status: {packet['inventory_status']}",
        f"- total_files: {packet['total_files']}",
        f"- filesystem_read_only: {packet['filesystem_read_only']}",
        f"- repo_mutation: {packet['repo_mutation']}",
        f"- artifact_regeneration: {packet['artifact_regeneration']}",
        f"- runtime_activation: {packet['runtime_activation']}",
        f"- forecast_routing: {packet['forecast_routing']}",
        f"- canon_mutation: {packet['canon_mutation']}",
        f"- recommended_next_patch: {packet['recommended_next_patch']}",
        "",
        "## Surface Counts",
    ]
    counts = packet.get("surface_counts", {})
    if isinstance(counts, dict):
        for name in sorted(counts):
            lines.append(f"- {name}: {counts[name]}")
    missing = packet.get("missing_roots", [])
    lines.extend(["", "## Missing Roots"])
    if isinstance(missing, list) and missing:
        lines.extend(f"- {item}" for item in missing)
    else:
        lines.append("- none")
    lines.extend(["", "## Surface Categories"])
    categories = packet.get("surface_categories", {})
    if isinstance(categories, dict):
        for name in sorted(categories):
            value = categories[name]
            count = value.get("count", 0) if isinstance(value, dict) else 0
            lines.append(f"- {name}: {count}")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
