from __future__ import annotations

def validate_review_resolution(replay_match: bool, lineage_cycle: bool, forbidden_posture: bool, forbidden_outcome: bool, diagnostics: list[dict], blockers: list[dict], authority_mutation: bool, execution_authority_present: bool, deployment_authority_present: bool) -> dict[str, object]:
    critical_diag = any(d.get('severity') == 'critical' and not d.get('resolved', False) for d in diagnostics)
    critical_blockers = any(b.get('severity') == 'critical' for b in blockers)
    failed = (not replay_match) or lineage_cycle or forbidden_posture or forbidden_outcome or critical_diag or critical_blockers or authority_mutation or execution_authority_present or deployment_authority_present
    gates = [
        {"gate": "review_resolution_posture_gate", "passed": not forbidden_posture, "reason": "forbidden posture rejected"},
        {"gate": "review_resolution_blocker_gate", "passed": not critical_blockers, "reason": "critical blockers fail closed"},
        {"gate": "review_resolution_outcome_gate", "passed": not forbidden_outcome, "reason": "forbidden outcome rejected"},
        {"gate": "review_resolution_closure_gate", "passed": replay_match and not critical_blockers, "reason": "closure requires replay match and no critical blockers"},
        {"gate": "review_resolution_replay_gate", "passed": replay_match and not lineage_cycle, "reason": "deterministic replay and acyclic lineage"},
        {"gate": "review_resolution_operator_review_gate", "passed": not (authority_mutation or execution_authority_present or deployment_authority_present), "reason": "non-authoritative operator mediated posture"},
    ]
    return {"status": "failed" if failed else "passed", "reason": "review resolution validated" if not failed else "review resolution failed closed", "gate_results": gates}
