from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "ABXAutoIngestShadowStabilizationReviewRecord.v1"
VALIDATION_PACK_JSON_PATH = Path("out/audit/abx_auto_ingest_validation_pack_001.latest.json")
PROJECTION_PACK_JSON_PATH = Path("out/projections/aal_viz_ingest_projection_pack_001.latest.json")
RECORD_JSON_PATH = Path("out/operator_review/abx_auto_ingest_shadow_stabilization_review_record_001.latest.json")
RECORD_MD_PATH = Path("out/operator_review/abx_auto_ingest_shadow_stabilization_review_record_001.latest.md")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _authority_locks() -> dict[str, bool]:
    return {
        "activation_authority": False,
        "baseline_mutation": False,
        "canon_mutation": False,
        "execution_authority": False,
        "forecast_authority": False,
        "github_writeback": False,
        "implementation_authority": False,
        "ingest_runner_mutation": False,
        "notion_writeback": False,
        "pipeline_or_route_mutation": False,
        "production_activation": False,
        "queue_mutation": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "token_minting": False,
    }


def _projection_authority_locked(projection_pack: Mapping[str, Any]) -> bool:
    return (
        projection_pack.get("schema_version") == "AALVizIngestProjectionPack.v1"
        and projection_pack.get("advisory_only") is True
        and projection_pack.get("projection_only") is True
        and projection_pack.get("non_authoritative") is True
        and projection_pack.get("execution_authority") is False
        and projection_pack.get("runtime_mutation") is False
        and projection_pack.get("canon_mutation") is False
        and projection_pack.get("authority") == "PROJECTION_ONLY"
    )


def build_abx_auto_ingest_shadow_stabilization_review_record(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    validation_pack = _read_json(root / VALIDATION_PACK_JSON_PATH)
    projection_pack = _read_json(root / PROJECTION_PACK_JSON_PATH)
    validation_ready = (
        validation_pack.get("schema_version") == "ABXAutoIngestValidationPack.v1"
        and validation_pack.get("final_status") == "PASS"
        and validation_pack.get("advisory_only") is True
        and validation_pack.get("projection_only") is True
        and validation_pack.get("non_authoritative") is True
        and validation_pack.get("execution_authority") is False
        and validation_pack.get("runtime_mutation") is False
        and validation_pack.get("canon_mutation") is False
        and validation_pack.get("check_results", {}).get("authority_leakage_scan") == "PASS_NO_FORBIDDEN_FIELDS"
        and validation_pack.get("check_results", {}).get("viz_projection_only") == "PASS_PROJECTION_ONLY"
        and validation_pack.get("success_criteria", {}).get("forecast_activation") == "PASS_BLOCKED"
        and validation_pack.get("success_criteria", {}).get("canon_mutation") == "PASS_BLOCKED"
    )
    projection_locked = _projection_authority_locked(projection_pack)
    review_ready = validation_ready and projection_locked

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "ABX_AUTO_INGEST_SHADOW_STABILIZATION_REVIEW_ACCEPTED"
        if review_ready
        else "ABX_AUTO_INGEST_SHADOW_STABILIZATION_REVIEW_BLOCKED",
        "record_id": "abx_auto_ingest_shadow_stabilization_review_record_001",
        "record_hash": "",
        "command": "BUILD_ABX_AUTO_INGEST_SHADOW_STABILIZATION_REVIEW_RECORD_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "decision_scope": "AUTO_INGEST_SHADOW_STABILIZATION_REVIEW_ONLY",
        "selected_decision": "APPROVE_SHADOW_STABILIZATION_REVIEW" if review_ready else "NOT_COMPUTABLE",
        "operator_instruction_observed": "continue",
        "validation_pack_accepted_as_reviewed_evidence": validation_ready,
        "projection_boundary_acknowledged": projection_locked,
        "shadow_stabilization_review_completed": review_ready,
        "source_validation_pack_path": str(VALIDATION_PACK_JSON_PATH),
        "source_validation_pack_hash": str(validation_pack.get("validation_hash", "NOT_COMPUTABLE")),
        "source_validation_status": str(validation_pack.get("final_status", "NOT_COMPUTABLE")),
        "source_projection_pack_path": str(PROJECTION_PACK_JSON_PATH),
        "source_projection_pack_hash": str(projection_pack.get("projection_hash", "NOT_COMPUTABLE")),
        "implementation_authorized": False,
        "activation_authority": False,
        "production_activation_allowed": False,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "ingest_runner_mutation_allowed": False,
        "pipeline_or_route_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "baseline_mutation_allowed": False,
        "forecast_authority": False,
        "forecast_weight_allowed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_planning_pr": False,
        "authority_locks": _authority_locks(),
        "decision_outcome_summary": (
            "ABX Auto Ingest validation pack is accepted for review-only shadow stabilization evidence; no "
            "activation, implementation, runtime, scheduler, queue, route, forecast, canon, baseline, token, "
            "writeback, ingest-runner, or execution authority is granted."
        ),
        "allowed_follow_on_actions": [
            "MAINTAIN_AUTO_INGEST_VALIDATION_PACK_AS_REVIEWED_EVIDENCE",
            "MAINTAIN_AAL_VIZ_INGEST_PROJECTION_ONLY_BOUNDARY",
            "KEEP_AUTO_INGEST_ACTIVATION_BLOCKED",
        ],
        "blocked_actions": [
            "AUTO_INGEST_ACTIVATION",
            "INGEST_RUNNER_BEHAVIOR_MUTATION",
            "PIPELINE_OR_ROUTE_MUTATION",
            "RUNTIME_OR_SCHEDULER_MUTATION",
            "QUEUE_MUTATION",
            "FORECAST_WEIGHTING",
            "CANON_PROMOTION",
            "BASELINE_MUTATION",
            "EXECUTION_AUTHORITY_GRANT",
            "LIVE_NOTION_WRITEBACK",
            "GITHUB_WRITEBACK_AUTOMATION",
            "TOKEN_MINTING",
        ],
        "recommended_next_action": (
            "maintain auto-ingest validation pack as reviewed stabilization evidence until a separate governed "
            "lane explicitly authorizes activation or runtime integration"
        ),
        "recommended_next_patch": "NOT_COMPUTABLE",
    }
    packet["record_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "record_hash"})
    return packet


def render_abx_auto_ingest_shadow_stabilization_review_record_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Auto Ingest Shadow Stabilization Review Record",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `selected_decision`: `{packet['selected_decision']}`",
        f"- `decision_scope`: `{packet['decision_scope']}`",
        f"- `shadow_stabilization_review_completed`: `{packet['shadow_stabilization_review_completed']}`",
        f"- `activation_authority`: `{packet['activation_authority']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        f"- `runtime_mutation_allowed`: `{packet['runtime_mutation_allowed']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Decision Boundary",
        "",
        str(packet["decision_outcome_summary"]),
        "",
        "## Blocked Actions",
        "",
    ]
    for item in packet["blocked_actions"]:
        lines.append(f"- `{item}`")
    return lines


def write_abx_auto_ingest_shadow_stabilization_review_record(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_auto_ingest_shadow_stabilization_review_record(root)
    write_canonical_json(target_root / RECORD_JSON_PATH, packet)
    _write_markdown(
        target_root / RECORD_MD_PATH,
        render_abx_auto_ingest_shadow_stabilization_review_record_markdown(packet),
    )
    return packet
