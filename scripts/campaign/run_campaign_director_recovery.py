#!/usr/bin/env python3
"""
Campaign Director Recovery (read-only Phase 1).

Recover canonical campaign state from repository artifacts only.
Emits recovery receipt under out/campaign_director/

Usage (scrubbed):
env -i \
PATH="$PATH" \
HOME="$HOME" \
USER="$USER" \
UV_CACHE_DIR="$HOME/.cache/uv" \
uv run python scripts/campaign/run_campaign_director_recovery.py \
  --campaign-root out/autonomous_structural_engineering_campaign_001
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Ensure core importable
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.campaign_director.state_recovery import recover_campaign_state
from core.campaign_director.continuity_validator import validate_continuity
from core.campaign_director.protected_state_guard import guard_recovery
from core.campaign_director.models import save_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--campaign-root",
        default="out/autonomous_structural_engineering_campaign_001",
        help="Path to campaign root artifacts",
    )
    parser.add_argument(
        "--output-dir",
        default="out/campaign_director",
        help="Where to emit receipts",
    )
    args = parser.parse_args()

    root = Path(args.campaign_root)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== CAMPAIGN DIRECTOR RECOVERY (READ-ONLY) ===")
    print(f"Campaign root: {root}")

    recovery = recover_campaign_state(root)
    continuity = validate_continuity(recovery, root)
    guard = guard_recovery(recovery)

    print(f"Recovery status: {recovery.recovery_status}")
    print(f"Latest sealed: {recovery.latest_sealed_batch} (cycle ~{recovery.latest_completed_cycle})")
    print(f"Next: {recovery.next_batch} cycles {recovery.next_cycles}")
    print(f"Protected valid: {recovery.protected_state.is_valid()}")
    print(f"Continuous eligible: {recovery.continuous_execution_eligible}")
    if guard.get("stop_signal"):
        print("*** PROTECTED STATE STOP ***")
        print(json.dumps(guard, indent=2))

    # Emit artifacts
    rec_dict = recovery.to_dict()
    rec_path = out_dir / "recovery_receipt.v1.json"
    save_json(rec_path, {
        "director_run_id": f"ABX_DIRECTOR_RECOVER_{recovery.campaign_id[:8]}",
        "recovery": rec_dict,
        "continuity": continuity,
        "guard": guard,
        "emitted_at": datetime.now(timezone.utc).isoformat() + "Z",
        "recovery_hash": recovery.recovery_hash,
    })

    # Also write state snapshot
    state_path = out_dir / "campaign_director_state.v1.json"
    save_json(state_path, rec_dict)

    print(f"Emitted: {rec_path}")
    print(f"Emitted: {state_path}")
    print("=== RECOVERY COMPLETE ===")
    return 0 if recovery.recovery_status in ("VALID", "PARTIAL_RESUMABLE") else 1


if __name__ == "__main__":
    sys.exit(main())