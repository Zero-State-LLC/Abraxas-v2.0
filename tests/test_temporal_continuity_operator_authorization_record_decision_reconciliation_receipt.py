from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from core.canonical.json import canonical_dumps
from core.temporal_continuity_operator_authorization_record_decision_reconciliation_receipt import (
    EXPECTED_HANDOFF,
    EXPECTED_NOTION_ROUTE,
    EXPECTED_TERMINAL_LANE,
    NOTION_DIFF_PATH,
    SOURCE_P102E_RECORD_PLAN_PATH,
    build_temporal_continuity_operator_authorization_record_decision_reconciliation_receipt,
    write_temporal_continuity_operator_authorization_record_decision_reconciliation_receipt,
)
from scripts import run_temporal_continuity_operator_authorization_record_decision_reconciliation_receipt

OUT_PATH = "out/temporal_continuity_operator_authorization_record_decision_reconciliation_receipt/latest.json"
SCHEMA_PATH = "contracts/canon/temporal_continuity_operator_authorization_record_decision_reconciliation_receipt.v1.schema.json"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_dumps(payload) + "\n", encoding="utf-8")


def _seed_p102e(root: Path, *, handoff: str = EXPECTED_HANDOFF) -> None:
    _write_json(
        root / SOURCE_P102E_RECORD_PLAN_PATH,
        {
            "artifact_type": "TemporalContinuitySelectedRepairExecutionAuthorizationRecordPlan.v1",
            "canonical_status": "ADVISORY_ONLY",
            "audit_only": True,
            "projection_only": True,
            "terminal_lane": EXPECTED_TERMINAL_LANE,
            "p102e_record_plan_status": "SELECTED_REPAIR_EXECUTION_AUTHORIZATION_RECORD_PLAN_READY",
            "authorization_record_required": True,
            "authorization_record_created": False,
            "authorization_granted": False,
            "valid_for_execution": False,
            "recommended_next_lane": handoff,
            "packet_hash": "f" * 64,
        },
    )


def _seed_notion_diff(root: Path, *, documented: bool = False) -> None:
    text = "repo notion diff\n"
    if documented:
        text += f"expected route: {EXPECTED_NOTION_ROUTE}\n"
    target = root / NOTION_DIFF_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def test_missing_p102e_fails_closed_not_computable(tmp_path: Path) -> None:
    _seed_notion_diff(tmp_path)
    packet = build_temporal_continuity_operator_authorization_record_decision_reconciliation_receipt(
        repo_root=tmp_path
    )
    assert packet["operator_decision_reconciliation_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert SOURCE_P102E_RECORD_PLAN_PATH in packet["missing_evidence"]
    assert packet["valid_for_execution"] is False


def test_p102e_handoff_blocks_on_missing_operator_decision_evidence(tmp_path: Path) -> None:
    _seed_p102e(tmp_path)
    _seed_notion_diff(tmp_path)
    packet = build_temporal_continuity_operator_authorization_record_decision_reconciliation_receipt(
        repo_root=tmp_path
    )
    assert (
        packet["operator_decision_reconciliation_status"]
        == "OPERATOR_AUTHORIZATION_RECORD_DECISION_RECONCILIATION_BLOCKED"
    )
    assert packet["observed_terminal_lane"] == EXPECTED_TERMINAL_LANE
    assert packet["handoff"] == EXPECTED_HANDOFF
    assert packet["missing_operator_decision_evidence"] == [
        "operator_authorization_record_decision_evidence"
    ]
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["recommended_human_operator_decision"] == "CREATE_OPERATOR_AUTHORIZATION_RECORD_DECISION_OR_HOLD"


def test_documented_notion_route_is_observed_without_authorizing_p103(tmp_path: Path) -> None:
    _seed_p102e(tmp_path)
    _seed_notion_diff(tmp_path, documented=True)
    packet = build_temporal_continuity_operator_authorization_record_decision_reconciliation_receipt(
        repo_root=tmp_path
    )
    assert packet["notion_expected_simulated_route_documented"] is True
    assert packet["notion_expected_simulated_route"] == EXPECTED_NOTION_ROUTE
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_undocumented_notion_route_is_not_fabricated(tmp_path: Path) -> None:
    _seed_p102e(tmp_path)
    _seed_notion_diff(tmp_path, documented=False)
    packet = build_temporal_continuity_operator_authorization_record_decision_reconciliation_receipt(
        repo_root=tmp_path
    )
    assert packet["notion_expected_simulated_route_documented"] is False
    assert packet["notion_expected_simulated_route"] == "NOT_DOCUMENTED_IN_REPO"


def test_authority_locks_remain_false(tmp_path: Path) -> None:
    _seed_p102e(tmp_path)
    _seed_notion_diff(tmp_path)
    packet = build_temporal_continuity_operator_authorization_record_decision_reconciliation_receipt(
        repo_root=tmp_path
    )
    for field in (
        "production_activation",
        "canon_promotion",
        "forecast_influence",
        "scheduler_mutation",
        "runtime_authority",
        "execution_authority",
        "authorization_authority",
        "authorization_record_creation_authority",
        "record_creation_authority",
        "token_minting_authority",
        "token_minting_allowed",
        "authorization_granted",
        "authorization_record_created",
        "valid_for_execution",
    ):
        assert packet[field] is False
    assert set(packet["authority_locks"].values()) == {False}
    assert packet["canonical_status"] == "ADVISORY_ONLY"


def test_determinism_repeated_builds_match(tmp_path: Path) -> None:
    _seed_p102e(tmp_path)
    _seed_notion_diff(tmp_path, documented=True)
    first = build_temporal_continuity_operator_authorization_record_decision_reconciliation_receipt(
        repo_root=tmp_path
    )
    second = build_temporal_continuity_operator_authorization_record_decision_reconciliation_receipt(
        repo_root=tmp_path
    )
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


def test_schema_accepts_generated_packet(tmp_path: Path) -> None:
    _seed_p102e(tmp_path)
    _seed_notion_diff(tmp_path)
    packet = build_temporal_continuity_operator_authorization_record_decision_reconciliation_receipt(
        repo_root=tmp_path
    )
    schema = json.loads(Path(SCHEMA_PATH).read_text(encoding="utf-8"))
    jsonschema.validate(packet, schema)


def test_writer_emits_canonical_json_with_final_newline(tmp_path: Path) -> None:
    _seed_p102e(tmp_path)
    _seed_notion_diff(tmp_path)
    packet = build_temporal_continuity_operator_authorization_record_decision_reconciliation_receipt(
        repo_root=tmp_path
    )
    out = tmp_path / "receipt.json"
    write_temporal_continuity_operator_authorization_record_decision_reconciliation_receipt(
        out, packet
    )
    text = out.read_text(encoding="utf-8")
    parsed = json.loads(text)
    assert text.endswith("\n")
    assert text == canonical_dumps(parsed) + "\n"


def test_runner_writes_expected_output_path(tmp_path: Path) -> None:
    _seed_p102e(tmp_path)
    _seed_notion_diff(tmp_path)
    packet = run_temporal_continuity_operator_authorization_record_decision_reconciliation_receipt.run(
        repo_root=tmp_path
    )
    expected = tmp_path / OUT_PATH
    assert expected.exists()
    content = json.loads(expected.read_text(encoding="utf-8"))
    assert (
        content["artifact_type"]
        == "TemporalContinuityOperatorAuthorizationRecordDecisionReconciliationReceipt.v1"
    )
    assert content["packet_hash"] == packet["packet_hash"]
