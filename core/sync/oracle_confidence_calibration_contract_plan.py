from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "OracleConfidenceCalibrationContractPlan.v1"
PLAN_ID = "ORACLE_CONFIDENCE_CALIBRATION_CONTRACT_PLAN_001"
OUT_JSON = "out/sync/oracle_confidence_calibration_contract_plan/latest.json"
OUT_MD = "out/sync/oracle_confidence_calibration_contract_plan/latest.md"
CALIBRATION_PLAN_PATH = "out/sync/oracle_confidence_calibration_plan/latest.json"
DECISION_REQUEST_PATH = "out/operator_review/global_ingest_operator_decision_request_001.latest.json"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
TARGET_CANDIDATE_ID = "ORACLE_CONFIDENCE_CALIBRATION"
IMPLEMENTATION_PATCH_ID = "PATCH-ABX-ORACLE-CONFIDENCE-CALIBRATION-001"

_PLANNED_CONTRACT_PATHS = (
    "contracts/oracle/oracle_confidence_calibration_profile.v1.schema.json",
    "contracts/oracle/oracle_confidence_calibration_bucket_set.v1.schema.json",
    "contracts/oracle/oracle_confidence_calibration_receipt.v1.schema.json",
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


def _contract_specs() -> list[dict[str, Any]]:
    return [
        {
            "contract_id": "ORACLE_CONFIDENCE_CALIBRATION_PROFILE",
            "path": _PLANNED_CONTRACT_PATHS[0],
            "purpose": "Declare deterministic calibration profile metadata, bucket policy, and advisory-only boundary flags.",
            "required_fields": [
                "schema_version",
                "profile_id",
                "target_candidate_id",
                "calibration_dimensions",
                "bucket_policy_ref",
                "advisory_only",
                "non_authoritative",
                "valid_for_execution",
            ],
        },
        {
            "contract_id": "ORACLE_CONFIDENCE_CALIBRATION_BUCKET_SET",
            "path": _PLANNED_CONTRACT_PATHS[1],
            "purpose": "Define deterministic bucket boundaries, uncertainty band labels, and ordering constraints.",
            "required_fields": [
                "schema_version",
                "bucket_set_id",
                "target_candidate_id",
                "bucket_count",
                "ordered_buckets",
                "uncertainty_band_labels",
                "advisory_only",
                "non_authoritative",
            ],
        },
        {
            "contract_id": "ORACLE_CONFIDENCE_CALIBRATION_RECEIPT",
            "path": _PLANNED_CONTRACT_PATHS[2],
            "purpose": "Emit advisory-only calibration receipts without treating confidence as truth or authorization.",
            "required_fields": [
                "schema_version",
                "receipt_id",
                "target_candidate_id",
                "profile_id",
                "bucket_set_id",
                "confidence_score",
                "uncertainty_band",
                "advisory_only",
                "non_authoritative",
                "valid_for_execution",
            ],
        },
    ]


def _planned_phases() -> list[dict[str, Any]]:
    return [
        {
            "phase_id": "OCC-CONTRACT-001",
            "phase_status": "PLANNED_ADVISORY_ONLY",
            "title": "Profile contract field formalization",
            "planned_outputs": [_PLANNED_CONTRACT_PATHS[0]],
            "boundary_guard": "contract-only planning; no runtime Oracle mutation",
        },
        {
            "phase_id": "OCC-CONTRACT-002",
            "phase_status": "PLANNED_ADVISORY_ONLY",
            "title": "Bucket semantics and ordering plan",
            "planned_outputs": [_PLANNED_CONTRACT_PATHS[1]],
            "boundary_guard": "deterministic bucket ordering only; no live prediction",
        },
        {
            "phase_id": "OCC-CONTRACT-003",
            "phase_status": "PLANNED_ADVISORY_ONLY",
            "title": "Receipt semantics and guardrail plan",
            "planned_outputs": [_PLANNED_CONTRACT_PATHS[2]],
            "boundary_guard": "advisory-only receipt semantics; confidence cannot become truth or authorization",
        },
    ]


def _acceptance_gates() -> list[dict[str, str]]:
    return [
        {
            "gate_id": "OCC-CONTRACT-GATE-001",
            "required_before": "authoring any calibration contract file",
            "status": "EXPLICIT_OPERATOR_DECISION_REQUIRED",
        },
        {
            "gate_id": "OCC-CONTRACT-GATE-002",
            "required_before": "using calibration outputs for runtime, queue, route, or scheduler mutation",
            "status": "AUTHORITY_DENIED",
        },
        {
            "gate_id": "OCC-CONTRACT-GATE-003",
            "required_before": "treating confidence as truth or authorization",
            "status": "FOREVER_DENIED_IN_THIS_PLAN",
        },
    ]


def build_oracle_confidence_calibration_contract_plan(
    *,
    repo_root: str | Path = ".",
    calibration_plan_path: str | Path = CALIBRATION_PLAN_PATH,
    decision_request_path: str | Path = DECISION_REQUEST_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    calibration_path = root / calibration_plan_path
    decision_path = root / decision_request_path
    calibration_plan = _load_json(calibration_path)
    decision_request = _load_json(decision_path)

    calibration_plan_ready = (
        calibration_plan.get("artifact_type") == "OracleConfidenceCalibrationPlan.v1"
        and calibration_plan.get("plan_status") == "PLAN_EMITTED_ADVISORY_ONLY"
        and calibration_plan.get("target_candidate_id") == TARGET_CANDIDATE_ID
    )
    operator_hold_active = (
        decision_request.get("schema_version") == "GlobalIngestOperatorDecisionRequest.v1"
        and decision_request.get("target_pipeline_id") == "oracle_signal"
        and decision_request.get("recommended_decision") == "HOLD"
        and decision_request.get("implementation_authorized") is False
    )

    missing_contract_paths = [
        rel_path for rel_path in _PLANNED_CONTRACT_PATHS if not (root / rel_path).exists()
    ]
    plan_ready = calibration_plan_ready and operator_hold_active and bool(missing_contract_paths)

    not_computable_reasons: list[str] = []
    if not calibration_plan_ready:
        not_computable_reasons.append("CALIBRATION_PLAN_NOT_READY")
    if not operator_hold_active:
        not_computable_reasons.append("GLOBAL_INGEST_OPERATOR_HOLD_NOT_OBSERVED")
    if not missing_contract_paths:
        not_computable_reasons.append("CONTRACT_PATHS_ALREADY_PRESENT")
    not_computable_reasons.extend(
        [
            "EXPLICIT_OPERATOR_DECISION_REQUIRED",
            "CONTRACT_AUTHORING_NOT_APPROVED",
            "CALIBRATION_OUTPUT_CANNOT_GRANT_TRUTH_OR_AUTHORIZATION",
        ]
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "plan_status": "CONTRACT_PLAN_EMITTED_ADVISORY_ONLY" if plan_ready else NOT_COMPUTABLE,
        "target_candidate_id": TARGET_CANDIDATE_ID,
        "implementation_patch_id": IMPLEMENTATION_PATCH_ID,
        "depends_on_artifacts": [
            Path(calibration_plan_path).as_posix(),
            Path(decision_request_path).as_posix(),
        ],
        "source_artifact_hashes": {
            Path(calibration_plan_path).as_posix(): _source_hash(calibration_path),
            Path(decision_request_path).as_posix(): _source_hash(decision_path),
        },
        "calibration_plan_ready": calibration_plan_ready,
        "operator_hold_active": operator_hold_active,
        "missing_contract_paths": missing_contract_paths,
        "contract_specs": _contract_specs(),
        "planned_contract_paths": list(_PLANNED_CONTRACT_PATHS),
        "planned_phases": _planned_phases(),
        "acceptance_gates": _acceptance_gates(),
        "blocked_actions": [
            "AUTO_CREATE_NEXT_PATCH",
            "AUTHOR_CONTRACT_FILES",
            "ORACLE_RUNTIME_MUTATION",
            "ORACLE_QUEUE_MUTATION",
            "ORACLE_ROUTE_MUTATION",
            "ORACLE_FORECAST_PROMOTION",
            "ORACLE_CANON_PROMOTION",
            "TREAT_CONFIDENCE_AS_TRUTH",
            "TREAT_CONFIDENCE_AS_AUTHORIZATION",
        ],
        "required_operator_actions": [
            "review_oracle_confidence_calibration_plan",
            "review_global_ingest_operator_decision_request",
            "maintain_global_ingest_hold_until_explicit_decision",
        ],
        "recommended_next_action": (
            "review the calibration contract plan as an advisory-only schema preparation surface; do not author contract files while the operator hold remains active"
            if plan_ready
            else "repair calibration contract-plan prerequisites before further Oracle planning"
        ),
        "recommended_next_patch": NOT_COMPUTABLE,
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


def write_oracle_confidence_calibration_contract_plan(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)


def write_oracle_confidence_calibration_contract_plan_markdown(
    path: str | Path, packet: dict[str, Any]
) -> None:
    lines = [
        "# Oracle Confidence Calibration Contract Plan",
        "",
        f"- `plan_id`: `{packet['plan_id']}`",
        f"- `plan_status`: `{packet['plan_status']}`",
        f"- `target_candidate_id`: `{packet['target_candidate_id']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        f"- `implementation_patch_id`: `{packet['implementation_patch_id']}`",
        f"- `calibration_plan_ready`: `{packet['calibration_plan_ready']}`",
        f"- `operator_hold_active`: `{packet['operator_hold_active']}`",
        f"- `valid_for_execution`: `{packet['valid_for_execution']}`",
        "",
        "## Planned Contract Paths",
    ]
    for rel_path in packet.get("planned_contract_paths", []):
        lines.append(f"- `{rel_path}`")
    lines.extend(["", "## Contract Specs"])
    for spec in packet.get("contract_specs", []):
        lines.append(f"- `{spec['contract_id']}`: {spec['purpose']}")
    lines.extend(["", "## Not Computable Reasons"])
    for reason in packet.get("not_computable_reasons", []):
        lines.append(f"- `{reason}`")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
