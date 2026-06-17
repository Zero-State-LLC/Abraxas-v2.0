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
from core.abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt import (
    COVERAGE_AUDIT_REGENERATION_LANE,
    RECEIPT_JSON_PATH as SCOPED_EXECUTION_RECEIPT_JSON_PATH,
)
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxResearchCanaryArtifactRegistryCoverageAuditRegenerationReceipt.v1"
RECEIPT_ID = "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_AUDIT_REGENERATION_RECEIPT_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt_001.latest.json"
)
RECEIPT_MD_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt_001.latest.md"
)
PRE_REPAIR_AUDIT_FIXTURE_PATH = Path(
    "tests/fixtures/abx_research_canary_artifact_registry_coverage_audit_001_pre_repair.latest.json"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"

BLOCKED_ACTIONS = [
    "RESEARCH_CANARY_SPINE_REFRESH",
    "RESEARCH_CANARY_ARTIFACT_REGENERATION",
    "P130_ACTIVATION",
    "ORPHAN_OUTPUT_REGISTRY_INCLUSION",
    "SCOPE_PREFIX_MUTATION_WITHOUT_OPERATOR_DECISION",
    "RUNTIME_MUTATION",
    "CANON_MUTATION",
    "QUEUE_MUTATION",
    "LIVE_NOTION_WRITEBACK",
    "GITHUB_WRITEBACK_AUTOMATION",
    "UNSCOPED_REGISTRY_REPAIR_EXECUTION",
    "DIRECT_REGISTRY_REPAIR",
]


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


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
        "direct_registry_lane_id_coverage": coverage.get("direct_registry_lane_id_coverage"),
        "lane_id_gap_count": coverage.get("lane_id_gap_count"),
        "output_path_gap_count": coverage.get("output_path_gap_count"),
        "orphan_research_output_count": coverage.get("orphan_research_output_count"),
    }


def _scoped_receipt_ready(scoped_receipt: Mapping[str, Any]) -> bool:
    return (
        scoped_receipt.get("schema_version")
        == "AbxResearchCanaryArtifactRegistryCoverageRepairScopedExecutionReceipt.v1"
        and scoped_receipt.get("status")
        == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_SCOPED_EXECUTION_RECEIPT_EMITTED"
        and scoped_receipt.get("repair_execution_performed") is True
        and scoped_receipt.get("registry_mutation_performed") is True
        and (
            scoped_receipt.get("recommended_next_lane") == COVERAGE_AUDIT_REGENERATION_LANE
            or scoped_receipt.get("downstream_status") == "COVERAGE_AUDIT_REGENERATION_OBSERVED"
        )
    )


def _historical_pre_snapshot(root: Path, existing_regen: Mapping[str, Any]) -> dict[str, Any] | None:
    if (
        existing_regen.get("status")
        == "RESEARCH_CANARY_REGISTRY_COVERAGE_AUDIT_REGENERATION_RECEIPT_EMITTED"
        and isinstance(existing_regen.get("pre_regeneration_audit"), dict)
    ):
        return dict(existing_regen["pre_regeneration_audit"])
    fixture_path = root / PRE_REPAIR_AUDIT_FIXTURE_PATH
    if fixture_path.is_file():
        return _audit_snapshot(_read_json(fixture_path))
    return None


def _post_regeneration_valid(post_audit: Mapping[str, Any]) -> bool:
    coverage = post_audit.get("coverage_summary", {})
    if not isinstance(coverage, dict):
        return False
    return (
        post_audit.get("audit_id") == AUDIT_ID
        and post_audit.get("audit_status") == NOT_COMPUTABLE
        and coverage.get("direct_registry_lane_id_coverage") is True
        and coverage.get("lane_id_gap_count") == 0
        and coverage.get("output_path_gap_count") == 0
        and coverage.get("orphan_research_output_count") == 10
    )


