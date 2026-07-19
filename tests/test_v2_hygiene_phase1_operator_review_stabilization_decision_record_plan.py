from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.v2_hygiene_phase1_operator_review_stabilization_decision_record_plan import (
    PLAN_JSON_PATH,
    build_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan,
    render_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_markdown,
    write_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan,
)
from scripts.hygiene import (
    run_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase1_operator_review_stabilization_decision_record_plan.v1.schema.json"
)


def test_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_ready() -> None:
    first = build_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan(
        REPO_ROOT
    )
    second = build_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan(
        REPO_ROOT
    )

    assert first["decision_record_plan_hash"] == second["decision_record_plan_hash"]
    assert (
        first["decision_record_plan_status"]
        == "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_PLAN_READY"
    )
    assert first["decision_record_required"] is True
    assert first["decision_record_creation_allowed"] is False
    assert first["decision_record_created"] is False
    assert first["operator_attestation_required"] is True
    assert first["operator_attested"] is False
    assert (
        first["recommended_next_lane"]
        == "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_DRY_RUN"
    )


def test_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_source_binding() -> None:
    packet = build_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan(
        REPO_ROOT
    )
    source = packet["source_strategy_plan"]

    assert source["source_observed"] is True
    assert (
        source["source_status"]
        == "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_STRATEGY_PLAN_READY"
    )
    assert (
        source["source_recommended_next_lane"]
        == "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_PLAN"
    )
    assert source["selected_strategy_id"] == "terminal_snapshot_strategy"
    assert source["operator_decision_required"] is True
    assert source["operator_decision_record_created"] is False


def test_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_shape() -> None:
    packet = build_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan(
        REPO_ROOT
    )
    record = packet["planned_decision_record"]
    group_ids = {group["group_id"] for group in record["required_field_groups"]}

    assert record["record_creation_allowed"] is False
    assert record["record_created"] is False
    assert record["default_disposition"] == "HOLD_FOR_OPERATOR_STABILIZATION_DECISION"
    assert "APPROVE_TERMINAL_SNAPSHOT_STRATEGY" in record["allowed_dispositions"]
    assert "AUTHORIZE_PHASE1_IMPLEMENTATION" in record["forbidden_dispositions"]
    assert "operator_identity" in group_ids
    assert "authority_boundary_acknowledgement" in group_ids
    authority_group = next(
        group
        for group in record["required_field_groups"]
        if group["group_id"] == "authority_boundary_acknowledgement"
    )
    assert "no_notion_writeback" in authority_group["fields"]


def test_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_denies_authority() -> None:
    packet = build_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan(
        REPO_ROOT
    )

    assert packet["authorization_granted"] is False
    assert packet["authorization_record_created"] is False
    assert packet["operator_attestation_created"] is False
    assert packet["operator_evidence_bundle_created"] is False
    assert packet["implementation_authorized"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["valid_for_execution"] is False
    assert packet["safe_to_prepare_patch"] is False
    assert packet["safe_to_auto_continue"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert all(finding["authority_granted"] is False for finding in packet["plan_findings"])


def test_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan(
        tmp_path
    )

    assert (
        packet["decision_record_plan_status"]
        == "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_PLAN_BLOCKED"
    )
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["valid_for_execution"] is False


def test_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    decision_record_plan_hash = packet_without_hash.pop("decision_record_plan_hash")
    assert decision_record_plan_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / PLAN_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["decision_record_plan_hash"] == packet["decision_record_plan_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_markdown() -> None:
    packet = build_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan(
        REPO_ROOT
    )
    markdown = (
        render_v2_hygiene_phase1_operator_review_stabilization_decision_record_plan_markdown(
            packet
        )
    )

    assert (
        markdown[0]
        == "# v2.0 Hygiene Phase 1 Operator Review Stabilization Decision Record Plan"
    )
    assert any("operator_identity" in line for line in markdown)
    assert any(
        "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_DRY_RUN"
        in line
        for line in markdown
    )
