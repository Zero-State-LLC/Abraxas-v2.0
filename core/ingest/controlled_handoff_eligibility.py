from __future__ import annotations

from typing import Any


def build_controlled_handoff_eligibility(
    *,
    oracle_signal_module_present: bool,
    shadow_receipt_valid: bool,
) -> dict[str, Any]:
    eligible = oracle_signal_module_present and shadow_receipt_valid
    return {
        "schema_version": "ControlledHandoffEligibility.v1",
        "status": "CONTROLLED_HANDOFF_ELIGIBLE" if eligible else "SHADOW_HANDOFF_ONLY",
        "controlled_handoff_eligible": eligible,
        "lane": "CONTROLLED" if eligible else "SHADOW",
        "advisory_only": True,
        "execution_authority": False,
        "runtime_mutation": False,
    }
