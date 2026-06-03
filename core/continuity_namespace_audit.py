from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ContinuityNamespaceAudit.v1"
AUDIT_ID = "CONTINUITY_NAMESPACE_AUDIT_001"
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"
BADGES_PATH = "docs/status/badges.json"
P102G_PATH = "out/temporal_continuity_historical_recovery_audit/latest.json"
OUT_PATH = "out/continuity_namespace_audit/latest.json"

P_LANE_RE = re.compile(r"(?<![A-Z0-9])P(?P<number>\d{1,3})(?P<suffix>[A-Z])?(?=$|[^A-Z0-9])")
PATH_REF_RE = re.compile(
    r"(?P<path>(?:core|scripts|contracts|tests|out|docs|Scripts)/[A-Za-z0-9_./-]+"
    r"(?:\.py|\.json|\.md|\.js))"
)

_TEXT_SUFFIXES = {
    ".cfg",
    ".css",
    ".html",
    ".js",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yml",
    ".yaml",
}

_DENIED_AUTHORITY: tuple[str, ...] = (
    "authorization_authority",
    "authorization_record_creation_authority",
    "canon_promotion",
    "execution_authority",
    "forecast_influence",
    "production_activation",
    "record_creation_authority",
    "runtime_authority",
    "scheduler_mutation",
    "token_minting_authority",
)

_REQUIRED_SURFACE_SUFFIXES: tuple[tuple[str, str], ...] = (
    ("core", ".py"),
    ("runner", ".py"),
    ("contract", ".json"),
    ("test", ".py"),
    ("artifact", ".json"),
)


