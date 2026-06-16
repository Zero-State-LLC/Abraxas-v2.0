from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.grok_abx_runes_operator_decision_record_plan import (
    PLAN_JSON_PATH,
    build_grok_abx_runes_operator_decision_record_plan,
    render_grok_abx_runes_operator_decision_record_plan_markdown,
    write_grok_abx_runes_operator_decision_record_plan,
)
from scripts import run_grok_abx_runes_operator_decision_record_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "grok_abx_runes_operator_decision_record_plan.v1.schema.json"
)


def test_grok_abx_runes_operator_decision_record_plan_ready() -> None:
    first = build_grok_abx_runes_operator_decision_record_plan(REPO_ROOT)
    second = build_grok_abx_runes_operator_decision_record_plan(REPO_ROOT)

    assert first["decision_record_plan_hash"] == second["decision_record_plan_hash"]
    assert first["status"] == "GROK_ABX_RUNES_OPERATOR_DECISION_RECORD_PLAN_READY"
    assert first["recommended_default_decision"] == "HOLD_FOR_OPERATOR_REVIEW"
    assert first["recommended_next_lane"] == "GROK_ABX_RUNES_OPERATOR_DECISION_RECORD_DRY_RUN"
    assert first["operator_input_required"] is True
    assert first["decision_record_created"] is False


def test_grok_abx_runes_operator_decision_record_plan_source_binding() -> None:
    packet = build_grok_abx_runes_operator_decision_record_plan(REPO_ROOT)
    source = packet["source_reconciliation_plan"]

    assert source["source_observed"] is True
    assert source["source_status"] == "GROK_ABX_RUNES_RECONCILIATION_HELD_FOR_OPERATOR"
    assert (
        source["source_recommended_next_lane"]
        == "GROK_ABX_RUNES_OPERATOR_REVIEW_DECISION_RECORD_PLAN"
    )
    assert source["source_valid_for_execution"] is False
    assert source["source_rune_registration_authorized"] is False
    assert source["source_notion_family_count"] == 19
    assert source["source_missing_representative_rune_count"] > 0


def test_grok_abx_runes_operator_decision_record_plan_carries_review_shape() -> None:
    packet = build_grok_abx_runes_operator_decision_record_plan(REPO_ROOT)
    group_ids = {group["group_id"] for group in packet["required_field_groups"]}

    assert "ACCEPT_GROK_ABX_RUNES_AS_EXTERNAL_BACKLOG" in packet["decision_options"]
    assert "AUTHORIZE_SEPARATE_ADVISORY_RUNE_REGISTRATION_PLANNING_LANE" in packet[
        "decision_options"
    ]
    assert "operator_identity" in group_ids
    assert "source_scope_acknowledgement" in group_ids
    assert "authority_boundary_acknowledgement" in group_ids
    assert "REGISTER_RUNE_CATALOG_ENTRIES" in packet["disallowed_follow_on_actions"]
    assert "MUTATE_YGGDRASIL_BINDINGS" in packet["disallowed_follow_on_actions"]
    assert "ASTRA" in packet["source_family_ids_for_review"]
    assert "VEIL" in packet["source_family_ids_for_review"]
    assert "pr_posted_and_merged" in packet["source_conflicting_claim_classes"]


def test_grok_abx_runes_operator_decision_record_plan_denies_authority() -> None:
    packet = build_grok_abx_runes_operator_decision_record_plan(REPO_ROOT)

    assert packet["authorization_granted"] is False
    assert packet["implementation_authorized"] is False
    assert packet["operator_attestation_created"] is False
    assert packet["authorization_record_created"] is False
    assert packet["catalog_mutation_authorized"] is False
    assert packet["rune_registration_authorized"] is False
    assert packet["yggdrasil_binding_mutation_authorized"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["pr_merge_authority"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["valid_for_execution"] is False
    assert packet["safe_to_prepare_patch"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert all(finding["authority_granted"] is False for finding in packet["plan_findings"])


def test_grok_abx_runes_operator_decision_record_plan_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_grok_abx_runes_operator_decision_record_plan(tmp_path)

    assert packet["status"] == "GROK_ABX_RUNES_OPERATOR_DECISION_RECORD_PLAN_BLOCKED"
    assert packet["source_reconciliation_plan"]["source_observed"] is False
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["valid_for_execution"] is False


def test_grok_abx_runes_operator_decision_record_plan_schema_and_hash_are_stable() -> None:
    packet = build_grok_abx_runes_operator_decision_record_plan(REPO_ROOT)
    packet_without_hash = dict(packet)
    decision_record_plan_hash = packet_without_hash.pop("decision_record_plan_hash")

    assert decision_record_plan_hash == canonical_hash(packet_without_hash)
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_grok_abx_runes_operator_decision_record_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_grok_abx_runes_operator_decision_record_plan(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / PLAN_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_grok_abx_runes_operator_decision_record_plan.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["decision_record_plan_hash"] == packet["decision_record_plan_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_grok_abx_runes_operator_decision_record_plan_markdown() -> None:
    packet = build_grok_abx_runes_operator_decision_record_plan(REPO_ROOT)
    markdown = render_grok_abx_runes_operator_decision_record_plan_markdown(packet)

    assert markdown[0] == "# Grok ABX-Runes Operator Decision Record Plan"
    assert any("ACCEPT_GROK_ABX_RUNES_AS_EXTERNAL_BACKLOG" in line for line in markdown)
    assert any("authority_boundary_acknowledgement" in line for line in markdown)
    assert any("rune_registration_remains_denied" in line for line in markdown)
