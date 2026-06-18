from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ContinuationFrontierReconciliation.v1"
RECEIPT_ID = "ABRAXAS_CONTINUATION_FRONTIER_RECONCILIATION_001"
OUT_JSON = "out/audit/continuation_frontier_reconciliation_001.latest.json"
OUT_MD = "out/audit/continuation_frontier_reconciliation_001.latest.md"

AUTHORITY_LOCKS: dict[str, bool] = {
    "execution_authority": False,
    "activation": False,
    "canon_mutation": False,
    "runtime_mutation": False,
    "scheduler_mutation": False,
    "queue_mutation": False,
    "notion_writeback": False,
    "github_writeback": False,
    "operator_attestation": False,
    "decision_record_creation": False,
    "token_minting": False,
}

STATUS_FIELDS: tuple[str, ...] = (
    "receipt_status",
    "review_status",
    "audit_status",
    "queue_status",
    "backlog_status",
    "terminal_state_status",
    "gate_status",
    "chain_closure_status",
    "downstream_status",
    "status",
    "lane_status",
    "operator_decision_record_review_status",
    "decision_record_plan_status",
    "final_status",
)

AUTHORITY_FIELD_NAMES: tuple[str, ...] = (
    "execution_authority",
    "authorization_granted",
    "activation_authorized",
    "valid_for_execution",
    "runtime_mutation",
    "canon_mutation",
    "scheduler_mutation",
    "queue_mutation",
    "notion_writeback_allowed",
    "github_writeback_allowed",
    "safe_to_auto_continue",
    "safe_to_prepare_patch",
    "safe_to_prepare_planning_pr",
)

FRONTIER_SOURCES: tuple[dict[str, str], ...] = (
    {
        "frontier_id": "notion_spec_completion_queue",
        "path": "out/sync/notion_spec_completion_queue/latest.json",
        "expected_classification": "NOT_COMPUTABLE",
    },
    {
        "frontier_id": "notion_operator_decision_backlog",
        "path": "out/sync/notion_operator_decision_backlog/latest.json",
        "expected_classification": "NOT_COMPUTABLE",
    },
    {
        "frontier_id": "notion_patch_queue_terminal_state",
        "path": "out/sync/notion_patch_queue_terminal_state/latest.json",
        "expected_classification": "NOT_COMPUTABLE",
    },
    {
        "frontier_id": "p102g_plus_operator_decision_surface_audit",
        "path": "out/operator_review/p102g_plus_operator_decision_surface_audit_001.latest.json",
        "expected_classification": "HELD_FOR_OPERATOR",
    },
    {
        "frontier_id": "runtime_integration_gate_receipt",
        "path": "out/audit/runtime_integration_gate_receipt_001.latest.json",
        "expected_classification": "OBSERVED",
    },
    {
        "frontier_id": "runtime_integration_gate_operator_review_advisory_spec_plan",
        "path": "out/audit/runtime_integration_gate_operator_review_advisory_spec_plan_001.latest.json",
        "expected_classification": "NOT_COMPUTABLE",
    },
    {
        "frontier_id": "belief_graph_operator_decision_record_review",
        "path": "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_review_001.latest.json",
        "expected_classification": "HELD_FOR_OPERATOR",
    },
    {
        "frontier_id": "codegen_phase1_validation_review_evidence_dry_run_review",
        "path": "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review_001.latest.json",
        "expected_classification": "HELD_FOR_OPERATOR",
    },
    {
        "frontier_id": "v2_hygiene_phase1_authorization_chain_compression_audit",
        "path": "out/operator_review/v2_hygiene_phase1_authorization_chain_compression_audit_001.latest.json",
        "expected_classification": "HELD_FOR_OPERATOR",
    },
    {
        "frontier_id": "v2_hygiene_phase1_stabilization_decision_record_plan",
        "path": "out/operator_review/v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_001.latest.json",
        "expected_classification": "HELD_FOR_OPERATOR",
    },
    {
        "frontier_id": "controlled_ingest_scheduler_governance_audit",
        "path": "out/audit/controlled_ingest_scheduler_governance_audit_001.latest.json",
        "expected_classification": "OBSERVED",
    },
    {
        "frontier_id": "runtime_handoff_receipt_set",
        "path": "out/ingest/runtime_handoff_receipt_set_001.latest.json",
        "expected_classification": "OBSERVED",
    },
    {
        "frontier_id": "oracle_intake_queue",
        "path": "out/ingest/oracle_intake_queue_001.latest.json",
        "expected_classification": "OBSERVED",
    },
    {
        "frontier_id": "research_canary_p129_activation_readiness",
        "path": "out/research_canary_activation_readiness_evidence_record/latest.json",
        "expected_classification": "OBSERVED",
    },
    {
        "frontier_id": "research_canary_p130_final_activation_authorization_review",
        "path": "out/research_canary_final_activation_authorization_review/latest.json",
        "expected_classification": "MISSING_ARTIFACT",
    },
    {
        "frontier_id": "research_canary_registry_coverage_audit_regeneration_receipt",
        "path": (
            "out/operator_review/"
            "abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt_001.latest.json"
        ),
        "expected_classification": "OBSERVED",
    },
    {
        "frontier_id": "research_canary_registry_coverage_repair_chain_closure_receipt",
        "path": (
            "out/operator_review/"
            "abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt_001.latest.json"
        ),
        "expected_classification": "OBSERVED",
    },
    {
        "frontier_id": "research_canary_orphan_output_registry_policy_review",
        "path": (
            "out/operator_review/abx_research_canary_orphan_output_registry_policy_review_001.latest.json"
        ),
        "expected_classification": "OBSERVED",
    },
    {
        "frontier_id": "research_canary_orphan_output_registry_policy_chain_closure_receipt",
        "path": (
            "out/operator_review/"
            "abx_research_canary_orphan_output_registry_policy_chain_closure_receipt_001.latest.json"
        ),
        "expected_classification": "OBSERVED",
    },
    {
        "frontier_id": "artifact_lineage_traceability_audit_regeneration_receipt",
        "path": (
            "out/operator_review/"
            "abx_artifact_lineage_registry_traceability_audit_regeneration_receipt_001.latest.json"
        ),
        "expected_classification": "OBSERVED",
    },
    {
        "frontier_id": "research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt",
        "path": (
            "out/operator_review/"
            "abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt_001.latest.json"
        ),
        "expected_classification": "OBSERVED",
    },
    {
        "frontier_id": "research_canary_orphan_output_registry_inclusion_chain_closure_receipt",
        "path": (
            "out/operator_review/"
            "abx_research_canary_orphan_output_registry_inclusion_chain_closure_receipt_001.latest.json"
        ),
        "expected_classification": "OBSERVED",
    },
    {
        "frontier_id": "artifact_lineage_direct_repair_frontier_revalidation",
        "path": (
            "out/operator_review/abx_artifact_lineage_direct_repair_frontier_revalidation_001.latest.json"
        ),
        "expected_classification": "OBSERVED",
    },
    {
        "frontier_id": "artifact_lineage_direct_repair_chain_closure_receipt",
        "path": (
            "out/operator_review/abx_artifact_lineage_direct_repair_chain_closure_receipt_001.latest.json"
        ),
        "expected_classification": "OBSERVED",
    },
)

