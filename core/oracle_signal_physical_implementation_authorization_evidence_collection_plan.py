from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "OracleSignalPhysicalImplementationAuthorizationEvidenceCollectionPlan.v1"
PLAN_JSON_PATH = Path(
    "out/operator_review/oracle_signal_physical_implementation_authorization_evidence_collection_plan_001.latest.json"
)
PLAN_MD_PATH = Path(
    "out/operator_review/oracle_signal_physical_implementation_authorization_evidence_collection_plan_001.latest.md"
)

SOURCE_RECORD_PLAN_PATH = Path(
    "out/operator_review/oracle_signal_physical_implementation_authorization_record_plan_001.latest.json"
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _authority_locks() -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "execution_authority": False,
        "forecast_weight": False,
        "github_writeback": False,
        "implementation_authority": False,
        "ingest_runner_mutation": False,
        "notion_writeback": False,
        "operator_evidence_attestation": False,
        "pipeline_or_route_mutation": False,
        "queue_mutation": False,
        "record_creation": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "token_minting": False,
    }


def build_oracle_signal_physical_implementation_authorization_evidence_collection_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    record_plan = _read_json(root / SOURCE_RECORD_PLAN_PATH)
    record_plan_ready = (
        record_plan.get("status") == "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_RECORD_PLAN_READY"
        and record_plan.get("record_plan_ready") is True
        and record_plan.get("record_creation_authorized") is False
        and record_plan.get("implementation_authorized") is False
        and record_plan.get("execution_authority") is False
        and record_plan.get("safe_to_create_authorization_record") is False
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_EVIDENCE_COLLECTION_PLAN_READY"
            if record_plan_ready
            else "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_EVIDENCE_COLLECTION_PLAN_BLOCKED"
        ),
        "plan_id": "oracle_signal_physical_implementation_authorization_evidence_collection_plan_001",
        "plan_hash": "",
        "command": "BUILD_ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_EVIDENCE_COLLECTION_PLAN_001",
        "target_pipeline_id": "oracle_signal",
        "decision_scope": "PHYSICAL_IMPLEMENTATION_AUTHORIZATION_EVIDENCE_COLLECTION_ONLY",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "source_record_plan_path": SOURCE_RECORD_PLAN_PATH.as_posix(),
        "source_record_plan_hash": str(record_plan.get("plan_hash", "NOT_COMPUTABLE")),
        "evidence_collection_plan_ready": record_plan_ready,
        "operator_evidence_attested": False,
        "record_creation_authorized": False,
        "implementation_authorized": False,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "ingest_runner_mutation_allowed": False,
        "pipeline_or_route_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "forecast_weight_allowed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "safe_to_create_authorization_record": False,
        "safe_to_prepare_implementation_pr": False,
        "authority_locks": _authority_locks(),
        "evidence_collection_steps": [
            {
                "step_id": "ORACLE-PHYS-EVIDENCE-001",
                "required": True,
                "description": "Collect explicit operator identity, role, timestamp, and selected decision for physical implementation authorization.",
            },
            {
                "step_id": "ORACLE-PHYS-EVIDENCE-002",
                "required": True,
                "description": "Bind the operator decision to the held physical implementation review hash and record-plan hash.",
            },
            {
                "step_id": "ORACLE-PHYS-EVIDENCE-003",
                "required": True,
                "description": "Collect acknowledgment that execution, runtime, scheduler, route, queue, canon, forecast, writeback, and token authority remain denied unless separately authorized.",
            },
            {
                "step_id": "ORACLE-PHYS-EVIDENCE-004",
                "required": True,
                "description": "Collect rollback and fail-closed acknowledgments for any future physical implementation proposal.",
            },
        ],
        "allowed_follow_on_actions": [
            "COLLECT_EXPLICIT_PHYSICAL_IMPLEMENTATION_OPERATOR_AUTHORIZATION",
            "VALIDATE_COLLECTED_OPERATOR_EVIDENCE_BEFORE_RECORD_DRY_RUN",
            "MAINTAIN_ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_HOLD",
        ],
        "blocked_actions": [
            "ATTEST_OPERATOR_EVIDENCE_WITHOUT_EXTERNAL_INPUT",
            "CREATE_AUTHORIZATION_RECORD_WITHOUT_OPERATOR_EVIDENCE",
            "CORE_ORACLE_SIGNAL_IMPLEMENTATION",
            "INGEST_RUNNER_BEHAVIOR_MUTATION",
            "PIPELINE_OR_ROUTE_MUTATION",
            "RUNTIME_OR_SCHEDULER_MUTATION",
            "QUEUE_MUTATION",
            "FORECAST_WEIGHTING",
            "CANON_PROMOTION",
            "EXECUTION_AUTHORITY_GRANT",
            "LIVE_NOTION_WRITEBACK",
            "GITHUB_WRITEBACK_AUTOMATION",
            "TOKEN_MINTING",
        ],
        "recommended_next_action": (
            "collect explicit operator authorization evidence externally; do not simulate, attest, or create "
            "an authorization record until that evidence exists"
        ),
        "recommended_next_patch": "NOT_COMPUTABLE",
    }
    packet["plan_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "plan_hash"})
    return packet


def render_oracle_signal_physical_implementation_authorization_evidence_collection_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Oracle Signal Physical Implementation Authorization Evidence Collection Plan",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `evidence_collection_plan_ready`: `{packet['evidence_collection_plan_ready']}`",
        f"- `operator_evidence_attested`: `{packet['operator_evidence_attested']}`",
        f"- `record_creation_authorized`: `{packet['record_creation_authorized']}`",
        f"- `implementation_authorized`: `{packet['implementation_authorized']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Evidence Collection Steps",
    ]
    for step in packet["evidence_collection_steps"]:
        lines.append(f"- `{step['step_id']}`: {step['description']}")
    lines.extend(["", "## Blocked Actions", ""])
    for item in packet["blocked_actions"]:
        lines.append(f"- `{item}`")
    return lines


def write_oracle_signal_physical_implementation_authorization_evidence_collection_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_oracle_signal_physical_implementation_authorization_evidence_collection_plan(root)
    write_canonical_json(target_root / PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / PLAN_MD_PATH,
        render_oracle_signal_physical_implementation_authorization_evidence_collection_plan_markdown(packet),
    )
    return packet
