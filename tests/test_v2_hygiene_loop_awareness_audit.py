from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.v2_hygiene_loop_awareness_audit import (
    build_v2_hygiene_loop_awareness_audit,
    render_v2_hygiene_loop_awareness_audit_markdown,
)
from scripts.hygiene import run_v2_hygiene_loop_awareness_audit

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/v2_hygiene_loop_awareness_audit.v1.schema.json"


def _result_by_id(packet: dict, check_id: str) -> dict:
    return {item["check_id"]: item for item in packet["check_results"]}[check_id]


def test_v2_hygiene_audit_is_advisory_and_ready() -> None:
    packet = build_v2_hygiene_loop_awareness_audit(REPO_ROOT)

    assert packet["artifact_type"] == "V2HygieneLoopAwarenessAudit.v1"
    assert packet["audit_status"] == "V2_HYGIENE_LOOP_AWARENESS_AUDIT_READY"
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False
    assert packet["safe_to_prepare_patch"] is False
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["evidence_only"] is True
    assert packet["valid_for_execution"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_v2_hygiene_audit_records_loop_hygiene_evidence() -> None:
    packet = build_v2_hygiene_loop_awareness_audit(REPO_ROOT)

    assert packet["missing_checks"] == []
    assert packet["partial_checks"] == []
    loop_check = _result_by_id(packet, "loop_dynamics_assessment_present")
    rune_check = _result_by_id(packet, "v2_runes_documented")

    assert loop_check["status"] == "PASSED"
    assert rune_check["status"] == "PASSED"
    assert packet["observed_evidence_paths"]


def test_v2_hygiene_audit_fails_closed_without_sources(tmp_path: Path) -> None:
    packet = build_v2_hygiene_loop_awareness_audit(tmp_path)

    assert packet["audit_status"] == "NOT_COMPUTABLE"
    assert packet["observed_evidence_paths"] == []
    assert set(packet["missing_evidence_paths"]) == set(packet["evidence_paths"])
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["safe_to_prepare_patch"] is False
    assert packet["valid_for_execution"] is False


def test_v2_hygiene_audit_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_loop_awareness_audit(REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("audit_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_audit_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = tmp_path / "out/sync/v2_hygiene_loop_awareness_audit/latest.json"
    out_md = tmp_path / "out/sync/v2_hygiene_loop_awareness_audit/latest.md"

    first = run_v2_hygiene_loop_awareness_audit.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_loop_awareness_audit.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_audit_markdown_names_missing_checks() -> None:
    packet = build_v2_hygiene_loop_awareness_audit(REPO_ROOT)
    markdown = render_v2_hygiene_loop_awareness_audit_markdown(packet)

    assert markdown[0] == "# v2.0 Hygiene Loop-Awareness Audit"
    assert any("loop_dynamics_assessment_present" in line for line in markdown)
    assert any("safe_to_auto_continue" in line for line in markdown)
