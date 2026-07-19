#!/usr/bin/env python3
"""
Validate existing campaign director / campaign artifacts (read-only).

Usage:
env -i ... uv run python scripts/campaign/run_campaign_director_validate.py --campaign ...
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.campaign_director.state_recovery import recover_campaign_state
from core.campaign_director.continuity_validator import validate_continuity
from core.campaign_director.protected_state_guard import guard_recovery


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign-root", default="out/autonomous_structural_engineering_campaign_001")
    parser.add_argument("--output-dir", default="out/campaign_director")
    args = parser.parse_args()

    root = Path(args.campaign_root)
    print("=== CAMPAIGN DIRECTOR VALIDATE ===")

    recovery = recover_campaign_state(root)
    continuity = validate_continuity(recovery, root)
    guard = guard_recovery(recovery)

    print("Recovery status:", recovery.recovery_status)
    print("Continuity:", continuity["validation_status"])
    print("Protected valid:", guard["valid"])

    # Check for director artifacts if present
    out = Path(args.output_dir)
    for name in ["campaign_director_state.v1.json", "bounded_plan.v1.json", "director_run_receipt.v1.json"]:
        p = out / name
        if p.exists():
            print(f"  Found {name}")

    # Basic schema presence
    schemas = list(Path("contracts/campaign_director").glob("*.schema.json"))
    print(f"Schemas present: {len(schemas)}")

    print("=== VALIDATE COMPLETE ===")
    return 0 if recovery.recovery_status == "VALID" else 1


if __name__ == "__main__":
    sys.exit(main())
