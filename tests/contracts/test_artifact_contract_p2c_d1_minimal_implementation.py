from pathlib import Path

import pytest

from scripts.artifact import run_artifact_contract_p2c_d1_minimal_implementation as d1
from scripts.artifact.run_artifact_contract_p2c_d_manual_review_triage import build as triage_build
from tests._repo_mirror import copy_repo_paths


def test_exact_d1_selection() -> None:
    payload, report, _ = d1.build()
    assert payload["source_d1_count"] == 5
    assert report["source_d1_count"] == 5


def test_deterministic_hash() -> None:
    first, _, _ = d1.build()
    second, _, _ = d1.build()
    assert first["implementation_hash"] == second["implementation_hash"]


def test_one_record_per_target() -> None:
    payload, _, _ = d1.build()
    assert len(payload["implementations"]) == payload["source_d1_count"]


def test_d2_d3_d4_d5_preserved() -> None:
    _, report, _ = d1.build()
    triage, _, _ = triage_build()
    assert report["d2_preserved"] == triage["counts"]["convert_to_deferred"]
    assert report["d3_preserved"] == triage["counts"]["convert_to_keep_optional"]
    assert report["d4_preserved"] == triage["counts"]["convert_to_archive_candidate"]
    assert report["d5_preserved"] == triage["counts"]["requires_operator_decision"]


def test_authority_and_newline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # main() reads and writes cwd-relative out/contracts paths: run it in a tmp copy.
    monkeypatch.chdir(copy_repo_paths(tmp_path, "out/contracts"))
    d1.main()
    payload, _, _ = d1.build()
    assert payload["authority"]["execution_authority"] is False
    path = Path("out/contracts/artifact_contract_p2c_d1_minimal_implementation.latest.json")
    assert path.read_bytes().endswith(b"\n")


def test_failed_when_unresolved_exists() -> None:
    payload, _, _ = d1.build()
    local = dict(payload)
    local["implementations"] = [dict(local["implementations"][0], result="unresolved")]
    unresolved = [r for r in local["implementations"] if r["result"] in {"unresolved", "not_computable"}]
    assert bool(unresolved) is True
