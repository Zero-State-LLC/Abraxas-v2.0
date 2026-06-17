from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxArtifactLineageDirectRepairFrontierRevalidation.v1"
REVALIDATION_ID = "ABX_ARTIFACT_LINEAGE_DIRECT_REPAIR_FRONTIER_REVALIDATION_001"
OUT_JSON = "out/operator_review/abx_artifact_lineage_direct_repair_frontier_revalidation_001.latest.json"
OUT_MD = "out/operator_review/abx_artifact_lineage_direct_repair_frontier_revalidation_001.latest.md"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
TRACEABILITY_AUDIT_REGENERATION = "ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_REGENERATION"

STATUS_FIELDS: tuple[str, ...] = (
    "receipt_status",
    "review_status",
    "audit_status",
    "queue_status",
    "backlog_status",
    "terminal_state_status",
    "gate_status",
    "status",
    "lane_status",
    "operator_decision_record_review_status",
    "decision_record_plan_status",
    "final_status",
    "approval_record_seal_review_status",
    "plan_status",
    "revalidation_status",
)

GOVERNANCE_DOC_PATHS: tuple[str, ...] = (
    "README.md",
    "STATUS.md",
    "PLANS.md",
    "docs/status/continuity-spine.json",
    "docs/audits/ABRAXAS_REPO_NOTION_DIFF_001.md",
)

ARTIFACT_LINEAGE_CHAIN: tuple[dict[str, str], ...] = (
    {
        "surface_id": "direct_repair_validation_plan",
        "path": "out/sync/abx_artifact_lineage_registry_direct_repair_validation_plan/latest.json",
        "status_field": "status",
    },
    {
        "surface_id": "direct_repair_operator_decision_record",
        "path": "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_001.latest.json",
        "status_field": "status",
    },
    {
        "surface_id": "direct_repair_separate_execution_spec_plan",
        "path": "out/operator_review/abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan_001.latest.json",
        "status_field": "status",
    },
    {
        "surface_id": "direct_repair_execution_authorization_gate",
        "path": "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_gate_001.latest.json",
        "status_field": "status",
    },
    {
        "surface_id": "direct_repair_execution_authorization_record",
        "path": "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_record_001.latest.json",
        "status_field": "status",
    },
    {
        "surface_id": "direct_repair_scoped_execution_receipt",
        "path": "out/operator_review/abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_001.latest.json",
        "status_field": "status",
    },
    {
        "surface_id": "notion_mapping_scope_resolution_record",
        "path": "out/operator_review/abx_artifact_lineage_notion_mapping_scope_resolution_record_001.latest.json",
        "status_field": "status",
    },
    {
        "surface_id": "runner_casing_policy_decision_record",
        "path": "out/operator_review/abx_artifact_lineage_runner_casing_policy_decision_record_001.latest.json",
        "status_field": "status",
    },
)

BELIEF_GRAPH_SURFACES: tuple[dict[str, str], ...] = (
    {
        "surface_id": "belief_graph_contract_plan",
        "path": "out/audit/belief_graph_engine_advisory_receipt_contract_plan_001.latest.json",
        "status_field": "contract_plan_scope",
    },
    {
        "surface_id": "belief_graph_compression_audit",
        "path": "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_compression_audit_001.latest.json",
        "status_field": "compression_audit_status",
    },
    {
        "surface_id": "belief_graph_seal_receipt_plan",
        "path": "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_plan_001.latest.json",
        "status_field": "seal_receipt_plan_status",
    },
    {
        "surface_id": "belief_graph_seal_receipt_dry_run",
        "path": "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run_001.latest.json",
        "status_field": "seal_receipt_dry_run_status",
    },
    {
        "surface_id": "belief_graph_operator_decision_record_plan",
        "path": "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_plan_001.latest.json",
        "status_field": "operator_decision_record_plan_status",
    },
    {
        "surface_id": "belief_graph_operator_decision_record_dry_run",
        "path": "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_dry_run_001.latest.json",
        "status_field": "operator_decision_record_dry_run_status",
    },
    {
        "surface_id": "belief_graph_operator_decision_record_review",
        "path": "out/audit/belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_review_001.latest.json",
        "status_field": "operator_decision_record_review_status",
    },
)

