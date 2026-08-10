from __future__ import annotations

from typing import Any, Mapping

from core.contract_validation import build_validation_report

from .models import ReplayLedger, ReplayTemporalDiff, ReplayLedgerValidationFinding, ReplayLedgerValidationReport

def validate_replay_ledger(ledger: ReplayLedger | Mapping[str, Any]) -> ReplayLedgerValidationReport:
    ledger_obj = ledger if isinstance(ledger, ReplayLedger) else ReplayLedger(**dict(ledger))
    findings=[]
    status="PASS"
    if ledger_obj.live_execution_allowed or ledger_obj.mutation_allowed or ledger_obj.routing_change_allowed:
        findings.append(ReplayLedgerValidationFinding("FLAGS_FORBIDDEN","error","live_execution/mutation/routing must be false."))
        status="BLOCKED"
    if ledger_obj.ledger_status=="LEDGER_READY" and not ledger_obj.entries:
        findings.append(ReplayLedgerValidationFinding("LEDGER_READY_REQUIRES_ENTRIES","not_computable","LEDGER_READY requires entries."))
        status="NOT_COMPUTABLE" if status!="BLOCKED" else status
    if ledger_obj.ledger_status=="STABLE_HISTORY" and len(ledger_obj.entries)<2:
        findings.append(ReplayLedgerValidationFinding("STABLE_HISTORY_REQUIRES_TWO","error","STABLE_HISTORY requires >=2 entries."))
        status="BLOCKED"
    if ledger_obj.created_by_lane=="SHADOW" and ledger_obj.ledger_status=="STABLE_HISTORY":
        findings.append(ReplayLedgerValidationFinding("SHADOW_STABLE_BLOCKED","error","SHADOW cannot mark STABLE_HISTORY."))
        status="BLOCKED"
    if ledger_obj.created_by_lane=="PROJECTION" and ledger_obj.authority_ref is not None:
        findings.append(ReplayLedgerValidationFinding("PROJECTION_AUTH_BLOCKED","error","PROJECTION cannot create authority."))
        status="BLOCKED"
    return build_validation_report(status, findings, subject_key="ledger_id", subject_id=ledger_obj.ledger_id)

def validate_replay_temporal_diff(diff: ReplayTemporalDiff | Mapping[str, Any]) -> ReplayLedgerValidationReport:
    d = diff if isinstance(diff, ReplayTemporalDiff) else ReplayTemporalDiff(**dict(diff))
    findings=[]
    status="PASS"
    if d.live_execution_allowed or d.mutation_allowed or d.routing_change_allowed:
        findings.append(ReplayLedgerValidationFinding("DIFF_FLAGS_FORBIDDEN","error","live_execution/mutation/routing must be false."))
        status="BLOCKED"
    if d.stability_score.mutation_allowed:
        findings.append(ReplayLedgerValidationFinding("SCORE_MUTATION_FORBIDDEN","error","stability_score.mutation_allowed must be false."))
        status="BLOCKED"
    if d.diff_status=="NO_DIVERGENCE" and (d.divergence_findings or d.stability_score.divergence_count!=0):
        findings.append(ReplayLedgerValidationFinding("NO_DIVERGENCE_INVALID","error","NO_DIVERGENCE requires no divergence findings and zero divergence_count."))
        status="BLOCKED"
    if d.diff_status=="NONDETERMINISM_DETECTED" and not any(f.divergence_type=="NONDETERMINISM" for f in d.divergence_findings):
        findings.append(ReplayLedgerValidationFinding("NONDET_FINDING_REQUIRED","error","NONDETERMINISM_DETECTED requires NONDETERMINISM finding."))
        status="BLOCKED"
    if d.diff_status=="BLOCKED_BY_INPUTS" and not any(f.divergence_type=="MISSING_INPUT" for f in d.divergence_findings):
        findings.append(ReplayLedgerValidationFinding("MISSING_INPUT_REQUIRED","error","BLOCKED_BY_INPUTS requires MISSING_INPUT finding."))
        status="BLOCKED"
    if d.created_by_lane=="SHADOW" and d.diff_status=="NO_DIVERGENCE":
        findings.append(ReplayLedgerValidationFinding("SHADOW_NO_DIVERGENCE_BLOCKED","error","SHADOW cannot mark authoritative NO_DIVERGENCE."))
        status="BLOCKED"
    if d.created_by_lane=="PROJECTION" and d.authority_ref is not None:
        findings.append(ReplayLedgerValidationFinding("PROJECTION_AUTH_BLOCKED","error","PROJECTION cannot create authority."))
        status="BLOCKED"
    return build_validation_report(status, findings, subject_key="diff_id", subject_id=d.diff_id)
