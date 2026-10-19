from pathlib import Path

import pytest

from scripts.artifact import run_artifact_contract_p0_repair_report as repair
from tests._repo_mirror import copy_repo_paths


def test_repair_hash_deterministic() -> None:
    one, _, _ = repair.build_p0_repair_payload()
    two, _, _ = repair.build_p0_repair_payload()
    assert one["repair_hash"] == two["repair_hash"]


def test_p0_count_derives_from_triage_output() -> None:
    payload, _, _ = repair.build_p0_repair_payload()
    calc = sum(1 for r in payload["repairs"])
    assert payload["p0_source_count"] == calc


def test_authority_fields_locked() -> None:
    payload, _, _ = repair.build_p0_repair_payload()
    assert payload["authority"]["projection_only"] is True
    assert payload["authority"]["inference_authority"] is False
    assert payload["authority"]["mutation_authority"] is False
    assert payload["authority"]["execution_authority"] is False


def test_json_newline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # main() reads and writes cwd-relative out/contracts paths: run it in a tmp copy.
    monkeypatch.chdir(copy_repo_paths(tmp_path, "out/contracts"))
    repair.main()
    assert Path("out/contracts/artifact_contract_p0_repair.latest.json").read_bytes().endswith(b"\n")


def test_status_repair_required_when_p1_or_p2_remain() -> None:
    payload, report, _ = repair.build_p0_repair_payload()
    if report["p1_remaining"] > 0 or report["p2_remaining"] > 0:
        assert payload["status"] == "repair_required"


def test_no_p0_defects_silently_dropped() -> None:
    payload, _, _ = repair.build_p0_repair_payload()
    for repair_row in payload["repairs"]:
        assert repair_row["result"] in {"repaired", "reclassified", "deferred", "not_computable"}
        assert repair_row["evidence"]