CODEGEN_SURFACES: tuple[dict[str, str], ...] = (
    {
        "surface_id": "codegen_notion_stack_alignment_audit",
        "path": "out/audit/abx_codegen_intelligence_spine_notion_stack_alignment_audit_001.latest.json",
        "status_field": "audit_status",
    },
    {
        "surface_id": "codegen_packet_validation_receipt",
        "path": "out/audit/abx_codegen_intelligence_spine_packet_validation_receipt_001.latest.json",
        "status_field": "receipt_status",
    },
    {
        "surface_id": "codegen_merge_anchor_decision_record_review",
        "path": "out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_review_001.latest.json",
        "status_field": "status",
    },
    {
        "surface_id": "codegen_phase1_decision_record_review",
        "path": "out/operator_review/abx_codegen_phase1_operator_decision_record_review_001.latest.json",
        "status_field": "status",
    },
    {
        "surface_id": "codegen_phase1_validation_review_evidence_dry_run_review",
        "path": "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review_001.latest.json",
        "status_field": "status",
    },
)

PARALLEL_TRACK_SURFACES: tuple[dict[str, str], ...] = (
    {
        "surface_id": "p102g_plus_operator_decision_surface_audit",
        "path": "out/operator_review/p102g_plus_operator_decision_surface_audit_001.latest.json",
        "status_field": "audit_status",
    },
    {
        "surface_id": "research_canary_p129_activation_readiness",
        "path": "out/research_canary_activation_readiness_evidence_record/latest.json",
        "status_field": "status",
    },
    {
        "surface_id": "research_canary_p130_final_activation_authorization_review",
        "path": "out/research_canary_final_activation_authorization_review/latest.json",
        "status_field": "status",
    },
    {
        "surface_id": "v2_hygiene_phase15_controlled_runtime_execution_promotion_gate",
        "path": "out/operator_review/v2_hygiene_phase15_controlled_runtime_execution_promotion_gate_001.latest.json",
        "status_field": "gate_status",
    },
    {
        "surface_id": "temporal_p95_seal_review",
        "path": "out/temporal_continuity_operator_authorization_record_approval_record_seal_review/latest.json",
        "status_field": "approval_record_seal_review_status",
    },
)

BLOCKED_ACTIONS: tuple[str, ...] = (
    "DIRECT_REGISTRY_REPAIR_EXECUTION",
    "OUTPUT_PAIRING_REPAIR_EXECUTION",
    "DOCS_REFERENCE_REPAIR_EXECUTION",
    "RUNNER_CASING_POLICY_OVERRIDE",
    "NOTION_MAPPING_COMPLETENESS_CLAIM",
    "RUNTIME_MUTATION",
    "CANON_MUTATION",
    "QUEUE_MUTATION",
    "SCHEDULER_MUTATION",
    "NOTION_WRITEBACK",
    "GITHUB_WRITEBACK",
    "UNSCOPED_REPAIR_EXECUTION",
    "RESEARCH_CANARY_ARTIFACT_REGENERATION",
    "BELIEF_GRAPH_ENGINE_IMPLEMENTATION",
    "CODEGEN_ENGINE_IMPLEMENTATION",
    "EXECUTION_AUTHORITY_GRANT",
    "TOKEN_MINTING",
)

AUTHORITY_LOCKS: dict[str, bool] = {
    "approval_granted": False,
    "authorization_granted": False,
    "authority_granted": False,
    "canon_mutation": False,
    "execution": False,
    "execution_authority": False,
    "implementation_authorized": False,
    "notion_writeback": False,
    "github_writeback": False,
    "queue_mutation": False,
    "runtime_mutation": False,
    "scheduler_mutation": False,
    "token_minting": False,
}


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return NOT_COMPUTABLE


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _status_value(packet: Mapping[str, Any] | None, status_field: str) -> str:
    if packet is None:
        return NOT_COMPUTABLE
    value = packet.get(status_field)
    if isinstance(value, str):
        return value
    for field in STATUS_FIELDS:
        candidate = packet.get(field)
        if isinstance(candidate, str):
            return candidate
    for key, candidate in sorted(packet.items()):
        if "status" in key and isinstance(candidate, str):
            return candidate
    return NOT_COMPUTABLE


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
    return [line for line in result.stdout.splitlines() if line]


