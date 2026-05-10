import hashlib
import json
from pathlib import Path

from core.audit.runtime_spine_audit import (
    REQUIRED_ARTIFACTS,
    build_runtime_spine_audit_report,
    write_runtime_spine_audit_artifact,
)


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")


def _valid_payload(status: str = "PASS") -> dict:
    return {"status": status, "receipt_hash": "abc"}


def _make_all(base: Path, status: str = "PASS") -> None:
    for rel in REQUIRED_ARTIFACTS:
        _write(base / rel, _valid_payload(status))


def test_full_fixture_set_deterministic_pass_or_warn_report(tmp_path: Path) -> None:
    _make_all(tmp_path, "PASS")
    report = build_runtime_spine_audit_report(tmp_path)
    assert report.summary.posture in {"PASS", "WARN"}


def test_missing_artifact_not_computable(tmp_path: Path) -> None:
    _make_all(tmp_path, "PASS")
    (tmp_path / REQUIRED_ARTIFACTS[0]).unlink()
    report = build_runtime_spine_audit_report(tmp_path)
    assert report.summary.posture == "NOT_COMPUTABLE"


def test_malformed_artifact_not_computable(tmp_path: Path) -> None:
    _make_all(tmp_path, "PASS")
    malformed = tmp_path / REQUIRED_ARTIFACTS[0]
    malformed.write_text("{bad json\n", encoding="utf-8")
    report = build_runtime_spine_audit_report(tmp_path)
    assert report.summary.posture == "NOT_COMPUTABLE"


def test_blocked_artifact_blocks_chain(tmp_path: Path) -> None:
    _make_all(tmp_path, "PASS")
    _write(tmp_path / REQUIRED_ARTIFACTS[2], _valid_payload("BLOCKED"))
    report = build_runtime_spine_audit_report(tmp_path)
    assert report.summary.posture == "BLOCKED"


def test_artifact_refs_sorted_deterministically(tmp_path: Path) -> None:
    _make_all(tmp_path, "PASS")
    report = build_runtime_spine_audit_report(tmp_path)
    assert [r.path for r in report.artifact_refs] == sorted(REQUIRED_ARTIFACTS)


def test_repeated_generation_identical_chain_hash(tmp_path: Path) -> None:
    _make_all(tmp_path, "PASS")
    r1 = build_runtime_spine_audit_report(tmp_path)
    r2 = build_runtime_spine_audit_report(tmp_path)
    assert r1.chain_hash == r2.chain_hash


def test_written_artifact_newline_and_stable_sha256(tmp_path: Path) -> None:
    _make_all(tmp_path, "PASS")
    first_hash = write_runtime_spine_audit_artifact(tmp_path)
    out_file = tmp_path / "out/audit/runtime_spine_audit.latest.json"
    text_one = out_file.read_text(encoding="utf-8")
    second_hash = write_runtime_spine_audit_artifact(tmp_path)
    text_two = out_file.read_text(encoding="utf-8")
    assert text_one.endswith("\n")
    assert text_one == text_two
    assert first_hash == second_hash
    assert hashlib.sha256(text_one.encode("utf-8")).hexdigest() == hashlib.sha256(text_two.encode("utf-8")).hexdigest()


def test_aggregator_uses_normalized_runtime_posture(tmp_path: Path) -> None:
    _make_all(tmp_path, "PASS")
    _write(tmp_path / REQUIRED_ARTIFACTS[1], {"runtime_posture": "WARN"})
    report = build_runtime_spine_audit_report(tmp_path)
    assert report.summary.posture == "WARN"
