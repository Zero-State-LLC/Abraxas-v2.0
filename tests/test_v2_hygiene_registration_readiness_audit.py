from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.sync.v2_hygiene_registration_readiness_audit import (
    build_v2_hygiene_registration_readiness_audit,
    render_v2_hygiene_registration_readiness_audit_markdown,
)
from scripts import run_v2_hygiene_registration_readiness_audit

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/v2_hygiene_registration_readiness_audit.v1.schema.json"


def test_v2_hygiene_registration_readiness_audit_held_for_operator() -> None:
    packet = build_v2_hygiene_registration_readiness_audit(REPO_ROOT)

    assert packet["audit_status"] == "V2_HYGIENE_REGISTRATION_READINESS_AUDIT_HELD_FOR_OPERATOR"
    assert packet["missing_module_registrations"] == []
    assert packet["missing_rune_registrations"] == []
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_v2_hygiene_registration_readiness_audit_denies_registration_authority() -> None:
    packet = build_v2_hygiene_registration_readiness_audit(REPO_ROOT)

    assert packet["registration_readiness"]["safe_to_register_modules"] is False
    assert packet["registration_readiness"]["safe_to_register_runes"] is False
    assert packet["operator_authorization_observed"] is False
    assert packet["authorization_granted"] is False
    assert packet["v2_module_registration_authorized"] is False
    assert packet["rune_registration_authorized"] is False
    assert packet["valid_for_execution"] is False
    assert packet["safe_to_auto_continue"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_v2_hygiene_registration_readiness_audit_carries_core_directive_context() -> None:
    packet = build_v2_hygiene_registration_readiness_audit(REPO_ROOT)

    context = packet["notion_core_directive_context"]
    assert context["page_title"] == "Abraxas v2.0 Core Directive"
    assert context["required_registers"] == ["OBSERVED", "INFERRED", "SPECULATIVE"]
    assert "hyperstitional charge" in context["required_loop_fields"]
    assert "Canon Spine" in context["authority_boundary"]


def test_v2_hygiene_registration_readiness_audit_fails_closed_without_sources(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_registration_readiness_audit(tmp_path)

    assert packet["audit_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["valid_for_execution"] is False


def test_v2_hygiene_registration_readiness_audit_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_registration_readiness_audit(REPO_ROOT)
    packet_without_hash = dict(packet)
    audit_hash = packet_without_hash.pop("audit_hash")
    assert audit_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_v2_hygiene_registration_readiness_audit_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = tmp_path / "out/sync/v2_hygiene_registration_readiness_audit/latest.json"
    out_md = tmp_path / "out/sync/v2_hygiene_registration_readiness_audit/latest.md"

    first = run_v2_hygiene_registration_readiness_audit.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_registration_readiness_audit.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_v2_hygiene_registration_readiness_audit_markdown_reports_hold_posture() -> None:
    packet = build_v2_hygiene_registration_readiness_audit(REPO_ROOT)
    markdown = render_v2_hygiene_registration_readiness_audit_markdown(packet)

    assert markdown[0] == "# v2.0 Hygiene Registration Readiness Audit"
    assert any("recommended_next_patch: NOT_COMPUTABLE" in line for line in markdown)
    assert packet["missing_module_registrations"] == []
    assert packet["missing_rune_registrations"] == []
