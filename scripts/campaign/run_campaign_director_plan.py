#!/usr/bin/env python3
"""
Campaign Director Plan (read-only Phase 1).

Recover -> validate -> resolve mode -> build bounded plan -> emit continuation.
No execution, no mutation.

Usage (scrubbed):
env -i PATH=... uv run python scripts/campaign/run_campaign_director_plan.py \
  --campaign ABRAXAS_STRUCTURAL_ENGINEERING_CAMPAIGN_001
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.campaign_director.state_recovery import recover_campaign_state
from core.campaign_director.protected_state_guard import guard_before_plan
from core.campaign_director.mode_resolver import resolve_mode
from core.campaign_director.execution_planner import build_bounded_plan
from core.campaign_director.continuation_emitter import emit_continuation, write_continuation_artifact
from core.campaign_director.models import save_json, DirectorReceipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign", default="ABRAXAS_STRUCTURAL_ENGINEERING_CAMPAIGN_001")
    parser.add_argument(
        "--campaign-root",
        default="out/autonomous_structural_engineering_campaign_001",
    )
    parser.add_argument("--output-dir", default="out/campaign_director")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.campaign_root)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== CAMPAIGN DIRECTOR PLAN (READ-ONLY) ===")

    recovery = recover_campaign_state(root)
    guard = guard_before_plan(recovery)
    decision = resolve_mode(recovery, root)
    plan = build_bounded_plan(recovery, decision)

    continuation = emit_continuation(recovery, plan)

    print(f"Mode: {decision.mode} authorized={decision.authorized}")
    print(f"Plan: {plan.batch_id} cycles={plan.cycle_range} stop_before={plan.stop_before_cycle}")
    print(f"Primaries: {plan.primary_candidates}")
    print(f"Recovery hash: {recovery.recovery_hash[:32]}...")
    print(f"Plan hash: {plan.plan_hash[:32]}...")

    if guard.get("stop_signal"):
        print("STOP: protected state violation")
        return 2

    # Emit
    plan_path = out_dir / "bounded_plan.v1.json"
    save_json(plan_path, plan.to_dict())

    cont_path = write_continuation_artifact(continuation, out_dir)

    # Director run receipt (Phase 1: read only)
    receipt = DirectorReceipt(
        director_run_id=f"ABX_DIRECTOR_RUN_{recovery.campaign_id[:8]}",
        campaign_id=recovery.campaign_id,
        recovery_hash=recovery.recovery_hash,
        mode_decision_hash=decision.decision_hash,
        plan_hash=plan.plan_hash,
        executed_lifecycle_count=0,
        terminal_status="CAMPAIGN_DIRECTOR_READ_ONLY_READY",
        continuation_hash=continuation.continuation_hash,
    )
    receipt_path = out_dir / "director_run_receipt.v1.json"
    save_json(receipt_path, receipt.to_dict())

    # Also state
    save_json(out_dir / "campaign_director_state.v1.json", recovery.to_dict())

    print(f"Emitted plan: {plan_path}")
    print(f"Emitted continuation: {cont_path}")
    print(f"Emitted receipt: {receipt_path}")
    print("=== PLAN COMPLETE (READ-ONLY) ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())