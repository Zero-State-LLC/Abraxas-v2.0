from __future__ import annotations

import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SCRIPT_DIR_KEY = _SCRIPT_DIR.casefold()
sys.path = [
    path
    for path in sys.path
    if os.path.abspath(path or os.curdir).casefold() != _SCRIPT_DIR_KEY
]

import subprocess  # noqa: E402
from pathlib import Path  # noqa: E402

DEFAULT_PYRIGHT_TIMEOUT_SECONDS = 120
ABRAXAS_FAST_CI_PYRIGHT_SCOPE_FULL = "full"

DEFAULT_FAST_CI_PYRIGHT_TARGETS: tuple[str, ...] = (
    "core/geometric_research_item.py",
    "core/geometric_signal_packet.py",
    "core/metric_operator_registry.py",
    "core/geometric_projection_spec.py",
    "core/yggdrasil_geometric_route_metadata.py",
    "core/oracle_geometric_signal_attachment.py",
    "core/oracle_geometric_attachment_replay_receipt.py",
    "core/oracle_geometric_attachment_stabilization_window.py",
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
    "tests/test_oracle_geometric_attachment_replay_receipt.py",
    "tests/test_oracle_geometric_attachment_stabilization_window.py",
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
    "core/chamfer_expected_distance_value_plan.py",
    "tests/test_chamfer_fixture_files.py",
    "tests/test_chamfer_expected_distance_value_plan.py",
    "tests/test_run_fast_ci.py",
    "core/operator_narrative_report.py",
    "core/operator_narrative_report_governance_audit.py",
    "core/operator_narrative_report_ui_overlay.py",
    "core/operator_narrative_report_ui_overlay_governance_audit.py",
    "core/operator_narrative_export_bundle.py",
    "core/operator_narrative_export_bundle_governance_audit.py",
    "core/operator_narrative_static_preview_bundle.py",
    "core/operator_narrative_static_preview_governance_audit.py",
    "core/operator_narrative_export_preview_archive_index.py",
    "core/operator_narrative_export_preview_archive_index_governance_audit.py",
    "core/operator_narrative_archive_chain_closure_receipt.py",
    "core/operator_narrative_archive_chain_stability_receipt.py",
    "core/operator_narrative_archive_chain_global_verification.py",
    "core/operator_narrative_static_archive_package.py",
    "core/operator_narrative_static_archive_package_governance_audit.py",
    "core/operator_narrative_static_archive_package_language_boundary_audit.py",
    "core/operator_narrative_static_archive_package_preflight_receipt.py",
    "core/operator_narrative_static_archive_package_boundary_receipt.py",
    "core/operator_narrative_static_archive_package_index_pointer_receipt.py",
    "core/operator_narrative_static_archive_package_final_index_receipt.py",
    "core/operator_narrative_static_archive_package_stability_receipt.py",
    "core/operator_narrative_static_archive_package_chain_closure_receipt.py",
    "core/operator_narrative_static_archive_package_completion_seal_receipt.py",
    "tests/test_operator_narrative_report.py",
    "tests/test_operator_narrative_report_governance_audit.py",
    "tests/test_operator_narrative_report_ui_overlay.py",
    "tests/test_operator_narrative_report_ui_overlay_governance_audit.py",
    "tests/test_operator_narrative_export_bundle.py",
    "tests/test_operator_narrative_export_bundle_governance_audit.py",
    "tests/test_operator_narrative_static_preview_bundle.py",
    "tests/test_operator_narrative_static_preview_governance_audit.py",
    "tests/test_operator_narrative_export_preview_archive_index.py",
    "tests/test_operator_narrative_export_preview_archive_index_governance_audit.py",
    "tests/test_operator_narrative_archive_chain_closure_receipt.py",
    "tests/test_operator_narrative_archive_chain_stability_receipt.py",
    "tests/test_operator_narrative_archive_chain_global_verification.py",
    "tests/test_operator_narrative_static_archive_package.py",
    "tests/test_operator_narrative_static_archive_package_governance_audit.py",
    "tests/test_operator_narrative_static_archive_package_language_boundary_audit.py",
    "tests/test_operator_narrative_static_archive_package_preflight_receipt.py",
    "tests/test_operator_narrative_static_archive_package_boundary_receipt.py",
    "tests/test_operator_narrative_static_archive_package_index_pointer_receipt.py",
    "tests/test_operator_narrative_static_archive_package_final_index_receipt.py",
    "tests/test_operator_narrative_static_archive_package_stability_receipt.py",
    "tests/test_operator_narrative_static_archive_package_chain_closure_receipt.py",
    "tests/test_operator_narrative_static_archive_package_completion_seal_receipt.py",
)


COMMANDS: list[list[str]] = [
    ["python", "-m", "scripts.run_artifact_regeneration", "--check-drift"],
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
