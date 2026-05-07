from __future__ import annotations

def validate_manual_execution_receipts(forbidden_receipt_status: bool, forbidden_receipt_action_as_allowed: bool, replay_match: bool, diagnostics: list[dict], acknowledgement_missing: bool, authorization_envelope_missing: bool, lineage_cycle: bool, authority_mutation: bool, execution_authority: bool, deployment_authority: bool, activation_authority: bool, auto_execution_attempted: bool) -> dict[str, object]:
    critical_unresolved=any(d.get('severity')=='critical' and not d.get('resolved',False) for d in diagnostics)
    failed=forbidden_receipt_status or forbidden_receipt_action_as_allowed or (not replay_match) or critical_unresolved or acknowledgement_missing or authorization_envelope_missing or lineage_cycle or authority_mutation or execution_authority or deployment_authority or activation_authority or auto_execution_attempted
    gates=[
        {"gate":"manual_execution_receipt_gate","passed":not forbidden_receipt_status,"reason":"forbidden receipt status rejected"},
        {"gate":"manual_execution_receipt_ledger_gate","passed":not authorization_envelope_missing,"reason":"authorization envelope linked"},
        {"gate":"manual_execution_receipt_scope_gate","passed":not forbidden_receipt_action_as_allowed,"reason":"forbidden actions excluded"},
        {"gate":"manual_execution_receipt_acknowledgement_gate","passed":not acknowledgement_missing,"reason":"acknowledgement present"},
        {"gate":"manual_execution_receipt_replay_gate","passed":replay_match and not lineage_cycle,"reason":"deterministic replay and lineage"},
        {"gate":"manual_execution_receipt_operator_review_gate","passed":not (authority_mutation or execution_authority or deployment_authority or activation_authority or auto_execution_attempted),"reason":"operator-only non-authoritative posture"},
    ]
    return {"status":"failed" if failed else "passed","reason":"manual execution receipt ledger validated" if not failed else "manual execution receipt ledger failed closed","gate_results":gates}
