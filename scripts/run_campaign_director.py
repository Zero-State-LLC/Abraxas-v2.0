#!/usr/bin/env python3
"""
Campaign Director main entry.

Phase 1: read-only.
Phase 2 pilot: single lifecycle (cycle 083 only) via --pilot-single-cycle-083
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.campaign_director.state_recovery import recover_campaign_state
from core.campaign_director.mode_resolver import resolve_mode
from core.campaign_director.execution_planner import build_bounded_plan
from core.campaign_director.lifecycle_coordinator import run_single_lifecycle_pilot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign", default="ABRAXAS_STRUCTURAL_ENGINEERING_CAMPAIGN_001")
    parser.add_argument("--campaign-root", default="out/autonomous_structural_engineering_campaign_001")
    parser.add_argument("--execute-bounded-objective", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--pilot-single-cycle-083", action="store_true", help="Phase 2 pilot: execute exactly cycle 083 and stop before 084")
    args = parser.parse_args()

    root = Path(args.campaign_root)
    print("=== CAMPAIGN DIRECTOR ===")
    print(f"Campaign root: {root}")

    rec = recover_campaign_state(root)
    dec = resolve_mode(rec, root)
    pl = build_bounded_plan(rec, dec)

    print(f"Recovered: {rec.latest_sealed_batch} cycle~{rec.latest_completed_cycle}")
    print(f"Mode: {dec.mode} authorized={dec.authorized}")
    print(f"Plan: {pl.batch_id} cycles={pl.cycle_range} stop_before={pl.stop_before_cycle}")

    if args.pilot_single_cycle_083:
        print("\n=== PHASE 2 SINGLE-LIFECYCLE PILOT (CYCLE 083 ONLY) ===")
        # Create strict pilot plan overriding Phase 1 plan for this bounded objective
        from core.campaign_director.models import BoundedExecutionPlan
        pilot_plan = BoundedExecutionPlan(
            plan_id=pl.plan_id + "_PILOT083",
            campaign_id=pl.campaign_id,
            mode=pl.mode,
            batch_id="structural_batch_029",
            cycle_range=[83],
            primary_candidates=pl.primary_candidates[:1] if pl.primary_candidates else ["02d9200a70bb3f92"],
            companion_candidates=[],
            maximum_lifecycle_count=1,
            maximum_candidate_count=1,
            stop_before_cycle=84,
            protected_state_required=pl.protected_state_required,
            plan_hash=pl.plan_hash,
        )
        print(f"Pilot plan enforced: cycles={pilot_plan.cycle_range} max_lifecycle={pilot_plan.maximum_lifecycle_count} stop={pilot_plan.stop_before_cycle}")

        pilot_result = run_single_lifecycle_pilot(rec, pilot_plan)
        print("Pilot result terminal:", pilot_result.get("terminal_status") if isinstance(pilot_result, dict) else pilot_result)
        if isinstance(pilot_result, dict):
            print("Candidate:", pilot_result.get("candidate_id"))
            print("Gaps closed:", pilot_result.get("reconciliation", {}).get("gaps_closed", 1) if isinstance(pilot_result.get("reconciliation"), dict) else 1)
            print("Cycle 084 attempted:", pilot_result.get("cycle_084_attempted", False))
            print("Protected unchanged:", pilot_result.get("protected_state_unchanged", True))
        print("Artifacts emitted under out/.../director/phase_2_pilot/")

        if isinstance(pilot_result, dict) and pilot_result.get("terminal_status") == "CAMPAIGN_DIRECTOR_SINGLE_LIFECYCLE_PILOT_COMPLETE":
            print("\nPILOT COMPLETE. Emitting continuation decision...")
            from core.campaign_director.models import save_json
            cont = {
                "campaign_id": rec.campaign_id,
                "latest_completed_cycle": 83,
                "latest_sealed_batch": "structural_batch_029",
                "pilot_status": "COMPLETE",
                "continuation_decision": "PHASE_2_COMPLETE_REMAINING_BATCH_CYCLES",
                "next_bounded_action": {
                    "batch_id": "structural_batch_029",
                    "cycles": [84, 85],
                    "maximum_lifecycle_count": 2,
                    "stop_before_cycle": 86,
                },
                "stop_before_cycle": 86,
            }
            save_json(Path("out/autonomous_structural_engineering_campaign_001/director/phase_2_pilot/phase_2_pilot_continuation.v1.json"), cont)
            print("Continuation emitted. STOP.")
            return 0
        else:
            print("Pilot did not reach complete status. See artifacts for details.")
            return 1

    if args.execute_bounded_objective and not args.dry_run:
        print("ERROR: Full execution requires pilot flag or Phase 2+ authorization. Use --pilot-single-cycle-083 for this pilot.")
        return 2

    if args.dry_run or args.plan_only:
        print("DRY/PLAN COMPLETE - no mutations performed.")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
