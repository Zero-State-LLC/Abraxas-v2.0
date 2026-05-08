from pathlib import Path

from scripts import run_artifact_contract_p2c_d_manual_review_triage as triage


def test_selection_exact_batch() -> None:
    payload, report, _ = triage.build()
    assert payload["source_p2c_d_count"] == report["source_p2c_d_count"]


def test_classified_once() -> None:
    payload, _, _ = triage.build()
    assert payload["source_p2c_d_count"] == len(payload["items"])


def test_hash_deterministic() -> None:
    first, _, _ = triage.build()
    second, _, _ = triage.build()
    assert first["triage_hash"] == second["triage_hash"]


def test_p2c_e_untouched() -> None:
    payload, report, _ = triage.build()
    assert payload["preservation"]["p2c_e_untouched"] is True
    assert report["p2c_e_count"] == 2


def test_authority_locked_and_newline() -> None:
    triage.main()
    artifact = Path("out/contracts/artifact_contract_p2c_d_manual_review_triage.latest.json")
    payload, _, _ = triage.build()
    assert payload["authority"]["execution_authority"] is False
    assert artifact.read_bytes().endswith(b"\n")
