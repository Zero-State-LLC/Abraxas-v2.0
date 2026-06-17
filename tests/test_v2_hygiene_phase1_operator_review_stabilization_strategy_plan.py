from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.v2_hygiene_phase1_operator_review_stabilization_strategy_plan import (
    PLAN_JSON_PATH,
    build_v2_hygiene_phase1_operator_review_stabilization_strategy_plan,
    render_v2_hygiene_phase1_operator_review_stabilization_strategy_plan_markdown,
    write_v2_hygiene_phase1_operator_review_stabilization_strategy_plan,
)
from scripts import (
    run_v2_hygiene_phase1_operator_review_stabilization_strategy_plan,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase1_operator_review_stabilization_strategy_plan.v1.schema.json"
)


def test_v2_hygiene_phase1_operator_review_stabilization_strategy_plan_ready() -> None:
    first = build_v2_hygiene_phase1_operator_review_stabilization_strategy_plan(
        REPO_ROOT
    )
    second = build_v2_hygiene_phase1_operator_review_stabilization_strategy_plan(
        REPO_ROOT
    )

    assert first["strategy_plan_hash"] == second["strategy_plan_hash"]
    assert (
        first["strategy_plan_status"]
        == "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_STRATEGY_PLAN_READY"
    )
    assert first["selected_strategy_id"] == "terminal_snapshot_strategy"
    assert first["operator_decision_required"] is True
    assert first["operator_decision_record_created"] is False
    assert (
        first["recommended_next_lane"]
        == "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_PLAN"
    )


def test_v2_hygiene_phase1_operator_review_stabilization_strategy_plan_source_binding() -> None:
    packet = build_v2_hygiene_phase1_operator_review_stabilization_strategy_plan(
        REPO_ROOT
    )
    source = packet["source_cycle_audit"]

    assert source["source_observed"] is True
    assert (
        source["source_status"]
        == "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_DEPENDENCY_CYCLE_AUDIT_HELD_FOR_OPERATOR"
    )
    assert source["cycle_observed"] is True
    assert source["naive_regeneration_safe"] is False
    assert source["implementation_authorized"] is False
    assert source["valid_for_execution"] is False


def test_v2_hygiene_phase1_operator_review_stabilization_strategy_plan_denies_authority() -> None:
    packet = build_v2_hygiene_phase1_operator_review_stabilization_strategy_plan(
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
    assert all(option["authority_granted"] is False for option in packet["strategy_options"])
    assert all(finding["authority_granted"] is False for finding in packet["plan_findings"])


def test_v2_hygiene_phase1_operator_review_stabilization_strategy_plan_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_phase1_operator_review_stabilization_strategy_plan(
        tmp_path
    )

    assert (
        packet["strategy_plan_status"]
        == "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_STRATEGY_PLAN_BLOCKED"
    )
    assert packet["selected_strategy_id"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["valid_for_execution"] is False


def test_v2_hygiene_phase1_operator_review_stabilization_strategy_plan_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_operator_review_stabilization_strategy_plan(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    strategy_plan_hash = packet_without_hash.pop("strategy_plan_hash")
    assert strategy_plan_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_phase1_operator_review_stabilization_strategy_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase1_operator_review_stabilization_strategy_plan(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / PLAN_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_operator_review_stabilization_strategy_plan.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["strategy_plan_hash"] == packet["strategy_plan_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_phase1_operator_review_stabilization_strategy_plan_markdown() -> None:
    packet = build_v2_hygiene_phase1_operator_review_stabilization_strategy_plan(
        REPO_ROOT
    )
    markdown = (
        render_v2_hygiene_phase1_operator_review_stabilization_strategy_plan_markdown(
            packet
        )
    )

    assert (
        markdown[0]
        == "# v2.0 Hygiene Phase 1 Operator Review Stabilization Strategy Plan"
    )
    assert any("terminal_snapshot_strategy" in line for line in markdown)
    assert any(
        "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_PLAN" in line
        for line in markdown
    )
