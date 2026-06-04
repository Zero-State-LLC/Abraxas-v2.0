from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.runtime_inventory import OUT_JSON as RUNTIME_INVENTORY_JSON

ARTIFACT_TYPE = "RepoNotionDiffPacket.v1"
DIFF_ID = "REPO_NOTION_DIFF_001"
OUT_JSON = "out/audit/repo_notion_diff_001.latest.json"
OUT_MD = "out/audit/repo_notion_diff_001.latest.md"

_NOTION_TARGETS: tuple[dict[str, Any], ...] = (
    {
        "notion_surface": "PATCH-ABX-RUNTIME-INVENTORY-001",
        "target_paths": (
            "contracts/canon/runtime_inventory_packet.v1.schema.json",
            "core/runtime_inventory.py",
            "scripts/run_runtime_inventory.py",
            "tests/test_runtime_inventory.py",
            "out/audit/runtime_inventory_001.latest.json",
            "out/audit/runtime_inventory_001.latest.md",
        ),
        "recommended_action": "preserve emitted runtime inventory packet",
    },
    {
        "notion_surface": "PATCH-ABX-REPO-NOTION-DIFF-001",
        "target_paths": (
            "contracts/canon/repo_notion_diff_packet.v1.schema.json",
            "core/repo_notion_diff.py",
            "scripts/run_repo_notion_diff.py",
            "tests/test_repo_notion_diff.py",
            "out/audit/repo_notion_diff_001.latest.json",
            "out/audit/repo_notion_diff_001.latest.md",
        ),
        "recommended_action": "preserve emitted repo-notion diff packet",
    },
    {
        "notion_surface": "PATCH-ABX-YGGDRASIL-ROUTE-NAMESPACE-MAPPING-001",
        "target_paths": (
            "contracts/canon/yggdrasil_route_namespace_mapping.v1.schema.json",
            "core/yggdrasil_route_namespace_mapping.py",
            "scripts/run_yggdrasil_route_namespace_mapping.py",
            "tests/test_yggdrasil_route_namespace_mapping.py",
            "out/yggdrasil/yggdrasil_route_namespace_mapping_001.latest.json",
            "out/yggdrasil/yggdrasil_route_namespace_mapping_001.latest.md",
        ),
        "recommended_action": "map existing route surfaces before any new route design",
    },
    {
        "notion_surface": "PATCH-ABX-RUNE-EQUIVALENT-SURFACE-AUDIT-001",
        "target_paths": (
            "contracts/canon/rune_equivalent_surface_audit.v1.schema.json",
            "core/rune_equivalent_surface_audit.py",
            "scripts/run_rune_equivalent_surface_audit.py",
            "tests/test_rune_equivalent_surface_audit.py",
            "out/audit/rune_equivalent_surface_audit_001.latest.json",
            "out/audit/rune_equivalent_surface_audit_001.latest.md",
        ),
        "recommended_action": "audit rune-equivalent surfaces without registration",
    },
    {
        "notion_surface": "PATCH-ABX-BELIEF-GRAPH-GAP-VERIFICATION-001",
        "target_paths": (
            "contracts/canon/belief_graph_gap_verification.v1.schema.json",
            "core/belief_graph_gap_verification.py",
            "scripts/run_belief_graph_gap_verification.py",
            "tests/test_belief_graph_gap_verification.py",
            "out/audit/belief_graph_gap_verification_001.latest.json",
        ),
        "recommended_action": "verify gap before any Belief Graph contract plan",
        "implementation_blocked": True,
    },
    {
        "notion_surface": "AAL-Viz Projection Spine",
        "target_paths": (
            "core/aal_viz_runtime_projection.py",
            "scripts/run_aal_viz_runtime_projection.py",
            "out/projections/aal_viz.latest.json",
        ),
        "recommended_action": "align existing projection spine, do not recreate it",
    },
    {
        "notion_surface": "Global Ingest Adapter Spine",
        "target_paths": (
            "scripts/run_ingest_once.py",
            "scripts/run_oracle_intake.py",
            "core/oracle_signal.py",
        ),
        "recommended_action": "align observed ingest entrypoints before expansion",
    },
    {
        "notion_surface": "Situation Runtime",
        "target_paths": (
            "scripts/run_operator_runtime_console.py",
            "core/operator_runtime_console.py",
        ),
        "recommended_action": "keep runtime implementation deferred until upstream diff clears",
        "implementation_blocked": True,
    },
)


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _load_inventory(repo_root: Path, inventory_path: str | Path) -> dict[str, Any]:
    target = repo_root / inventory_path
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _inventory_paths(inventory: dict[str, Any]) -> set[str]:
    records = inventory.get("records", [])
    if not isinstance(records, list):
        return set()
    return {str(record.get("path")) for record in records if isinstance(record, dict) and record.get("path")}


