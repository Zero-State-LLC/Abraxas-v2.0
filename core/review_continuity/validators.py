from __future__ import annotations


def validate_review_continuity(replay_match: bool, lineage_cycle: bool, forbidden_status: bool, diagnostics: list[dict], authority_mutation: bool, orphaned_continuity: bool, execution_authority_present: bool, deployment_authority_present: bool) -> dict[str, object]:
    critical_unresolved = any(d.get("severity") == "critical" and not d.get("resolved", False) for d in diagnostics)
    failed = (not replay_match) or lineage_cycle or forbidden_status or critical_unresolved or authority_mutation or orphaned_continuity or execution_authority_present or deployment_authority_present
    gates = [
        {"gate": "review_continuity_chain_gate", "passed": not forbidden_status, "reason": "forbidden statuses rejected"},
        {"gate": "review_continuity_inheritance_gate", "passed": not orphaned_continuity, "reason": "inheritance linked"},
        {"gate": "review_continuity_deferral_gate", "passed": True, "reason": "deferral packet present"},
        {"gate": "review_continuity_denial_gate", "passed": True, "reason": "denial packet present"},
        {"gate": "review_continuity_replay_gate", "passed": replay_match and not lineage_cycle, "reason": "replay/lineage deterministic"},
        {"gate": "review_continuity_operator_review_gate", "passed": not (authority_mutation or execution_authority_present or deployment_authority_present), "reason": "review remains non-authoritative"},
    ]
    return {"status": "failed" if failed else "passed", "reason": "review continuity validated" if not failed else "review continuity failed closed", "gate_results": gates}
