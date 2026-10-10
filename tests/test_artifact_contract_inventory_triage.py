from pathlib import Path

import pytest

from scripts.artifact import run_artifact_contract_inventory_triage as triage
from tests._repo_mirror import copy_repo_paths


def test_deterministic_triage_hash_across_runs() -> None:
    first, _, _ = triage.build_triage_payload()
    second, _, _ = triage.build_triage_payload()
    assert first["triage_hash"] == second["triage_hash"]


def test_every_source_gap_gets_exactly_one_classification() -> None:
    payload, _, _ = triage.build_triage_payload()
    assert payload["source_gap_count"] == len(payload["classifications"])


def test_status_failed_with_p0_true_defect() -> None:
    counts = {
        "p0": 1,
        "true_defects": 1,
        "naming_normalization_issues": 0,
        "audit_engine_rule_too_strict": 0,
        "legacy_exceptions": 0,
        "false_positives": 0,
        "deferred_scope": 0,
    }
    assert triage._status_from_counts(counts) == "failed"


def test_status_repair_required_with_naming_issue() -> None:
    counts = {
        "p0": 0,
        "true_defects": 0,
        "naming_normalization_issues": 1,
        "audit_engine_rule_too_strict": 0,
        "legacy_exceptions": 0,
        "false_positives": 0,
        "deferred_scope": 0,
    }
    assert triage._status_from_counts(counts) == "repair_required"


def test_passed_with_documented_exceptions_only() -> None:
    counts = {
        "p0": 0,
        "true_defects": 0,
        "naming_normalization_issues": 0,
        "audit_engine_rule_too_strict": 0,
        "legacy_exceptions": 1,
        "false_positives": 0,
        "deferred_scope": 1,
    }
    assert triage._status_from_counts(counts) == "passed_with_documented_exceptions"


def test_authority_fields_locked() -> None:
    payload, _, _ = triage.build_triage_payload()
    assert payload["authority"]["projection_only"] is True
    assert payload["authority"]["inference_authority"] is False
    assert payload["authority"]["mutation_authority"] is False
    assert payload["authority"]["execution_authority"] is False


def test_canonical_json_newline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # main() reads and writes cwd-relative out/contracts paths: run it in a tmp copy.
    monkeypatch.chdir(copy_repo_paths(tmp_path, "out/contracts"))
    triage.main()
    out = Path("out/contracts/artifact_contract_inventory_triage.latest.json")
    assert out.read_bytes().endswith(b"\n")
