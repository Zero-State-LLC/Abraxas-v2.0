from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping

from .models import CanaryScope, CanaryDurationPolicy, CanaryGuardrail, CanaryEvidenceRequirement, CanaryRollbackLink, CanaryOperatorApprovalRef, AuthorityRef, CanaryActivation

SCHEMA_VERSION = "CanaryActivation.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_canary_activation_json(activation: CanaryActivation | Mapping[str, Any]) -> str:
    payload = asdict(activation) if isinstance(activation, CanaryActivation) else dict(activation)
    payload.pop("activation_hash", None)
    return _canonical_json(payload)


def canary_activation_hash(activation: CanaryActivation | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_canary_activation_json(activation))


def build_canary_activation(
    activation_id: str,
    proposal_id: str,
    proposal_hash: str,
    scope: CanaryScope,
    duration_policy: CanaryDurationPolicy,
    guardrails: tuple[CanaryGuardrail, ...],
    evidence_requirements: CanaryEvidenceRequirement,
    rollback_link: CanaryRollbackLink,
    operator_approval_ref: CanaryOperatorApprovalRef,
    activation_status: str,
    created_by_lane: str,
    authority_ref: AuthorityRef | None,
) -> CanaryActivation:
    draft = CanaryActivation(
        SCHEMA_VERSION,
        activation_id,
        proposal_id,
        proposal_hash,
        scope,
        duration_policy,
        guardrails,
        evidence_requirements,
        rollback_link,
        operator_approval_ref,
        activation_status,
        created_by_lane,
        authority_ref,
        False,
        True,
        False,
        False,
        "PENDING",
    )
    return replace(draft, activation_hash=canary_activation_hash(draft))


def write_canary_activation_contract_audit(base_dir: Path | str = ".") -> str:
    activation = build_canary_activation(
        activation_id="canary-activation-v1",
        proposal_id="promotion-proposal-v1",
        proposal_hash="proposal-hash-1",
        scope=CanaryScope("SUBSYSTEM", "forecast-runtime"),
        duration_policy=CanaryDurationPolicy("dur-1", "ON_OPERATOR_START", "ON_WINDOW_LIMIT", 3, "EXPIRE_ON_WINDOW_LIMIT"),
        guardrails=(CanaryGuardrail("g1", "BRIER_DELTA", {"max_delta": 0.03}, "HALT_AND_REVIEW", True),),
        evidence_requirements=CanaryEvidenceRequirement(True, True, True, True, 3, 3),
        rollback_link=CanaryRollbackLink("rb-1", True, ("runtime/forecast",), "ROLLBACK_ON_BREACH"),
        operator_approval_ref=CanaryOperatorApprovalRef("receipt://operator/review/1", "queue://operator/review/1", "OPERATOR_RECEIPT_REQUIRED"),
        activation_status="READY_FOR_CANARY",
        created_by_lane="FORECAST",
        authority_ref=None,
    )
    from .validator import validate_canary_activation

    report = validate_canary_activation(activation)
    payload = {
        "status": report.status,
        "activation_hash": activation.activation_hash,
        "receipt_hash": report.receipt_hash,
        "findings": [asdict(f) for f in report.findings],
        "schema_version": activation.schema_version,
    }
    text = _canonical_json(payload) + "\n"
    out = Path(base_dir) / "out/audit/canary_activation_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)
