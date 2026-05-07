from __future__ import annotations

def validate_manual_execution(forbidden_authorization_status: bool, forbidden_envelope_status: bool, forbidden_action_as_allowed: bool, replay_match: bool, diagnostics: list[dict], acknowledgement_missing: bool, rollback_ready: bool, closure_ready: bool, lineage_cycle: bool, authority_mutation: bool, execution_authority: bool, deployment_authority: bool, activation_authority: bool, auto_execution_attempted: bool) -> dict[str, object]:
    critical_unresolved = any(d.get('severity') == 'critical' and not d.get('resolved', False) for d in diagnostics)
    failed = forbidden_authorization_status or forbidden_envelope_status or forbidden_action_as_allowed or (not replay_match) or critical_unresolved or acknowledgement_missing or (not rollback_ready) or (not closure_ready) or lineage_cycle or authority_mutation or execution_authority or deployment_authority or activation_authority or auto_execution_attempted
    gates = [
        {"gate": "manual_execution_authorization_gate", "passed": not forbidden_authorization_status, "reason": "forbidden authorization rejected"},
        {"gate": "manual_execution_envelope_gate", "passed": not forbidden_envelope_status, "reason": "forbidden envelope rejected"},
        {"gate": "manual_execution_eligibility_gate", "passed": rollback_ready and closure_ready and not acknowledgement_missing, "reason": "eligibility constrained"},
        {"gate": "manual_execution_scope_gate", "passed": not forbidden_action_as_allowed, "reason": "forbidden actions excluded"},
        {"gate": "manual_execution_acknowledgement_gate", "passed": not acknowledgement_missing, "reason": "acknowledgement present"},
        {"gate": "manual_execution_replay_gate", "passed": replay_match and not lineage_cycle, "reason": "deterministic replay and lineage"},
        {"gate": "manual_execution_operator_review_gate", "passed": not (authority_mutation or execution_authority or deployment_authority or activation_authority or auto_execution_attempted), "reason": "operator-only non-authoritative posture"},
    ]
    return {"status": "failed" if failed else "passed", "reason": "manual execution envelope validated" if not failed else "manual execution envelope failed closed", "gate_results": gates}
