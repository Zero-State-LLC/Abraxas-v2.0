"""Safe, read-only status demo for Abraxas v2.0.

Reads existing out/ artifacts and prints a summary of the current operator
state. Does NOT write any files, does NOT invoke any runners, does NOT touch
research_canary artifacts, and does NOT require external services.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent
_NO_ARTIFACT = "(artifact not found)"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _short_hash(h: str, length: int = 16) -> str:
    if not h or len(h) < length:
        return h or "(none)"
    return h[:length] + "..."


def _print_section(title: str) -> None:
    print(f"\n{title}")
    print("  " + "-" * (len(title) - 0))


def _field(label: str, value: Any, width: int = 22) -> None:
    print(f"  {label:<{width}} : {value}")


def print_status() -> None:
    print("=== ABRAXAS v2.0 — SAFE STATUS DEMO ===")
    print("[READ-ONLY: no files written, no artifacts mutated]")

    _print_section("DOCTRINE VALIDATOR")
    validation = _read_json(_ROOT / "out" / "validation" / "latest.json")
    if validation:
        _field("summary_status", validation.get("summary_status", _NO_ARTIFACT))
        _field("contract_count", validation.get("contract_count", _NO_ARTIFACT))
        _field("seal_recommendation", validation.get("seal_recommendation", _NO_ARTIFACT))
    else:
        print(f"  {_NO_ARTIFACT}")
        print("  Run: python scripts/run_doctrine_validator.py")

    _print_section("TRANSPORT CHAIN — CURRENT FRONTIER")
    plan = _read_json(
        _ROOT / "out" / "metric_operator"
        / "transport_fixture_corpus_creation_plan_001.latest.json"
    )
    if plan:
        fpp = plan.get("fixture_path_plan", {})
        _field("plan_status", plan.get("plan_status", _NO_ARTIFACT))
        _field("plan_stage", plan.get("plan_stage", _NO_ARTIFACT))
        _field("operator_id", plan.get("operator_id", _NO_ARTIFACT))
        _field(
            "fixture_count",
            (
                f"{fpp.get('fixture_count', '?')}"
                f" (valid={fpp.get('valid_fixture_count', '?')}"
                f"  invalid={fpp.get('invalid_fixture_count', '?')}"
                f"  not_computable={fpp.get('not_computable_fixture_count', '?')})"
            ),
        )
        _field("next_step", plan.get("recommended_next_step", _NO_ARTIFACT))
        _field("canonical_hash", _short_hash(plan.get("canonical_hash", "")))
    else:
        print(f"  {_NO_ARTIFACT}")

    _print_section("IMPLEMENTATION GATE")
    gate = _read_json(
        _ROOT / "out" / "metric_operator"
        / "transport_computation_implementation_gate_001.latest.json"
    )
    if gate:
        locks = gate.get("authority_locks", {})
        _field("gate_status", gate.get("gate_status", _NO_ARTIFACT))
        _field(
            "computation_authorized",
            locks.get("transport_computation_implementation_authorized", _NO_ARTIFACT),
        )
        _field(
            "lp_solver_authorized",
            locks.get("lp_solver_invocation_authorized_for_test_vectors", _NO_ARTIFACT),
        )
    else:
        print(f"  {_NO_ARTIFACT}")

    _print_section("AUTHORITY POSTURE")
    ref = plan or gate
    if ref:
        locks = ref.get("authority_locks", {})
        for key in (
            "production_activation",
            "forecast_influence",
            "runtime_mutation",
            "canon_promotion",
            "shadow_lane_only",
        ):
            _field(key, locks.get(key, _NO_ARTIFACT))
    else:
        print(f"  {_NO_ARTIFACT}")

    print("\n=== END STATUS (read-only) ===\n")


def main() -> None:
    print_status()
    sys.exit(0)


if __name__ == "__main__":
    main()
