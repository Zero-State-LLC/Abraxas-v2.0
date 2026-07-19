from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.v2_live_notion_surface_reconciliation import (
    build_v2_live_notion_surface_reconciliation,
    render_v2_live_notion_surface_reconciliation_markdown,
)
from scripts.hygiene import run_v2_live_notion_surface_reconciliation

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/v2_live_notion_surface_reconciliation.v1.schema.json"


def test_v2_live_notion_surface_reconciliation_holds_for_operator() -> None:
    packet = build_v2_live_notion_surface_reconciliation(REPO_ROOT)

    assert (
        packet["reconciliation_status"]
        == "V2_LIVE_NOTION_SURFACE_RECONCILIATION_READY_HELD_FOR_OPERATOR"
    )
    assert any(
        phase["phase"] == "Phase 1: Foundations & Hygiene Layer"
        and phase["notion_status"] == "Ready for work"
        for phase in packet["live_notion_phases"]
    )
    assert any(
        source["observed_status"]
        == "V2_HYGIENE_LOOP_AWARENESS_OPERATOR_AUTHORIZATION_GATE_HELD_FOR_OPERATOR"
        for source in packet["repo_source_records"]
    )
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_v2_live_notion_surface_reconciliation_denies_authority() -> None:
    packet = build_v2_live_notion_surface_reconciliation(REPO_ROOT)

    assert packet["operator_authorization_observed"] is False
    assert packet["operator_authorization_record_created"] is False
    assert packet["authorization_granted"] is False
    assert packet["v2_module_registration_authorized"] is False
    assert packet["rune_registration_authorized"] is False
    assert packet["implementation_authorized"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["safe_to_auto_continue"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_v2_live_notion_surface_reconciliation_preserves_live_page_evidence() -> None:
    packet = build_v2_live_notion_surface_reconciliation(REPO_ROOT)

    titles = {surface["title"] for surface in packet["live_notion_surfaces"]}
    assert "Abraxas v2.0 - Upgrade Completion Receipt (2026-06-13)" in titles
    assert "v2.0 Implementation Surfaces" in titles
    assert "ABRAXAS v2.0 - Repo Notion Sync Receipt 2026-06-12" in titles
    assert all(
        "authority" in surface["authority_statement"]
        for surface in packet["live_notion_surfaces"]
    )


def test_v2_live_notion_surface_reconciliation_fails_closed_without_sources(
    tmp_path: Path,
) -> None:
    packet = build_v2_live_notion_surface_reconciliation(tmp_path)

    assert packet["reconciliation_status"] == "NOT_COMPUTABLE"
    assert packet["valid_for_execution"] is False
    assert any(source["observed"] is False for source in packet["repo_source_records"])


def test_v2_live_notion_surface_reconciliation_schema_and_hash_are_stable() -> None:
    packet = build_v2_live_notion_surface_reconciliation(REPO_ROOT)
    packet_without_hash = dict(packet)
    reconciliation_hash = packet_without_hash.pop("reconciliation_hash")
    assert reconciliation_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_live_notion_surface_reconciliation_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = tmp_path / "out/sync/v2_live_notion_surface_reconciliation/latest.json"
    out_md = tmp_path / "out/sync/v2_live_notion_surface_reconciliation/latest.md"

    first = run_v2_live_notion_surface_reconciliation.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_live_notion_surface_reconciliation.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_live_notion_surface_reconciliation_markdown_names_phase1() -> None:
    packet = build_v2_live_notion_surface_reconciliation(REPO_ROOT)
    markdown = render_v2_live_notion_surface_reconciliation_markdown(packet)

    assert markdown[0] == "# v2.0 Live Notion Surface Reconciliation"
    assert any("Phase 1: Foundations & Hygiene Layer: Ready for work" in line for line in markdown)
    assert any("recommended_next_patch: NOT_COMPUTABLE" in line for line in markdown)
