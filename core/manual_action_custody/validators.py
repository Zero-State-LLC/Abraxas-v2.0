from __future__ import annotations

def validate_manual_action_custody(forbidden_custody_status: bool, forbidden_escalation_type: bool, replay_match: bool, diagnostics: list[dict], receipt_missing: bool, acknowledgement_missing: bool, lineage_cycle: bool, authority_mutation: bool, execution_authority: bool, deployment_authority: bool, activation_authority: bool, auto_execution_attempted: bool) -> dict[str, object]:
    critical_unresolved = any(d.get('severity') == 'critical' and not d.get('resolved', False) for d in diagnostics)
    failed = forbidden_custody_status or forbidden_escalation_type or (not replay_match) or critical_unresolved or receipt_missing or acknowledgement_missing or lineage_cycle or authority_mutation or execution_authority or deployment_authority or activation_authority or auto_execution_attempted
    gates = [
        {"gate": "manual_action_custody_gate", "passed": not forbidden_custody_status, "reason": "forbidden custody status rejected"},
        {"gate": "manual_action_handoff_gate", "passed": not receipt_missing, "reason": "receipt/handoff linked"},
        {"gate": "manual_action_acknowledgement_gate", "passed": not acknowledgement_missing, "reason": "acknowledgement present"},
        {"gate": "manual_action_escalation_gate", "passed": not forbidden_escalation_type, "reason": "forbidden escalation rejected"},
        {"gate": "manual_action_replay_gate", "passed": replay_match and not lineage_cycle, "reason": "deterministic replay and lineage"},
        {"gate": "manual_action_operator_review_gate", "passed": not (authority_mutation or execution_authority or deployment_authority or activation_authority or auto_execution_attempted), "reason": "operator-only non-authoritative posture"},
    ]
    return {"status": "failed" if failed else "passed", "reason": "manual action custody validated" if not failed else "manual action custody failed closed", "gate_results": gates}