def build_abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    scoped_receipt = _read_json(root / SCOPED_EXECUTION_RECEIPT_JSON_PATH)
    pre_audit = _read_json(root / AUDIT_JSON_PATH)
    existing_regen = _read_json(root / RECEIPT_JSON_PATH)
    scoped_ready = _scoped_receipt_ready(scoped_receipt)
    current_pre_snapshot = _audit_snapshot(pre_audit)
    if (
        current_pre_snapshot.get("audit_status") == NOT_COMPUTABLE
        and current_pre_snapshot.get("lane_id_gap_count") == 0
    ):
        pre_snapshot = _historical_pre_snapshot(root, existing_regen) or current_pre_snapshot
    else:
        pre_snapshot = current_pre_snapshot
    post_audit = build_abx_research_canary_artifact_registry_coverage_audit(repo_root=root) if scoped_ready else {}
    post_snapshot = _audit_snapshot(post_audit) if post_audit else {}
    pre_gap_confirmed = (
        pre_snapshot.get("audit_status") == "RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_GAP_CONFIRMED"
    )
    post_repair_ready = _post_regeneration_valid(post_audit) if post_audit else False
    regeneration_verified = scoped_ready and post_repair_ready and pre_gap_confirmed

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": RECEIPT_ID,
        "status": (
            "RESEARCH_CANARY_REGISTRY_COVERAGE_AUDIT_REGENERATION_RECEIPT_EMITTED"
            if regeneration_verified
            else "RESEARCH_CANARY_REGISTRY_COVERAGE_AUDIT_REGENERATION_RECEIPT_BLOCKED"
        ),
        "receipt_id": "abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt_001",
        "receipt_hash": "",
        "command": "BUILD_ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_AUDIT_REGENERATION_RECEIPT_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "source_scoped_execution_receipt": {
            "source_scoped_execution_receipt_path": str(SCOPED_EXECUTION_RECEIPT_JSON_PATH),
            "source_scoped_execution_receipt_hash": str(scoped_receipt.get("receipt_hash", NOT_COMPUTABLE)),
            "source_status": str(scoped_receipt.get("status", NOT_COMPUTABLE)),
            "source_scoped_execution_receipt_ready": scoped_ready,
        },
        "authorization_scope": "SCOPED_RESEARCH_CANARY_REGISTRY_COVERAGE_AUDIT_REGENERATION_ONLY",
        "audit_regeneration_performed": regeneration_verified,
        "execution_allowed": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "safe_to_auto_continue": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "github_writeback_allowed": False,
        "notion_writeback_allowed": False,
        "pre_regeneration_audit": {
            "audit_path": str(AUDIT_JSON_PATH),
            **pre_snapshot,
        },
        "post_regeneration_audit": post_snapshot if scoped_ready else {},
        "audit_transition": {
            "audit_status_before": pre_snapshot.get("audit_status", NOT_COMPUTABLE),
            "audit_status_after": post_snapshot.get("audit_status", NOT_COMPUTABLE),
            "lane_id_gap_count_before": pre_snapshot.get("lane_id_gap_count", NOT_COMPUTABLE),
            "lane_id_gap_count_after": post_snapshot.get("lane_id_gap_count", NOT_COMPUTABLE),
            "output_path_gap_count_before": pre_snapshot.get("output_path_gap_count", NOT_COMPUTABLE),
            "output_path_gap_count_after": post_snapshot.get("output_path_gap_count", NOT_COMPUTABLE),
        },
        "governance_preservation": {
            "p130_hold_preserved": True,
            "orphan_exclusion_preserved": True,
            "research_canary_spine_refresh_performed": False,
            "p102g_temporal_continuity_spine_edge_preserved": True,
        },
        "blocked_actions": list(BLOCKED_ACTIONS),
        "downstream_status": "COVERAGE_REPAIR_CHAIN_COMPLETE" if regeneration_verified else NOT_COMPUTABLE,
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_action": (
            "coverage repair chain is complete; do not reopen registry repair without separate operator review"
            if regeneration_verified
            else "complete scoped execution receipt prerequisites before audit regeneration"
        ),
    }
    packet["receipt_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "receipt_hash"})
    return packet


def render_abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    transition = packet.get("audit_transition", {})
    return [
        "# ABX Research Canary Artifact Registry Coverage Audit Regeneration Receipt 001",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `artifact_id`: `{packet['artifact_id']}`",
        f"- `audit_regeneration_performed`: `{packet['audit_regeneration_performed']}`",
        f"- `audit_status_before`: `{transition.get('audit_status_before', NOT_COMPUTABLE)}`",
        f"- `audit_status_after`: `{transition.get('audit_status_after', NOT_COMPUTABLE)}`",
        f"- `lane_id_gap_count_before`: `{transition.get('lane_id_gap_count_before', NOT_COMPUTABLE)}`",
        f"- `lane_id_gap_count_after`: `{transition.get('lane_id_gap_count_after', NOT_COMPUTABLE)}`",
        f"- `downstream_status`: `{packet['downstream_status']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        "",
        "## Preserved Holds",
        "",
        "- `P130_ACTIVATION` remains blocked",
        "- `ORPHAN_OUTPUT_REGISTRY_INCLUSION` remains blocked",
        "- `RESEARCH_CANARY_SPINE_REFRESH` remains blocked",
        "- `RUNTIME_MUTATION` remains blocked",
        "- `CANON_MUTATION` remains blocked",
        "- `QUEUE_MUTATION` remains blocked",
    ]


def write_abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt(root)
    if packet["audit_regeneration_performed"]:
        write_abx_research_canary_artifact_registry_coverage_audit(
            source_root=root,
            out_root=target_root,
        )
    write_canonical_json(target_root / RECEIPT_JSON_PATH, packet)
    _write_markdown(
        target_root / RECEIPT_MD_PATH,
        render_abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt_markdown(packet),
    )
    return packet
