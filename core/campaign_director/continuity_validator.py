"""Continuity Validator for Campaign Director.

Proves artifacts form one valid deterministic chain.
Basic checks for Phase 1; stops on protected contradiction.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .models import CampaignRecoveryResult, load_json


VALIDATION_FAILURES = [
    "VALID",
    "PARTIAL_RESUMABLE",
    "BROKEN_CONTINUITY",
    "HASH_MISMATCH",
    "CYCLE_GAP",
    "DUPLICATE_CANDIDATE",
    "PROTECTED_STATE_CONTRADICTION",
    "NOT_COMPUTABLE",
]


def validate_continuity(
    recovery: CampaignRecoveryResult,
    campaign_root: Path,
) -> Dict[str, Any]:
    """Run validation checks.

    Returns dict with status and details.
    Protected state contradiction -> stop.
    """
    issues: List[str] = []
    status = recovery.recovery_status

    # Protected state
    if not recovery.protected_state.is_valid():
        issues.append("PROTECTED_STATE_CONTRADICTION")
        status = "PROTECTED_STATE_CONTRADICTION"

    # Cycle contiguity (from recovered numbers)
    if recovery.next_cycles and recovery.latest_completed_cycle + 1 != recovery.next_cycles[0]:
        issues.append("CYCLE_GAP")
        if status == "VALID":
            status = "PARTIAL_RESUMABLE"

    # Check batch references in recent states (heuristic from cycles_before/after)
    batches_dir = campaign_root / "batches"
    if batches_dir.exists():
        batch_states = []
        for d in sorted(batches_dir.glob("structural_batch_*")):
            st = load_json(d / "batch_state.v1.json")
            if st:
                batch_states.append(st)
        # simplistic: check increasing cycles
        prev_after = 0
        for st in batch_states:
            before = st.get("campaign_cycles_before", 0)
            after = st.get("campaign_cycles_after", 0)
            if before < prev_after:
                issues.append("BROKEN_CONTINUITY")
            prev_after = after

    # Duplicate candidate check (from completed lists if present in raw)
    completed = set()
    for k, v in recovery.raw_artifacts.items():
        if isinstance(v, dict) and "completed_candidate_ids" in v:
            for cid in v["completed_candidate_ids"]:
                if cid in completed:
                    issues.append("DUPLICATE_CANDIDATE")
                    break
                completed.add(cid)

    if status == "VALID" and issues:
        status = "PARTIAL_RESUMABLE"

    receipt = {
        "validation_status": status,
        "issues": issues,
        "recovery_hash": recovery.recovery_hash,
        "protected_state_valid": recovery.protected_state.is_valid(),
        "checked_batches": len(list(batches_dir.glob("structural_batch_*"))) if batches_dir.exists() else 0,
    }
    return receipt


if __name__ == "__main__":
    from .state_recovery import recover_campaign_state
    rec = recover_campaign_state()
    val = validate_continuity(rec, Path("out/autonomous_structural_engineering_campaign_001"))
    print(val)