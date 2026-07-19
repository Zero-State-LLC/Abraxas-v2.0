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
]

RUNNERS = [
    "scripts/run_brier_ledger.py",
    "scripts/run_canary_overlay.py",
    "scripts/run_weight_drift_simulation.py",
    "scripts/run_canary_promotion_review.py",
    "scripts/run_canary_policy_scheduler.py",
]


def test_runtime_modules_do_not_call_write_canonical_json() -> None:
    for rel in RUNTIME_MODULES:
        text = (REPO / rel).read_text(encoding="utf-8")
        assert "write_canonical_json" not in text, f"{rel} still publishes"


def test_runners_publish_via_canonical_json() -> None:
    for rel in RUNNERS:
        text = (REPO / rel).read_text(encoding="utf-8")
        assert "write_canonical_json" in text, f"{rel} missing sole-writer publish"
