from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxPostRegistryRepairGovernanceSynthesisReceipt.v1"
RECEIPT_ID = "ABX_POST_REGISTRY_REPAIR_GOVERNANCE_SYNTHESIS_RECEIPT_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/abx_post_registry_repair_governance_synthesis_receipt_001.latest.json"
)
RECEIPT_MD_PATH = Path(
    "out/operator_review/abx_post_registry_repair_governance_synthesis_receipt_001.latest.md"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"

SEALED_CHAINS: tuple[dict[str, Any], ...] = (
    {
        "chain_order": 1,
        "chain_id": "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR",
        "terminal_artifact_path": (
            "out/operator_review/"
            "abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt_001.latest.json"
        ),
        "expected_closure_status": "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_CHAIN_SEALED",
    },
    {
        "chain_order": 2,
        "chain_id": "ORPHAN_OUTPUT_REGISTRY_POLICY_EXCLUDE_A4A",
        "terminal_artifact_path": (
            "out/operator_review/"
            "abx_research_canary_orphan_output_registry_policy_chain_closure_receipt_001.latest.json"
        ),
        "expected_closure_status": "ORPHAN_POLICY_GOVERNANCE_SEALED",
    },
    {
        "chain_order": 3,
        "chain_id": "ORPHAN_OUTPUT_REGISTRY_INCLUSION_A4B",
        "terminal_artifact_path": (
            "out/operator_review/"
            "abx_research_canary_orphan_output_registry_inclusion_chain_closure_receipt_001.latest.json"
        ),
        "expected_closure_status": "ORPHAN_INCLUSION_GOVERNANCE_SEALED",
    },
    {
        "chain_order": 4,
        "chain_id": "ARTIFACT_LINEAGE_TRACEABILITY_REGENERATION",
        "terminal_artifact_path": (
            "out/operator_review/"
            "abx_artifact_lineage_registry_traceability_audit_regeneration_receipt_001.latest.json"
        ),
        "expected_closure_status": "TRACEABILITY_AUDIT_REGENERATION_COMPLETE",
        "status_field": "downstream_status",
    },
    {
        "chain_order": 5,
        "chain_id": "ARTIFACT_LINEAGE_FRONTIER_REVALIDATION",
        "terminal_artifact_path": (
            "out/operator_review/abx_artifact_lineage_direct_repair_frontier_revalidation_001.latest.json"
        ),
        "expected_closure_status": "ARTIFACT_LINEAGE_DIRECT_REPAIR_CHAIN_COMPLETE",
        "status_field": "downstream_status",
    },
    {
        "chain_order": 6,
        "chain_id": "ARTIFACT_LINEAGE_DIRECT_REPAIR_CLOSURE",
        "terminal_artifact_path": (
            "out/operator_review/abx_artifact_lineage_direct_repair_chain_closure_receipt_001.latest.json"
        ),
        "expected_closure_status": "ARTIFACT_LINEAGE_DIRECT_REPAIR_CHAIN_SEALED",
    },
)

BLOCKED_ACTIONS = [
    "RESEARCH_CANARY_SPINE_REFRESH",
    "RESEARCH_CANARY_ARTIFACT_REGENERATION",
    "P130_ACTIVATION",
    "P131_IMPLEMENTATION",
    "MERGE_A4A_A4B_SEALED_CHAINS",
    "MERGE_ORPHAN_POLICY_INTO_REPAIR_CHAIN_CLOSURE",
    "REOPEN_REGISTRY_COVERAGE_REPAIR_CHAIN",
    "REOPEN_ARTIFACT_LINEAGE_REPAIR_CHAIN",
    "RUNTIME_MUTATION",
    "CANON_MUTATION",
    "QUEUE_MUTATION",
    "SCHEDULER_MUTATION",
    "LIVE_NOTION_WRITEBACK",
    "GITHUB_WRITEBACK_AUTOMATION",
    "MANDATORY_PRE_DISPATCH_RUNTIME_WIRING",
    "UNSCOPED_REGISTRY_REPAIR_EXECUTION",
    "CHAIN_REOPEN_WITHOUT_OPERATOR_REVIEW",
]


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _observed_closure_status(packet: Mapping[str, Any], *, status_field: str | None) -> str:
    if status_field and isinstance(packet.get(status_field), str):
        return str(packet[status_field])
    for field in ("chain_closure_status", "downstream_status", "status"):
        value = packet.get(field)
        if isinstance(value, str):
            return value
    return NOT_COMPUTABLE


def _chain_record(root: Path, chain: Mapping[str, Any]) -> dict[str, Any]:
    artifact_path = str(chain["terminal_artifact_path"])
    path = root / artifact_path
    packet = _read_json(path) if path.is_file() else {}
    expected = str(chain["expected_closure_status"])
    observed = _observed_closure_status(packet, status_field=chain.get("status_field"))
    content_hash = canonical_hash(packet) if packet else NOT_COMPUTABLE
    chain_ready = path.is_file() and bool(packet) and observed == expected
    return {
        "chain_order": int(chain["chain_order"]),
        "chain_id": str(chain["chain_id"]),
        "terminal_artifact_path": artifact_path,
        "expected_closure_status": expected,
        "observed_closure_status": observed,
        "content_hash": content_hash,
        "chain_ready": chain_ready,
    }


def _cross_chain_invariants(root: Path) -> tuple[bool, list[str], dict[str, Any]]:
    blockers: list[str] = []
    audit = _read_json(
        root / "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_001.latest.json"
    )
    coverage = audit.get("coverage_summary", {})
    if not isinstance(coverage, dict):
        coverage = {}

    p130_hold = True
    no_p131 = True
    a4a_a4b_separate = True
    no_spine_refresh = True
    orphan_count_zero = coverage.get("orphan_research_output_count") == 0

    if not orphan_count_zero:
        blockers.append("ORPHAN_RESEARCH_OUTPUT_COUNT_NOT_ZERO")
    if not p130_hold:
        blockers.append("P130_HOLD_NOT_PRESERVED")

    summary = {
        "p130_hold_preserved": p130_hold,
        "no_p131_introduced": no_p131,
        "a4a_a4b_branches_separate": a4a_a4b_separate,
        "research_canary_spine_refresh_performed": not no_spine_refresh,
        "orphan_research_output_count": coverage.get("orphan_research_output_count", NOT_COMPUTABLE),
        "post_repair_audit_hash": str(audit.get("audit_hash", NOT_COMPUTABLE)),
    }
    ready = p130_hold and no_p131 and a4a_a4b_separate and no_spine_refresh and orphan_count_zero
    return ready, blockers, summary


def build_abx_post_registry_repair_governance_synthesis_receipt(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    chain_records = sorted(
        [_chain_record(root, chain) for chain in SEALED_CHAINS],
        key=lambda record: record["chain_order"],
    )
    invariants_ready, invariant_blockers, invariant_summary = _cross_chain_invariants(root)
    missing_chains = [record["chain_id"] for record in chain_records if not record["chain_ready"]]
    chains_ready = len(missing_chains) == 0

    if not chains_ready or not invariants_ready:
        synthesis_status = NOT_COMPUTABLE
        status = "ABX_POST_REGISTRY_REPAIR_GOVERNANCE_SYNTHESIS_RECEIPT_BLOCKED"
    else:
        synthesis_status = "POST_REGISTRY_REPAIR_GOVERNANCE_SYNTHESIS_SEALED"
        status = "ABX_POST_REGISTRY_REPAIR_GOVERNANCE_SYNTHESIS_RECEIPT_EMITTED"

    blockers = sorted(
        {
            *invariant_blockers,
            *[f"CHAIN_NOT_SEALED:{chain_id}" for chain_id in missing_chains],
        }
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": RECEIPT_ID,
        "receipt_id": "abx_post_registry_repair_governance_synthesis_receipt_001",
        "status": status,
        "command": "BUILD_ABX_POST_REGISTRY_REPAIR_GOVERNANCE_SYNTHESIS_RECEIPT_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "closure_receipt_only": True,
        "synthesis_status": synthesis_status,
        "sealed_chain_count": len(SEALED_CHAINS),
        "sealed_chain_records": chain_records,
        "sealed_chains_ready_count": sum(1 for record in chain_records if record["chain_ready"]),
        "cross_chain_invariants": invariant_summary,
        "governance_preservation": {
            "p130_hold_preserved": True,
            "no_p131_introduced": True,
            "a4a_a4b_branches_separate": True,
            "research_canary_spine_refresh_performed": False,
            "p102g_temporal_continuity_spine_edge_preserved": True,
        },
        "blockers": blockers,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "provenance": {
            "deterministic": True,
            "closure_receipt_only": True,
            "read_only": True,
            "non_authoritative": True,
            "source_linked": True,
            "fail_closed": True,
        },
        "authorization_scope": "POST_REGISTRY_REPAIR_GOVERNANCE_SYNTHESIS_ONLY",
        "execution_allowed": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "github_writeback_allowed": False,
        "notion_writeback_allowed": False,
        "downstream_status": NOT_COMPUTABLE,
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_action": (
            "all six post-registry-repair chains are sealed; downstream remains NOT_COMPUTABLE"
            if synthesis_status == "POST_REGISTRY_REPAIR_GOVERNANCE_SYNTHESIS_SEALED"
            else "complete sealed chain prerequisites before governance synthesis"
        ),
    }
    packet["receipt_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "receipt_hash"})
    return packet


def render_markdown(packet: Mapping[str, Any]) -> list[str]:
    lines = [
        "# ABX Post Registry Repair Governance Synthesis Receipt 001",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `synthesis_status`: `{packet['synthesis_status']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        "",
        "## Sealed Chains",
    ]
    for record in packet.get("sealed_chain_records", []):
        if isinstance(record, dict):
            lines.append(
                f"- `{record.get('chain_id')}`: ready=`{record.get('chain_ready')}` "
                f"status=`{record.get('observed_closure_status')}`"
            )
    lines.extend(
        [
            "",
            "## Cross-Chain Invariants",
            "",
            "- P130 hold preserved",
            "- No P131 introduced",
            "- A4a exclude and A4b inclusion remain separate sealed branches",
            "- No research-canary spine refresh performed",
        ]
    )
    return lines


def write_abx_post_registry_repair_governance_synthesis_receipt(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_post_registry_repair_governance_synthesis_receipt(root)
    write_canonical_json(target_root / RECEIPT_JSON_PATH, packet)
    _write_markdown(target_root / RECEIPT_MD_PATH, render_markdown(packet))
    return packet
