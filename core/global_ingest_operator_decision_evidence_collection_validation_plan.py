from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "GlobalIngestOperatorDecisionEvidenceCollectionValidationPlan.v1"
SOURCE_DRY_RUN_PATH = Path(
    "out/operator_review/global_ingest_operator_decision_evidence_collection_dry_run_001.latest.json"
)
VALIDATION_PLAN_JSON_PATH = Path(
    "out/operator_review/global_ingest_operator_decision_evidence_collection_validation_plan_001.latest.json"
)
VALIDATION_PLAN_MD_PATH = Path(
    "out/operator_review/global_ingest_operator_decision_evidence_collection_validation_plan_001.latest.md"
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _bundle_group_checks(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for idx, group in enumerate(groups, start=1):
        missing_fields = [str(item) for item in group.get("missing_fields", [])]
        checks.append(
            {
                "check_id": f"group_{idx:03d}",
                "group_id": str(group.get("group_id", "")),
                "attested": group.get("attested"),
                "field_count": group.get("field_count"),
                "missing_field_count": len(missing_fields),
                "passed": (
                    group.get("attested") is False
                    and isinstance(group.get("field_count"), int)
                    and group.get("field_count", 0) >= len(missing_fields)
                    and bool(missing_fields)
                ),
            }
        )
    return checks


def _invariant_checks(packet: Mapping[str, Any], readiness_summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    checks = [
        ("packet_simulated_only", packet.get("simulated_only"), True),
        ("packet_operator_input_required", packet.get("operator_input_required"), True),
        ("packet_valid_for_execution", packet.get("valid_for_execution"), False),
        ("packet_valid_for_decision_record", packet.get("valid_for_decision_record"), False),
        ("summary_simulated_only", readiness_summary.get("simulated_only"), True),
        ("summary_operator_input_required", readiness_summary.get("operator_input_required"), True),
        ("summary_groups_ready", readiness_summary.get("groups_ready"), 0),
        ("summary_evidence_bundle_complete", readiness_summary.get("evidence_bundle_complete"), False),
        ("summary_valid_for_decision_record", readiness_summary.get("valid_for_decision_record"), False),
    ]
    return [
        {
            "check_id": check_id,
            "observed": observed,
            "expected": expected,
            "passed": observed == expected,
        }
        for check_id, observed, expected in checks
    ]


def build_global_ingest_operator_decision_evidence_collection_validation_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    source_path = root / SOURCE_DRY_RUN_PATH
    source_payload = _read_json(source_path)
    source_observed = source_payload is not None

    status = "NOT_COMPUTABLE"
    source_dry_run_hash = "NOT_COMPUTABLE"
    source_dry_run_status = "NOT_COMPUTABLE"
    target_pipeline_id = "oracle_signal"
    decision_scope = "IMPLEMENTATION_SPEC_DECISION_REQUIRED"
    source_request_id = "NOT_COMPUTABLE"
    source_hashes = {
        "global_ingest_operator_decision_request": "NOT_COMPUTABLE",
        "global_pipeline_gap_backlog": "NOT_COMPUTABLE",
        "global_ingest_alignment_plan": "NOT_COMPUTABLE",
        "oracle_signal_intake_boundary_implementation_plan": "NOT_COMPUTABLE",
        "notion_operator_decision_backlog": "NOT_COMPUTABLE",
        "notion_spec_completion_queue": "NOT_COMPUTABLE",
        "global_pipeline_doctrine_proof": "NOT_COMPUTABLE",
    }
    simulated_evidence_bundle: list[dict[str, Any]] = []
    source_review_artifacts: list[str] = []
    readiness_summary: dict[str, Any] = {
        "simulated_only": False,
        "operator_input_required": False,
        "groups_ready": -1,
        "groups_total": -1,
        "evidence_bundle_complete": False,
        "valid_for_decision_record": False,
        "evaluation_blockers": ["source_dry_run_missing_or_unreadable"],
    }
    blockers = [
        "source_dry_run_missing_or_unreadable",
        f"source_path:{SOURCE_DRY_RUN_PATH}",
    ]

    if source_payload is not None:
        source_dry_run_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_dry_run_status = str(source_payload.get("status", "NOT_COMPUTABLE"))
        target_pipeline_id = str(source_payload.get("target_pipeline_id", target_pipeline_id))
        decision_scope = str(source_payload.get("decision_scope", decision_scope))
        source_request_id = str(source_payload.get("source_request_id", source_request_id))
        source_hashes = {
            str(key): str(value) for key, value in dict(source_payload.get("source_hashes", {})).items()
        }
        source_review_artifacts = [str(item) for item in source_payload.get("source_review_artifacts", [])]
        simulated_evidence_bundle = list(source_payload.get("simulated_evidence_bundle", []))
        readiness_summary = dict(source_payload.get("readiness_summary", readiness_summary))

        if source_dry_run_status != "GLOBAL_INGEST_OPERATOR_DECISION_EVIDENCE_COLLECTION_DRY_RUN_READY":
            status = "BLOCKED_BY_GLOBAL_INGEST_OPERATOR_DECISION_EVIDENCE_COLLECTION_DRY_RUN"
            blockers = [f"source_dry_run_status:{source_dry_run_status}"]
        else:
            bundle_checks = _bundle_group_checks(simulated_evidence_bundle)
            invariant_checks = _invariant_checks(source_payload, readiness_summary)
            bundle_failures = [check["check_id"] for check in bundle_checks if not check["passed"]]
            invariant_failures = [check["check_id"] for check in invariant_checks if not check["passed"]]
            if bundle_failures or invariant_failures:
                status = "GLOBAL_INGEST_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_PLAN_BLOCKED_BY_DRY_RUN"
                blockers = sorted(bundle_failures + invariant_failures)
            else:
                status = "GLOBAL_INGEST_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_PLAN_READY"
                blockers = []

    bundle_checks = _bundle_group_checks(simulated_evidence_bundle)
    invariant_checks = _invariant_checks(source_payload or {}, readiness_summary)
    validation_checks = [
        {"check_id": "source_dry_run_hash_present", "passed": source_dry_run_hash != "NOT_COMPUTABLE"},
        {"check_id": "source_request_id_present", "passed": source_request_id != "NOT_COMPUTABLE"},
        {"check_id": "simulated_bundle_present", "passed": bool(simulated_evidence_bundle)},
        {"check_id": "evaluation_blockers_present", "passed": bool(readiness_summary.get("evaluation_blockers"))},
    ]
    validation_blockers = sorted(
        list(
            {
                *(["simulated_evidence_bundle_missing"] if not simulated_evidence_bundle else []),
                *[check["check_id"] for check in bundle_checks if not check["passed"]],
                *[check["check_id"] for check in invariant_checks if not check["passed"]],
            }
        )
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "validation_plan_id": "global_ingest_operator_decision_evidence_collection_validation_plan_001",
        "validation_plan_hash": "",
        "command": "BUILD_GLOBAL_INGEST_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_PLAN_001",
        "artifact_type": "GlobalIngestOperatorDecisionEvidenceCollectionValidationPlan.v1",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "validation_plan_only": True,
        "simulated_only": True,
        "operator_input_required": True,
        "implementation_authorized": False,
        "execution_authority": False,
        "promotion_allowed": False,
        "forecast_weight_allowed": False,
        "runtime_mutation_allowed": False,
        "baseline_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "valid_for_execution": False,
        "valid_for_decision_record": False,
        "decision_scope": decision_scope,
        "target_pipeline_id": target_pipeline_id,
        "recommended_next_action": (
            "preserve the oracle_signal hold and verify the simulated evidence bundle shape before collecting any explicit operator decision evidence"
        ),
        "recommended_next_patch": "NOT_COMPUTABLE",
        "recommended_next_state": "hold",
        "source_dry_run_path": str(SOURCE_DRY_RUN_PATH),
        "source_dry_run_observed": source_observed,
        "source_dry_run_hash": source_dry_run_hash,
        "source_dry_run_status": source_dry_run_status,
        "source_request_id": source_request_id,
        "source_hashes": source_hashes,
        "source_review_artifacts": source_review_artifacts,
        "bundle_group_checks": bundle_checks,
        "invariant_checks": invariant_checks,
        "validation_checks": validation_checks,
        "source_readiness_summary": readiness_summary,
        "validation_blockers": validation_blockers,
        "blockers": blockers,
    }
    packet["validation_plan_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "validation_plan_hash"}
    )
    return packet


def render_global_ingest_operator_decision_evidence_collection_validation_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Global Ingest Operator Decision Evidence Collection Validation Plan",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `target_pipeline_id`: `{packet['target_pipeline_id']}`",
        f"- `recommended_next_state`: `{packet['recommended_next_state']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Validation Blockers",
        "",
    ]
    for item in packet["validation_blockers"]:
        lines.append(f"- `{item}`")
    return lines


def write_global_ingest_operator_decision_evidence_collection_validation_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_global_ingest_operator_decision_evidence_collection_validation_plan(
        root
    )
    write_canonical_json(target_root / VALIDATION_PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / VALIDATION_PLAN_MD_PATH,
        render_global_ingest_operator_decision_evidence_collection_validation_plan_markdown(
            packet
        ),
    )
    return packet
