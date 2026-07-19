from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.grok_abx_runes_operator_decision_record_review import (
    REVIEW_JSON_PATH,
    build_grok_abx_runes_operator_decision_record_review,
    render_grok_abx_runes_operator_decision_record_review_markdown,
    write_grok_abx_runes_operator_decision_record_review,
)
from scripts.codegen import run_grok_abx_runes_operator_decision_record_review

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "grok_abx_runes_operator_decision_record_review.v1.schema.json"
)


def test_grok_abx_runes_operator_decision_record_review_holds_for_operator() -> None:
    first = build_grok_abx_runes_operator_decision_record_review(REPO_ROOT)
    second = build_grok_abx_runes_operator_decision_record_review(REPO_ROOT)

    assert first["review_hash"] == second["review_hash"]
    assert (
        first["status"]
        == "GROK_ABX_RUNES_OPERATOR_DECISION_RECORD_REVIEW_HELD_FOR_OPERATOR"
    )
    assert first["source_dry_run_ready"] is True
    assert first["selected_operator_decision"] == "HOLD_FOR_OPERATOR_REVIEW"
    assert (
        first["selected_follow_on_action"]
        == "MAINTAIN_GROK_ABX_RUNES_OPERATOR_REVIEW_HOLD"
    )
    assert first["operator_attestations_present"] is False
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert first["safe_to_auto_continue"] is False


def test_grok_abx_runes_operator_decision_record_review_preserves_terminal_hold() -> None:
    packet = build_grok_abx_runes_operator_decision_record_review(REPO_ROOT)
    finding_ids = {finding["finding_id"] for finding in packet["review_findings"]}

    assert "simulated_decision_record_shape_validated" in finding_ids
    assert "operator_attestations_missing" in finding_ids
    assert "external_backlog_acceptance_denied" in finding_ids
    assert "rune_registration_denied" in finding_ids
    assert "catalog_and_yggdrasil_mutation_denied" in finding_ids
    assert "operator_identity_not_attested" in packet["validation_blockers"]
    assert "grok_claim_disposition_not_attested" in packet["validation_blockers"]


def test_grok_abx_runes_operator_decision_record_review_denies_authority() -> None:
    packet = build_grok_abx_runes_operator_decision_record_review(REPO_ROOT)

    assert packet["decision_record_created"] is False
    assert packet["authorization_record_created"] is False
    assert packet["external_backlog_accepted"] is False
    assert packet["separate_registration_planning_authorized"] is False
    assert packet["catalog_mutation_authorized"] is False
    assert packet["rune_registration_authorized"] is False
    assert packet["yggdrasil_binding_mutation_authorized"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["pr_merge_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert all(finding["authority_granted"] is False for finding in packet["review_findings"])


def test_grok_abx_runes_operator_decision_record_review_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_grok_abx_runes_operator_decision_record_review(tmp_path)

    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["source_dry_run_ready"] is False
    assert packet["source_readiness"] == "SOURCE_DRY_RUN_MISSING"
    assert packet["selected_operator_decision"] == "NOT_COMPUTABLE"
    assert packet["selected_follow_on_action"] == "NOT_COMPUTABLE"


def test_grok_abx_runes_operator_decision_record_review_schema_and_hash_are_stable() -> None:
    packet = build_grok_abx_runes_operator_decision_record_review(REPO_ROOT)
    packet_without_hash = dict(packet)
    review_hash = packet_without_hash.pop("review_hash")

    assert review_hash == canonical_hash(packet_without_hash)
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_grok_abx_runes_operator_decision_record_review_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_grok_abx_runes_operator_decision_record_review(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / REVIEW_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_grok_abx_runes_operator_decision_record_review.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["review_hash"] == packet["review_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_grok_abx_runes_operator_decision_record_review_markdown() -> None:
    packet = build_grok_abx_runes_operator_decision_record_review(REPO_ROOT)
    markdown = render_grok_abx_runes_operator_decision_record_review_markdown(packet)

    assert markdown[0] == "# Grok ABX-Runes Operator Decision Record Review"
    assert any("operator_attestations_present" in line for line in markdown)
    assert any("catalog_and_yggdrasil_mutation_denied" in line for line in markdown)
