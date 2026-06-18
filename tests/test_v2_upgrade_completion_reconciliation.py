from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.v2_upgrade_completion_reconciliation import (
    build_v2_upgrade_completion_reconciliation,
    render_v2_upgrade_completion_reconciliation_markdown,
)
from scripts import run_v2_upgrade_completion_reconciliation

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/v2_upgrade_completion_reconciliation.v1.schema.json"


def test_v2_upgrade_completion_reconciliation_holds_for_operator() -> None:
    packet = build_v2_upgrade_completion_reconciliation(REPO_ROOT)

    assert (
        packet["reconciliation_status"]
        == "V2_UPGRADE_COMPLETION_RECONCILIATION_READY_HELD_FOR_OPERATOR"
    )
    assert packet["notion_completion_receipt"]["mode"] == "ADVISORY_ONLY"
    assert packet["repo_evidence_summary"]["operator_gate"]["observed_status"] == (
        "V2_HYGIENE_LOOP_AWARENESS_OPERATOR_AUTHORIZATION_GATE_HELD_FOR_OPERATOR"
    )
    assert packet["repo_evidence_summary"]["missing_checks"] == []
    assert packet["repo_evidence_summary"]["partial_checks"] == []
    assert packet["repo_evidence_summary"]["alignment_required_workstreams"] == []
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_v2_upgrade_completion_reconciliation_denies_authority() -> None:
    packet = build_v2_upgrade_completion_reconciliation(REPO_ROOT)

    assert packet["operator_authorization_observed"] is False
    assert packet["operator_authorization_record_created"] is False
    assert packet["authorization_granted"] is False
    assert packet["v2_module_registration_authorized"] is False
    assert packet["rune_registration_authorized"] is False
    assert packet["projection_surface_mutation_authorized"] is False
    assert packet["schema_mutation_authorized"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["safe_to_auto_continue"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_v2_upgrade_completion_reconciliation_preserves_notion_modules_and_runes() -> None:
    packet = build_v2_upgrade_completion_reconciliation(REPO_ROOT)

    assert "Retrocausal Signal Hygiene Module" in packet["notion_completion_receipt"][
        "notion_v2_modules"
    ]
    assert "Mandatory Output Schema Enforcer" in packet["notion_completion_receipt"][
        "notion_v2_modules"
    ]
    assert "RUNE.HYPERSTITION_TAG" in packet["notion_completion_receipt"][
        "notion_v2_runes"
    ]
    assert "RUNE.OUTPUT_REGISTER_ENFORCE" in packet["notion_completion_receipt"][
        "notion_v2_runes"
    ]


def test_v2_upgrade_completion_reconciliation_fails_closed_without_sources(
    tmp_path: Path,
) -> None:
    packet = build_v2_upgrade_completion_reconciliation(tmp_path)

    assert packet["reconciliation_status"] == "NOT_COMPUTABLE"
    assert packet["repo_evidence_summary"]["audit"]["observed"] is False
    assert packet["repo_evidence_summary"]["operator_gate"]["observed"] is False
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["valid_for_execution"] is False


def test_v2_upgrade_completion_reconciliation_schema_and_hash_are_stable() -> None:
    packet = build_v2_upgrade_completion_reconciliation(REPO_ROOT)
    packet_without_hash = dict(packet)
    reconciliation_hash = packet_without_hash.pop("reconciliation_hash")
    assert reconciliation_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_upgrade_completion_reconciliation_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = tmp_path / "out/sync/v2_upgrade_completion_reconciliation/latest.json"
    out_md = tmp_path / "out/sync/v2_upgrade_completion_reconciliation/latest.md"

    first = run_v2_upgrade_completion_reconciliation.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_upgrade_completion_reconciliation.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_upgrade_completion_reconciliation_markdown_names_hold() -> None:
    packet = build_v2_upgrade_completion_reconciliation(REPO_ROOT)
    markdown = render_v2_upgrade_completion_reconciliation_markdown(packet)

    assert markdown[0] == "# v2.0 Upgrade Completion Reconciliation"
    assert any("recommended_next_patch: NOT_COMPUTABLE" in line for line in markdown)
    assert any("V2_HYGIENE_LOOP_AWARENESS_OPERATOR_AUTHORIZATION_GATE" in line for line in markdown)
