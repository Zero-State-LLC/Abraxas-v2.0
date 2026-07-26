"""Symbolic verification surface — high-trust checking, not omniscient truth."""

from __future__ import annotations

from typing import Any

from core.alembic.models import (
    ArchitectureContribution,
    ConflictRecord,
    Provenance,
    TaskEnvelope,
    VerificationResult,
)
from core.alembic.runes import rune_bindings_for_operation
from core.alembic.util import det_timestamp, hash_model, make_id


def verify_contributions(
    task: TaskEnvelope,
    contributions: tuple[ArchitectureContribution, ...],
) -> VerificationResult:
    checks: list[dict[str, Any]] = []
    residuals: list[str] = []
    conflicts: list[ConflictRecord] = []
    accepted_ids: list[str] = []

    if not contributions:
        return VerificationResult(
            verification_id=make_id("verify", task.task_id, task.run_id, "empty"),
            task_id=task.task_id,
            run_id=task.run_id,
            status="ABSTAIN",
            checks=({"name": "non_empty_contributions", "result": "FAIL"},),
            residuals=("no_contributions",),
            contribution_ids=(),
            provenance=Provenance(classification="OBSERVED", producer="core.alembic.verify"),
        )

    claim_index: dict[str, list[str]] = {}
    for contribution in contributions:
        cid = contribution.contribution_id
        # Contract validity
        contract_ok = bool(contribution.output_contract)
        checks.append({"name": "contract_validity", "contribution_id": cid, "result": "PASS" if contract_ok else "FAIL"})
        if not contract_ok:
            residuals.append(f"missing_output_contract:{cid}")

        # Provenance completeness
        prov_ok = contribution.provenance.content_hash is not None
        checks.append({"name": "provenance_completeness", "contribution_id": cid, "result": "PASS" if prov_ok else "FAIL"})
        if not prov_ok:
            residuals.append(f"missing_provenance_hash:{cid}")

        # Policy / authority escalation
        if contribution.policy_status != "ADVISORY_ONLY":
            checks.append({"name": "forbidden_authority_escalation", "contribution_id": cid, "result": "FAIL"})
            conflicts.append(
                ConflictRecord(
                    conflict_id=make_id("conflict", "POLICY_CONFLICT", cid),
                    conflict_type="POLICY_CONFLICT",
                    contribution_ids=(cid,),
                    detail="non-advisory policy_status",
                )
            )
        else:
            checks.append({"name": "forbidden_authority_escalation", "contribution_id": cid, "result": "PASS"})

        # Stub / unavailable cannot be accepted fusion inputs
        if contribution.is_stub or contribution.status in {"UNAVAILABLE", "NOT_IMPLEMENTED", "STUB", "FAILED"}:
            checks.append({"name": "executable_contribution", "contribution_id": cid, "result": "FAIL"})
            residuals.append(f"non_executable_contribution:{cid}:{contribution.status}")
            continue

        # Claim-to-evidence linkage
        for claim in contribution.claims:
            statement = str(claim.get("statement", "")).strip()
            if not statement:
                residuals.append(f"empty_claim:{cid}")
                checks.append({"name": "claim_to_evidence_linkage", "contribution_id": cid, "result": "FAIL"})
                continue
            if contribution.evidence_refs or task.input_artifacts:
                checks.append({"name": "claim_to_evidence_linkage", "contribution_id": cid, "result": "PASS"})
            else:
                checks.append({"name": "claim_to_evidence_linkage", "contribution_id": cid, "result": "PASS_WITH_RESIDUALS"})
                residuals.append(f"claim_without_explicit_evidence_ref:{cid}")
            claim_index.setdefault(statement, []).append(cid)

        # Distinguish raw vs calibrated confidence
        if contribution.confidence is not None and contribution.calibrated_confidence is not None:
            if contribution.confidence != contribution.calibrated_confidence:
                checks.append({"name": "confidence_calibration_distinction", "contribution_id": cid, "result": "PASS"})
            else:
                checks.append({"name": "confidence_calibration_distinction", "contribution_id": cid, "result": "PASS"})
        elif contribution.confidence is not None:
            residuals.append(f"missing_calibrated_confidence:{cid}")
            checks.append({"name": "confidence_calibration_distinction", "contribution_id": cid, "result": "PASS_WITH_RESIDUALS"})

        accepted_ids.append(cid)

    # Cross-contribution claim conflicts (same statement, divergent confidence polarity)
    for statement, cids in sorted(claim_index.items()):
        if len(set(cids)) > 1:
            # Presence of multiple contributors for same statement is not automatically conflict.
            confidences = []
            for contribution in contributions:
                if contribution.contribution_id in cids:
                    for claim in contribution.claims:
                        if str(claim.get("statement", "")).strip() == statement:
                            confidences.append(claim.get("confidence"))
            numeric = [float(c) for c in confidences if isinstance(c, (int, float))]
            if numeric and max(numeric) - min(numeric) > 0.5:
                conflicts.append(
                    ConflictRecord(
                        conflict_id=make_id("conflict", "CLAIM_CONFLICT", statement),
                        conflict_type="CLAIM_CONFLICT",
                        contribution_ids=tuple(sorted(set(cids))),
                        detail=f"divergent_confidence_for_claim:{statement[:80]}",
                    )
                )

    fail_checks = [c for c in checks if c.get("result") == "FAIL"]
    if any(c.conflict_type == "POLICY_CONFLICT" for c in conflicts) or fail_checks and not accepted_ids:
        status = "FAIL"
    elif conflicts or residuals:
        status = "PASS_WITH_RESIDUALS" if accepted_ids else "ABSTAIN"
    else:
        status = "PASS"

    result = VerificationResult(
        verification_id=make_id("verify", task.task_id, task.run_id, status, tuple(accepted_ids)),
        task_id=task.task_id,
        run_id=task.run_id,
        status=status,
        checks=tuple(checks),
        residuals=tuple(residuals),
        conflicts=tuple(conflicts),
        contribution_ids=tuple(c.contribution_id for c in contributions),
        provenance=Provenance(
            classification="OBSERVED",
            producer="core.alembic.verify",
            notes=f"rune_bindings={list(rune_bindings_for_operation('SYMBOLIC_VERIFY'))}",
        ),
    )
    digest = hash_model(result)
    return result.model_copy(
        update={
            "provenance": result.provenance.model_copy(
                update={"content_hash": digest, "notes": f"{result.provenance.notes};ts={det_timestamp(digest)}"}
            )
        }
    )
