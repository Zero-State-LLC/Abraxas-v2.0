from pathlib import Path

import pytest

from scripts.artifact import run_artifact_contract_p2c_d_manual_review_triage as triage


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


def test_authority_locked_and_newline(tmp_path: Path) -> None:
    canonical = triage.DEFAULT_OUTPUT_ROOT / "artifact_contract_p2c_d_manual_review_triage.latest.json"
    canonical_before = canonical.read_bytes()

    triage.main(tmp_path)
    artifact = tmp_path / "artifact_contract_p2c_d_manual_review_triage.latest.json"
    payload, _, _ = triage.build()
    assert payload["authority"]["execution_authority"] is False
    assert artifact.read_bytes().endswith(b"\n")
    assert canonical.read_bytes() == canonical_before

    first = artifact.read_bytes()
    triage.main(tmp_path)
    assert artifact.read_bytes() == first


def test_default_output_root_and_failure_preserve_canonical_files(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert triage.DEFAULT_OUTPUT_ROOT == Path("out/contracts")
    canonical = {
        path: path.read_bytes()
        for path in triage.DEFAULT_OUTPUT_ROOT.glob(
            "artifact_contract_p2c_d_manual_review_triage*.latest.json"
        )
    }

    def fail_build() -> tuple[dict, dict, list[dict]]:
        raise RuntimeError("controlled build failure")

    monkeypatch.setattr(triage, "build", fail_build)
    with pytest.raises(RuntimeError, match="controlled build failure"):
        triage.main()

    assert {path: path.read_bytes() for path in canonical} == canonical
