from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_phase1_operator_review_request import (
    build_abx_codegen_phase1_operator_review_request,
    render_abx_codegen_phase1_operator_review_request_markdown,
    write_abx_codegen_phase1_operator_review_request,
)
from scripts.codegen import run_abx_codegen_phase1_operator_review_request

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_codegen_phase1_review_request_is_held() -> None:
    first = build_abx_codegen_phase1_operator_review_request(REPO_ROOT)
    second = build_abx_codegen_phase1_operator_review_request(REPO_ROOT)

    assert first["request_hash"] == second["request_hash"]
    assert first["status"] == "ABX_CODEGEN_PHASE1_OPERATOR_REVIEW_REQUEST_HELD"
    assert first["decision_scope"] == "PHASE1_CODEGEN_IMPLEMENTATION_REVIEW_REQUIRED"
    assert first["evidence_packet_ready_for_review"] is True
    assert first["recommended_decision"] == "HOLD_FOR_OPERATOR_REVIEW"
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_codegen_phase1_review_request_denies_authority() -> None:
    packet = build_abx_codegen_phase1_operator_review_request(REPO_ROOT)

    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["safe_to_auto_continue"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert "CODEGEN_PHASE1_IMPLEMENTATION" in packet["blocked_actions"]
    assert "AUTHORIZATION_RECORD_CREATION" in packet["blocked_actions"]


def test_codegen_phase1_review_request_carries_review_items() -> None:
    packet = build_abx_codegen_phase1_operator_review_request(REPO_ROOT)

    assert "HOLD_FOR_OPERATOR_REVIEW" in packet["decision_options"]
    assert "APPROVE_PHASE1_IMPLEMENTATION_REVIEW_ONLY" in packet["decision_options"]
    assert any("separate authorization-record lane" in item for item in packet["required_operator_review_items"])
    assert any("no shadow replay execution" in item for item in packet["required_operator_review_items"])


def test_codegen_phase1_review_request_writer_schema_and_markdown(tmp_path: Path) -> None:
    packet = write_abx_codegen_phase1_operator_review_request(REPO_ROOT, out_root=tmp_path)
    json_path = tmp_path / "out/operator_review/abx_codegen_phase1_operator_review_request_001.latest.json"
    md_path = tmp_path / "out/operator_review/abx_codegen_phase1_operator_review_request_001.latest.md"

    assert json_path.exists()
    assert md_path.exists()
    runner_packet = run_abx_codegen_phase1_operator_review_request.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )
    assert runner_packet["request_hash"] == packet["request_hash"]

    schema = json.loads(
        (REPO_ROOT / "contracts/operator_review/abx_codegen_phase1_operator_review_request.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    validate(packet, schema)
    markdown = render_abx_codegen_phase1_operator_review_request_markdown(packet)
    assert markdown[0] == "# ABX Codegen Phase 1 Operator Review Request"
    assert any("HOLD_FOR_OPERATOR_REVIEW" in line for line in markdown)
