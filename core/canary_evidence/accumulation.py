from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping

from .models import CanaryObservationWindow, CanaryEvidenceRef, CanaryGuardrailObservation, CanaryReadinessSummary, AuthorityRef, CanaryEvidenceAccumulation

SCHEMA_VERSION = "CanaryEvidenceAccumulation.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_canary_evidence_accumulation_json(accumulation: CanaryEvidenceAccumulation | Mapping[str, Any]) -> str:
    payload = asdict(accumulation) if isinstance(accumulation, CanaryEvidenceAccumulation) else dict(accumulation)
    payload.pop("accumulation_hash", None)
    return _canonical_json(payload)


def canary_evidence_accumulation_hash(accumulation: CanaryEvidenceAccumulation | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_canary_evidence_accumulation_json(accumulation))


def build_canary_evidence_accumulation(
    accumulation_id: str,
    activation_id: str,
    activation_hash: str,
    observation_windows: tuple[CanaryObservationWindow, ...],
    evidence_refs: tuple[CanaryEvidenceRef, ...],
    guardrail_observations: tuple[CanaryGuardrailObservation, ...],
    readiness_summary: CanaryReadinessSummary,
    accumulation_status: str,
    created_by_lane: str,
    authority_ref: AuthorityRef | None,
) -> CanaryEvidenceAccumulation:
    draft = CanaryEvidenceAccumulation(
        SCHEMA_VERSION,
        accumulation_id,
        activation_id,
        activation_hash,
        observation_windows,
        evidence_refs,
        guardrail_observations,
        readiness_summary,
        accumulation_status,
        created_by_lane,
        authority_ref,
        False,
        False,
        False,
        "PENDING",
    )
    return replace(draft, accumulation_hash=canary_evidence_accumulation_hash(draft))


def write_canary_evidence_accumulation_contract_audit(base_dir: Path | str = ".") -> str:
    accumulation = build_canary_evidence_accumulation(
        accumulation_id="canary-evidence-v1",
        activation_id="act-1",
        activation_hash="act-hash-1",
        observation_windows=(CanaryObservationWindow("w1", 1, "WINDOW_POLICY_V1", 3, 2, "OBSERVING"),),
        evidence_refs=(CanaryEvidenceRef("BRIER_LEDGER_ENTRY", "b1", "h1", "READ_ONLY_EVIDENCE"),),
        guardrail_observations=(CanaryGuardrailObservation("g1", "BRIER_DELTA", "WINDOW_MEAN", {"max_delta": 0.03}, False, "", "CONTINUE_OBSERVING"),),
        readiness_summary=CanaryReadinessSummary(3, 2, False, True, False, False, False),
        accumulation_status="OBSERVING",
        created_by_lane="FORECAST",
        authority_ref=None,
    )
    from .validator import validate_canary_evidence_accumulation

    report = validate_canary_evidence_accumulation(accumulation)
    payload = {
        "status": report.status,
        "accumulation_hash": accumulation.accumulation_hash,
        "receipt_hash": report.receipt_hash,
        "findings": [asdict(f) for f in report.findings],
        "schema_version": accumulation.schema_version,
    }
    text = _canonical_json(payload) + "\n"
    out = Path(base_dir) / "out/audit/canary_evidence_accumulation_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)
