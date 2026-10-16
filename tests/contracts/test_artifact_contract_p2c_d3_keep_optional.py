from pathlib import Path

import pytest

from scripts.artifact import run_artifact_contract_p2c_d3_keep_optional as d3
from tests._repo_mirror import copy_repo_paths


def test_exact_d3_target_selection() -> None:
    payload, report, _ = d3.build()
    from scripts.artifact.run_artifact_contract_p2c_d_manual_review_triage import build as triage_build
    triage, _, _ = triage_build()
    expected = triage["counts"]["convert_to_keep_optional"]
    assert payload["source_d3_count"] == expected
    assert report["source_d3_count"] == expected


def test_deterministic_keep_hash() -> None:
    first, _, _ = d3.build()
    second, _, _ = d3.build()
    assert first["keep_hash"] == second["keep_hash"]


def test_one_keep_record_per_target() -> None:
    payload, _, _ = d3.build()
    assert len(payload["keeps"]) == payload["source_d3_count"]


def test_no_mutation_d4_d5() -> None:
    _, report, _ = d3.build()
    from scripts.artifact.run_artifact_contract_p2c_d_manual_review_triage import build as triage_build
    triage, _, _ = triage_build()
    assert report["d4_preserved"] == triage["counts"]["convert_to_archive_candidate"]
    assert report["d5_preserved"] == 1


def test_no_mutation_cleared_queues() -> None:
    payload, _, _ = d3.build()
    assert payload["cleared_queues_preserved"]["P1A"] == 0
    assert payload["cleared_queues_preserved"]["P2C-D1"] == 5
    from scripts.artifact.run_artifact_contract_p2c_d_manual_review_triage import build as triage_build
    triage, _, _ = triage_build()
    assert payload["cleared_queues_preserved"]["P2C-D2"] == triage["counts"]["convert_to_deferred"]


def test_authority_and_newline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # main() reads and writes cwd-relative out/contracts paths: run it in a tmp copy.
    monkeypatch.chdir(copy_repo_paths(tmp_path, "out/contracts"))
    d3.main()
    payload, _, _ = d3.build()
    assert payload["authority"]["execution_authority"] is False
    assert Path("out/contracts/artifact_contract_p2c_d3_keep_optional.latest.json").read_bytes().endswith(b"\n")


def test_failure_when_unresolved_exists() -> None:
    payload, _, _ = d3.build()
    fake = dict(payload)
    fake["keeps"] = [dict(fake["keeps"][0], result="unresolved")]
    unresolved = [r for r in fake["keeps"] if r["result"] in {"unresolved", "not_computable"}]
    assert bool(unresolved)


def test_repair_required_when_d3_clears_but_downstream_remains() -> None:
    payload, report, _ = d3.build()
    if report["d4_preserved"] > 0 or report["d5_preserved"] > 0:
        assert payload["status"] == "repair_required"
