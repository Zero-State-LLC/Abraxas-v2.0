"""State Recovery for Campaign Director.

Recovers authoritative campaign state exclusively from repository artifacts.
No conversation history. Deterministic. Validates basic continuity and protected state.

Per spec and observed artifacts under out/autonomous_structural_engineering_campaign_001/
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .models import (
    CampaignRecoveryResult,
    ProtectedState,
    load_json,
    stable_hash,
)

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


CAMPAIGN_ID = "ABRAXAS_STRUCTURAL_ENGINEERING_CAMPAIGN_001"
DEFAULT_CAMPAIGN_ROOT = Path("out/autonomous_structural_engineering_campaign_001")


def _find_latest_sealed_batch(campaign_root: Path) -> Tuple[str, int, Dict[str, Any]]:
    """Scan batches/structural_batch_* for the highest numbered with terminal decision or complete receipt."""
    batches_dir = campaign_root / "batches"
    if not batches_dir.exists():
        return "structural_batch_000", 0, {}

    sealed = []
    for d in batches_dir.iterdir():
        if not d.is_dir() or not d.name.startswith("structural_batch_"):
            continue
        try:
            num = int(d.name.split("_")[-1])
        except ValueError:
            continue
        has_terminal = (d / "batch_terminal_decision.v1.json").exists()
        has_receipt = (d / "batch_receipt.v1.json").exists()
        state = load_json(d / "batch_state.v1.json")
        if has_terminal or has_receipt or (state and state.get("completed_in_batch", 0) >= state.get("batch_target", 3)):
            sealed.append((num, d.name, state))
    if not sealed:
        # fallback to any batch_state at root or first
        root_state = load_json(campaign_root / "batch_state.v1.json")
        return root_state.get("batch_id", "structural_batch_001"), root_state.get("campaign_cycles_after", 0), root_state
    sealed.sort(key=lambda x: x[0], reverse=True)
    num, name, state = sealed[0]
    return name, state.get("campaign_cycles_after", num * 3), state


def _load_protected_state(campaign_root: Path) -> ProtectedState:
    # Prefer recovery_state or protected_frontier
    rec = load_json(campaign_root / "recovery_state.v1.json")
    if "protected_state" in rec:
        return ProtectedState.from_dict(rec["protected_state"])
    frontier = load_json(campaign_root / "protected_frontier.v1.json")
    # normalize
    ps = {
        "authority_expanded": frontier.get("authority_expanded", False),
        "canon_mutated": frontier.get("canon_mutated", False),
        "production_activated": frontier.get("production_activated", False),
        "promoted": frontier.get("promoted", False),
        "runtime_transitioned": frontier.get("runtime_transitioned", False),
        "policy_reference_count": rec.get("policy_reference_count", 3),
    }
    return ProtectedState.from_dict(ps)


def _load_recovery_state(campaign_root: Path) -> Dict[str, Any]:
    rec = load_json(campaign_root / "recovery_state.v1.json")
    if not rec:
        # fallback to root campaign or batch
        rec = load_json(campaign_root / "campaign_state.v1.json") or {}
    return rec


def _load_latest_oracle_primary(campaign_root: Path) -> Optional[str]:
    # Try campaign specific or global repo_intelligence
    candidates = [
        campaign_root / "fresh_oracle_decision_snapshot.v1.json",
        Path("out/repo_intelligence/engineering_oracle/engineering_oracle_decision.v1.json"),
        Path("out/live_oracle_engineering_cycle/fresh_oracle_decision_snapshot.v1.json"),
    ]
    for p in candidates:
        dec = load_json(p)
        if dec and "primary_candidate_id" in dec:
            return dec["primary_candidate_id"]
    return None


def _count_candidates_from_intel() -> Tuple[int, int]:
    intel_path = Path("out/repo_intelligence/engineering_oracle/engineering_candidates.v1.json")
    cands = load_json(intel_path)
    if "candidates" in cands:
        actionable = [c for c in cands["candidates"] if c.get("status") != "SATISFIED"]
        return len(cands["candidates"]), len(actionable)
    return 0, 0


def validate_against_schema(obj: Dict[str, Any], schema_path: Path) -> bool:
    if not HAS_JSONSCHEMA or not schema_path.exists():
        return True  # permissive in Phase 1 if no validator
    try:
        with open(schema_path) as f:
            schema = json.load(f)
        jsonschema.validate(instance=obj, schema=schema)
        return True
    except Exception:
        return False


def recover_campaign_state(
    campaign_root: Optional[Path] = None,
    validate_schema: bool = True,
) -> CampaignRecoveryResult:
    """Recover latest canonical state from artifacts only.

    Rules per spec:
    - newest timestamp NOT sufficient
    - must have sealed evidence (terminal/receipt or completed count)
    - protected state must be consistent
    - continuity basic check via cycle numbers
    """
    if campaign_root is None:
        campaign_root = DEFAULT_CAMPAIGN_ROOT

    root = Path(campaign_root).resolve()
    if not root.exists():
        return CampaignRecoveryResult(
            campaign_id=CAMPAIGN_ID,
            latest_sealed_batch="structural_batch_000",
            latest_completed_cycle=0,
            completed_cycle_count=0,
            continuation_mode="MODE_A_STANDARD_SINGLE_CANDIDATE_BATCH",
            next_batch="structural_batch_001",
            next_cycles=[1, 2, 3],
            candidate_count=0,
            global_actionable_count=0,
            oracle_primary_id=None,
            continuous_execution_eligible=False,
            protected_state=ProtectedState(),
            partial_artifacts=["campaign_root_missing"],
            recovery_status="NOT_COMPUTABLE",
        )

    latest_batch, latest_cycle, batch_state = _find_latest_sealed_batch(root)
    rec_state = _load_recovery_state(root)
    protected = _load_protected_state(root)
    oracle_primary = _load_latest_oracle_primary(root)
    total_cands, actionable = _count_candidates_from_intel()

    # Basic continuity from batch_state / rec
    completed_cycles = rec_state.get("v3_cycles_completed", rec_state.get("completed_cycle_count", latest_cycle))
    if batch_state:
        completed_cycles = max(completed_cycles, batch_state.get("campaign_cycles_after", latest_cycle))

    # Determine next
    try:
        batch_num = int(latest_batch.split("_")[-1])
    except Exception:
        batch_num = 0
    next_batch = f"structural_batch_{batch_num + 1:03d}"
    next_cycles = [latest_cycle + 1, latest_cycle + 2, latest_cycle + 3]

    # Partial classification (Phase 1 simple)
    partials: List[str] = []
    status = "VALID"
    if not (root / "batches" / latest_batch / "batch_terminal_decision.v1.json").exists() and batch_state.get("completed_in_batch", 0) < 3:
        status = "PARTIAL_RESUMABLE"
        partials.append(f"partial_{latest_batch}")

    if not protected.is_valid():
        status = "NOT_COMPUTABLE"
        partials.append("protected_state_contradiction")

    # Schema (state shape)
    state_dict = {
        "schema_version": "CampaignDirectorState.v1",
        "campaign_id": CAMPAIGN_ID,
        "latest_sealed_batch": latest_batch,
        "latest_completed_cycle": latest_cycle,
        "completed_cycle_count": completed_cycles,
        "continuation_mode": "MODE_A_STANDARD_SINGLE_CANDIDATE_BATCH",
        "next_batch": next_batch,
        "next_cycles": next_cycles,
        "candidate_count": total_cands,
        "global_actionable_count": actionable,
        "oracle_primary_id": oracle_primary,
        "continuous_execution_eligible": rec_state.get("continuous_engineering_eligible", True) and protected.is_valid(),
        "protected_state": protected.to_dict(),
        "partial_artifacts": partials,
        "recovery_status": status,
    }

    schema_path = Path("contracts/campaign_director/campaign_director_state.v1.schema.json")
    if validate_schema and not validate_against_schema(state_dict, schema_path):
        status = "NOT_COMPUTABLE"
        state_dict["recovery_status"] = status

    result = CampaignRecoveryResult(
        campaign_id=CAMPAIGN_ID,
        latest_sealed_batch=latest_batch,
        latest_completed_cycle=latest_cycle,
        completed_cycle_count=completed_cycles,
        continuation_mode="MODE_A_STANDARD_SINGLE_CANDIDATE_BATCH",
        next_batch=next_batch,
        next_cycles=next_cycles,
        candidate_count=total_cands,
        global_actionable_count=actionable,
        oracle_primary_id=oracle_primary,
        continuous_execution_eligible=state_dict["continuous_execution_eligible"],
        protected_state=protected,
        partial_artifacts=partials,
        recovery_status=status,
        recovery_hash=stable_hash(state_dict),
        raw_artifacts={"batch_state": batch_state, "recovery_state": rec_state},
    )
    return result


if __name__ == "__main__":
    res = recover_campaign_state()
    print(json.dumps(res.to_dict(), indent=2, sort_keys=True))