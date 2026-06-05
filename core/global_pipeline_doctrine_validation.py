from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

PROOF_SCHEMA_VERSION = "GlobalPipelineDoctrineValidationProof.v1"
REVIEW_SCHEMA_VERSION = "GlobalPipelineDoctrineValidationOperatorReviewPacket.v1"

PROOF_JSON_PATH = Path("out/global_pipeline_doctrine_validation/latest.json")
PROOF_MD_PATH = Path("out/global_pipeline_doctrine_validation/latest.md")
REVIEW_JSON_PATH = Path("out/global_pipeline_doctrine_validation/operator_review_packet.latest.json")
REVIEW_MD_PATH = Path("out/global_pipeline_doctrine_validation/operator_review_packet.latest.md")

REGISTRY_PATH = Path("out/global_pipeline_registry/latest.json")
VALIDATION_PATH = Path("out/validation/latest.json")


def _read_json(root: Path, rel_path: Path) -> dict[str, Any]:
    import json

    return json.loads((root / rel_path).read_text(encoding="utf-8"))


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_global_pipeline_doctrine_validation_proof(
    root: Path | str = ".",
    *,
    source_root: Path | str | None = None,
) -> dict[str, Any]:
    base = Path(root)
    source_base = Path(source_root) if source_root is not None else base
    registry = _read_json(source_base, REGISTRY_PATH)
    validation = _read_json(source_base, VALIDATION_PATH)

    registry_by_id = {item["pipeline_id"]: item for item in registry["pipelines"]}
    validation_by_id = {item["pipeline_id"]: item for item in validation["results"]}
    missing_validation_ids = sorted(
        pipeline_id
        for pipeline_id in registry_by_id
        if pipeline_id not in validation_by_id
    )

    legacy_contract_posture_ids = sorted(
        item["pipeline_id"]
        for item in validation["results"]
        if item.get("status") == "legacy_contract_posture"
    )
    doctrine_compliant_ids = sorted(
        item["pipeline_id"]
        for item in validation["results"]
        if item.get("status") == "doctrine_compliant"
    )
    repair_required_ids = sorted(
        item["pipeline_id"]
        for item in validation["results"]
        if item.get("status") == "repair_required"
    )
    failed_ids = sorted(
        item["pipeline_id"]
        for item in validation["results"]
        if item.get("status") == "failed"
    )
    missing_contract_ids = sorted(
        item["pipeline_id"]
        for item in registry["pipelines"]
        if item.get("contract_status") != "observed"
    )
    authority_violation_ids = sorted(
        item["pipeline_id"]
        for item in registry["pipelines"]
        if any(value is not False for value in item.get("authority", {}).values())
    )

    status = "GLOBAL_PIPELINE_DOCTRINE_VALIDATION_PROOF_EMITTED"
    recommended_next_state = "hold"
    if authority_violation_ids:
        recommended_next_state = "repair"

    proof: dict[str, Any] = {
        "schema_version": PROOF_SCHEMA_VERSION,
        "proof_id": "",
        "status": status,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "baseline_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "forecast_weight_allowed": False,
        "promotion_allowed": False,
        "registry_source_hash": registry["registry_id"],
        "validation_source_summary": validation["summary"],
        "pipeline_count": registry["pipeline_count"],
        "tier_counts": registry["tier_counts"],
        "observed_validation_count": len(validation["results"]),
        "missing_validation_count": len(missing_validation_ids),
        "missing_validation_ids": missing_validation_ids,
        "doctrine_compliant_count": len(doctrine_compliant_ids),
        "doctrine_compliant_ids": doctrine_compliant_ids,
        "legacy_contract_posture_count": len(legacy_contract_posture_ids),
        "legacy_contract_posture_ids": legacy_contract_posture_ids,
        "repair_required_count": len(repair_required_ids),
        "repair_required_ids": repair_required_ids,
        "failed_count": len(failed_ids),
        "failed_ids": failed_ids,
        "missing_contract_count": len(missing_contract_ids),
        "missing_contract_ids": missing_contract_ids,
        "authority_violation_count": len(authority_violation_ids),
        "authority_violation_ids": authority_violation_ids,
        "proof_complete": True,
        "physical_repo_implementation_ready": False,
        "not_computable_reasons": [],
        "recommended_next_state": recommended_next_state,
        "recommended_next_commands": [
            "BUILD_GLOBAL_PIPELINE_AAL_VIZ_DASHBOARD_001",
            "HOLD_FOR_OPERATOR_REVIEW",
        ],
    }
    proof["proof_id"] = canonical_hash({k: v for k, v in proof.items() if k != "proof_id"})
    return proof