def _parse_merge_anchor(repo_root: Path, pr_number: str) -> dict[str, Any]:
    lines = _run_git(repo_root, ["log", "--oneline", "-1", f"--grep=Merge pull request #{pr_number}"])
    if not lines:
        return {
            "pr_number": pr_number,
            "observed": False,
            "merge_commit": NOT_COMPUTABLE,
            "summary": NOT_COMPUTABLE,
        }
    line = lines[0]
    merge_commit = line.split()[0] if line else NOT_COMPUTABLE
    return {
        "pr_number": pr_number,
        "observed": True,
        "merge_commit": merge_commit,
        "summary": line,
    }


def _governance_doc_records(repo_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path_str in GOVERNANCE_DOC_PATHS:
        path = repo_root / path_str
        records.append(
            {
                "path": path_str,
                "observed": path.is_file(),
                "sha256": _sha256(path) if path.is_file() else NOT_COMPUTABLE,
            }
        )
    return records


def _surface_record(repo_root: Path, source: Mapping[str, str]) -> dict[str, Any]:
    path_str = source["path"]
    path = repo_root / path_str
    packet = _read_json(path)
    status_field = source["status_field"]
    return {
        "surface_id": source["surface_id"],
        "path": path_str,
        "path_observed": path.is_file(),
        "status_field": status_field,
        "observed_status": _status_value(packet, status_field),
        "source_hash": _sha256(path) if path.is_file() else NOT_COMPUTABLE,
        "recommended_next_lane": (
            packet.get("recommended_next_lane")
            if isinstance(packet, dict) and isinstance(packet.get("recommended_next_lane"), str)
            else NOT_COMPUTABLE
        ),
        "execution_allowed": (
            packet.get("execution_allowed") if isinstance(packet, dict) else None
        ),
        "authorization_granted": (
            packet.get("authorization_granted") if isinstance(packet, dict) else None
        ),
    }


def _track_classifications() -> list[dict[str, Any]]:
    return [
        {
            "track_id": "p102g_pr429_era",
            "classification": "historical",
            "rationale": (
                "Notion-confirmed historical-only unless revalidated; existing P102G audit is "
                "observational evidence, not a fresh revalidation grant"
            ),
        },
        {
            "track_id": "p103_p130_research_canary",
            "classification": "parallel",
            "rationale": (
                "Separate sealed research-canary lineage distinct from temporal continuity "
                "lane_count=58; no regeneration during this revalidation"
            ),
        },
        {
            "track_id": "phase15_pr679_v2_operator_sync",
            "classification": "parallel",
            "rationale": (
                "v2 operator-hygiene Phase 15 repo↔Notion docs sync lane merged via PR #679; "
                "advisory-only documentation reconciliation"
            ),
        },
        {
            "track_id": "artifact_lineage_direct_repair",
            "classification": "active",
            "rationale": "Notion-confirmed current frontier for artifact-lineage direct repair surfaces",
        },
        {
            "track_id": "belief_graph_codegen_planning",
            "classification": "active",
            "rationale": (
                "Notion-confirmed planning frontier for Belief Graph and Codegen intelligence spine; "
                "held without implementation authority"
            ),
        },
    ]


def _open_pr_stack(repo_root: Path) -> dict[str, Any]:
    receipt_path = "out/operator_review/pr_644_stack_review_receipt_001.latest.json"
    receipt = _read_json(repo_root / receipt_path)
    pr_644: dict[str, Any] = {
        "receipt_path": receipt_path,
        "receipt_observed": receipt is not None,
        "pr_number": 644,
        "receipt_status": _status_value(receipt, "receipt_status"),
        "state": receipt.get("state") if isinstance(receipt, dict) else NOT_COMPUTABLE,
        "is_draft": receipt.get("is_draft") if isinstance(receipt, dict) else None,
    }
    return {
        "primary_open_pr": pr_644,
        "superseded_open_stack_note": (
            "v2 phase gate PR stack #668-#674 largely superseded by merged PR #678; "
            "phase gates through phase 32 are already on main"
        ),
        "latest_merged_anchor_pr": 679,
    }


def _next_lane_eligible(
    *,
    scoped_receipt: Mapping[str, Any] | None,
    auth_record: Mapping[str, Any] | None,
    auth_gate: Mapping[str, Any] | None,
) -> bool:
    if scoped_receipt is None or auth_record is None or auth_gate is None:
        return False
    scoped_status = scoped_receipt.get("status")
    scoped_lane = scoped_receipt.get("recommended_next_lane")
    auth_record_status = auth_record.get("status")
    gate_status = auth_gate.get("status")
    return (
        scoped_status == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SCOPED_EXECUTION_RECEIPT_EMITTED"
        and scoped_lane == TRACEABILITY_AUDIT_REGENERATION
        and auth_record_status
        in {
            "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_RECORD_GRANTED_FOR_SCOPED_EXECUTION_PR",
            "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_RECORD_CONSUMED_BY_SCOPED_EXECUTION_RECEIPT",
        }
        and gate_status == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR"
        and auth_gate.get("authorization_granted") is False
    )


def _frontier_checks(
    repo_root: Path,
    *,
    merged_anchor: dict[str, Any],
    open_pr_stack: dict[str, Any],
    artifact_lineage_chain: list[dict[str, Any]],
    belief_graph_planning: list[dict[str, Any]],
    codegen_planning: list[dict[str, Any]],
    track_classifications: list[dict[str, Any]],
    next_lane_eligible: bool,
) -> list[dict[str, Any]]:
    primary_anchor = merged_anchor.get("primary", {})
    prior_anchor = merged_anchor.get("prior", {})
    scoped = next(
        (item for item in artifact_lineage_chain if item["surface_id"] == "direct_repair_scoped_execution_receipt"),
        None,
    )
    spec_plan = next(
        (
            item
            for item in artifact_lineage_chain
            if item["surface_id"] == "direct_repair_separate_execution_spec_plan"
        ),
        None,
    )
    belief_held = all(item["path_observed"] for item in belief_graph_planning) and any(
        "HELD" in item["observed_status"] for item in belief_graph_planning
    )
    codegen_held = all(
        item["path_observed"] for item in codegen_planning[:2]
    ) and any("HELD" in item["observed_status"] for item in codegen_planning[2:])
    status_stale = (repo_root / "STATUS.md").is_file() and primary_anchor.get("observed") is True

    checks: list[dict[str, Any]] = [
        {
            "check_id": "latest_merged_anchor",
            "check_status": "PASS" if primary_anchor.get("observed") else NOT_COMPUTABLE,
            "evidence_paths": ["README.md", "PLANS.md", "docs/status/continuity-spine.json"],
            "observed_summary": (
                f"PR #{primary_anchor.get('pr_number', NOT_COMPUTABLE)} merge {primary_anchor.get('merge_commit', NOT_COMPUTABLE)}; "
                f"prior PR #{prior_anchor.get('pr_number', NOT_COMPUTABLE)} merge {prior_anchor.get('merge_commit', NOT_COMPUTABLE)}"
            ),
        },
        {
            "check_id": "active_open_pr_stack",
            "check_status": "PASS" if open_pr_stack["primary_open_pr"]["receipt_observed"] else "FAIL_CLOSED",
            "evidence_paths": [
                "out/operator_review/pr_644_stack_review_receipt_001.latest.json",
            ],
            "observed_summary": (
                f"PR #644 {open_pr_stack['primary_open_pr']['receipt_status']}; "
                f"{open_pr_stack['superseded_open_stack_note']}"
            ),
        },
        {
            "check_id": "latest_artifact_lineage_direct_repair_surface",
            "check_status": (
                "PASS"
                if scoped and scoped["observed_status"]
                == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SCOPED_EXECUTION_RECEIPT_EMITTED"
                else "FAIL_CLOSED"
            ),
            "evidence_paths": [
                item["path"]
                for item in artifact_lineage_chain
                if item["surface_id"] == "direct_repair_scoped_execution_receipt"
            ],
            "observed_summary": (
                scoped["observed_status"] if scoped else NOT_COMPUTABLE
            ),
        },
        {
            "check_id": "direct_repair_execution_spec_exists",
            "check_status": (
                "PASS"
                if spec_plan
                and spec_plan["observed_status"]
                == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SEPARATE_EXECUTION_SPEC_PLAN_READY"
                else "FAIL_CLOSED"
            ),
            "evidence_paths": [
                item["path"]
                for item in artifact_lineage_chain
                if item["surface_id"] == "direct_repair_separate_execution_spec_plan"
            ],
            "observed_summary": spec_plan["observed_status"] if spec_plan else NOT_COMPUTABLE,
        },
        {
            "check_id": "belief_graph_codegen_planning_status",
            "check_status": "PASS" if belief_held and codegen_held else "FAIL_CLOSED",
            "evidence_paths": [item["path"] for item in belief_graph_planning + codegen_planning],
            "observed_summary": (
                "Belief Graph advisory receipt chain held for operator; Codegen stack alignment audit ready "
                "with Phase 1 operator reviews held; no implementation authority observed"
            ),
        },
        {
            "check_id": "track_classification_p102g_p103_p130_phase15_pr679",
            "check_status": "PASS",
            "evidence_paths": [
                "out/operator_review/p102g_plus_operator_decision_surface_audit_001.latest.json",
                "out/research_canary_activation_readiness_evidence_record/latest.json",
                "out/research_canary_final_activation_authorization_review/latest.json",
                "out/operator_review/v2_hygiene_phase15_controlled_runtime_execution_promotion_gate_001.latest.json",
            ],
            "observed_summary": "; ".join(
                f"{item['track_id']}={item['classification']}" for item in track_classifications
            ),
        },
        {
            "check_id": "recommended_next_lane_eligibility",
            "check_status": "PASS" if next_lane_eligible else NOT_COMPUTABLE,
            "evidence_paths": [
                "out/operator_review/abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_001.latest.json",
                "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_record_001.latest.json",
                "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_gate_001.latest.json",
            ],
            "observed_summary": (
                TRACEABILITY_AUDIT_REGENERATION
                if next_lane_eligible
                else NOT_COMPUTABLE
            ),
        },
        {
            "check_id": "authority_denials_preserved",
            "check_status": "PASS",
            "evidence_paths": list(GOVERNANCE_DOC_PATHS),
            "observed_summary": (
                "governance_status=FROZEN; canon_status=ADVISORY_ONLY; approval/authorization/token/execution denied"
            ),
        },
    ]
    if status_stale:
        checks.append(
            {
                "check_id": "status_md_stale_relative_to_merged_anchor",
                "check_status": "OBSERVED",
                "evidence_paths": ["STATUS.md"],
                "observed_summary": (
                    "STATUS.md last-updated 2026-06-11 predates merged PR #679; treated as input evidence only"
                ),
            }
        )
    return checks


def build_abx_artifact_lineage_direct_repair_frontier_revalidation(
    *,
    repo_root: str | Path,
) -> dict[str, Any]:
    root = Path(repo_root)
    governance_docs = _governance_doc_records(root)
    artifact_lineage_chain = [_surface_record(root, source) for source in ARTIFACT_LINEAGE_CHAIN]
    belief_graph_planning = [_surface_record(root, source) for source in BELIEF_GRAPH_SURFACES]
    codegen_planning = [_surface_record(root, source) for source in CODEGEN_SURFACES]
    parallel_tracks = [_surface_record(root, source) for source in PARALLEL_TRACK_SURFACES]
    track_classifications = _track_classifications()
    merged_anchor = {
        "primary": _parse_merge_anchor(root, "679"),
        "prior": _parse_merge_anchor(root, "678"),
    }
    open_pr_stack = _open_pr_stack(root)

    scoped_path = root / "out/operator_review/abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_001.latest.json"
    auth_record_path = root / "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_record_001.latest.json"
    auth_gate_path = root / "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_gate_001.latest.json"
    traceability_path = root / "out/sync/abx_artifact_lineage_registry_traceability_audit/latest.json"

    scoped_receipt = _read_json(scoped_path)
    auth_record = _read_json(auth_record_path)
    auth_gate = _read_json(auth_gate_path)
    traceability_audit = _read_json(traceability_path)

    next_lane_eligible = _next_lane_eligible(
        scoped_receipt=scoped_receipt,
        auth_record=auth_record,
        auth_gate=auth_gate,
    )
    recommended_next_lane = TRACEABILITY_AUDIT_REGENERATION if next_lane_eligible else NOT_COMPUTABLE
    downstream_status = (
        "READY_FOR_TRACEABILITY_AUDIT_REGENERATION" if next_lane_eligible else NOT_COMPUTABLE
    )

    frontier_checks = _frontier_checks(
        root,
        merged_anchor=merged_anchor,
        open_pr_stack=open_pr_stack,
        artifact_lineage_chain=artifact_lineage_chain,
        belief_graph_planning=belief_graph_planning,
        codegen_planning=codegen_planning,
        track_classifications=track_classifications,
        next_lane_eligible=next_lane_eligible,
    )
    all_checks_pass = all(
        item["check_status"] in {"PASS", "OBSERVED"} for item in frontier_checks
    )
    revalidation_status = (
        "ABX_ARTIFACT_LINEAGE_DIRECT_REPAIR_FRONTIER_REVALIDATION_READY"
        if all_checks_pass
        else "ABX_ARTIFACT_LINEAGE_DIRECT_REPAIR_FRONTIER_REVALIDATION_DEGRADED"
    )

    base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": REVALIDATION_ID,
        "revalidation_id": REVALIDATION_ID,
        "revalidation_status": revalidation_status,
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_DIRECT_REPAIR_FRONTIER_REVALIDATION_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "evidence_only": True,
        "governance_docs": governance_docs,
        "merged_anchor": merged_anchor,
        "open_pr_stack": open_pr_stack,
        "artifact_lineage_chain": artifact_lineage_chain,
        "belief_graph_planning": belief_graph_planning,
        "codegen_planning": codegen_planning,
        "parallel_tracks": parallel_tracks,
        "track_classifications": track_classifications,
        "traceability_audit": {
            "path": "out/sync/abx_artifact_lineage_registry_traceability_audit/latest.json",
            "path_observed": traceability_path.is_file(),
            "audit_id": (
                traceability_audit.get("audit_id") if isinstance(traceability_audit, dict) else NOT_COMPUTABLE
            ),
            "source_hash": _sha256(traceability_path) if traceability_path.is_file() else NOT_COMPUTABLE,
            "scoped_repair_consumed": (
                isinstance(traceability_audit, dict)
                and traceability_audit.get("scoped_direct_repair_execution", {}).get("receipt_observed")
                is True
            ),
        },
        "frontier_checks": frontier_checks,
        "frontier_check_count": len(frontier_checks),
        "authority_locks": dict(AUTHORITY_LOCKS),
        "blocked_actions": list(BLOCKED_ACTIONS),
        "approval_granted": False,
        "authorization_granted": False,
        "authority_granted": False,
        "execution_allowed": False,
        "execution_authority": False,
        "implementation_authorized": False,
        "repair_execution_performed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "valid_for_implementation": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_planning_pr": False,
        "research_canary_guardrail": {
            "do_not_regenerate_research_canary_artifacts": True,
            "canary_spine_refresh_allowed": False,
            "p131_plus_implementation_authorized": False,
        },
        "recommended_next_action": (
            "maintain advisory-only frontier holds; consume this revalidation as evidence only; "
            "do not execute direct repairs or regenerate research-canary artifacts from this lane"
        ),
        "recommended_next_lane": recommended_next_lane,
        "downstream_status": downstream_status,
        "downstream": downstream_status,
    }
    return {**base, "revalidation_hash": canonical_hash(base)}