def _path_observed(repo_root: Path, inventory_paths: set[str], target_path: str) -> bool:
    if target_path in inventory_paths:
        return True
    if (repo_root / target_path).exists():
        return True
    prefix = target_path.rstrip("/") + "/"
    return any(path.startswith(prefix) for path in inventory_paths)


def _match_strength(observed_count: int, total_count: int) -> str:
    if total_count > 0 and observed_count == total_count:
        return "EXACT"
    if observed_count > 0:
        return "PARTIAL"
    return "MISSING"


def _duplicate_risk(match_strength: str, target_paths: tuple[str, ...]) -> str:
    if match_strength == "EXACT":
        return "LOW"
    if match_strength == "PARTIAL":
        return "HIGH"
    if any(path.startswith(("core/", "contracts/", "scripts/")) for path in target_paths):
        return "MEDIUM"
    return "LOW"


def _diff_records(repo_root: Path, inventory: dict[str, Any]) -> list[dict[str, Any]]:
    inventory_paths = _inventory_paths(inventory)
    records: list[dict[str, Any]] = []
    for target in _NOTION_TARGETS:
        target_paths = tuple(str(path) for path in target["target_paths"])
        observed_paths = sorted(path for path in target_paths if _path_observed(repo_root, inventory_paths, path))
        missing_paths = sorted(path for path in target_paths if path not in observed_paths)
        match_strength = _match_strength(len(observed_paths), len(target_paths))
        records.append(
            {
                "notion_surface": str(target["notion_surface"]),
                "target_paths": list(target_paths),
                "observed_paths": observed_paths,
                "missing_paths": missing_paths,
                "match_strength": match_strength,
                "duplicate_risk": _duplicate_risk(match_strength, target_paths),
                "implementation_blocked": bool(target.get("implementation_blocked", False)),
                "recommended_action": str(target["recommended_action"]),
            }
        )
    return sorted(records, key=lambda item: item["notion_surface"])


def _summary(records: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "total_targets": len(records),
        "observed": sum(1 for record in records if record["match_strength"] == "EXACT"),
        "partial": sum(1 for record in records if record["match_strength"] == "PARTIAL"),
        "missing": sum(1 for record in records if record["match_strength"] == "MISSING"),
        "blocked": sum(1 for record in records if record["implementation_blocked"] is True),
    }


def build_repo_notion_diff(
    *,
    repo_root: str | Path,
    runtime_inventory_path: str | Path = RUNTIME_INVENTORY_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    inventory = _load_inventory(root, runtime_inventory_path)
    records = _diff_records(root, inventory)
    inventory_target = root / runtime_inventory_path
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "diff_id": DIFF_ID,
        "diff_status": "EMITTED_ADVISORY_ONLY" if inventory else "NOT_COMPUTABLE",
        "notion_source": "ABRAXAS_PATCH_QUEUE_REVISED_001",
        "patch_id": "PATCH-ABX-REPO-NOTION-DIFF-001",
        "depends_on_patch": "PATCH-ABX-RUNTIME-INVENTORY-001",
        "runtime_inventory_path": Path(runtime_inventory_path).as_posix(),
        "runtime_inventory_hash": _sha256(inventory_target),
        "match_strength_recorded": True,
        "duplicate_risk_recorded": True,
        "summary": _summary(records),
        "diff_records": records,
        "blocked_implementation_surfaces": sorted(
            record["notion_surface"] for record in records if record["implementation_blocked"] is True
        ),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "repo_mutation": False,
        "forecast_routing": False,
        "canon_mutation": False,
        "runtime_activation": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "recommended_next_patch": "PATCH-ABX-YGGDRASIL-ROUTE-NAMESPACE-MAPPING-001",
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


def write_repo_notion_diff(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)


def write_repo_notion_diff_markdown(path: str | Path, packet: dict[str, Any]) -> None:
    lines = [
        "# Repo Notion Diff",
        "",
        f"- diff_id: {packet['diff_id']}",
        f"- diff_status: {packet['diff_status']}",
        f"- runtime_inventory_path: {packet['runtime_inventory_path']}",
        f"- recommended_next_patch: {packet['recommended_next_patch']}",
        f"- repo_mutation: {packet['repo_mutation']}",
        f"- forecast_routing: {packet['forecast_routing']}",
        f"- canon_mutation: {packet['canon_mutation']}",
        f"- execution_authority: {packet['execution_authority']}",
        "",
        "## Summary",
    ]
    summary = packet.get("summary", {})
    if isinstance(summary, dict):
        for key in sorted(summary):
            lines.append(f"- {key}: {summary[key]}")
    lines.extend(["", "## Diff Records"])
    for record in packet.get("diff_records", []):
        lines.append(
            "- "
            f"{record['notion_surface']}: "
            f"{record['match_strength']} "
            f"(duplicate_risk={record['duplicate_risk']})"
        )
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
