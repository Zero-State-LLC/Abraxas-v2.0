from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "GlobalIngestOperatorDecisionEvidenceCollectionDryRun.v1"
SOURCE_PLAN_PATH = Path(
    "out/operator_review/global_ingest_operator_decision_evidence_collection_plan_001.latest.json"
)
DRY_RUN_JSON_PATH = Path(
    "out/operator_review/global_ingest_operator_decision_evidence_collection_dry_run_001.latest.json"
)
DRY_RUN_MD_PATH = Path(
    "out/operator_review/global_ingest_operator_decision_evidence_collection_dry_run_001.latest.md"
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


def build_global_ingest_operator_decision_evidence_collection_dry_run(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    plan = _read_json(root / SOURCE_PLAN_PATH)
    source_observed = plan is not None

    status = "NOT_COMPUTABLE"
    target_pipeline_id = "oracle_signal"
    decision_scope = "IMPLEMENTATION_SPEC_DECISION_REQUIRED"
    source_plan_hash = "NOT_COMPUTABLE"
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
    evaluation_blockers = [
        "source_evidence_collection_plan_missing_or_unreadable",
        f"source_path:{SOURCE_PLAN_PATH}",
    ]

    if plan is not None:
        target_pipeline_id = str(plan["target_pipeline_id"])
        decision_scope = str(plan["decision_scope"])
        source_plan_hash = str(plan["plan_hash"])
        source_request_id = str(plan["source_request_id"])
        source_hashes = {
            str(key): str(value) for key, value in dict(plan["source_hashes"]).items()
        }
        simulated_evidence_bundle = []
        for group in plan["evidence_bundle_groups"]:
            simulated_evidence_bundle.append(
                {
                    "group_id": str(group["group_id"]),
                    "attested": False,
                    "field_count": len(group["required_fields"]),
                    "missing_fields": [str(item) for item in group["required_fields"]],
                }
            )
        status = "GLOBAL_INGEST_OPERATOR_DECISION_EVIDENCE_COLLECTION_DRY_RUN_READY"
        evaluation_blockers = [
            "operator_identity_not_attested",
            "operator_decision_not_attested",
            "operator_acknowledgements_not_attested",
            "operator_provenance_evidence_not_attested",
            "operator_record_output_not_attested",
        ]

    readiness_summary = {
        "simulated_only": True,
        "operator_input_required": True,
        "groups_ready": 0,
        "groups_total": len(simulated_evidence_bundle),
        "evidence_bundle_complete": False,
        "valid_for_decision_record": False,
        "evaluation_blockers": evaluation_blockers,
    }

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "dry_run_id": "global_ingest_operator_decision_evidence_collection_dry_run_001",
        "dry_run_hash": "",
        "command": "BUILD_GLOBAL_INGEST_OPERATOR_DECISION_EVIDENCE_COLLECTION_DRY_RUN_001",
        "artifact_type": "GlobalIngestOperatorDecisionEvidenceCollectionDryRun.v1",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
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
            "preserve the oracle_signal hold and use the simulated evidence bundle to guide explicit operator decision evidence collection before any decision record exists"
        ),
        "recommended_next_patch": "NOT_COMPUTABLE",
        "recommended_next_state": "hold",
        "source_evidence_collection_plan_path": str(SOURCE_PLAN_PATH),
        "source_evidence_collection_plan_observed": source_observed,
        "source_evidence_collection_plan_hash": source_plan_hash,
        "source_request_id": source_request_id,
        "source_hashes": source_hashes,
        "simulated_evidence_bundle": simulated_evidence_bundle,
        "readiness_summary": readiness_summary,
        "evaluation_blockers": evaluation_blockers,
    }
    packet["dry_run_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "dry_run_hash"}
    )
    return packet


def render_global_ingest_operator_decision_evidence_collection_dry_run_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Global Ingest Operator Decision Evidence Collection Dry Run",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `target_pipeline_id`: `{packet['target_pipeline_id']}`",
        f"- `recommended_next_state`: `{packet['recommended_next_state']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Evaluation Blockers",
        "",
    ]
    for item in packet["evaluation_blockers"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Simulated Evidence Bundle", ""])
    for item in packet["simulated_evidence_bundle"]:
        lines.append(f"- `{item['group_id']}`: `{item['field_count']}` required fields")
    return lines


def write_global_ingest_operator_decision_evidence_collection_dry_run(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_global_ingest_operator_decision_evidence_collection_dry_run(root)
    write_canonical_json(target_root / DRY_RUN_JSON_PATH, packet)
    _write_markdown(
        target_root / DRY_RUN_MD_PATH,
        render_global_ingest_operator_decision_evidence_collection_dry_run_markdown(
            packet
        ),
    )
    return packet