def build_global_pipeline_doctrine_validation_operator_review_packet(
    proof_packet: dict[str, Any] | None = None,
    root: Path | str = ".",
    *,
    source_root: Path | str | None = None,
) -> dict[str, Any]:
    proof = proof_packet or build_global_pipeline_doctrine_validation_proof(
        root,
        source_root=source_root,
    )
    blocked_reasons: list[str] = []
    if proof["authority_violation_count"] > 0:
        blocked_reasons.append("AUTHORITY_VIOLATION_PRESENT")
    if proof["failed_count"] > 0:
        blocked_reasons.append("FAILED_DOCTRINE_VALIDATION_PRESENT")
    if proof["repair_required_count"] > 0:
        blocked_reasons.append("REPAIR_REQUIRED_VALIDATION_PRESENT")
    if proof["missing_contract_count"] > 0:
        blocked_reasons.append("MISSING_GLOBAL_PIPELINE_CONTRACTS")
    if proof["missing_validation_count"] > 0:
        blocked_reasons.append("MISSING_GLOBAL_PIPELINE_VALIDATION_COVERAGE")
    if proof["legacy_contract_posture_count"] > 0:
        blocked_reasons.append("LEGACY_CONTRACT_POSTURE_PRESENT")

    if proof["authority_violation_count"] > 0:
        review_state = "rejected"
        priority = "P0"
    elif blocked_reasons:
        review_state = "repair_required"
        priority = "P1"
    else:
        review_state = "eligible_for_operator_review"
        priority = "P2"

    review: dict[str, Any] = {
        "schema_version": REVIEW_SCHEMA_VERSION,
        "review_packet_id": "",
        "proof_id": proof["proof_id"],
        "status": "GLOBAL_PIPELINE_DOCTRINE_VALIDATION_OPERATOR_REVIEW_PACKET_EMITTED",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "baseline_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "forecast_weight_allowed": False,
        "promotion_allowed": False,
        "state": review_state,
        "priority": priority,
        "allowed_decisions": (
            ["REJECT", "HOLD"]
            if review_state == "rejected"
            else ["HOLD", "REQUEST_REPAIR", "REJECT"]
            if review_state == "repair_required"
            else ["HOLD", "APPROVE_OPERATOR_REVIEW", "REJECT"]
        ),
        "required_operator_actions": (
            ["remove_authority_leakage"]
            if review_state == "rejected"
            else [
                "review_global_pipeline_doctrine_validation_proof",
                "acknowledge_global_pipeline_gaps",
                "defer_repo_execution_until_dashboard_surfaces_exist",
            ]
        ),
        "blocked_reasons": blocked_reasons,
        "recommended_next_state": review_state,
    }
    review["review_packet_id"] = canonical_hash(
        {k: v for k, v in review.items() if k != "review_packet_id"}
    )
    return review


def write_global_pipeline_doctrine_validation_artifacts(
    root: Path | str = ".",
    *,
    source_root: Path | str | None = None,
) -> dict[str, dict[str, Any]]:
    base = Path(root)
    proof = build_global_pipeline_doctrine_validation_proof(
        base,
        source_root=source_root,
    )
    review = build_global_pipeline_doctrine_validation_operator_review_packet(proof)

    write_canonical_json(base / PROOF_JSON_PATH, proof)
    write_canonical_json(base / REVIEW_JSON_PATH, review)

    _write_markdown(
        base / PROOF_MD_PATH,
        [
            "# Global Pipeline Doctrine Validation Proof",
            "",
            f"- `status`: `{proof['status']}`",
            f"- `pipeline_count`: `{proof['pipeline_count']}`",
            f"- `observed_validation_count`: `{proof['observed_validation_count']}`",
            f"- `missing_validation_count`: `{proof['missing_validation_count']}`",
            f"- `legacy_contract_posture_count`: `{proof['legacy_contract_posture_count']}`",
            f"- `missing_contract_count`: `{proof['missing_contract_count']}`",
            f"- `recommended_next_state`: `{proof['recommended_next_state']}`",
            "",
            "## Recommended Next Commands",
            *[f"- `{command}`" for command in proof["recommended_next_commands"]],
        ],
    )
    _write_markdown(
        base / REVIEW_MD_PATH,
        [
            "# Global Pipeline Doctrine Validation Operator Review Packet",
            "",
            f"- `status`: `{review['status']}`",
            f"- `state`: `{review['state']}`",
            f"- `priority`: `{review['priority']}`",
            "",
            "## Blocked Reasons",
            *([f"- `{reason}`" for reason in review["blocked_reasons"]] or ["- none"]),
            "",
            "## Required Operator Actions",
            *[f"- `{action}`" for action in review["required_operator_actions"]],
        ],
    )

    return {
        "proof_packet": proof,
        "operator_review_packet": review,
    }