P130_CODE_PATHS: tuple[str, ...] = (
    "core/research_canary_final_activation_authorization_review.py",
    "scripts/run_research_canary_final_activation_authorization_review.py",
    "tests/test_research_canary_final_activation_authorization_review.py",
    "contracts/canon/research_canary_final_activation_authorization_review.v1.schema.json",
    "docs/audits/REPO_FINAL_SEAL_P101_P130_research_canary_evidence_chain_closed.md",
    "docs/audits/REPO_EXECUTION_RECEIPT_P130_final_activation_authorization_review_boundary_held.md",
)

STALE_NOTION_LANES: tuple[dict[str, str], ...] = (
    {
        "lane_id": "P131_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_DECISION_RECORD",
        "source": "COPILOT_PROMPT_BATCH_F_P130_P132_FINAL_AUTHORIZATION_DECISION_ROUTING",
    },
    {
        "lane_id": "P132_RESEARCH_CANARY_FINAL_ACTIVATION_DENIAL_HOLD_ROUTING",
        "source": "COPILOT_PROMPT_BATCH_F_P130_P132_FINAL_AUTHORIZATION_DECISION_ROUTING",
    },
    {
        "lane_id": "P133_RESEARCH_CANARY_LIVE_ACTIVATION_PLAN_DRAFT",
        "source": "COPILOT_PROMPT_BATCH_F_P130_P132_FINAL_AUTHORIZATION_DECISION_ROUTING",
    },
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _status_value(packet: Mapping[str, Any] | None) -> str:
    if packet is None:
        return "NOT_COMPUTABLE"
    for field in STATUS_FIELDS:
        value = packet.get(field)
        if isinstance(value, str):
            return value
    for key, value in sorted(packet.items()):
        if "status" in key and isinstance(value, str):
            return value
    return "NOT_COMPUTABLE"


def _authority_summary(packet: Mapping[str, Any] | None) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    if packet is None:
        return summary
    locks = packet.get("authority_locks")
    if isinstance(locks, dict):
        for key, value in sorted(locks.items()):
            if isinstance(value, bool):
                summary[str(key)] = value
    for field in AUTHORITY_FIELD_NAMES:
        value = packet.get(field)
        if isinstance(value, bool):
            summary[field] = value
    return dict(sorted(summary.items()))


def _has_authority_drift(summary: Mapping[str, Any]) -> bool:
    safe_true_fields = {
        "advisory_only",
        "projection_only",
        "non_authoritative",
        "evidence_only",
        "shadow_only",
    }
    return any(
        value is True and key not in safe_true_fields
        for key, value in summary.items()
    )


def _classify_source(
    *, packet: Mapping[str, Any] | None, path_exists: bool, expected_classification: str
) -> str:
    if not path_exists:
        return "MISSING_ARTIFACT"
    status = _status_value(packet)
    if expected_classification == "MISSING_ARTIFACT":
        return "OBSERVED"
    if expected_classification == "OBSERVED":
        return "OBSERVED"
    if expected_classification == "HELD_FOR_OPERATOR" and status == "NOT_COMPUTABLE":
        return "HELD_FOR_OPERATOR"
    if "HELD_FOR_OPERATOR" in status or status.endswith("_HELD"):
        return "HELD_FOR_OPERATOR"
    if status == "NOT_COMPUTABLE":
        return "NOT_COMPUTABLE"
    if expected_classification == "NOT_COMPUTABLE":
        return "NOT_COMPUTABLE"
    return "OBSERVED"


def _source_record(repo_root: Path, source: Mapping[str, str]) -> dict[str, Any]:
    path = source["path"]
    packet_path = repo_root / path
    packet = _read_json(packet_path)
    path_exists = packet_path.exists()
    authority_summary = _authority_summary(packet)
    classification = _classify_source(
        packet=packet,
        path_exists=path_exists,
        expected_classification=source["expected_classification"],
    )
    return {
        "frontier_id": source["frontier_id"],
        "path": path,
        "path_observed": path_exists,
        "classification": classification,
        "expected_classification": source["expected_classification"],
        "observed_status": _status_value(packet),
        "recommended_next_lane": (
            packet.get("recommended_next_lane")
            if isinstance(packet, dict) and isinstance(packet.get("recommended_next_lane"), str)
            else "NOT_COMPUTABLE"
        ),
        "recommended_next_patch": (
            packet.get("recommended_next_patch")
            if isinstance(packet, dict) and isinstance(packet.get("recommended_next_patch"), str)
            else "NOT_COMPUTABLE"
        ),
        "authority_summary": authority_summary,
        "authority_drift_observed": _has_authority_drift(authority_summary),
    }


def _path_statuses(repo_root: Path, paths: tuple[str, ...]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(paths):
        records.append({"path": path, "observed": (repo_root / path).exists()})
    return records


def _run_git(repo_root: Path, args: list[str]) -> list[str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return []
    if result.returncode != 0:
        return []
    return sorted(line for line in result.stdout.splitlines() if line)


def _dirty_work_assessment(repo_root: Path) -> dict[str, Any]:
    short_status = _run_git(repo_root, ["status", "--short"])
    tracked_scripts = _run_git(repo_root, ["ls-files", "Scripts"])
    untracked_scripts = [
        line
        for line in _run_git(repo_root, ["ls-files", "--others", "--exclude-standard"])
        if line.startswith("Scripts/")
    ]
    return {
        "status_short": short_status,
        "tracked_change_count": sum(1 for line in short_status if not line.startswith("?? ")),
        "untracked_path_count": sum(1 for line in short_status if line.startswith("?? ")),
        "scripts_casing_tracked_count": len(tracked_scripts),
        "scripts_casing_untracked_count": len(untracked_scripts),
        "scripts_casing_tracked_paths_sample": tracked_scripts[:25],
        "scripts_casing_untracked_paths_sample": untracked_scripts[:25],
        "workspace_mutation_performed_by_receipt": False,
    }


def _stale_notion_records(repo_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in STALE_NOTION_LANES:
        lane_id = item["lane_id"]
        repo_hits = _run_git(repo_root, ["grep", "-l", lane_id])
        records.append(
            {
                "lane_id": lane_id,
                "source": item["source"],
                "classification": "STALE_NOTION_SPEC",
                "repo_authorization_observed": False,
                "repo_hits": repo_hits,
                "reason": (
                    "Repo docs preserve no-P131 boundary; this Notion lane is superseded until "
                    "fresh governed operator decision evidence exists."
                ),
            }
        )
    return records


def build_continuation_frontier_reconciliation(
    *,
    repo_root: str | Path,
) -> dict[str, Any]:
    root = Path(repo_root)
    frontier_records = [_source_record(root, source) for source in FRONTIER_SOURCES]
    frontier_records = sorted(frontier_records, key=lambda record: record["frontier_id"])
    stale_records = _stale_notion_records(root)
    missing_records = [
        {
            "frontier_id": record["frontier_id"],
            "path": record["path"],
            "classification": record["classification"],
            "observed_status": record["observed_status"],
        }
        for record in frontier_records
        if record["classification"] == "MISSING_ARTIFACT"
    ]
    p130_code_records = _path_statuses(root, P130_CODE_PATHS)
    p130_output_observed = (
        root / "out/research_canary_final_activation_authorization_review/latest.json"
    ).exists()
    p130_code_present = all(record["observed"] for record in p130_code_records)

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "receipt_id": RECEIPT_ID,
        "receipt_status": "CONTINUATION_FRONTIER_RECONCILIATION_EMITTED_ADVISORY_ONLY",
        "frontier_records": frontier_records,
        "stale_notion_records": stale_records,
        "missing_artifact_records": missing_records,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "authority_drift_observed": any(
            record["authority_drift_observed"] for record in frontier_records
        ),
        "classification_counts": {
            classification: (
                sum(1 for record in frontier_records if record["classification"] == classification)
                + sum(1 for record in stale_records if record["classification"] == classification)
            )
            for classification in (
                "OBSERVED",
                "HELD_FOR_OPERATOR",
                "MISSING_ARTIFACT",
                "STALE_NOTION_SPEC",
                "NOT_COMPUTABLE",
            )
        },
        "p130_artifact_drift": {
            "code_and_tests_observed": p130_code_present,
            "output_artifact_observed": p130_output_observed,
            "classification": (
                "OBSERVED" if p130_output_observed else "MISSING_ARTIFACT"
            ),
            "canary_artifact_regeneration_performed": False,
            "canary_spine_refresh_allowed": False,
            "code_path_records": p130_code_records,
        },
        "dirty_work_assessment": _dirty_work_assessment(root),
        "research_canary_guardrail": {
            "do_not_regenerate_research_canary_artifacts": True,
            "requires_validated_p128_to_p130_replay_for_canary_regeneration": True,
            "p131_plus_implementation_authorized": False,
        },
        "recommended_next_action": (
            "hold for fresh governed operator decision or fresh Notion patch spec; preserve "
            "current advisory surfaces and resolve P130 artifact drift without canary sweep"
        ),
        "recommended_next_lane": "NOT_COMPUTABLE",
        "safe_to_auto_continue": False,
        "valid_for_execution": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "execution_authority": False,
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_continuation_frontier_reconciliation(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    write_canonical_json(path, packet)


def write_continuation_frontier_reconciliation_markdown(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    lines = [
        "# Continuation Frontier Reconciliation 001",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- receipt_status: {packet['receipt_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- authority_drift_observed: {packet['authority_drift_observed']}",
        "",
        "## Classification Counts",
    ]
    counts = packet.get("classification_counts", {})
    if isinstance(counts, dict):
        for key in sorted(counts):
            lines.append(f"- {key}: {counts[key]}")
    lines.extend(["", "## Frontier Records"])
    for record in packet.get("frontier_records", []):
        if isinstance(record, dict):
            lines.append(
                "- "
                f"{record['frontier_id']}: {record['classification']} "
                f"({record['observed_status']})"
            )
    lines.extend(["", "## Stale Notion Records"])
    for record in packet.get("stale_notion_records", []):
        if isinstance(record, dict):
            lines.append(f"- {record['lane_id']}: {record['classification']}")
    lines.extend(["", "## P130 Artifact Drift"])
    p130 = packet.get("p130_artifact_drift", {})
    if isinstance(p130, dict):
        lines.append(f"- code_and_tests_observed: {p130['code_and_tests_observed']}")
        lines.append(f"- output_artifact_observed: {p130['output_artifact_observed']}")
        lines.append(f"- classification: {p130['classification']}")
        lines.append(
            "- canary_artifact_regeneration_performed: "
            f"{p130['canary_artifact_regeneration_performed']}"
        )
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
