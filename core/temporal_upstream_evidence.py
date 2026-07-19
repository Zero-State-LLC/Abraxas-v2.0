"""Deterministic upstream evidence receipt for temporal coherence chain."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json
from core.config import RuntimePaths
from core.temporal_state_diff import _surface_paths_from_runtime_paths

RECEIPT_ID = "temporal_upstream_evidence_001"


def _artifact_dependencies(paths: RuntimePaths) -> list[dict[str, str]]:
    return [
        {
            "artifact_key": "temporal_state_diff",
            "path": paths.temporal_state_diff_latest.as_posix(),
            "dependency_class": "required",
            "dependency_required": "true",
            "producer_script": "scripts/temporal/run_temporal_state_diff.py",
            "lineage_role": "required_child",
        },
        {
            "artifact_key": "cross_run_topology_fusion",
            "path": paths.cross_run_topology_fusion_latest.as_posix(),
            "dependency_class": "required",
            "dependency_required": "true",
            "producer_script": "scripts/run_cross_run_topology_fusion.py",
            "lineage_role": "required_child",
        },
        {
            "artifact_key": "live_projection_refresh",
            "path": paths.live_projection_refresh_latest.as_posix(),
            "dependency_class": "required",
            "dependency_required": "true",
            "producer_script": "scripts/viz/run_live_projection_refresh.py",
            "consumed_by": "temporal_state_diff",
            "lineage_role": "required_parent",
        },
        {
            "artifact_key": "universal_ingest_receipt",
            "path": (paths.out_dir / "ingest" / "universal_ingest_receipt_001.latest.json").as_posix(),
            "dependency_class": "optional",
            "dependency_required": "false",
            "source": "universal_ingest",
            "lane": "SHADOW",
            "lineage_role": "optional_parent",
        },
        {
            "artifact_key": "universal_ingest_validation_result",
            "path": (paths.out_dir / "ingest" / "universal_ingest.validation_result.latest.json").as_posix(),
            "dependency_class": "optional",
            "dependency_required": "false",
            "source": "universal_ingest",
            "lane": "SHADOW",
            "lineage_role": "optional_parent",
        },
        {
            "artifact_key": "universal_ingest_conflict_report",
            "path": (paths.out_dir / "ingest" / "universal_ingest.conflict_report.latest.json").as_posix(),
            "dependency_class": "optional",
            "dependency_required": "false",
            "source": "universal_ingest",
            "lane": "SHADOW",
            "lineage_role": "optional_parent",
        },
    ]


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _hash_sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _classify_state(*, exists: bool, readable: bool, observed_status: str | None) -> str:
    if not exists:
        return "MISSING"
    if not readable:
        return "UNREADABLE"
    if observed_status == "NOT_COMPUTABLE":
        return "AVAILABLE_DEGRADED"
    return "AVAILABLE"


def build_temporal_upstream_evidence_receipt() -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    temporal_state_diff_sources = _surface_paths_from_runtime_paths(paths)
    checked: list[dict[str, Any]] = []
    for dep in _artifact_dependencies(paths):
        path = Path(dep["path"])
        exists = path.exists()
        payload = _read_json(path) if exists else None
        readable = payload is not None
        observed_status = (
            str(payload.get("final_status"))
            if isinstance(payload, dict) and "final_status" in payload
            else None
        )
        if observed_status is None and isinstance(payload, dict):
            observed_status = str(payload.get("status")) if "status" in payload else None
        blockers = payload.get("remaining_blockers") if isinstance(payload, dict) else None
        if not isinstance(blockers, list):
            blockers = []
        evidence_state = _classify_state(
            exists=exists,
            readable=readable,
            observed_status=observed_status,
        )
        entry = {
            **dep,
            "artifact_path": dep["path"],
            "exists": exists,
            "readable": readable,
            "hash_sha256": _hash_sha256(path) if readable else None,
            "hash": _hash_sha256(path) if readable else None,
            "observed_status": observed_status,
            "status": observed_status,
            "blockers": sorted(str(item) for item in blockers),
            "evidence_state": evidence_state,
            "advisory_only": True,
            "authority_granted": False,
            "forecast_authority": False,
            "mutation_allowed": False,
        }
        if dep["artifact_key"] == "live_projection_refresh":
            expected = temporal_state_diff_sources["live_projection_refresh"].as_posix()
            entry["temporal_state_diff_expected_path"] = expected
            entry["path_consumption_match"] = dep["path"] == expected
        checked.append(entry)

    required = [item for item in checked if item["dependency_class"] == "required"]
    required_states = {item["evidence_state"] for item in required}
    if "MISSING" in required_states or "UNREADABLE" in required_states:
        final = "NOT_READY"
    elif "AVAILABLE_DEGRADED" in required_states:
        final = "DEGRADED_READY"
    else:
        final = "READY"

    lineage_assertions = {
        "live_projection_refresh_consumed_by_temporal_state_diff": any(
            item.get("artifact_key") == "live_projection_refresh"
            and item.get("path_consumption_match") is True
            for item in checked
        )
    }

    return {
        "schema_version": "TemporalUpstreamEvidenceReceipt.v1",
        "receipt_id": RECEIPT_ID,
        "checked_artifacts": checked,
        "lineage_assertions": lineage_assertions,
        "final_evidence_status": final,
        "governance_flags": {
            "evidence_only": True,
            "advisory_only": True,
            "non_authoritative": True,
            "mutation_allowed": False,
            "authority_granted": False,
            "forecast_authority": False,
            "auto_execute": False,
            "command_channel": False,
        },
    }


def build_temporal_upstream_evidence_markdown(receipt: dict[str, Any]) -> str:
    lines = [
        "# Temporal Upstream Evidence Receipt",
        "",
        f"- receipt_id: `{receipt['receipt_id']}`",
        f"- final_evidence_status: `{receipt['final_evidence_status']}`",
        "",
        "## Checked Artifacts",
        "",
    ]
    for item in receipt["checked_artifacts"]:
        lines.append(
            f"- `{item['artifact_key']}` → `{item['evidence_state']}` ({item['dependency_class']})"
        )
    lines.extend([
        "",
        "## Lineage Assertions",
        f"- live_projection_refresh_consumed_by_temporal_state_diff: `{receipt.get('lineage_assertions', {}).get('live_projection_refresh_consumed_by_temporal_state_diff')}`",
    ])
    return "\n".join(lines) + "\n"


def write_temporal_upstream_evidence_receipt(path: Path, receipt: dict[str, Any]) -> None:
    write_canonical_json(path, receipt)
    path.with_suffix(".md").write_text(
        build_temporal_upstream_evidence_markdown(receipt), encoding="utf-8"
    )
