from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_intelligence_spine_phase1_operator_evidence_packet import (
    build_abx_codegen_intelligence_spine_phase1_operator_evidence_packet,
    render_abx_codegen_intelligence_spine_phase1_operator_evidence_packet_markdown,
)
from core.canonical.json import canonical_hash
from scripts import run_abx_codegen_intelligence_spine_phase1_operator_evidence_packet

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_intelligence_spine_phase1_operator_evidence_packet.v1.schema.json"
)


def test_codegen_phase1_operator_evidence_packet_is_held() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_operator_evidence_packet(
        repo_root=REPO_ROOT
    )

    assert (
        packet["phase1_operator_evidence_packet_status"]
        == "ABX_CODEGEN_PHASE1_OPERATOR_EVIDENCE_PACKET_HELD_FOR_OPERATOR"
    )
    assert packet["source_operator_authorization_request_plan"]["source_ready"] is True
    assert packet["missing_evidence"] == []
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["safe_to_auto_continue"] is False


def test_codegen_phase1_operator_evidence_packet_binds_required_artifacts() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_operator_evidence_packet(
        repo_root=REPO_ROOT
    )

    items = {item["evidence_id"]: item for item in packet["evidence_items"]}
    assert "phase1_operator_authorization_request_plan" in items
    assert "phase1_implementation_boundary_review" in items
    assert "phase1_code_detail_plan" in items
    assert "module_surface_plan" in items
    assert all(item["observed"] is True for item in items.values())
    assert all(item["grants_authority"] is False for item in items.values())


def test_codegen_phase1_operator_evidence_packet_requires_human_review() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_operator_evidence_packet(
        repo_root=REPO_ROOT
    )

    checks = {item["check"]: item for item in packet["operator_review_checklist"]}
    assert "confirm_no_operator_attestation_is_present_in_this_packet" in checks
    assert all(item["requires_human_review"] is True for item in checks.values())
    assert all(item["satisfied_by_packet"] is False for item in checks.values())


def test_codegen_phase1_operator_evidence_packet_preserves_denials() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_operator_evidence_packet(
        repo_root=REPO_ROOT
    )

    denials = {item["action"]: item for item in packet["explicit_denials"]}
    assert denials["operator_decision_record_creation"]["authorized"] is False
    assert denials["operator_attestation"]["authorized"] is False
    assert denials["authorization_record_creation"]["authorized"] is False
    assert denials["phase1_implementation"]["authorized"] is False
    assert denials["shadow_replay_execution"]["authorized"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_phase1_operator_evidence_packet_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_operator_evidence_packet(
        repo_root=tmp_path
    )

    assert packet["phase1_operator_evidence_packet_status"] == "NOT_COMPUTABLE"
    assert packet["source_operator_authorization_request_plan"]["source_ready"] is False
    assert "phase1_operator_authorization_request_plan" in packet["missing_evidence"]


def test_codegen_phase1_operator_evidence_packet_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_operator_evidence_packet(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_phase1_operator_evidence_packet_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_phase1_operator_evidence_packet_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_intelligence_spine_phase1_operator_evidence_packet.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_intelligence_spine_phase1_operator_evidence_packet.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_phase1_operator_evidence_packet_markdown() -> None:
    packet = build_abx_codegen_intelligence_spine_phase1_operator_evidence_packet(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_intelligence_spine_phase1_operator_evidence_packet_markdown(
        packet
    )

    assert markdown[0] == "# ABX Codegen Intelligence Spine Phase 1 Operator Evidence Packet"
    assert any("phase1_code_detail_plan" in line for line in markdown)
    assert any("operator_attestation" in line for line in markdown)
