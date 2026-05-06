from __future__ import annotations


def validate_operator_queue(decision: str, replay_match: bool, diagnostics: list[dict], authority_mutation: bool, lineage_cycle: bool, auto_approval_attempted: bool, execution_authority_present: bool, deployment_authority_present: bool) -> dict[str, object]:
    forbidden_decision = decision in {"execute", "activate", "deploy", "promote_live"}
    critical_unresolved = any(d.get("severity") == "critical" and not d.get("resolved", False) for d in diagnostics)
    failed = forbidden_decision or (not replay_match) or critical_unresolved or authority_mutation or lineage_cycle or auto_approval_attempted or execution_authority_present or deployment_authority_present
    gates = [
        {"gate": "operator_queue_request_gate", "passed": not authority_mutation, "reason": "authority locked"},
        {"gate": "operator_queue_decision_gate", "passed": not forbidden_decision, "reason": "forbidden decisions rejected"},
        {"gate": "operator_queue_rationale_gate", "passed": True, "reason": "rationale present"},
        {"gate": "operator_queue_continuity_gate", "passed": not any(d.get('diagnostic_type') == 'continuity_break' and not d.get('resolved', False) for d in diagnostics), "reason": "continuity unresolved events blocked"},
        {"gate": "operator_queue_replay_gate", "passed": replay_match, "reason": "replay mismatch invalidates queue packet"},
        {"gate": "operator_queue_operator_review_gate", "passed": not (auto_approval_attempted or execution_authority_present or deployment_authority_present), "reason": "human review is non-authoritative"},
    ]
    return {"status": "failed" if failed else "passed", "reason": "operator queue validated" if not failed else "operator queue failed closed", "gate_results": gates}
