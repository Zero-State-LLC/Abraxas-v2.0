"""Deterministic fusion of canonical architecture contributions."""

from __future__ import annotations

from typing import Any

from core.alembic.models import (
    ArchitectureContribution,
    ConflictRecord,
    FusionResult,
    Provenance,
    TaskEnvelope,
    VerificationResult,
)
from core.alembic.util import det_timestamp, hash_model, make_id


def fuse_contributions(
    task: TaskEnvelope,
    contributions: tuple[ArchitectureContribution, ...],
    verification: VerificationResult,
    *,
    fusion_method: str = "deterministic_evidence_union",
) -> FusionResult:
    ordered = tuple(sorted(contributions, key=lambda item: item.contribution_id))
    input_ids = tuple(item.contribution_id for item in ordered)
    accepted: list[ArchitectureContribution] = []
    rejected: list[ArchitectureContribution] = []

    if verification.status in {"FAIL", "ABSTAIN", "NOT_COMPUTABLE"}:
        rejected = list(ordered)
    else:
        failed_ids = {
            check.get("contribution_id")
            for check in verification.checks
            if check.get("result") == "FAIL" and check.get("contribution_id")
        }
        for item in ordered:
            if item.is_stub or item.status in {"UNAVAILABLE", "NOT_IMPLEMENTED", "STUB", "FAILED", "ABSTAIN"} or item.contribution_id in failed_ids:
                rejected.append(item)
            elif item.lane == "SHADOW" and task.lane != "SHADOW":
                # Shadow cannot become active fusion input.
                rejected.append(item)
            else:
                accepted.append(item)

    conflicts = list(verification.conflicts)
    # Detect absence vs disagreement for claim keys.
    claim_map: dict[str, list[Any]] = {}
    for item in accepted:
        for claim in item.claims:
            key = str(claim.get("statement", "")).strip()
            if key:
                claim_map.setdefault(key, []).append(claim.get("confidence"))

    for key, values in sorted(claim_map.items()):
        present = [v for v in values if v is not None]
        if len(present) >= 2:
            numeric = [float(v) for v in present if isinstance(v, (int, float))]
            if numeric and max(numeric) - min(numeric) > 0.5:
                conflicts.append(
                    ConflictRecord(
                        conflict_id=make_id("conflict", "UNCERTAINTY_CONFLICT", key),
                        conflict_type="UNCERTAINTY_CONFLICT",
                        contribution_ids=tuple(item.contribution_id for item in accepted),
                        detail=f"confidence_disagreement:{key[:80]}",
                        resolved=False,
                    )
                )

    unresolved = [c for c in conflicts if not c.resolved]
    residuals = list(verification.residuals)
    if unresolved:
        residuals.append("unresolved_conflicts_present")

    fused_claims = []
    evidence_refs: list[str] = []
    for item in accepted:
        for claim in item.claims:
            fused_claims.append(
                {
                    "statement": claim.get("statement"),
                    "status": claim.get("status", "INFERRED"),
                    "confidence": claim.get("confidence"),
                    "source_contribution_id": item.contribution_id,
                    "source_architecture_id": item.architecture_id,
                }
            )
        evidence_refs.extend(item.evidence_refs)

    # Do not average incompatible confidences; report distribution instead.
    confidences = [
        float(claim["confidence"])
        for claim in fused_claims
        if isinstance(claim.get("confidence"), (int, float))
    ]
    calibrated = [
        float(item.calibrated_confidence)
        for item in accepted
        if isinstance(item.calibrated_confidence, (int, float))
    ]

    if not accepted:
        status = "ABSTAIN" if verification.status != "FAIL" else "FAIL"
        fused_output: dict[str, Any] = {
            "claims": [],
            "reason": "no_accepted_contributions",
        }
        confidence = None
        calibrated_confidence = None
        uncertainty = None
        conflict_resolution = "unresolved_fail_closed"
    else:
        status = "PASS_WITH_RESIDUALS" if unresolved or residuals else "PASS"
        fused_output = {
            "claims": fused_claims,
            "evidence_refs": sorted(set(evidence_refs)),
            "confidence_distribution": confidences,
            "calibrated_confidence_distribution": calibrated,
        }
        confidence = None  # explicit: do not invent a single averaged confidence
        calibrated_confidence = None
        uncertainty = None if not confidences else round(max(confidences) - min(confidences), 6) if len(confidences) > 1 else 0.0
        conflict_resolution = "recorded_unresolved" if unresolved else "no_conflicts"

    result = FusionResult(
        fusion_id=make_id("fusion", task.task_id, task.run_id, input_ids, status),
        task_id=task.task_id,
        run_id=task.run_id,
        input_contribution_ids=input_ids,
        accepted_contribution_ids=tuple(item.contribution_id for item in accepted),
        rejected_contribution_ids=tuple(item.contribution_id for item in rejected),
        conflicts=tuple(conflicts),
        conflict_resolution=conflict_resolution,
        fusion_method=fusion_method,
        fused_output=fused_output,
        uncertainty=uncertainty,
        confidence=confidence,
        calibrated_confidence=calibrated_confidence,
        verification_summary={"status": verification.status, "verification_id": verification.verification_id},
        calibration_summary={
            "raw_confidence_distinct_from_calibrated": True,
            "aggregated_confidence_policy": "distribution_only_no_forced_average",
        },
        policy_summary={
            "advisory_only": True,
            "shadow_isolated": True,
            "authority_expanded": False,
        },
        lineage=tuple(
            f"{item.contribution_id}->{item.architecture_id}->{item.adapter_id}" for item in ordered
        ),
        residuals=tuple(residuals),
        status=status,
        provenance=Provenance(classification="OBSERVED", producer="core.alembic.fusion"),
    )
    digest = hash_model(result)
    return result.model_copy(
        update={
            "provenance": result.provenance.model_copy(
                update={"content_hash": digest, "notes": det_timestamp(digest)}
            )
        }
    )