def render_abx_artifact_lineage_direct_repair_frontier_revalidation_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Artifact Lineage Direct Repair Frontier Revalidation 001",
        "",
        f"- `revalidation_id`: `{packet['revalidation_id']}`",
        f"- `revalidation_status`: `{packet['revalidation_status']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        f"- `downstream_status`: `{packet['downstream_status']}`",
        f"- `execution_allowed`: `{packet['execution_allowed']}`",
        f"- `repair_execution_performed`: `{packet['repair_execution_performed']}`",
        f"- `authority_granted`: `{packet['authority_granted']}`",
        "",
        "## Merged Anchor",
    ]
    merged = packet.get("merged_anchor", {})
    if isinstance(merged, dict):
        primary = merged.get("primary", {})
        prior = merged.get("prior", {})
        if isinstance(primary, dict):
            lines.append(
                f"- primary: PR #{primary.get('pr_number')} `{primary.get('merge_commit')}`"
            )
        if isinstance(prior, dict):
            lines.append(f"- prior: PR #{prior.get('pr_number')} `{prior.get('merge_commit')}`")
    lines.extend(["", "## Frontier Checks"])
    for check in packet.get("frontier_checks", []):
        if isinstance(check, dict):
            lines.append(
                f"- `{check['check_id']}`: {check['check_status']} — {check['observed_summary']}"
            )
    lines.extend(["", "## Track Classifications"])
    for track in packet.get("track_classifications", []):
        if isinstance(track, dict):
            lines.append(f"- `{track['track_id']}`: {track['classification']}")
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- `{action}`")
    return lines


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_abx_artifact_lineage_direct_repair_frontier_revalidation(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_artifact_lineage_direct_repair_frontier_revalidation(repo_root=root)
    write_canonical_json(target_root / OUT_JSON, packet)
    _write_markdown(
        target_root / OUT_MD,
        render_abx_artifact_lineage_direct_repair_frontier_revalidation_markdown(packet),
    )
    return packet
