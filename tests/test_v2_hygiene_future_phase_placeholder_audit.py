from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.v2_hygiene_future_phase_placeholder_audit import (
    build_v2_hygiene_future_phase_placeholder_audit,
    render_v2_hygiene_future_phase_placeholder_audit_markdown,
    write_v2_hygiene_future_phase_placeholder_audit,
)
from scripts import run_v2_hygiene_future_phase_placeholder_audit

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/v2_hygiene_future_phase_placeholder_audit.v1.schema.json"


def test_v2_hygiene_future_phase_placeholder_audit_ready() -> None:
    first = build_v2_hygiene_future_phase_placeholder_audit(REPO_ROOT)
    second = build_v2_hygiene_future_phase_placeholder_audit(REPO_ROOT)

    assert first["audit_hash"] == second["audit_hash"]
    assert first["status"] == "V2_HYGIENE_FUTURE_PHASE_PLACEHOLDER_AUDIT_READY"
    assert first["source_ready"] is True
    assert first["placeholder_summary"]["future_phase_count"] == 2
    assert first["placeholder_summary"]["placeholder_phase_count"] == 2
    assert first["placeholder_summary"]["blocked_phase_count"] == 2
    assert first["placeholder_summary"]["backlog_ready_count"] == 0
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_v2_hygiene_future_phase_placeholder_audit_denies_authority() -> None:
    packet = build_v2_hygiene_future_phase_placeholder_audit(REPO_ROOT)

    assert packet["implementation_authorized"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["valid_for_execution"] is False
    assert packet["safe_to_prepare_patch"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["acceptance_gate_summary"]["safe_to_prepare_phase3_backlog"] is False
    assert packet["acceptance_gate_summary"]["safe_to_prepare_phase4_backlog"] is False
    assert packet["acceptance_gate_summary"]["safe_to_integrate_output_surface"] is False
    assert packet["acceptance_gate_summary"]["safe_to_activate_feature_flags"] is False
    assert packet["acceptance_gate_summary"]["safe_to_promote_components"] is False
    assert all(value is False for value in packet["authority_locks"].values())
    assert all(
        phase["implementation_authorized"] is False
        for phase in packet["phase_records"]
    )


def test_v2_hygiene_future_phase_placeholder_audit_maps_notion_placeholders() -> None:
    packet = build_v2_hygiene_future_phase_placeholder_audit(REPO_ROOT)
    phases = {phase["phase_id"]: phase for phase in packet["phase_records"]}

    assert phases["phase3"]["title"] == "Phase 3: Output Surface Integration"
    assert phases["phase3"]["notion_status"] == "Placeholder"
    assert phases["phase3"]["spec_detail_ready"] is False
    assert phases["phase4"]["title"] == "Phase 4: Full Integration & Promotion"
    assert phases["phase4"]["repo_audit_status"] == (
        "PLACEHOLDER_CONFIRMED_HELD_FOR_NOTION_SPEC"
    )
    assert {
        source["phase_id"] for source in packet["notion_future_phase_sources"]
    } == {"phase3", "phase4"}


def test_v2_hygiene_future_phase_placeholder_audit_fails_closed_without_sources(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_future_phase_placeholder_audit(tmp_path)

    assert packet["status"] == "V2_HYGIENE_FUTURE_PHASE_PLACEHOLDER_AUDIT_BLOCKED"
    assert packet["source_ready"] is False
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["implementation_authorized"] is False
    assert packet["blockers"] == ["v2_hygiene_future_phase_sources_not_ready"]


def test_v2_hygiene_future_phase_placeholder_audit_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_future_phase_placeholder_audit(REPO_ROOT)
    packet_without_hash = dict(packet)
    audit_hash = packet_without_hash.pop("audit_hash")
    assert audit_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_future_phase_placeholder_audit_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_future_phase_placeholder_audit(
        REPO_ROOT, out_root=tmp_path
    )
    out_json = tmp_path / "out/sync/v2_hygiene_future_phase_placeholder_audit/latest.json"
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_future_phase_placeholder_audit.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["audit_hash"] == packet["audit_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_future_phase_placeholder_audit_markdown() -> None:
    packet = build_v2_hygiene_future_phase_placeholder_audit(REPO_ROOT)
    markdown = render_v2_hygiene_future_phase_placeholder_audit_markdown(packet)

    assert markdown[0] == "# v2.0 Hygiene Future Phase Placeholder Audit"
    assert any("phase3" in line for line in markdown)
    assert any("phase4" in line for line in markdown)
    assert any("placeholder_phase_count" in line for line in markdown)
