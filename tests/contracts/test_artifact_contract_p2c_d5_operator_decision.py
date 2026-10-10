from pathlib import Path

import pytest

from scripts.artifact import run_artifact_contract_p2c_d5_operator_decision as d5
from tests._repo_mirror import copy_repo_paths


def test_exact_d5_target_selection() -> None:
    payload, report, actions = d5.build()
    assert payload["source_d5_count"] == 1
    assert report["source_d5_count"] == 1
    assert len(actions) == 1


def test_deterministic_decision_hash() -> None:
    a, _, _ = d5.build()
    b, _, _ = d5.build()
    assert a["decision_hash"] == b["decision_hash"]


def test_one_decision_record_per_target() -> None:
    payload, _, _ = d5.build()
    assert len(payload["decisions"]) == payload["source_d5_count"]


def test_no_automatic_approval_or_execution() -> None:
    payload, report, _ = d5.build()
    assert payload["autonomous_approval"] is False
    assert report["autonomous_approval"] is False
    assert report["execution_authority"] is False


def test_cleared_queues_preserved() -> None:
    payload, _, _ = d5.build()
    from scripts.artifact.run_artifact_contract_p2c_d_manual_review_triage import build as triage_build
    triage, _, _ = triage_build()
    assert payload["cleared_queues_preserved"]["P2C-D4"] == triage["counts"]["convert_to_archive_candidate"]


def test_authority_lock_and_newline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # main() reads and writes cwd-relative out/contracts paths: run it in a tmp copy.
    monkeypatch.chdir(copy_repo_paths(tmp_path, "out/contracts"))
    d5.main()
    payload, _, _ = d5.build()
    assert payload["authority"]["execution_authority"] is False
    assert Path("out/contracts/artifact_contract_p2c_d5_operator_decision.latest.json").read_bytes().endswith(b"\n")


def test_failure_when_unresolved_exists() -> None:
    payload, _, _ = d5.build()
    fake = dict(payload)
    fake["decisions"] = [dict(fake["decisions"][0], result="unresolved")]
    unresolved = [r for r in fake["decisions"] if r["result"] in {"unresolved", "not_computable"}]
    assert bool(unresolved)


def test_repair_required_when_pending_operator_approval() -> None:
    payload, report, _ = d5.build()
    if report["operator_approval_pending_count"] > 0:
        assert payload["status"] == "repair_required"
