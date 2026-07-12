#!/usr/bin/env python3
"""Authority resolver for engineering candidates (consumes known operator grant)."""

from typing import Dict, Any, List

def resolve_authority(cand: Dict[str, Any]) -> Dict[str, Any]:
    # Observed from verified grant + authority_boundary all false
    grant = "broad_operator_grant_all_engineering_tied_to_approval"
    boundary = {
        "promotion_authorized": False,
        "production_activation_allowed": False,
        "active_skill_replacement_allowed": False,
        "automatic_transition_allowed": False,
    }

    observed = cand.get("authority_observed", [])
    permitted = grant in observed or "advisory_engineering" in cand.get("authority_required", [])

    status = "PERMITTED_ADVISORY" if permitted else "BLOCKED"
    prohibited = [
        "production_activation",
        "canon_mutation",
        "promotion",
        "runtime_execution"
    ]

    return {
        "authority_status": status,
        "authority_evidence": [grant] if permitted else [],
        "prohibited_transitions": prohibited,
        "boundary": boundary,
    }
