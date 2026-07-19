"""Runner: WASSERSTEIN CPU BASELINE COMPUTATION — BOUNDED SHADOW TEST-VECTOR.

Solver: DETERMINISTIC_1D_SORTED_CDF_TRANSPORT_ONLY
Lane:   SHADOW (test vectors only)
Scope:  TEST_VECTOR_COMPUTATION_ONLY
Output: out/metric_operator/wasserstein_cpu_baseline_computation_receipt_001.latest.json
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.wasserstein_cpu_baseline_computation import (
    FIXTURE_DIR,
    SOURCE_GATE_HASH,
    WassersteinCpuBaselineComputationError,
    build_authority_locks,
    build_blocked_scopes,
    build_comparison_summary,
    build_solver_policy_summary,
    build_wasserstein_cpu_baseline_computation_receipt,
    run_computation,
    serialize_wasserstein_cpu_baseline_computation_receipt,
    validate_wasserstein_cpu_baseline_computation_receipt,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

GENERATED_BY = "WASSERSTEIN_CPU_BASELINE_COMPUTATION_001"

OUT_PATH = Path(
    "out/metric_operator/wasserstein_cpu_baseline_computation_receipt_001.latest.json"
)


def _load_fixture_dir(directory: Path) -> list[dict]:
    return [
        json.loads(f.read_text(encoding="utf-8"))
        for f in sorted(directory.iterdir())
        if f.suffix == ".json"
    ]


def main() -> int:
    log.info("WASSERSTEIN CPU BASELINE COMPUTATION — BOUNDED SHADOW TEST-VECTOR")
    log.info("Solver: DETERMINISTIC_1D_SORTED_CDF_TRANSPORT_ONLY")
    log.info("Lane: SHADOW | Scope: TEST_VECTOR_COMPUTATION_ONLY")

    gate_path = Path(
        "out/metric_operator/wasserstein_cpu_baseline_implementation_gate_001.latest.json"
    )
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    if gate.get("canonical_hash") != SOURCE_GATE_HASH:
        log.error(
            "Gate canonical_hash mismatch: got %s expected %s",
            gate.get("canonical_hash"),
            SOURCE_GATE_HASH,
        )
        return 1
    if gate.get("gate_status") != "WASSERSTEIN_CPU_BASELINE_IMPLEMENTATION_GATE_READY":
        log.error("Gate not READY: %s", gate.get("gate_status"))
        return 1
    log.info("Gate verified: %s", gate["gate_status"])

    valid_fixtures = _load_fixture_dir(FIXTURE_DIR / "valid")
    invalid_fixtures = _load_fixture_dir(FIXTURE_DIR / "invalid")
    nc_fixtures = _load_fixture_dir(FIXTURE_DIR / "not_computable")
    total = len(valid_fixtures) + len(invalid_fixtures) + len(nc_fixtures)
    log.info(
        "Fixtures loaded: valid=%d invalid=%d not_computable=%d total=%d",
        len(valid_fixtures),
        len(invalid_fixtures),
        len(nc_fixtures),
        total,
    )

    valid_results, invalid_results, nc_results = run_computation(
        valid_fixtures, invalid_fixtures, nc_fixtures
    )

    comparison_summary = build_comparison_summary(
        valid_results, invalid_results, nc_results
    )
    log.info(
        "Comparison: valid_matched=%d/%d invalid_routed=%d/%d nc_routed=%d/%d all_matched=%s",
        comparison_summary["valid_matched"],
        comparison_summary["total_valid"],
        comparison_summary["invalid_routed_as_invalid_input"],
        comparison_summary["total_invalid"],
        comparison_summary["nc_routed_as_not_computable"],
        comparison_summary["total_not_computable"],
        comparison_summary["all_matched"],
    )

    payload: dict = {
        "valid_fixture_results": valid_results,
        "invalid_fixture_results": invalid_results,
        "not_computable_fixture_results": nc_results,
        "comparison_summary": comparison_summary,
        "solver_policy_summary": build_solver_policy_summary(),
        "blocked_scopes": build_blocked_scopes(),
        "authority_locks": build_authority_locks(),
        "provenance": {
            "source": "WASSERSTEIN_CPU_BASELINE_COMPUTATION",
            "generated_by": GENERATED_BY,
            "source_gate_hash": SOURCE_GATE_HASH,
            "evidence_refs": [
                (
                    "WassersteinCpuBaselineImplementationGate.v1:"
                    "wasserstein_cpu_baseline_implementation_gate_001"
                ),
                (
                    "WassersteinCpuBaselineImplementationPlan.v1:"
                    "wasserstein_cpu_baseline_implementation_plan_001"
                ),
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }

    try:
        packet = build_wasserstein_cpu_baseline_computation_receipt(payload)
    except WassersteinCpuBaselineComputationError as exc:
        log.error("Receipt build failed: %s", exc)
        return 1

    try:
        validate_wasserstein_cpu_baseline_computation_receipt(packet)
    except WassersteinCpuBaselineComputationError as exc:
        log.error("Receipt validation failed: %s", exc)
        return 1

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_cpu_baseline_computation_receipt(packet),
        encoding="utf-8",
    )

    al = packet["authority_locks"]
    cs = packet["comparison_summary"]
    log.info(
        "Wrote %s  canonical_hash=%s  status=%s",
        OUT_PATH,
        packet["canonical_hash"][:16] + "...",
        packet["computation_status"],
    )

    print(f"receipt_id={packet['receipt_id']}")
    print(f"computation_status={packet['computation_status']}")
    print(f"valid_matched={cs['valid_matched']}/{cs['total_valid']}")
    print(f"invalid_routed={cs['invalid_routed_as_invalid_input']}/{cs['total_invalid']}")
    print(f"nc_routed={cs['nc_routed_as_not_computable']}/{cs['total_not_computable']}")
    print(f"all_matched={cs['all_matched']}")
    print(f"wasserstein_cpu_baseline_computation_authorized={al['wasserstein_cpu_baseline_computation_authorized']}")
    print(f"emits_metric_values={al['emits_metric_values']}")
    print(f"intended_lane={packet['intended_lane']}")
    print(f"canonical_hash={packet['canonical_hash']}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
