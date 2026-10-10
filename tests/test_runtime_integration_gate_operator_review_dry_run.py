from __future__ import annotations

from pathlib import Path

from core.runtime_integration_gate_operator_review_dry_run import (
    build_runtime_integration_gate_operator_review_dry_run,
    write_runtime_integration_gate_operator_review_dry_run,
)
from core.runtime_integration_gate_operator_review_dry_run_review import (
    build_runtime_integration_gate_operator_review_dry_run_review,
    write_runtime_integration_gate_operator_review_dry_run_review,
)

from tests._repo_mirror import make_repo_mirror

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_runtime_integration_gate_operator_review_dry_run_is_advisory_only() -> None:
    packet = build_runtime_integration_gate_operator_review_dry_run(repo_root=REPO_ROOT)
    assert packet["status"] == "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DRY_RUN_READY"
    assert packet["validation_passed"] is True
    assert packet["simulated_only"] is True
    assert packet["operator_attestation_present"] is False
    assert packet["recommended_next_lane"] == "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DRY_RUN_REVIEW"
    assert packet["authority_locks"]["mandatory_pre_dispatch_wiring"] is False
    assert packet["authority_locks"]["valid_for_runtime_wiring"] is False


def test_runtime_integration_gate_operator_review_dry_run_review_held_for_operator(
    tmp_path: Path,
) -> None:
    # The review reads the dry run from the same root it was written to: use a
    # working-tree mirror so the tracked out/ dry run is not rewritten.
    mirror = make_repo_mirror(tmp_path)
    write_runtime_integration_gate_operator_review_dry_run(repo_root=mirror)
    packet = build_runtime_integration_gate_operator_review_dry_run_review(repo_root=mirror)
    assert packet["status"] == "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DRY_RUN_REVIEW_HELD_FOR_OPERATOR"
    assert packet["source_ready"] is True
    assert packet["operator_attestation_present"] is False
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["authority_locks"]["mandatory_pre_dispatch_wiring"] is False


def test_runtime_integration_gate_operator_review_dry_run_review_writer(tmp_path: Path) -> None:
    write_runtime_integration_gate_operator_review_dry_run(REPO_ROOT, out_root=tmp_path)
    packet = write_runtime_integration_gate_operator_review_dry_run_review(
        REPO_ROOT,
        out_root=tmp_path,
    )
    json_path = tmp_path / "out/audit/runtime_integration_gate_operator_review_dry_run_review_001.latest.json"
    assert json_path.exists()
    assert packet["status"] == "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DRY_RUN_REVIEW_HELD_FOR_OPERATOR"
