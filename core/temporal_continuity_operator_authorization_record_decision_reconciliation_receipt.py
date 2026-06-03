from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityOperatorAuthorizationRecordDecisionReconciliationReceipt.v1"
SOURCE_P102E_RECORD_PLAN_PATH = (
    "out/temporal_continuity_selected_repair_execution_authorization_record_plan/latest.json"
)
NOTION_DIFF_PATH = "docs/audits/ABRAXAS_REPO_NOTION_DIFF_001.md"

EXPECTED_NOTION_ROUTE = (
    "P103_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_REVIEW"
)
EXPECTED_HANDOFF = "OPERATOR_AUTHORIZATION_RECORD_DECISION_REQUIRED"
EXPECTED_TERMINAL_LANE = "P102E_SELECTED_REPAIR_EXECUTION_AUTHORIZATION_RECORD_PLAN"

_STATUS_NOT_COMPUTABLE = "NOT_COMPUTABLE"
_STATUS_RECONCILED_BLOCKED = "OPERATOR_AUTHORIZATION_RECORD_DECISION_RECONCILIATION_BLOCKED"

_DENIED_AUTHORITY: tuple[str, ...] = (
    "authorization_authority",
    "authorization_record_creation_authority",
    "canon_promotion",
    "execution_authority",
    "forecast_influence",
    "production_activation",
    "record_creation_authority",
    "runtime_authority",
    "scheduler_mutation",
    "token_minting_authority",
)


class _ObservedSource(dict[str, Any]):
    pass