def _read_json(root: Path, rel_path: str) -> dict[str, Any]:
    path = root / rel_path
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _file_hash(root: Path, rel_path: str) -> str:
    path = root / rel_path
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _git_lines(root: Path, args: list[str]) -> list[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return []
    return [line for line in completed.stdout.splitlines() if line]


def _tracked_files(root: Path) -> list[str]:
    files = _git_lines(root, ["ls-files", "--cached", "--others", "--exclude-standard"])
    if files:
        return sorted(path for path in files if path != OUT_PATH)
    return sorted(
        rel_path
        for path in root.rglob("*")
        for rel_path in [path.relative_to(root).as_posix()]
        if path.is_file() and ".git" not in path.parts and rel_path != OUT_PATH
    )


def _is_text_path(path: str) -> bool:
    return Path(path).suffix in _TEXT_SUFFIXES


def _read_text(root: Path, rel_path: str) -> str:
    try:
        return (root / rel_path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _namespace_for_path(path: str) -> str:
    lowered = path.lower()
    if "temporal_continuity" in lowered or lowered.startswith("docs/plans/p102"):
        return "TEMPORAL_CONTINUITY"
    if "research_canary" in lowered or "research_shadow" in lowered or "research_boundary" in lowered or "research_promotion" in lowered:
        return "RESEARCH_CANARY"
    if "operator_narrative" in lowered or lowered.startswith("out/archive/"):
        return "OPERATOR_NARRATIVE_ARCHIVE"
    if "chamfer" in lowered:
        return "CHAMFER_METRIC"
    if "metric_operator" in lowered:
        return "METRIC_OPERATOR"
    if "yggdrasil" in lowered or "rune" in lowered:
        return "YGGDRASIL"
    if "aal_viz" in lowered or "projection" in lowered:
        return "AAL_VIZ_PROJECTION"
    if "artifact_contract" in lowered or lowered.startswith("out/contracts/"):
        return "ARTIFACT_CONTRACT"
    if lowered.startswith("docs/plans/"):
        return "PLANNING_DOCS"
    return "GENERAL_REPO"


def _extract_p_lane_refs(text: str) -> list[str]:
    return [f"P{match.group('number')}{match.group('suffix') or ''}" for match in P_LANE_RE.finditer(text)]


def _p_number(lane_id: str) -> str:
    match = P_LANE_RE.match(lane_id)
    if not match:
        return "NOT_COMPUTABLE"
    return f"P{match.group('number')}"


def _continuity_lane_ids(spine: dict[str, Any]) -> set[str]:
    lanes = spine.get("continuity_lanes")
    if not isinstance(lanes, list):
        return set()
    lane_ids: set[str] = set()
    for item in lanes:
        if isinstance(item, dict) and isinstance(item.get("lane_id"), str):
            lane_ids.add(item["lane_id"])
    return lane_ids


def _source_state(root: Path) -> dict[str, Any]:
    spine = _read_json(root, CONTINUITY_SPINE_PATH)
    badges = _read_json(root, BADGES_PATH)
    p102g = _read_json(root, P102G_PATH)
    signals = badges.get("signals") if isinstance(badges.get("signals"), dict) else {}
    return {
        "canon": signals.get("canon_status", p102g.get("canon_status", "NOT_COMPUTABLE")),
        "downstream": p102g.get("observed_current_downstream", p102g.get("recommended_next_lane", "NOT_COMPUTABLE")),
        "governance": signals.get("governance_status", p102g.get("governance_status", "NOT_COMPUTABLE")),
        "highest_observed_lane": spine.get("highest_lane", p102g.get("observed_current_highest_lane", "NOT_COMPUTABLE")),
        "lane_count": spine.get("lane_count", "NOT_COMPUTABLE"),
        "source_hashes": {
            BADGES_PATH: _file_hash(root, BADGES_PATH),
            CONTINUITY_SPINE_PATH: _file_hash(root, CONTINUITY_SPINE_PATH),
            P102G_PATH: _file_hash(root, P102G_PATH),
        },
    }


def _scan_lane_references(root: Path, tracked_files: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, set[str]]]:
    by_lane: dict[str, dict[str, Any]] = {}
    p_number_namespaces: dict[str, set[str]] = defaultdict(set)
    for path in tracked_files:
        if not _is_text_path(path):
            continue
        text = _read_text(root, path)
        if not text:
            continue
        namespace = _namespace_for_path(path)
        for lane_id in _extract_p_lane_refs(text):
            record = by_lane.setdefault(
                lane_id,
                {
                    "lane_id": lane_id,
                    "p_number": _p_number(lane_id),
                    "namespaces": set(),
                    "occurrence_count": 0,
                    "paths": defaultdict(int),
                },
            )
            record["namespaces"].add(namespace)
            record["occurrence_count"] += 1
            record["paths"][path] += 1
            p_number_namespaces[_p_number(lane_id)].add(namespace)

    inventory: list[dict[str, Any]] = []
    namespace_map: dict[str, dict[str, Any]] = {}
    for lane_id, record in sorted(by_lane.items(), key=lambda item: (_p_number(item[0]), item[0])):
        paths = [
            {"path": path, "occurrence_count": count, "namespace": _namespace_for_path(path)}
            for path, count in sorted(record["paths"].items())
        ]
        namespaces = sorted(record["namespaces"])
        inventory.append(
            {
                "lane_id": lane_id,
                "p_number": record["p_number"],
                "namespaces": namespaces,
                "occurrence_count": record["occurrence_count"],
                "path_count": len(paths),
                "paths": paths,
            }
        )
        for namespace in namespaces:
            ns = namespace_map.setdefault(
                namespace,
                {
                    "namespace_id": namespace,
                    "lane_ids": set(),
                    "p_numbers": set(),
                    "reference_count": 0,
                    "path_count": 0,
                    "paths": set(),
                },
            )
            ns["lane_ids"].add(lane_id)
            ns["p_numbers"].add(record["p_number"])
            ns["reference_count"] += record["occurrence_count"]
            for path_row in paths:
                if path_row["namespace"] == namespace:
                    ns["paths"].add(path_row["path"])

    namespaces_out = []
    for namespace, record in sorted(namespace_map.items()):
        namespaces_out.append(
            {
                "namespace_id": namespace,
                "lane_ids": sorted(record["lane_ids"], key=lambda value: (_p_number(value), value)),
                "p_numbers": sorted(record["p_numbers"]),
                "reference_count": record["reference_count"],
                "path_count": len(record["paths"]),
                "paths": sorted(record["paths"]),
            }
        )
    return namespaces_out, inventory, p_number_namespaces


def _collisions(inventory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    branch_namespaces = {
        "AAL_VIZ_PROJECTION",
        "ARTIFACT_CONTRACT",
        "CHAMFER_METRIC",
        "METRIC_OPERATOR",
        "OPERATOR_NARRATIVE_ARCHIVE",
        "RESEARCH_CANARY",
        "TEMPORAL_CONTINUITY",
        "YGGDRASIL",
    }
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in inventory:
        grouped[record["p_number"]].append(record)
    out: list[dict[str, Any]] = []
    for p_number, records in sorted(grouped.items()):
        namespaces = sorted(
            {
                namespace
                for record in records
                for namespace in record["namespaces"]
                if namespace in branch_namespaces
            }
        )
        lane_ids = sorted({record["lane_id"] for record in records}, key=lambda value: (_p_number(value), value))
        semantic_branch_count = len(namespaces)
        if semantic_branch_count <= 1:
            continue
        out.append(
            {
                "p_number": p_number,
                "lane_ids": lane_ids,
                "namespaces": namespaces,
                "semantic_branch_count": semantic_branch_count,
                "collision_type": "P_NUMBER_NAMESPACE_COLLISION",
                "resolution_required": True,
            }
        )
    return out


def _walk_json_strings(value: Any, *, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], str]]:
    if isinstance(value, str):
        return [(path, value)]
    if isinstance(value, dict):
        rows: list[tuple[tuple[str, ...], str]] = []
        for key in sorted(value):
            rows.extend(_walk_json_strings(value[key], path=(*path, key)))
        return rows
    if isinstance(value, list):
        rows = []
        for index, item in enumerate(value):
            rows.extend(_walk_json_strings(item, path=(*path, str(index))))
        return rows
    return []


