from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.grok_abx_runes_reconciliation_plan import (
    PLAN_JSON_PATH,
    build_grok_abx_runes_reconciliation_plan,
    render_grok_abx_runes_reconciliation_plan_markdown,
    write_grok_abx_runes_reconciliation_plan,
)
from scripts.codegen import run_grok_abx_runes_reconciliation_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/operator_review/grok_abx_runes_reconciliation_plan.v1.schema.json"


def test_grok_abx_runes_reconciliation_plan_holds_external_work_for_operator() -> None:
    packet = build_grok_abx_runes_reconciliation_plan(REPO_ROOT)

    assert packet["reconciliation_status"] == "GROK_ABX_RUNES_RECONCILIATION_HELD_FOR_OPERATOR"
    assert packet["source_conversation"]["source_type"] == "external_grok_share"
    assert packet["source_conversation"]["source_is_repo_authoritative"] is False
    assert packet["source_conversation"]["source_grants_authority"] is False
    assert packet["grok_claim_digest"]["notion_rune_family_count"] == 19
    assert packet["recommended_next_lane"] == "GROK_ABX_RUNES_OPERATOR_REVIEW_DECISION_RECORD_PLAN"


def test_grok_abx_runes_reconciliation_plan_reconciles_missing_local_runes() -> None:
    packet = build_grok_abx_runes_reconciliation_plan(REPO_ROOT)
    repo_evidence = packet["repo_evidence"]

    assert repo_evidence["catalog_observed"] is True
    assert repo_evidence["all_representative_grok_runes_registered"] is False
    assert "RUNE.SYMBOLIC.TEMPORAL_RESONANCE" in repo_evidence[
        "representative_grok_rune_ids_missing_from_catalog"
    ]
    assert "RUNE.ASTRA.v1.0" in repo_evidence[
        "representative_grok_rune_ids_missing_from_catalog"
    ]
    assert repo_evidence["registration_safe_to_register_runes"] is False
    assert repo_evidence["operator_authorization_observed"] is False


def test_grok_abx_runes_reconciliation_plan_denies_grok_execution_claim_authority() -> None:
    packet = build_grok_abx_runes_reconciliation_plan(REPO_ROOT)

    assert "pr_posted_and_merged" in packet["grok_claim_digest"]["conflicting_claim_classes"]
    assert "canon_promotion_authorized" in packet["grok_claim_digest"][
        "conflicting_claim_classes"
    ]
    assert packet["authorization_granted"] is False
    assert packet["operator_authorization_record_created"] is False
    assert packet["rune_registration_authorized"] is False
    assert packet["catalog_mutation_authorized"] is False
    assert packet["yggdrasil_binding_mutation_authorized"] is False
    assert packet["pr_merge_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["safe_to_prepare_patch"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert all(
        finding["authority_granted"] is False
        for finding in packet["reconciliation_findings"]
    )


def test_grok_abx_runes_reconciliation_plan_schema_and_hash_are_stable() -> None:
    first = build_grok_abx_runes_reconciliation_plan(REPO_ROOT)
    second = build_grok_abx_runes_reconciliation_plan(REPO_ROOT)
    without_hash = dict(first)
    reconciliation_hash = without_hash.pop("reconciliation_hash")

    assert first["reconciliation_hash"] == second["reconciliation_hash"]
    assert reconciliation_hash == canonical_hash(without_hash)
    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(first, schema)


def test_grok_abx_runes_reconciliation_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_grok_abx_runes_reconciliation_plan(REPO_ROOT, out_root=tmp_path)
    out_json = tmp_path / PLAN_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_grok_abx_runes_reconciliation_plan.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["reconciliation_hash"] == packet["reconciliation_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_grok_abx_runes_reconciliation_plan_markdown() -> None:
    packet = build_grok_abx_runes_reconciliation_plan(REPO_ROOT)
    markdown = render_grok_abx_runes_reconciliation_plan_markdown(packet)

    assert markdown[0] == "# Grok ABX-Runes Reconciliation Plan"
    assert any("ASTRA v1.0" in line for line in markdown)
    assert any("VEIL v1.0" in line for line in markdown)
    assert any("operator_gate_blocks_registration" in line for line in markdown)
