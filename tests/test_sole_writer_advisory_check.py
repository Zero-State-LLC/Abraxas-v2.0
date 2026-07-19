"""Tests for WS1.7 sole-writer advisory check."""

from __future__ import annotations

from pathlib import Path

from core.production_readiness.sole_writer_check import (
    build_sole_writer_report,
    is_authorized_writer,
    scan_file,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_authorized_run_scripts() -> None:
    assert is_authorized_writer("scripts/run_fast_ci.py")
    assert is_authorized_writer("core/canonical/json.py")
    assert not is_authorized_writer("core/some_module.py")


def test_tests_directory_not_scanned_as_findings() -> None:
    report = build_sole_writer_report(REPO_ROOT, write=False)
    for finding in report["findings"]:
        assert not finding["path"].startswith("tests/")
    assert "tests" not in report.get("by_package", {})


def test_report_shape_and_noise_reduction() -> None:
    report = build_sole_writer_report(REPO_ROOT, write=False)
    assert report["schema_version"] == "sole_writer_advisory_report.v1"
    assert report["always_exit_zero"] is True
    # Original naive heuristic reported 1400+; hardened heuristic must be far lower.
    assert report["finding_count"] < 500
    assert report["policy"]["fail_closed_ready"] is False


def test_scan_file_requires_write_and_out(tmp_path: Path) -> None:
    repo = tmp_path
    mod = repo / "core"
    mod.mkdir()
    # read-only out path — should not flag
    p1 = mod / "reader.py"
    p1.write_text('data = Path("out/audit/x.json").read_text()\n', encoding="utf-8")
    assert scan_file(repo, p1) == []
    # write with out path — should flag
    p2 = mod / "writer.py"
    p2.write_text(
        'Path("out/audit/x.json").write_text("{}", encoding="utf-8")\n',
        encoding="utf-8",
    )
    findings = scan_file(repo, p2)
    assert len(findings) == 1
    assert findings[0].kind == "potential_out_write"
