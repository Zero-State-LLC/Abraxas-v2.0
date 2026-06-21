from __future__ import annotations

from pathlib import Path

from core.canonical.json import canonical_hash

from core.codegen.fixture_validation import (
    validate_shadow_replay_fixture,
    validate_shadow_replay_fixtures,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = (
    "tests/fixtures/codegen/shadow_replay_fixture_golden.v1.json",
    "tests/fixtures/codegen/shadow_replay_fixture_meta_gate.v1.json",
)


def test_validate_shadow_replay_fixture_matches_expected_recommendation() -> None:
    receipt = validate_shadow_replay_fixture(FIXTURES[0], repo_root=REPO_ROOT)

    assert receipt["status"] == "FIXTURE_VALIDATION_PASSED"
    assert receipt["expected_recommendation"] == "HOLD_FOR_OPERATOR"
    assert receipt["observed_recommendation"] == "HOLD_FOR_OPERATOR"
    assert receipt["execution_authority"] is False
    assert receipt["canonical_hash"] == canonical_hash(
        {key: value for key, value in receipt.items() if key != "canonical_hash"}
    )


def test_validate_meta_gate_fixture_uses_24_run_constraint() -> None:
    receipt = validate_shadow_replay_fixture(FIXTURES[1], repo_root=REPO_ROOT)

    assert receipt["status"] == "FIXTURE_VALIDATION_PASSED"
    assert receipt["expected_recommendation"] == "HOLD_FOR_META_GATE"
    assert receipt["run_count"] == 24
    assert receipt["constraints"]["no_network"] is True
    assert receipt["constraints"]["no_file_write"] is True


def test_validate_shadow_replay_fixtures_emits_summary() -> None:
    summary = validate_shadow_replay_fixtures(FIXTURES, repo_root=REPO_ROOT)

    assert summary["status"] == "FIXTURE_VALIDATION_SUMMARY_PASSED"
    assert summary["fixture_count"] == 2
    assert summary["passed_count"] == 2
    assert summary["failed_count"] == 0
    assert summary["shadow_replay_only"] is True
    assert summary["execution_authority"] is False
