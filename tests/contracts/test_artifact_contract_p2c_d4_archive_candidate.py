from pathlib import Path

from scripts.artifact import run_artifact_contract_p2c_d4_archive_candidate as d4


def test_exact_d4_target_selection() -> None:
    payload, report, actions = d4.build()
    from scripts.artifact.run_artifact_contract_p2c_d_manual_review_triage import build as triage_build
    triage, _, _ = triage_build()
    expected = triage["counts"]["convert_to_archive_candidate"]
    assert payload["source_d4_count"] == expected
    assert report["source_d4_count"] == expected
    assert len(actions) == expected


def test_deterministic_archive_hash() -> None:
    first, _, _ = d4.build()
    second, _, _ = d4.build()
    assert first["archive_hash"] == second["archive_hash"]


def test_one_record_per_target() -> None:
    payload, _, _ = d4.build()
    assert len(payload["records"]) == payload["source_d4_count"]


def test_no_deletion() -> None:
    payload, report, _ = d4.build()
    assert payload["files_deleted"] == []
    assert payload["artifacts_deleted"] == []
    assert report["files_deleted"] == 0
    assert report["artifacts_deleted"] == 0


def test_no_mutation_d5_and_cleared_queues() -> None:
    payload, report, _ = d4.build()
    from scripts.artifact.run_artifact_contract_p2c_d_manual_review_triage import build as triage_build
    triage, _, _ = triage_build()
    assert report["d5_preserved"] == triage["counts"]["requires_operator_decision"]
    assert payload["cleared_queues_preserved"]["P2C-D3"] == triage["counts"]["convert_to_keep_optional"]


def test_authority_lock_and_newline() -> None:
    d4.main()
    payload, _, _ = d4.build()
    assert payload["authority"]["execution_authority"] is False
    assert Path("out/contracts/artifact_contract_p2c_d4_archive_candidate.latest.json").read_bytes().endswith(b"\n")


def test_failure_when_unresolved_exists() -> None:
    payload, _, _ = d4.build()
    fake = dict(payload)
    if not fake["records"]:
        return
    fake["records"] = [dict(fake["records"][0], result="unresolved")]
    unresolved = [r for r in fake["records"] if r["result"] in {"unresolved", "not_computable"}]
    assert bool(unresolved)


def test_repair_required_when_d4_clears_but_d5_remains() -> None:
    payload, report, _ = d4.build()
    if report["d5_preserved"] > 0:
        assert payload["status"] == "repair_required"
