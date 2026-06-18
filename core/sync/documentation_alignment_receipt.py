from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "DocumentationAlignmentReceipt.v1"
RECEIPT_ID = "DOCUMENTATION_ALIGNMENT_RECEIPT_001"
RECEIPT_JSON_PATH = Path("out/sync/documentation_alignment_receipt_001.latest.json")
RECEIPT_MD_PATH = Path("out/sync/documentation_alignment_receipt_001.latest.md")
NOT_COMPUTABLE = "NOT_COMPUTABLE"

SOURCE_ARTIFACT_PATHS: tuple[str, ...] = (
    "README.md",
    "PLANS.md",
    "AGENTS.md",
    "docs/status/badges.json",
    "docs/status/continuity-spine.json",
    "out/audit/continuation_frontier_reconciliation_001.latest.json",
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt_001.latest.json",
    "out/operator_review/abx_research_canary_orphan_output_registry_policy_chain_closure_receipt_001.latest.json",
    "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_chain_closure_receipt_001.latest.json",
    "out/operator_review/abx_artifact_lineage_registry_traceability_audit_regeneration_receipt_001.latest.json",
    "out/operator_review/abx_artifact_lineage_direct_repair_frontier_revalidation_001.latest.json",
    "out/operator_review/abx_artifact_lineage_direct_repair_chain_closure_receipt_001.latest.json",
    "out/operator_review/abx_post_registry_repair_governance_synthesis_receipt_001.latest.json",
)


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return NOT_COMPUTABLE


def _source_hashes(root: Path) -> dict[str, str]:
    return {path: _sha256(root / path) for path in SOURCE_ARTIFACT_PATHS}


def build_documentation_alignment_receipt(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source_hashes = _source_hashes(root)

    packet: dict[str, Any] = {
        "artifact_type": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": "DOCUMENTATION_ALIGNMENT_RECEIPT_EMITTED_ADVISORY_ONLY",
        "receipt_time": NOT_COMPUTABLE,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "governance_status": "FROZEN",
        "canon_status": "ADVISORY_ONLY",
        "execution_authority": False,
        "valid_for_execution": False,
        "runtime_mutation": False,
        "canon_mutation": False,
        "forecast_routing": False,
        "scope": ["README.md", "PLANS.md", "AGENTS.md", "STATUS.md", "docs/status/*"],
        "preserved_baselines": {
            "continuity_lane_count": 58,
            "highest_observed_lane": "P102G",
            "downstream_when_missing_evidence": NOT_COMPUTABLE,
        },
        "synchronized_wording": {
            "research_canary_registry_repair_state": (
                "P103-P130 registry coverage repair chain (#681-#688) sealed at repair closure; "
                "28 canonical paths registered; A4b inclusion registered 10 derived-optional orphan paths "
                "separately; P130 hold preserved; downstream NOT_COMPUTABLE."
            ),
            "research_canary_orphan_policy_state": (
                "Orphan exclude policy governance sealed (ORPHAN_POLICY_GOVERNANCE_SEALED); "
                "operator-authorized A4b inclusion sealed separately (ORPHAN_INCLUSION_GOVERNANCE_SEALED); "
                "orphan count 0 via derived-optional registration; downstream NOT_COMPUTABLE."
            ),
            "artifact_lineage_traceability_state": (
                "Artifact-lineage traceability audit regeneration is complete "
                "(TRACEABILITY_AUDIT_REGENERATION_COMPLETE); advisory-only; downstream NOT_COMPUTABLE."
            ),
            "artifact_lineage_repair_state": (
                "Artifact-lineage direct repair and traceability audit regeneration complete; "
                "frontier revalidation reports ARTIFACT_LINEAGE_DIRECT_REPAIR_CHAIN_COMPLETE; "
                "chain closure sealed (ARTIFACT_LINEAGE_DIRECT_REPAIR_CHAIN_SEALED); "
                "post-registry-repair synthesis receipt consolidates six sealed chains; "
                "advisory-only; downstream NOT_COMPUTABLE."
            ),
            "continuity_spine_state": (
                "58 observed temporal-continuity lanes; highest observed temporal-continuity lane P102G; "
                "downstream remains NOT_COMPUTABLE without explicit operator decision evidence."
            ),
            "namespace_stabilization_state": (
                "Namespace/status surfaces are observational and deterministic; "
                "governance_status remains FROZEN and canon_status remains ADVISORY_ONLY."
            ),
            "operator_sync_state": (
                "Notion queue and operator backlog are advisory-only, terminal/blocked for governed operator "
                "decision, and deny Notion/GitHub writeback plus auto-continuation."
            ),
            "oracle_planning_state": (
                "Oracle intake boundary and confidence calibration surfaces are planning/dry-run only; "
                "planned contracts/runners do not authorize runtime, forecast, queue, canon, or execution mutation."
            ),
        },
        "unsupported_claims": [
            "research canary activation authorization",
            "live controlled ingest execution",
            "Notion writeback completeness",
            "downstream lane after missing evidence",
            "orphan output registry inclusion without separate operator governance",
            "reopening sealed registry repair chain",
            "reopening sealed artifact-lineage repair chain",
        ],
        "drift_identified": [
            {
                "surface": "PLANS.md",
                "drift": "artifact-lineage section did not mention frontier revalidation or chain closure sealed state",
                "resolution": "added frontier revalidation, chain closure, and synthesis receipt bullets",
            },
            {
                "surface": "AGENTS.md",
                "drift": "missing compact guardrail for artifact-lineage chain sealed",
                "resolution": "added ARTIFACT_LINEAGE_DIRECT_REPAIR_CHAIN_SEALED and synthesis receipt guardrail",
            },
            {
                "surface": "STATUS.md",
                "drift": "stale artifact-lineage in-progress wording relative to sealed closure receipts",
                "resolution": "refreshed sealed-chain summary with synthesis receipt reference",
            },
        ],
        "source_artifact_hashes": source_hashes,
        "recommended_next_action": (
            "review documentation alignment receipt and keep all unsupported claims NOT_COMPUTABLE "
            "until governed evidence exists"
        ),
    }
    return {**packet, "packet_hash": canonical_hash(packet)}


def render_markdown(packet: Mapping[str, Any]) -> list[str]:
    lines = [
        "# Documentation Alignment Receipt 001",
        "",
        f"- `receipt_id`: `{packet['receipt_id']}`",
        f"- `status`: `{packet['status']}`",
        f"- `governance_status`: `{packet['governance_status']}`",
        f"- `canon_status`: `{packet['canon_status']}`",
        "",
        "## Synchronized Wording",
    ]
    wording = packet.get("synchronized_wording", {})
    if isinstance(wording, Mapping):
        for key, value in sorted(wording.items()):
            lines.append(f"- `{key}`: {value}")
    return lines


def write_documentation_alignment_receipt(
    repo_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_documentation_alignment_receipt(root)
    write_canonical_json(target_root / RECEIPT_JSON_PATH, packet)
    target_root.joinpath(RECEIPT_MD_PATH).parent.mkdir(parents=True, exist_ok=True)
    target_root.joinpath(RECEIPT_MD_PATH).write_text(
        "\n".join(render_markdown(packet)) + "\n",
        encoding="utf-8",
    )
    return packet
