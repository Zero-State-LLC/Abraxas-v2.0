"""WP-D: runtime modules must not write out/; runners own publication."""

from __future__ import annotations

from pathlib import Path


REPO = Path(__file__).resolve().parents[1]

RUNTIME_MODULES = [
    "core/brier/runtime.py",
    "core/canary/runtime.py",
    "core/drift/runtime.py",
    "core/canary_promotion/runtime.py",
    "core/canary_scheduler/runtime.py",
    # WP-D batch 2
    "core/forecast/runtime.py",
    "core/external_action_proposals/runtime.py",
    "core/overlay_observability/runtime.py",
    "core/oracle/runtime.py",
    "core/sandbox/runtime.py",
    "core/operator_queue/runtime.py",
    "core/state/runtime.py",
]

RUNNERS = [
    "scripts/run_brier_ledger.py",
    "scripts/run_canary_overlay.py",
    "scripts/run_weight_drift_simulation.py",
    "scripts/run_canary_promotion_review.py",
    "scripts/run_canary_policy_scheduler.py",
    "scripts/run_forecast_candidates.py",
    "scripts/run_external_action_proposals.py",
    "scripts/run_overlay_observability.py",
    "scripts/run_oracle_intake.py",
    "scripts/run_adaptive_sandbox.py",
    "scripts/run_operator_approval_queue.py",
    "scripts/run_state_engine.py",
]


def test_runtime_modules_do_not_call_write_canonical_json() -> None:
    for rel in RUNTIME_MODULES:
        text = (REPO / rel).read_text(encoding="utf-8")
        assert "write_canonical_json" not in text, f"{rel} still publishes"


def test_runners_publish_via_canonical_json() -> None:
    for rel in RUNNERS:
        text = (REPO / rel).read_text(encoding="utf-8")
        assert "write_canonical_json" in text, f"{rel} missing sole-writer publish"
