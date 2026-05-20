from __future__ import annotations

import json
from pathlib import Path
from shutil import copy2

from core.operator_narrative_static_archive_package_completion_seal_receipt import (
    PATCH_ID,
    RECEIPT_ID,
    SCHEMA_VERSION,
    build_operator_narrative_static_archive_package_completion_seal_receipt_packet,
    write_operator_narrative_static_archive_package_completion_seal_receipt,
)


def test_current_baseline_degraded() -> None:
    p = build_operator_narrative_static_archive_package_completion_seal_receipt_packet()
    assert p["final_status"] == "STATIC_ARCHIVE_PACKAGE_COMPLETION_SEAL_DEGRADED"
    assert p["completion_posture"] == "STATIC_ARCHIVE_PACKAGE_COMPLETION_SEALED_WITH_OBSERVED_BLOCKERS"


def test_not_computable_without_p71_doc(tmp_path: Path) -> None:
    (tmp_path / "out").mkdir()
    p = build_operator_narrative_static_archive_package_completion_seal_receipt_packet(repo_root=tmp_path)
    assert p["final_status"] == "NOT_COMPUTABLE"


def test_hash_repeatable() -> None:
    a = build_operator_narrative_static_archive_package_completion_seal_receipt_packet()
    b = build_operator_narrative_static_archive_package_completion_seal_receipt_packet()
    assert a["completion_hash"] == b["completion_hash"]


def test_markdown_newline(tmp_path: Path) -> None:
    p = build_operator_narrative_static_archive_package_completion_seal_receipt_packet()
    out = tmp_path / "p72.json"
    write_operator_narrative_static_archive_package_completion_seal_receipt(out, p)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")


def test_schema_constants() -> None:
    s = json.loads(Path("contracts/operator_attention/operator_narrative_static_archive_package_completion_seal_receipt.v1.schema.json").read_text(encoding="utf-8"))
    assert s["properties"]["schema_version"]["const"] == SCHEMA_VERSION
    assert s["properties"]["patch_id"]["const"] == PATCH_ID
    assert s["properties"]["receipt_id"]["const"] == RECEIPT_ID


def _copy_p64_to_p68_json(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    out_dir = tmp_path / "out"
    (out_dir / "package").mkdir(parents=True)
    (out_dir / "audit").mkdir(parents=True)
    copy2(
        repo_root / "out/package/operator_narrative_static_archive_package_001.latest.json",
        out_dir / "package/operator_narrative_static_archive_package_001.latest.json",
    )
    for name in (
        "operator_narrative_static_archive_package_governance_audit_001.latest.json",
        "operator_narrative_static_archive_package_language_boundary_audit_001.latest.json",
        "operator_narrative_static_archive_package_stability_receipt_001.latest.json",
        "operator_narrative_static_archive_package_chain_closure_receipt_001.latest.json",
    ):
        copy2(repo_root / f"out/audit/{name}", out_dir / f"audit/{name}")


def _write_p71_doc(tmp_path: Path) -> None:
    p71 = tmp_path / "docs/plans/P71_planning_gate_static_archive_package_completion_seal.md"
    p71.parent.mkdir(parents=True, exist_ok=True)
    p71.write_text("P71_PLAN_READY\nP71_COMPLETION_SEAL_PLANNING_REQUIRED\n", encoding="utf-8")


def test_fallback_hydrates_missing_p69_and_p70(tmp_path: Path) -> None:
    _copy_p64_to_p68_json(tmp_path)
    _write_p71_doc(tmp_path)
    packet = build_operator_narrative_static_archive_package_completion_seal_receipt_packet(repo_root=tmp_path)
    assert packet["package_chain_status_summary"]["P69"] != "NOT_COMPUTABLE"
    assert packet["package_chain_status_summary"]["P70"] != "NOT_COMPUTABLE"
    assert packet["source_hashes"]["P69"] != "NOT_COMPUTABLE"
    assert packet["source_hashes"]["P70"] != "NOT_COMPUTABLE"
    assert "P69 missing/corrupt" not in packet["blocker_summary"]
    assert "P70 missing/corrupt" not in packet["blocker_summary"]


def test_fallback_p69_and_p70_fail_closed_without_prerequisites(tmp_path: Path) -> None:
    _write_p71_doc(tmp_path)
    packet = build_operator_narrative_static_archive_package_completion_seal_receipt_packet(repo_root=tmp_path)
    assert packet["final_status"] == "NOT_COMPUTABLE"
    assert "P69 missing/corrupt" in packet["blocker_summary"]
    assert "P70 missing/corrupt" in packet["blocker_summary"]
