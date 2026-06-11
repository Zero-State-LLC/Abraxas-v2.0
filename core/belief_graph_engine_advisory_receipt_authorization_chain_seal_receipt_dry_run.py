from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_plan import (
    OUT_JSON as SOURCE_SEAL_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "BeliefGraphEngineAdvisoryReceiptAuthorizationChainSealReceiptDryRun.v1"
DRY_RUN_ID = "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_DRY_RUN_001"
OUT_JSON = (
    "out/audit/"
    "belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run_001.latest.md"
)

EXPECTED_SOURCE_STATUS = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_PLAN_READY"
)
EXPECTED_NEXT_LANE = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_DRY_RUN"
)
RECOMMENDED_NEXT_LANE = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_REVIEW"
)


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _read_json(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _check(check_id: str, passed: bool) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed}


def _source_requirements(source: Mapping[str, Any]) -> list[dict[str, Any]]:
    requirements = source.get("seal_receipt_requirements", [])
    if not isinstance(requirements, list):
        return []
    results: list[dict[str, Any]] = []
    for item in requirements:
        if isinstance(item, Mapping):
            requirement_id = str(item.get("requirement_id", "NOT_COMPUTABLE"))
            status = str(item.get("requirement_status", "NOT_COMPUTABLE"))
            results.append(
                {
                    "check_id": f"source_requirement:{requirement_id}",
                    "source_status": status,
                    "passed": status in {"SATISFIED", "ENFORCED", "HELD_FOR_OPERATOR", "PLANNED_ONLY"},
                }
            )
    return sorted(results, key=lambda row: row["check_id"])


