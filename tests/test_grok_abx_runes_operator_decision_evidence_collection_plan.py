from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.grok_abx_runes_operator_decision_evidence_collection_plan import (
    PLAN_JSON_PATH,
    build_grok_abx_runes_operator_decision_evidence_collection_plan,
    render_grok_abx_runes_operator_decision_evidence_collection_plan_markdown,
    write_grok_abx_runes_operator_decision_evidence_collection_plan,
)
from scripts.codegen import run_grok_abx_runes_operator_decision_evidence_collection_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "grok_abx_runes_operator_decision_evidence_collection_plan.v1.schema.json"
)


def test_grok_abx_runes_operator_decision_evidence_collection_plan_ready() -> None:
    first = build_grok_abx_runes_operator_decision_evidence_collection_plan(REPO_ROOT)
    second = build_grok_abx_runes_operator_decision_evidence_collection_plan(REPO_ROOT)

    assert first["plan_hash"] == second["plan_hash"]
    assert (
        first["status"]
        == "GROK_ABX_RUNES_OPERATOR_DECISION_EVIDENCE_COLLECTION_PLAN_READY"
    )
    assert first["source_review_ready"] is True
    assert first["evidence_collection_only"] is True
    assert first["recommended_default_decision"] == "HOLD_FOR_OPERATOR_REVIEW"
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_grok_abx_runes_operator_decision_evidence_collection_plan_groups_fields() -> None:
    packet = build_grok_abx_runes_operator_decision_evidence_collection_plan(REPO_ROOT)
    groups = {group["group_id"]: group for group in packet["evidence_bundle_groups"]}

    assert set(groups) == {
        "operator_identity",
        "grok_claim_disposition",
        "authority_acknowledgements",
        "provenance_evidence",
        "evidence_outputs",
    }
    assert "operator_id" in groups["operator_identity"]["required_fields"]
    assert "selected_decision" in groups["grok_claim_disposition"]["required_fields"]
    assert "reviewed_decision_record_review_hash" in groups["provenance_evidence"][
        "required_fields"
    ]
    assert packet["evidence_readiness_summary"]["required_field_count"] > 0
    assert "RUNE_REGISTRATION" in packet["disallowed_follow_on_actions"]


def test_grok_abx_runes_operator_decision_evidence_collection_plan_denies_authority() -> None:
    packet = build_grok_abx_runes_operator_decision_evidence_collection_plan(REPO_ROOT)

    assert packet["operator_evidence_collected"] is False
    assert packet["operator_attestation_created"] is False
    assert packet["evidence_bundle_created"] is False
    assert packet["decision_record_created"] is False
    assert packet["authorization_record_created"] is False
    assert packet["external_backlog_accepted"] is False
    assert packet["separate_registration_planning_authorized"] is False
    assert packet["catalog_mutation_authorized"] is False
    assert packet["rune_registration_authorized"] is False
    assert packet["yggdrasil_binding_mutation_authorized"] is False
    assert packet["valid_for_execution"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_grok_abx_runes_operator_decision_evidence_collection_plan_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_grok_abx_runes_operator_decision_evidence_collection_plan(tmp_path)

    assert (
        packet["status"]
        == "GROK_ABX_RUNES_OPERATOR_DECISION_EVIDENCE_COLLECTION_PLAN_BLOCKED"
    )
    assert packet["source_review_ready"] is False
    assert packet["source_review_hash"] == "NOT_COMPUTABLE"
    assert packet["blockers"]
    assert packet["valid_for_execution"] is False


def test_grok_abx_runes_operator_decision_evidence_collection_plan_schema_and_hash_are_stable() -> None:
    packet = build_grok_abx_runes_operator_decision_evidence_collection_plan(REPO_ROOT)
    packet_without_hash = dict(packet)
    plan_hash = packet_without_hash.pop("plan_hash")

    assert plan_hash == canonical_hash(packet_without_hash)
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_grok_abx_runes_operator_decision_evidence_collection_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_grok_abx_runes_operator_decision_evidence_collection_plan(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / PLAN_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_grok_abx_runes_operator_decision_evidence_collection_plan.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["plan_hash"] == packet["plan_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_grok_abx_runes_operator_decision_evidence_collection_plan_markdown() -> None:
    packet = build_grok_abx_runes_operator_decision_evidence_collection_plan(REPO_ROOT)
    markdown = render_grok_abx_runes_operator_decision_evidence_collection_plan_markdown(
        packet
    )

    assert markdown[0] == "# Grok ABX-Runes Operator Decision Evidence Collection Plan"
    assert any("grok_claim_disposition" in line for line in markdown)
    assert any("reviewed_decision_record_review_hash" in line for line in markdown)