def _recommended_next_lane_references(root: Path, tracked_files: list[str], observed_lanes: set[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    docs_plan_prefixes = {
        path.split("/", 2)[-1].split("_", 1)[0]
        for path in tracked_files
        if path.startswith("docs/plans/P") and "_" in path
    }
    references: list[dict[str, Any]] = []
    orphaned: list[dict[str, Any]] = []
    for path in tracked_files:
        if not path.endswith(".json"):
            continue
        payload = _read_json(root, path)
        if not payload:
            continue
        for key_path, value in _walk_json_strings(payload):
            if not key_path or key_path[-1] != "recommended_next_lane":
                continue
            lane_match = P_LANE_RE.search(value)
            extracted_lane = lane_match.group(0) if lane_match else "NOT_COMPUTABLE"
            if value == "NOT_COMPUTABLE":
                status = "FAIL_CLOSED_TERMINAL"
            elif extracted_lane != "NOT_COMPUTABLE" and (
                extracted_lane in observed_lanes or extracted_lane in docs_plan_prefixes
            ):
                status = "RESOLVED_TO_OBSERVED_LANE"
            elif extracted_lane != "NOT_COMPUTABLE":
                status = "MISSING_REPO_EVIDENCE"
            else:
                status = "NON_LANE_TERMINAL_MARKER"
            row = {
                "path": path,
                "json_pointer": "/" + "/".join(key_path),
                "recommended_next_lane": value,
                "extracted_lane_id": extracted_lane,
                "resolution_status": status,
            }
            references.append(row)
            if status == "MISSING_REPO_EVIDENCE":
                orphaned.append(row)
    return references, orphaned


def _missing_referenced_paths(root: Path, tracked_files: list[str]) -> list[dict[str, Any]]:
    missing: dict[str, set[str]] = defaultdict(set)
    for path in tracked_files:
        if not _is_text_path(path):
            continue
        text = _read_text(root, path)
        for match in PATH_REF_RE.finditer(text):
            ref = match.group("path")
            if not (root / ref).exists():
                missing[ref].add(path)
    return [
        {"referenced_path": ref, "referenced_by": sorted(sources), "missing": True}
        for ref, sources in sorted(missing.items())
    ]


def _surface_completeness(root: Path, namespaces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for namespace in namespaces:
        ns = namespace["namespace_id"]
        if ns not in {"TEMPORAL_CONTINUITY", "RESEARCH_CANARY", "OPERATOR_NARRATIVE_ARCHIVE", "CHAMFER_METRIC"}:
            continue
        missing = []
        for lane_id in namespace["lane_ids"]:
            lane_paths = [path for path in namespace["paths"] if lane_id.lower() in path.lower()]
            if not lane_paths:
                continue
            observed_types = set()
            for path in lane_paths:
                if path.startswith("core/") and path.endswith(".py"):
                    observed_types.add("core")
                if path.startswith("scripts/run_") and path.endswith(".py"):
                    observed_types.add("runner")
                if path.startswith("contracts/") and path.endswith(".json"):
                    observed_types.add("contract")
                if path.startswith("tests/") and path.endswith(".py"):
                    observed_types.add("test")
                if path.startswith("out/") and path.endswith(".json"):
                    observed_types.add("artifact")
            missing_types = [name for name, _suffix in _REQUIRED_SURFACE_SUFFIXES if name not in observed_types]
            if missing_types:
                missing.append({"lane_id": lane_id, "missing_surface_types": missing_types})
        if missing:
            rows.append({"namespace_id": ns, "missing_surfaces": missing})
    return rows


def _ambiguous_identifiers(collisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for collision in collisions:
        rows.append(
            {
                "identifier": collision["p_number"],
                "ambiguity_type": "GLOBAL_NUMERIC_P_LANE_REUSED_ACROSS_NAMESPACES",
                "namespaces": collision["namespaces"],
                "lane_ids": collision["lane_ids"],
                "requires_composite_namespace": True,
            }
        )
    return rows


def build_continuity_namespace_audit(repo_root: Path | str | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    tracked_files = _tracked_files(root)
    spine = _read_json(root, CONTINUITY_SPINE_PATH)
    observed_lanes = _continuity_lane_ids(spine)
    source_state = _source_state(root)
    observed_namespaces, inventory, _p_number_namespaces = _scan_lane_references(root, tracked_files)
    collision_rows = _collisions(inventory)
    recommended_refs, orphaned_refs = _recommended_next_lane_references(root, tracked_files, observed_lanes)
    missing_paths = _missing_referenced_paths(root, tracked_files)
    missing_surfaces = _surface_completeness(root, observed_namespaces)
    ambiguous = _ambiguous_identifiers(collision_rows)
    global_safe = not collision_rows and not ambiguous
    selected_policy = "D_HYBRID_CANONICAL_GLOBAL_IDS_WITH_BRANCH_LOCAL_ALIASES"
    if global_safe:
        selected_policy = "A_GLOBALLY_UNIQUE_NUMERIC_P_LANES"

    packet: dict[str, Any] = {
        "advisory_only": True,
        "ambiguous_identifiers": ambiguous,
        "artifact_type": ARTIFACT_TYPE,
        "audit_id": AUDIT_ID,
        "audit_only": True,
        "authority_locks": {name: False for name in _DENIED_AUTHORITY},
        "authorization_authority": False,
        "authorization_granted": False,
        "authorization_record_created": False,
        "authorization_record_creation_authority": False,
        "canon_promotion": False,
        "collisions": collision_rows,
        "denied_authority": list(_DENIED_AUTHORITY),
        "execution_authority": False,
        "forecast_influence": False,
        "global_p_numbering_safe": global_safe,
        "lane_reference_inventory": inventory,
        "missing_referenced_surfaces": {
            "missing_path_references": missing_paths,
            "missing_required_surface_types": missing_surfaces,
        },
        "mock_data": False,
        "namespace_policy_recommendation": {
            "evaluated_options": [
                {
                    "option": "A",
                    "policy": "globally_unique_numeric_p_lanes",
                    "recommended": global_safe,
                    "reason": "Safe only when no numeric P-lane is reused across semantic namespaces.",
                },
                {
                    "option": "B",
                    "policy": "namespace_scoped_p_lanes",
                    "recommended": False,
                    "reason": "Solves collisions but weakens existing global continuity surfaces unless paired with canonical IDs.",
                },
                {
                    "option": "C",
                    "policy": "composite_lane_ids",
                    "recommended": False,
                    "reason": "Composite IDs remove ambiguity but require a migration surface before becoming canonical.",
                },
                {
                    "option": "D",
                    "policy": "hybrid_canonical_global_ids_plus_branch_local_aliases",
                    "recommended": not global_safe,
                    "reason": "Preserves current global lane history while requiring composite namespace aliases for branch-local P-number reuse.",
                },
            ],
            "recommended_policy": selected_policy,
            "required_future_rule": "Use composite namespace aliases for branch-local references that reuse a numeric P-lane already observed in another semantic namespace.",
        },
        "observed_namespaces": observed_namespaces,
        "orphaned_references": orphaned_refs,
        "production_activation": False,
        "projection_only": True,
        "recommended_next_action": "ADOPT_HYBRID_NAMESPACE_POLICY_BEFORE_ANY_NEW_CONTINUITY_NUMBERING" if not global_safe else "MAINTAIN_GLOBAL_NUMERIC_P_LANE_POLICY",
        "recommended_next_lane": "NOT_COMPUTABLE",
        "recommended_next_lane_references": recommended_refs,
        "record_creation_authority": False,
        "runtime_authority": False,
        "scheduler_mutation": False,
        "source_state": source_state,
        "token_minting_allowed": False,
        "token_minting_authority": False,
        "valid_for_execution": False,
    }
    packet["packet_hash"] = canonical_hash(packet)
    return packet


def write_continuity_namespace_audit(path: Path | str, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
