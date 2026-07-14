from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

ARTIFACT_TYPE = "OracleConfidenceCalibrationPlan.v1"
PLAN_ID = "ORACLE_CONFIDENCE_CALIBRATION_PLAN_001"
OUT_JSON = "out/sync/oracle_confidence_calibration_plan/latest.json"
OUT_MD = "out/sync/oracle_confidence_calibration_plan/latest.md"
RESEARCH_RECEIPT_PATH = "out/sync/oracle_signal_research_intake_receipt/latest.json"
DECISION_REQUEST_PATH = "out/operator_review/global_ingest_operator_decision_request_001.latest.json"
TARGET_CANDIDATE_ID = "ORACLE_CONFIDENCE_CALIBRATION"
TARGET_ALLOWED_STATUS = "ADVISORY_IMPLEMENTATION_CANDIDATE"
PATCH_ID = "PATCH-ABX-ORACLE-CONFIDENCE-CALIBRATION-001"

_PLANNED_CONTRACT_PATHS = (
    "contracts/oracle/oracle_confidence_calibration_profile.v1.schema.json",
    "contracts/oracle/oracle_confidence_calibration_bucket_set.v1.schema.json",
    "contracts/oracle/oracle_confidence_calibration_receipt.v1.schema.json",
)
_PLANNED_RUNNER_PATHS = ("scripts/run_oracle_confidence_calibration.py",)
_PLANNED_TEST_PATHS = ("tests/test_oracle_confidence_calibration.py",)
_PLANNED_ARTIFACT_PATHS = (
    "out/oracle/oracle_confidence_calibration_receipt.latest.json",
    "out/oracle/oracle_confidence_calibration_receipt.latest.md",
)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _source_hash(path: Path) -> str:
    try:
        return canonical_hash(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        return NOT_COMPUTABLE


def _find_candidate(packet: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    for item in packet.get("candidate_mappings", []):
        if item.get("candidate_id") == candidate_id:
            return item
    return {}


def _planned_phases() -> list[dict[str, Any]]:
    return [
        {
            "phase_id": "OCC-PHASE-001",
            "phase_status": "PLANNED_ADVISORY_ONLY",
            "title": "Calibration profile contract planning",
            "planned_outputs": list(_PLANNED_CONTRACT_PATHS),
            "boundary_guard": "contract-only additions; no runtime Oracle mutation",
        },
        {
            "phase_id": "OCC-PHASE-002",
            "phase_status": "PLANNED_ADVISORY_ONLY",
            "title": "Calibration receipt and bucket semantics",
            "planned_outputs": [
                _PLANNED_ARTIFACT_PATHS[0],
                _PLANNED_ARTIFACT_PATHS[1],
            ],
            "boundary_guard": "receipt-only advisory confidence surface with no truth authority",
        },
        {
            "phase_id": "OCC-PHASE-003",
            "phase_status": "PLANNED_ADVISORY_ONLY",
            "title": "Boundary runner and deterministic validation",
            "planned_outputs": [
                *_PLANNED_RUNNER_PATHS,
                *_PLANNED_TEST_PATHS,
            ],
            "boundary_guard": "offline deterministic replay only; no live prediction or routing",
        },
    ]


def _acceptance_gates() -> list[dict[str, str]]:
    return [
        {
            "gate_id": "OCC-GATE-001",
            "required_before": "any calibration implementation patch",
            "status": "EXPLICIT_OPERATOR_DECISION_REQUIRED",
        },
        {
            "gate_id": "OCC-GATE-002",
            "required_before": "any runtime, queue, route, or scheduler mutation",
            "status": "AUTHORITY_DENIED",
        },
        {
            "gate_id": "OCC-GATE-003",
            "required_before": "treating calibration output as truth or authorization",
            "status": "FOREVER_DENIED_IN_THIS_PLAN",
        },
    ]


def build_oracle_confidence_calibration_plan(
    *,
    repo_root: str | Path = ".",
    research_receipt_path: str | Path = RESEARCH_RECEIPT_PATH,
    decision_request_path: str | Path = DECISION_REQUEST_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    research_path = root / research_receipt_path
    decision_path = root / decision_request_path
    research_packet = _load_json(research_path)
    decision_packet = _load_json(decision_path)

    candidate_mapping = _find_candidate(research_packet, TARGET_CANDIDATE_ID)
    research_ready = (
        research_packet.get("schema_version") == "OracleSignalResearchIntakeReceipt.v1"
        and research_packet.get("downstream") == NOT_COMPUTABLE
        and candidate_mapping.get("allowed_status") == TARGET_ALLOWED_STATUS
    )
    operator_hold_active = (
        decision_packet.get("schema_version") == "GlobalIngestOperatorDecisionRequest.v1"
        and decision_packet.get("target_pipeline_id") == "oracle_signal"
        and decision_packet.get("recommended_decision") == "HOLD"
        and decision_packet.get("implementation_authorized") is False
    )
    planning_artifact_ready = research_ready and operator_hold_active

    not_computable_reasons: list[str] = []
    if not research_ready:
        not_computable_reasons.append("RESEARCH_RECEIPT_NOT_READY")
    if not operator_hold_active:
        not_computable_reasons.append("GLOBAL_INGEST_OPERATOR_HOLD_NOT_OBSERVED")
    not_computable_reasons.extend(
        [
            "EXPLICIT_OPERATOR_DECISION_REQUIRED",
            "IMPLEMENTATION_AUTHORITY_DENIED",
            "CALIBRATION_OUTPUT_CANNOT_GRANT_TRUTH_OR_AUTHORIZATION",
        ]
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "plan_status": "PLAN_EMITTED_ADVISORY_ONLY" if planning_artifact_ready else NOT_COMPUTABLE,
        "target_candidate_id": TARGET_CANDIDATE_ID,
        "target_allowed_status": TARGET_ALLOWED_STATUS,
        "source_research_package": research_packet.get("source_research_package", {}),
        "depends_on_artifacts": [
            Path(research_receipt_path).as_posix(),
            Path(decision_request_path).as_posix(),
        ],
        "source_artifact_hashes": {
            Path(research_receipt_path).as_posix(): _source_hash(research_path),
            Path(decision_request_path).as_posix(): _source_hash(decision_path),
        },
        "research_ready": research_ready,
        "operator_hold_active": operator_hold_active,
        "candidate_mapping": candidate_mapping,
        "calibration_dimensions": [
            "confidence_score",
            "uncertainty_band",
            "calibration_bucket",
            "trajectory_confidence_reference",
        ],
        "planned_contract_paths": list(_PLANNED_CONTRACT_PATHS),
        "planned_runner_paths": list(_PLANNED_RUNNER_PATHS),
        "planned_test_paths": list(_PLANNED_TEST_PATHS),
        "planned_artifact_paths": list(_PLANNED_ARTIFACT_PATHS),
        "planned_phases": _planned_phases(),
        "acceptance_gates": _acceptance_gates(),
        "blocked_actions": [
            "AUTO_CREATE_NEXT_PATCH",
            "ORACLE_RUNTIME_MUTATION",
            "ORACLE_QUEUE_MUTATION",
            "ORACLE_ROUTE_MUTATION",
            "ORACLE_FORECAST_PROMOTION",
            "ORACLE_CANON_PROMOTION",
            "LIVE_PREDICTION",
            "TREAT_CONFIDENCE_AS_TRUTH",
            "TREAT_CONFIDENCE_AS_AUTHORIZATION",
        ],
        "required_operator_actions": [
            "review_oracle_signal_research_intake_receipt",
            "review_global_ingest_operator_decision_request",
            "maintain_global_ingest_hold_until_explicit_decision",
        ],
        "recommended_next_action": (
            "review the calibration plan as an advisory-only preparation surface; do not open an implementation patch while the operator hold remains active"
            if planning_artifact_ready
            else "repair calibration-plan prerequisites before any further Oracle planning"
        ),
        "recommended_next_patch": NOT_COMPUTABLE,
        "implementation_patch_id": PATCH_ID,
        "safe_to_prepare_planning_pr": False,
        "safe_to_prepare_implementation_pr": False,
        "safe_to_auto_continue": False,
        "implementation_authorized": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "forecast_routing": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "valid_for_execution": False,
        "governance_locks": {
            "governance_status": "FROZEN",
            "canon_status": "ADVISORY_ONLY",
            "execution_authority": False,
            "canon_mutation_allowed": False,
            "runtime_mutation_allowed": False,
            "research_candidates_canonized": False,
            "downstream": NOT_COMPUTABLE,
        },
        "not_computable_reasons": not_computable_reasons,
        "downstream": NOT_COMPUTABLE,
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_oracle_confidence_calibration_plan(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)


def write_oracle_confidence_calibration_plan_markdown(path: str | Path, packet: dict[str, Any]) -> None:
    lines = [
        "# Oracle Confidence Calibration Plan",
        "",
        f"- `plan_id`: `{packet['plan_id']}`",
        f"- `plan_status`: `{packet['plan_status']}`",
        f"- `target_candidate_id`: `{packet['target_candidate_id']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        f"- `implementation_patch_id`: `{packet['implementation_patch_id']}`",
        f"- `research_ready`: `{packet['research_ready']}`",
        f"- `operator_hold_active`: `{packet['operator_hold_active']}`",
        f"- `valid_for_execution`: `{packet['valid_for_execution']}`",
        "",
        "## Planned Contract Paths",
    ]
    for rel_path in packet.get("planned_contract_paths", []):
        lines.append(f"- `{rel_path}`")
    lines.extend(["", "## Planned Phases"])
    for phase in packet.get("planned_phases", []):
        lines.append(f"- `{phase['phase_id']}`: {phase['title']}")
    lines.extend(["", "## Not Computable Reasons"])
    for reason in packet.get("not_computable_reasons", []):
        lines.append(f"- `{reason}`")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
