from __future__ import annotations
from core.proposal_sandbox_routing.constraints import FORBIDDEN_RESTRICTED_ACTIONS
from core.proposal_sandbox_routing.lanes import FORBIDDEN_LANE_TYPES
from core.proposal_sandbox_routing.routes import FORBIDDEN_ROUTE_STATUSES, FORBIDDEN_ROUTE_TYPES

def validate_proposal_sandbox_routing(route_type: str, route_status: str, lane_type: str, actions: list[str], replay_match: bool, diagnostics: list[dict[str, object]], lineage_cycle_detected: bool, authority_mutation: bool, production_routing_authority: bool, deployment_authority: bool, execution_authority: bool, auto_execution_attempted: bool) -> dict[str, object]:
    critical = any(d.get("severity") == "critical" and not d.get("resolved") for d in diagnostics)
    failed = any([
        route_type in FORBIDDEN_ROUTE_TYPES,
        route_status in FORBIDDEN_ROUTE_STATUSES,
        lane_type in FORBIDDEN_LANE_TYPES,
        bool(set(actions).intersection(FORBIDDEN_RESTRICTED_ACTIONS)),
        not replay_match,
        critical,
        lineage_cycle_detected,
        authority_mutation,
        production_routing_authority,
        deployment_authority,
        execution_authority,
        auto_execution_attempted,
    ])
    return {"status": "failed" if failed else "passed", "critical_unresolved": critical}
