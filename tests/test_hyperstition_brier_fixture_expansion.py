from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import canonical_hash
from core.hyperstition_brier_fixture_expansion import (
    BRIER_SCORE,
    DEFAULT_OUT_PATH,
    STATUS,
    build_hyperstition_brier_fixture_expansion_receipt,
)
from scripts.belief.run_hyperstition_brier_fixture_expansion_receipt import run


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_hyperstition_brier_receipt_preserves_authority_locks() -> None:
    packet = build_hyperstition_brier_fixture_expansion_receipt(
        repo_root=REPO_ROOT
    )

    assert packet["status"] == STATUS
    assert packet["brier_score"] == BRIER_SCORE
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["sandbox_gate_issued"] is False
    assert packet["boundary"]["brier_resolution"] is False
    assert packet["boundary"]["forecast_execution"] is False


def test_hyperstition_brier_receipt_hash_is_canonical() -> None:
    packet = build_hyperstition_brier_fixture_expansion_receipt(
        repo_root=REPO_ROOT
    )
    without_hash = {
        key: value for key, value in packet.items() if key != "canonical_hash"
    }

    assert packet["canonical_hash"] == canonical_hash(without_hash)


def test_hyperstition_brier_fixture_suite_is_bounded_and_advisory() -> None:
    packet = build_hyperstition_brier_fixture_expansion_receipt(
        repo_root=REPO_ROOT
    )
    loop_dynamics = packet["loop_dynamics"]
    fixture_suite = packet["brier_fixture_suite"]

    assert 0.0 <= loop_dynamics["hyperstitional_charge"] <= 1.0
    assert 0.0 <= loop_dynamics["retrocausal_risk"] <= 1.0
    assert fixture_suite["fixture_count"] == 4
    assert 0.0 <= fixture_suite["mean_shadow_brier"] <= 1.0
    assert fixture_suite["resolution_allowed"] is False
    assert fixture_suite["outcome_binding_allowed"] is False
    assert fixture_suite["forecast_execution_allowed"] is False
    for row in fixture_suite["fixture_rows"]:
        assert 0.0 <= row["probability"] <= 1.0
        assert 0.0 <= row["shadow_brier_component"] <= 1.0
        assert row["brier_resolution_allowed"] is False


def test_hyperstition_tag_rune_evidence_is_repo_real() -> None:
    packet = build_hyperstition_brier_fixture_expansion_receipt(
        repo_root=REPO_ROOT
    )
    evidence = packet["hyperstition_rune_evidence"]

    assert evidence["rune_id"] == "RUNE.HYPERSTITION_TAG"
    assert evidence["advisory_tag_applied"] is True
    assert evidence["strict_requires_tag"] is True
    assert evidence["execution_authority"] is False


def test_hyperstition_brier_missing_sources_fail_closed(tmp_path: Path) -> None:
    packet = build_hyperstition_brier_fixture_expansion_receipt(
        repo_root=tmp_path
    )

    assert packet["source_status"] == "NOT_COMPUTABLE"
    assert packet["source_observation_ratio"] == 0.0
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["canonical_hash"] == canonical_hash(
        {key: value for key, value in packet.items() if key != "canonical_hash"}
    )


def test_hyperstition_brier_runner_writes_receipt(tmp_path: Path) -> None:
    out_path = tmp_path / "receipt.latest.json"
    packet = run(repo_root=REPO_ROOT, out_path=out_path)
    written = json.loads(out_path.read_text(encoding="utf-8"))

    assert out_path.exists()
    assert written == packet
    assert written["status"] == STATUS
    assert written["canonical_hash"] == packet["canonical_hash"]
    assert DEFAULT_OUT_PATH.endswith(".latest.json")
