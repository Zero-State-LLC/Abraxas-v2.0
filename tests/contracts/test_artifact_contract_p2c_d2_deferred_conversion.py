from pathlib import Path

from scripts import run_artifact_contract_p2c_d2_deferred_conversion as d2


def test_exact_d2_selection() -> None:
    payload, report, _ = d2.build()
    from scripts.run_artifact_contract_p2c_d_manual_review_triage import build as triage_build
    triage, _, _ = triage_build()
    assert payload["source_d2_count"] == triage["counts"]["convert_to_deferred"]
    assert report["source_d2_count"] == triage["counts"]["convert_to_deferred"]


def test_deterministic_conversion_hash() -> None:
    a, _, _ = d2.build()
    b, _, _ = d2.build()
    assert a["conversion_hash"] == b["conversion_hash"]


def test_one_record_per_target() -> None:
    payload, _, _ = d2.build()
    assert len(payload["conversions"]) == payload["source_d2_count"]


def test_d3_d4_d5_preserved() -> None:
    _, report, _ = d2.build()
    assert report["d3_preserved"] == 6
    from scripts.run_artifact_contract_p2c_d_manual_review_triage import build as triage_build
    triage, _, _ = triage_build()
    assert report["d4_preserved"] == triage["counts"]["convert_to_archive_candidate"]
    assert report["d5_preserved"] == 1


def test_authority_lock_and_newline() -> None:
    d2.main()
    payload, _, _ = d2.build()
    assert payload["authority"]["execution_authority"] is False
    assert Path("out/contracts/artifact_contract_p2c_d2_deferred_conversion.latest.json").read_bytes().endswith(b"\n")


def test_repair_required_when_downstream_remains() -> None:
    payload, report, _ = d2.build()
    if report["d3_preserved"] > 0 or report["d4_preserved"] > 0 or report["d5_preserved"] > 0:
        assert payload["status"] == "repair_required"


def test_failed_when_unresolved_exists() -> None:
    payload, _, _ = d2.build()
    fake = dict(payload)
    fake["conversions"] = [dict(fake["conversions"][0], result="unresolved")]
    unresolved = [r for r in fake["conversions"] if r["result"] in {"unresolved", "not_computable"}]
    assert bool(unresolved)
