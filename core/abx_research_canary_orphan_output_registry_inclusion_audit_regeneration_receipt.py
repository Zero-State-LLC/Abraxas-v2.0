from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_research_canary_artifact_registry_coverage_audit import (
    AUDIT_ID,
    OUT_JSON as AUDIT_JSON_PATH,
    OUT_MD as AUDIT_MD_PATH,
    build_abx_research_canary_artifact_registry_coverage_audit,
    write_abx_research_canary_artifact_registry_coverage_audit,
)
from core.abx_research_canary_orphan_output_registry_inclusion_constants import ORPHAN_OUTPUT_JSON_PATHS
from core.abx_research_canary_orphan_output_registry_inclusion_scoped_execution_receipt import (
    AUDIT_REGENERATION_LANE,
    RECEIPT_JSON_PATH as SCOPED_RECEIPT_JSON_PATH,
)
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxResearchCanaryOrphanOutputRegistryInclusionAuditRegenerationReceipt.v1"
RECEIPT_ID = AUDIT_REGENERATION_LANE
RECEIPT_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt_001.latest.json"
)
RECEIPT_MD_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt_001.latest.md"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _audit_snapshot(audit: Mapping[str, Any]) -> dict[str, Any]:
    coverage = audit.get("coverage_summary", {})
    if not isinstance(coverage, dict):
        coverage = {}
    return {
        "audit_hash": str(audit.get("audit_hash", NOT_COMPUTABLE)),
        "audit_status": str(audit.get("audit_status", NOT_COMPUTABLE)),
        "orphan_research_output_count": coverage.get("orphan_research_output_count"),
    }


def _scoped_receipt_ready(scoped_receipt: Mapping[str, Any]) -> bool:
    return (
        scoped_receipt.get("schema_version") == "AbxResearchCanaryOrphanOutputRegistryInclusionScopedExecutionReceipt.v1"
        and scoped_receipt.get("status")
        == "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_SCOPED_EXECUTION_RECEIPT_EMITTED"
        and scoped_receipt.get("registry_mutation_performed") is True
        and scoped_receipt.get("recommended_next_lane") == RECEIPT_ID
    )


def _post_regeneration_valid(post_audit: Mapping[str, Any]) -> bool:
    coverage = post_audit.get("coverage_summary", {})
    if not isinstance(coverage, dict):
        return False
    return (
        post_audit.get("audit_id") == AUDIT_ID
        and coverage.get("orphan_research_output_count") == 0
        and coverage.get("lane_id_gap_count") == 0
        and coverage.get("output_path_gap_count") == 0
    )


def build_abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    scoped_receipt = _read_json(root / SCOPED_RECEIPT_JSON_PATH)
    pre_audit = _read_json(root / AUDIT_JSON_PATH)
    scoped_ready = _scoped_receipt_ready(scoped_receipt)
    pre_snapshot = _audit_snapshot(pre_audit) if pre_audit else {}
    post_audit = build_abx_research_canary_artifact_registry_coverage_audit(repo_root=root) if scoped_ready else {}
    post_snapshot = _audit_snapshot(post_audit) if post_audit else {}
    regeneration_verified = scoped_ready and _post_regeneration_valid(post_audit) if post_audit else False

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": RECEIPT_ID,
        "status": (
            "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_AUDIT_REGENERATION_RECEIPT_EMITTED"
            if regeneration_verified
            else "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_AUDIT_REGENERATION_RECEIPT_BLOCKED"
        ),
        "receipt_id": "abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt_001",
        "command": "BUILD_ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_AUDIT_REGENERATION_RECEIPT_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "source_scoped_execution_receipt": {
            "path": str(SCOPED_RECEIPT_JSON_PATH),
            "hash": str(scoped_receipt.get("receipt_hash", NOT_COMPUTABLE)),
            "status": str(scoped_receipt.get("status", NOT_COMPUTABLE)),
            "observed": scoped_ready,
        },
        "authorization_scope": "SCOPED_ORPHAN_OUTPUT_REGISTRY_INCLUSION_AUDIT_REGENERATION_ONLY",
        "audit_regeneration_performed": regeneration_verified,
        "included_orphan_path_count": len(ORPHAN_OUTPUT_JSON_PATHS),
        "pre_regeneration_audit": {"audit_path": str(AUDIT_JSON_PATH), **pre_snapshot},
        "post_regeneration_audit": post_snapshot if scoped_ready else {},
        "audit_transition": {
            "orphan_research_output_count_before": pre_snapshot.get("orphan_research_output_count", NOT_COMPUTABLE),
            "orphan_research_output_count_after": post_snapshot.get("orphan_research_output_count", NOT_COMPUTABLE),
        },
        "governance_preservation": {
            "p130_hold_preserved": True,
            "research_canary_spine_refresh_performed": False,
            "repair_chain_remains_sealed": True,
        },
        "downstream_status": "ORPHAN_INCLUSION_CHAIN_COMPLETE" if regeneration_verified else NOT_COMPUTABLE,
        "recommended_next_lane": NOT_COMPUTABLE,
    }
    return {**packet, "receipt_hash": canonical_hash(packet)}


def render_markdown(packet: Mapping[str, Any]) -> list[str]:
    return [
        "# ABX Research Canary Orphan Output Registry Inclusion Audit Regeneration Receipt 001",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `downstream_status`: `{packet['downstream_status']}`",
        f"- `included_orphan_path_count`: `{packet['included_orphan_path_count']}`",
    ]


def write_abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
    *,
    write_audit: bool = True,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    scoped_receipt = _read_json(root / SCOPED_RECEIPT_JSON_PATH)
    if _scoped_receipt_ready(scoped_receipt) and write_audit:
        write_abx_research_canary_artifact_registry_coverage_audit(source_root=root, out_root=target_root)
    packet = build_abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt(root)
    write_canonical_json(target_root / RECEIPT_JSON_PATH, packet)
    _write_markdown(target_root / RECEIPT_MD_PATH, render_markdown(packet))
    return packet
