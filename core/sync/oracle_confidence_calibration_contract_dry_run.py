from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "OracleConfidenceCalibrationContractDryRun.v1"
DRY_RUN_ID = "ORACLE_CONFIDENCE_CALIBRATION_CONTRACT_DRY_RUN_001"
OUT_JSON = "out/sync/oracle_confidence_calibration_contract_dry_run/latest.json"
OUT_MD = "out/sync/oracle_confidence_calibration_contract_dry_run/latest.md"
CONTRACT_PLAN_PATH = "out/sync/oracle_confidence_calibration_contract_plan/latest.json"
DECISION_REQUEST_PATH = "out/operator_review/global_ingest_operator_decision_request_001.latest.json"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
TARGET_CANDIDATE_ID = "ORACLE_CONFIDENCE_CALIBRATION"
NEXT_CANDIDATE_ARTIFACTS = (
    "out/sync/oracle_confidence_calibration_contract_validation_plan/latest.json",
    "out/sync/oracle_confidence_calibration_contract_validation_plan/latest.md",
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


def _simulated_contract_bundle(contract_specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    bundle: list[dict[str, Any]] = []
    for spec in contract_specs:
        required_fields = spec.get("required_fields", [])
        bundle.append(
            {
                "contract_id": spec.get("contract_id", NOT_COMPUTABLE),
                "path": spec.get("path", NOT_COMPUTABLE),
                "simulated_only": True,
                "authoring_performed": False,
                "valid_for_authoring": False,
                "required_field_count": len(required_fields) if isinstance(required_fields, list) else 0,
                "required_fields": list(required_fields) if isinstance(required_fields, list) else [],
            }
        )
    return bundle


def build_oracle_confidence_calibration_contract_dry_run(
    *,
    repo_root: str | Path = ".",
    contract_plan_path: str | Path = CONTRACT_PLAN_PATH,
    decision_request_path: str | Path = DECISION_REQUEST_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    plan_path = root / contract_plan_path
    request_path = root / decision_request_path
    contract_plan = _load_json(plan_path)
    decision_request = _load_json(request_path)

    contract_plan_ready = (
        contract_plan.get("artifact_type") == "OracleConfidenceCalibrationContractPlan.v1"
        and contract_plan.get("plan_status") == "CONTRACT_PLAN_EMITTED_ADVISORY_ONLY"
        and contract_plan.get("target_candidate_id") == TARGET_CANDIDATE_ID
    )
    operator_hold_active = (
        decision_request.get("schema_version") == "GlobalIngestOperatorDecisionRequest.v1"
        and decision_request.get("target_pipeline_id") == "oracle_signal"
        and decision_request.get("recommended_decision") == "HOLD"
        and decision_request.get("implementation_authorized") is False
    )

    contract_specs = contract_plan.get("contract_specs", [])
    missing_contract_paths = contract_plan.get("missing_contract_paths", [])
    simulated_contract_bundle = _simulated_contract_bundle(
        contract_specs if isinstance(contract_specs, list) else []
    )
    dry_run_ready = (
        contract_plan_ready
        and operator_hold_active
        and bool(simulated_contract_bundle)
        and bool(missing_contract_paths)
    )

    not_computable_reasons: list[str] = []
    if not contract_plan_ready:
        not_computable_reasons.append("CONTRACT_PLAN_NOT_READY")
    if not operator_hold_active:
        not_computable_reasons.append("GLOBAL_INGEST_OPERATOR_HOLD_NOT_OBSERVED")
    if not simulated_contract_bundle:
        not_computable_reasons.append("CONTRACT_SPECS_MISSING")
    if not missing_contract_paths:
        not_computable_reasons.append("MISSING_CONTRACT_PATHS_NOT_OBSERVED")
    not_computable_reasons.extend(
        [
            "EXPLICIT_OPERATOR_DECISION_REQUIRED",
            "CONTRACT_AUTHORING_NOT_APPROVED",
            "DRY_RUN_CANNOT_GRANT_TRUTH_OR_AUTHORIZATION",
        ]
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "dry_run_id": DRY_RUN_ID,
        "dry_run_status": (
            "ORACLE_CONFIDENCE_CALIBRATION_CONTRACT_DRY_RUN_READY"
            if dry_run_ready
            else NOT_COMPUTABLE
        ),
        "target_candidate_id": TARGET_CANDIDATE_ID,
        "depends_on_artifacts": [
            Path(contract_plan_path).as_posix(),
            Path(decision_request_path).as_posix(),
        ],
        "source_artifact_hashes": {
            Path(contract_plan_path).as_posix(): _source_hash(plan_path),
            Path(decision_request_path).as_posix(): _source_hash(request_path),
        },
        "source_contract_plan_path": Path(contract_plan_path).as_posix(),
        "source_contract_plan_hash": _source_hash(plan_path),
        "source_request_id": decision_request.get("request_id", NOT_COMPUTABLE),
        "source_review_artifacts": [
            Path(contract_plan_path).as_posix(),
            "out/sync/oracle_confidence_calibration_plan/latest.json",
            Path(decision_request_path).as_posix(),
        ],
        "contract_plan_ready": contract_plan_ready,
        "operator_hold_active": operator_hold_active,
        "missing_contract_paths": list(missing_contract_paths)
        if isinstance(missing_contract_paths, list)
        else [],
        "simulated_contract_bundle": simulated_contract_bundle,
        "simulated_contract_count": len(simulated_contract_bundle),
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
            "review_oracle_confidence_calibration_contract_plan",
            "review_global_ingest_operator_decision_request",
            "maintain_global_ingest_hold_until_explicit_decision",
        ],
        "recommended_next_action": (
            "review the calibration contract dry run as an advisory-only simulated contract bundle; do not author contract files while the operator hold remains active"
            if dry_run_ready
            else "repair calibration contract dry-run prerequisites before further Oracle planning"
        ),
        "recommended_next_patch": NOT_COMPUTABLE,
        "next_candidate_artifacts": list(NEXT_CANDIDATE_ARTIFACTS),
        "safe_to_prepare_planning_pr": False,
        "safe_to_prepare_implementation_pr": False,
        "safe_to_auto_continue": False,
        "authoring_performed": False,
        "implementation_authorized": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "dry_run_only": True,
        "execution_authority": False,
        "forecast_routing": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "valid_for_execution": False,
        "valid_for_authoring": False,
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


def write_oracle_confidence_calibration_contract_dry_run(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)


def write_oracle_confidence_calibration_contract_dry_run_markdown(
    path: str | Path, packet: dict[str, Any]
) -> None:
    lines = [
        "# Oracle Confidence Calibration Contract Dry Run",
        "",
        f"- `dry_run_id`: `{packet['dry_run_id']}`",
        f"- `dry_run_status`: `{packet['dry_run_status']}`",
        f"- `target_candidate_id`: `{packet['target_candidate_id']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        f"- `contract_plan_ready`: `{packet['contract_plan_ready']}`",
        f"- `operator_hold_active`: `{packet['operator_hold_active']}`",
        f"- `valid_for_authoring`: `{packet['valid_for_authoring']}`",
        f"- `valid_for_execution`: `{packet['valid_for_execution']}`",
        "",
        "## Simulated Contract Bundle",
    ]
    for item in packet.get("simulated_contract_bundle", []):
        lines.append(f"- `{item['contract_id']}` -> `{item['path']}`")
    lines.extend(["", "## Not Computable Reasons"])
    for reason in packet.get("not_computable_reasons", []):
        lines.append(f"- `{reason}`")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