def build_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run(
    *,
    repo_root: str | Path,
    source_seal_receipt_plan_path: str | Path = SOURCE_SEAL_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_seal_receipt_plan_path).as_posix()
    source = _read_json(root / source_seal_receipt_plan_path)

    source_status = str(source.get("seal_receipt_plan_status", "NOT_COMPUTABLE"))
    source_observed = bool(source)
    source_ready = (
        source.get("artifact_type")
        == "BeliefGraphEngineAdvisoryReceiptAuthorizationChainSealReceiptPlan.v1"
        and source_status == EXPECTED_SOURCE_STATUS
        and source.get("recommended_next_lane") == EXPECTED_NEXT_LANE
        and source.get("seal_receipt_plan_only") is True
        and source.get("seal_receipt_creation_allowed") is False
        and source.get("seal_receipt_created") is False
        and source.get("recursive_chain_sealed") is False
        and source.get("recursive_chain_continuation_allowed") is False
        and source.get("authorization_chain_continuation_allowed") is False
        and source.get("authorization_record_created") is False
        and source.get("authorization_token_created") is False
        and source.get("authorization_granted") is False
        and source.get("execution_authority") is False
    )

    requirement_results = _source_requirements(source)
    authority_results = [
        _check("source_advisory_only_true", source.get("advisory_only") is True),
        _check("source_projection_only_true", source.get("projection_only") is True),
        _check("source_non_authoritative_true", source.get("non_authoritative") is True),
        _check("source_seal_receipt_plan_only_true", source.get("seal_receipt_plan_only") is True),
        _check("source_seal_receipt_created_false", source.get("seal_receipt_created") is False),
        _check("source_seal_receipt_creation_allowed_false", source.get("seal_receipt_creation_allowed") is False),
        _check("source_recursive_chain_sealed_false", source.get("recursive_chain_sealed") is False),
        _check("source_recursive_chain_continuation_allowed_false", source.get("recursive_chain_continuation_allowed") is False),
        _check("source_authorization_granted_false", source.get("authorization_granted") is False),
        _check("source_authorization_token_created_false", source.get("authorization_token_created") is False),
        _check("source_execution_authority_false", source.get("execution_authority") is False),
        _check("source_valid_for_execution_false", source.get("valid_for_execution") is False),
        _check("source_valid_for_implementation_false", source.get("valid_for_implementation") is False),
    ]
    authority_results = sorted(authority_results, key=lambda row: row["check_id"])
    all_results = requirement_results + authority_results
    failed_checks = sorted(str(row["check_id"]) for row in all_results if row.get("passed") is False)

    if not source_observed:
        dry_run_status = "NOT_COMPUTABLE"
        validation_passed = False
        recommended_next_lane = "NOT_COMPUTABLE"
        blockers = ["source_seal_receipt_plan_missing_or_unreadable", f"source_path:{source_path}"]
    elif source_status != EXPECTED_SOURCE_STATUS:
        dry_run_status = "BLOCKED_BY_BELIEF_GRAPH_AUTHORIZATION_CHAIN_SEAL_RECEIPT_PLAN"
        validation_passed = False
        recommended_next_lane = "NOT_COMPUTABLE"
        blockers = [f"source_seal_receipt_plan_status:{source_status}"]
    elif not source_ready:
        dry_run_status = "BLOCKED_BY_FAILED_SEAL_RECEIPT_PLAN_SOURCE"
        validation_passed = False
        recommended_next_lane = "NOT_COMPUTABLE"
        blockers = ["source_seal_receipt_plan_invariants_failed"]
    elif failed_checks:
        dry_run_status = "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_DRY_RUN_FAILED"
        validation_passed = False
        recommended_next_lane = "NOT_COMPUTABLE"
        blockers = [f"validation_check_failed:{check_id}" for check_id in failed_checks]
    else:
        dry_run_status = "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_DRY_RUN_READY"
        validation_passed = True
        recommended_next_lane = RECOMMENDED_NEXT_LANE
        blockers = []

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "dry_run_id": DRY_RUN_ID,
        "seal_receipt_dry_run_status": dry_run_status,
        "source_seal_receipt_plan": {
            "path": source_path,
            "hash": _sha256(root / source_seal_receipt_plan_path),
            "seal_receipt_plan_status": source_status,
            "recommended_next_lane": str(source.get("recommended_next_lane", "NOT_COMPUTABLE")),
            "source_observed": source_observed,
            "source_ready": source_ready,
        },
        "requirement_validation_results": requirement_results,
        "authority_invariant_validation_results": authority_results,
        "validation_passed": validation_passed,
        "validation_blockers": sorted(blockers),
        "seal_receipt_dry_run_only": True,
        "seal_receipt_created": False,
        "seal_receipt_creation_allowed": False,
        "recursive_chain_sealed": False,
        "recursive_chain_continuation_allowed": False,
        "authorization_chain_continuation_allowed": False,
        "authorization_record_creation_record_creation_allowed": False,
        "authorization_record_creation_allowed": False,
        "authorization_record_created": False,
        "authorization_token_created": False,
        "operator_approved": False,
        "authorization_granted": False,
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_action": (
            "prepare a separate advisory seal-receipt review only; do not create a seal receipt, "
            "resume recursive authorization lanes, mint tokens, or implement the Belief Graph engine"
            if validation_passed
            else "repair source seal-receipt plan evidence before any seal-receipt review"
        ),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "receipt_code_creation_authorized": False,
        "receipt_implementation_authorized": False,
        "receipt_implementation_performed": False,
        "belief_graph_engine_implementation_authorized": False,
        "belief_graph_engine_implementation_performed": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "forecast_routing_allowed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "authority_locks": {
            "authorization_chain_continuation": False,
            "authorization_chain_sealing": False,
            "authorization_grant": False,
            "authorization_record_creation": False,
            "authorization_record_creation_record_creation": False,
            "authorization_token_creation": False,
            "belief_promotion": False,
            "canon_mutation": False,
            "execution_authority": False,
            "forecast_routing": False,
            "github_writeback": False,
            "notion_writeback": False,
            "queue_mutation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "truth_assignment": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Belief Graph Engine Advisory Receipt Authorization Chain Seal Receipt Dry Run",
        "",
        f"- dry_run_id: {packet['dry_run_id']}",
        f"- seal_receipt_dry_run_status: {packet['seal_receipt_dry_run_status']}",
        f"- validation_passed: {packet['validation_passed']}",
        f"- seal_receipt_dry_run_only: {packet['seal_receipt_dry_run_only']}",
        f"- seal_receipt_creation_allowed: {packet['seal_receipt_creation_allowed']}",
        f"- seal_receipt_created: {packet['seal_receipt_created']}",
        f"- recursive_chain_sealed: {packet['recursive_chain_sealed']}",
        f"- recursive_chain_continuation_allowed: {packet['recursive_chain_continuation_allowed']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- authorization_granted: {packet['authorization_granted']}",
        f"- execution_authority: {packet['execution_authority']}",
        "",
        "## Validation Blockers",
    ]
    blockers = packet.get("validation_blockers", [])
    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- none")
    lines.extend(["", "## Authority Invariant Checks"])
    for result in packet.get("authority_invariant_validation_results", []):
        if isinstance(result, dict):
            lines.append(f"- {result['check_id']}: {result['passed']}")
    return lines


def write_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
