from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

DEFAULT_PYRIGHT_TIMEOUT_SECONDS = 120
ABRAXAS_FAST_CI_PYRIGHT_SCOPE_FULL = "full"

DEFAULT_FAST_CI_PYRIGHT_TARGETS: tuple[str, ...] = (
    "core/geometric_research_item.py",
    "core/geometric_signal_packet.py",
    "core/metric_operator_registry.py",
    "core/geometric_projection_spec.py",
    "core/yggdrasil_geometric_route_metadata.py",
    "core/oracle_geometric_signal_attachment.py",
    "core/heavy_tail_signal_calibrator.py",
    "core/counterfactual_geometry_engine.py",
    "core/reservoir_geometry_diagnostic.py",
    "core/metric_operator_baseline_test_vector_pack.py",
    "core/chamfer_baseline_implementation_plan.py",
    "core/chamfer_test_vector_schema_plan.py",
    "core/chamfer_valid_fixture_implementation_plan.py",
    "core/chamfer_invalid_fixture_implementation_plan.py",
    "core/chamfer_not_computable_fixture_implementation_plan.py",
    "core/chamfer_fixture_plan_consolidation_receipt.py",
    "core/chamfer_fixture_implementation_readiness_review.py",
    "core/chamfer_expected_distance_policy_plan.py",
    "core/chamfer_fixture_creation_authorization_review.py",
    "core/chamfer_fixture_creation_pr_plan.py",
    "core/chamfer_fixture_creation_actual_pr_gate.py",
    "core/chamfer_expected_distance_values_actual_pr_gate.py",
    "scripts/run_fast_ci.py",
    "tests/test_geometric_research_item.py",
    "tests/test_geometric_signal_packet.py",
    "tests/test_metric_operator_registry.py",
    "tests/test_geometric_projection_spec.py",
    "tests/test_yggdrasil_geometric_route_metadata.py",
    "tests/test_oracle_geometric_signal_attachment.py",
    "tests/test_heavy_tail_signal_calibrator.py",
    "tests/test_counterfactual_geometry_engine.py",
    "tests/test_reservoir_geometry_diagnostic.py",
    "tests/test_metric_operator_baseline_test_vector_pack.py",
    "tests/test_chamfer_baseline_implementation_plan.py",
    "tests/test_chamfer_test_vector_schema_plan.py",
    "tests/test_chamfer_valid_fixture_implementation_plan.py",
    "tests/test_chamfer_invalid_fixture_implementation_plan.py",
    "tests/test_chamfer_not_computable_fixture_implementation_plan.py",
    "tests/test_chamfer_fixture_plan_consolidation_receipt.py",
    "tests/test_chamfer_fixture_implementation_readiness_review.py",
    "tests/test_chamfer_expected_distance_policy_plan.py",
    "tests/test_chamfer_fixture_creation_authorization_review.py",
    "tests/test_chamfer_fixture_creation_pr_plan.py",
    "tests/test_chamfer_fixture_creation_actual_pr_gate.py",
    "tests/test_chamfer_expected_distance_values_actual_pr_gate.py",
    "tests/test_chamfer_expected_distance_values.py",
    "tests/test_run_fast_ci.py",
)


COMMANDS: list[list[str]] = [
    ["python", "scripts/run_artifact_regeneration.py", "--check-drift"],
    [
        "python",
        "-m",
        "pytest",
        "-q",
        "-m",
        "not slow and not integration and not canon and not artifact",
    ],
    ["python", "-m", "ruff", "check", "."],
]


def _preflight_check() -> int:
    try:
        import jsonschema  # noqa: F401
    except ModuleNotFoundError:
        print(
            "Missing test dependency: jsonschema. "
            "Install dev extras first: python -m pip install -e '.[dev]'",
            file=sys.stderr,
            flush=True,
        )
        return 1
    return 0


def _pyright_timeout_seconds() -> int:
    raw = os.environ.get("ABRAXAS_PYRIGHT_TIMEOUT_SECONDS", str(DEFAULT_PYRIGHT_TIMEOUT_SECONDS))
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_PYRIGHT_TIMEOUT_SECONDS
    return value if value > 0 else DEFAULT_PYRIGHT_TIMEOUT_SECONDS


def _resolve_pyright_command() -> tuple[list[str], str]:
    scope = os.environ.get("ABRAXAS_FAST_CI_PYRIGHT_SCOPE", "bounded").strip().lower()
    if scope == ABRAXAS_FAST_CI_PYRIGHT_SCOPE_FULL:
        return (["pyright"], "full")

    targets: list[str] = []
    for rel_path in DEFAULT_FAST_CI_PYRIGHT_TARGETS:
        if Path(rel_path).exists():
            targets.append(rel_path)
        else:
            print(f"[fast-ci] skipping missing pyright target: {rel_path}", flush=True)

    return (["pyright", *targets], "bounded")


def main() -> int:
    preflight_status = _preflight_check()
    if preflight_status != 0:
        return preflight_status

    pyright_timeout_seconds = _pyright_timeout_seconds()

    for command in COMMANDS:
        print("+", " ".join(command), flush=True)
        completed = subprocess.run(command, check=False)
        if completed.returncode != 0:
            return completed.returncode

    pyright_command, pyright_scope = _resolve_pyright_command()
    print(f"[fast-ci] pyright scope: {pyright_scope}", flush=True)
    print("+", " ".join(pyright_command), flush=True)
    try:
        completed = subprocess.run(pyright_command, check=False, timeout=pyright_timeout_seconds)
    except subprocess.TimeoutExpired:
        print(
            f"Command timed out after {pyright_timeout_seconds}s: {' '.join(pyright_command)}",
            file=sys.stderr,
            flush=True,
        )
        return 124

    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