def _observe_json_source(*, root: Path, rel_path: str) -> _ObservedSource:
    source_path = root / rel_path
    observed = source_path.exists()
    readable = False
    malformed_json = False
    file_hash = "NOT_COMPUTABLE"
    payload: dict[str, Any] | None = None

    if observed:
        try:
            source_bytes = source_path.read_bytes()
            readable = True
            file_hash = hashlib.sha256(source_bytes).hexdigest()
        except OSError:
            source_bytes = b""

        if readable:
            try:
                parsed = json.loads(source_bytes.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                malformed_json = True
                parsed = None

            if isinstance(parsed, dict):
                payload = parsed
            else:
                malformed_json = True

    return _ObservedSource(
        path=rel_path,
        observed=observed,
        readable=readable,
        malformed_json=malformed_json,
        file_hash=file_hash,
        payload=payload,
    )


def _observe_text_source(*, root: Path, rel_path: str) -> dict[str, Any]:
    source_path = root / rel_path
    observed = source_path.exists()
    readable = False
    file_hash = "NOT_COMPUTABLE"
    text = ""

    if observed:
        try:
            source_bytes = source_path.read_bytes()
            readable = True
            file_hash = hashlib.sha256(source_bytes).hexdigest()
            text = source_bytes.decode("utf-8")
        except (OSError, UnicodeDecodeError):
            readable = False
            text = ""

    return {
        "path": rel_path,
        "observed": observed,
        "readable": readable,
        "file_hash": file_hash,
        "text": text,
    }


def _classify(p102e: _ObservedSource) -> dict[str, Any]:
    if not bool(p102e["observed"]):
        return {
            "status": _STATUS_NOT_COMPUTABLE,
            "reasons": ["P102E_SOURCE_MISSING"],
        }
    if not bool(p102e["readable"]):
        return {
            "status": _STATUS_NOT_COMPUTABLE,
            "reasons": ["P102E_SOURCE_UNREADABLE"],
        }
    if bool(p102e["malformed_json"]):
        return {
            "status": _STATUS_NOT_COMPUTABLE,
            "reasons": ["P102E_SOURCE_MALFORMED_JSON"],
        }

    payload = p102e["payload"] if isinstance(p102e["payload"], dict) else {}
    reasons: list[str] = []
    if payload.get("terminal_lane") != EXPECTED_TERMINAL_LANE:
        reasons.append("P102E_TERMINAL_LANE_MISMATCH")
    if payload.get("recommended_next_lane") != EXPECTED_HANDOFF:
        reasons.append("P102E_HANDOFF_MISMATCH")
    if payload.get("authorization_record_required") is not True:
        reasons.append("P102E_RECORD_NOT_REQUIRED")
    if payload.get("authorization_record_created") is not False:
        reasons.append("P102E_RECORD_CREATION_DRIFT")
    if payload.get("authorization_granted") is not False:
        reasons.append("P102E_AUTHORIZATION_GRANT_DRIFT")
    if payload.get("valid_for_execution") is not False:
        reasons.append("P102E_EXECUTION_VALIDITY_DRIFT")

    reasons.append("OPERATOR_AUTHORIZATION_RECORD_DECISION_EVIDENCE_MISSING")

    return {
        "status": _STATUS_RECONCILED_BLOCKED if len(reasons) == 1 else _STATUS_NOT_COMPUTABLE,
        "reasons": reasons,
    }


def build_temporal_continuity_operator_authorization_record_decision_reconciliation_receipt(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    p102e = _observe_json_source(root=root, rel_path=SOURCE_P102E_RECORD_PLAN_PATH)
    notion_diff = _observe_text_source(root=root, rel_path=NOTION_DIFF_PATH)
    p102e_payload = p102e["payload"] if isinstance(p102e["payload"], dict) else {}
    classification = _classify(p102e)

    notion_route_documented = bool(
        notion_diff["readable"] and EXPECTED_NOTION_ROUTE in str(notion_diff["text"])
    )
    notion_expected_route = (
        EXPECTED_NOTION_ROUTE if notion_route_documented else "NOT_DOCUMENTED_IN_REPO"
    )

    missing_operator_decision_evidence = [
        "operator_authorization_record_decision_evidence",
    ]
    missing_evidence = list(missing_operator_decision_evidence)
    if not bool(p102e["observed"]):
        missing_evidence.append(SOURCE_P102E_RECORD_PLAN_PATH)

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "reconciliation_receipt_only": True,
        "production_activation": False,
        "canon_promotion": False,
        "forecast_influence": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "execution_authority": False,
        "authorization_authority": False,
        "authorization_record_creation_authority": False,
        "record_creation_authority": False,
        "token_minting_authority": False,
        "token_minting_allowed": False,
        "authorization_granted": False,
        "authorization_record_created": False,
        "valid_for_execution": False,
        "observed_terminal_lane": str(p102e_payload.get("terminal_lane", "NOT_COMPUTABLE")),
        "handoff": str(p102e_payload.get("recommended_next_lane", "NOT_COMPUTABLE")),
        "source_p102e_record_plan_path": SOURCE_P102E_RECORD_PLAN_PATH,
        "source_p102e_record_plan_observed": bool(p102e["observed"]),
        "source_p102e_record_plan_readable": bool(p102e["readable"]),
        "source_p102e_record_plan_hash": str(p102e["file_hash"]),
        "source_p102e_record_plan_status": str(
            p102e_payload.get("p102e_record_plan_status", "NOT_COMPUTABLE")
        ),
        "source_authorization_record_required": bool(
            p102e_payload.get("authorization_record_required", False)
        ),
        "source_authorization_record_created": bool(
            p102e_payload.get("authorization_record_created", False)
        ),
        "source_authorization_granted": bool(
            p102e_payload.get("authorization_granted", False)
        ),
        "source_valid_for_execution": bool(p102e_payload.get("valid_for_execution", False)),
        "notion_diff_path": NOTION_DIFF_PATH,
        "notion_diff_observed": bool(notion_diff["observed"]),
        "notion_diff_readable": bool(notion_diff["readable"]),
        "notion_diff_hash": str(notion_diff["file_hash"]),
        "notion_expected_simulated_route_documented": notion_route_documented,
        "notion_expected_simulated_route": notion_expected_route,
        "repo_to_notion_reconciliation_result": (
            "BLOCKED_BY_MISSING_OPERATOR_DECISION_EVIDENCE"
        ),
        "operator_decision_reconciliation_status": str(classification["status"]),
        "missing_operator_decision_evidence": missing_operator_decision_evidence,
        "missing_evidence": missing_evidence,
        "blocking_reasons": [str(reason) for reason in classification["reasons"]],
        "recommended_next_lane": "NOT_COMPUTABLE",
        "recommended_next_lane_reason": (
            "P102E requires an explicit human/operator authorization-record decision before any P103-like route can be considered; no such operator decision evidence is present in the repo."
        ),
        "recommended_human_operator_decision": "CREATE_OPERATOR_AUTHORIZATION_RECORD_DECISION_OR_HOLD",
        "authority_locks": {authority: False for authority in sorted(_DENIED_AUTHORITY)},
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }

    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def write_temporal_continuity_operator_authorization_record_decision_reconciliation_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
