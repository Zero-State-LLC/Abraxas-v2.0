from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.canonical.json import canonical_hash
from core.generated_artifact_registry import build_generated_artifact_registry
from core.operator_narrative_static_preview_bundle import PREVIEW_SECTIONS, build_operator_narrative_static_preview_markdown
from core.operator_narrative_static_preview_governance_audit import (
    build_operator_narrative_static_preview_governance_audit_markdown,
    build_operator_narrative_static_preview_governance_audit_packet,
    write_operator_narrative_static_preview_governance_audit,
)


def _preview() -> dict:
    packet = {
        "schema_version": "OperatorNarrativeStaticPreviewBundle.v1",
        "patch_id": "PATCH-P48-OPERATOR-NARRATIVE-STATIC-PREVIEW-BUNDLE-001",
        "preview_id": "operator_narrative_static_preview_001",
        "final_status": "PREVIEW_ONLY",
        "preview_posture": "COMPLETE",
        "preview_sections": PREVIEW_SECTIONS,
        "static_preview_summary": {"artifact_manifest_count": 1, "hash_inventory_count": 1, "lineage_key_count": 1},
        "manifest_preview": [{"artifact_id": "a", "role": "report_json", "path": "out/reports/operator_narrative_report_001.latest.json", "sha256": "h"}],
        "hash_inventory_preview": {"a": "h"},
        "lineage_preview": {"p42_report_hash": "h42"},
        "governance_preview": {},
        "audit_preview": {"final_status": "PASS", "audit_posture": "CLEAN", "finding_counts": {"PASS": 1, "WARN": 0, "FAIL": 0}},
        "passive_references": {
            "report_json": "out/reports/operator_narrative_report_001.latest.json",
            "report_markdown": "out/reports/operator_narrative_report_001.latest.md",
            "export_bundle_json": "out/exports/operator_narrative_export_bundle_001.latest.json",
            "export_bundle_markdown": "out/exports/operator_narrative_export_bundle_001.latest.md",
        },
        "source_artifacts": {"export_bundle_json": "out/exports/operator_narrative_export_bundle_001.latest.json"},
        "source_hashes": {"export_bundle_json": "h"},
        "blocker_summary": [],
        "governance_flags": {
            "preview_only": True,
            "static_only": True,
            "passive_preview_only": True,
            "read_only": True,
            "non_interactive": True,
            "non_authoritative": True,
            "source_linked": True,
            "advisory_only": True,
            "script_allowed": False,
            "html_script_allowed": False,
            "external_fetch_allowed": False,
            "form_allowed": False,
            "button_allowed": False,
            "command_authority": False,
            "ui_command_authority": False,
            "action_authority": False,
            "recommendation_authority": False,
            "inference_authority": False,
            "prediction_allowed": False,
            "forecast_authority": False,
            "trend_prediction_allowed": False,
            "readiness_claims_allowed": False,
            "mutation_allowed": False,
            "authority_granted": False,
            "execution_authority": False,
            "routing_change_allowed": False,
            "queue_mutation_allowed": False,
            "canon_mutation_allowed": False,
            "runtime_mutation_allowed": False,
            "adaptive_behavior_allowed": False,
            "psychological_claims_allowed": False,
            "speculative_causation_allowed": False,
            "auto_execute": False,
            "auto_approve": False,
            "command_channel": False,
            "bidirectional_control": False,
        },
        "provenance": {"deterministic": True, "preview_only": True, "read_only": True, "passive_preview_only": True, "fail_closed": True},
    }
    packet["preview_hash"] = canonical_hash(packet)
    return packet


def _audit(packet: dict | None = None, md: str | None = None) -> dict:
    pkt = _preview() if packet is None else packet
    text = build_operator_narrative_static_preview_markdown(pkt) if md is None else md
    return build_operator_narrative_static_preview_governance_audit_packet(preview_packet=pkt, preview_markdown_text=text)


def test_status_ladder_and_determinism(tmp_path: Path) -> None:
    packet = _audit()
    assert packet["final_status"] == "PASS"
    assert packet["audit_posture"] == "CLEAN"
    twin = _audit(deepcopy(_preview()))
    assert packet["audit_hash"] == twin["audit_hash"]

    bad = _preview()
    bad["preview_hash"] = "x"
    assert _audit(bad)["final_status"] == "FAIL"

    missing = build_operator_narrative_static_preview_governance_audit_packet(
        preview_path=tmp_path / "missing.json",
        preview_markdown_path=tmp_path / "missing.md",
    )
    assert missing["final_status"] == "NOT_COMPUTABLE"


def test_preview_hash_section_and_markdown_order_failures() -> None:
    bad_hash = _preview()
    bad_hash["preview_hash"] = "bad"
    assert any(f["category"] == "PREVIEW_HASH" for f in _audit(bad_hash)["findings"])

    bad_sections = _preview()
    bad_sections["preview_sections"] = list(reversed(PREVIEW_SECTIONS))
    bad_sections["preview_hash"] = canonical_hash({k: v for k, v in bad_sections.items() if k != "preview_hash"})
    assert any(f["category"] == "SECTION_ORDER" for f in _audit(bad_sections)["findings"])

    md = build_operator_narrative_static_preview_markdown(_preview()).replace("## export_bundle_summary", "## blockers", 1)
    assert any("markdown" in f["message"] for f in _audit(md=md)["findings"])


def test_passive_active_and_governance_failures() -> None:
    bad_url = _preview()
    bad_url["passive_references"]["bad"] = "https://example.test/a.json"
    bad_url["preview_hash"] = canonical_hash({k: v for k, v in bad_url.items() if k != "preview_hash"})
    assert any(f["category"] == "PASSIVE_REFERENCES" for f in _audit(bad_url)["findings"])

    active = _preview()
    active["command_url"] = "out/reports/operator_narrative_report_001.latest.json"
    active["preview_hash"] = canonical_hash({k: v for k, v in active.items() if k != "preview_hash"})
    assert any(f["category"] == "ACTIVE_SURFACE" for f in _audit(active)["findings"])

    gov = _preview()
    gov["governance_flags"]["preview_only"] = False
    gov["governance_flags"]["button_allowed"] = True
    gov["preview_hash"] = canonical_hash({k: v for k, v in gov.items() if k != "preview_hash"})
    findings = _audit(gov)["findings"]
    assert any("affirm flag" in f["message"] for f in findings)
    assert any("deny flag" in f["message"] for f in findings)


def test_language_boundary_and_governance_key_exclusions() -> None:
    clean = _audit()
    assert clean["final_status"] == "PASS"

    prose = _preview()
    prose["blocker_summary"] = ["operator should do hidden work"]
    prose["preview_hash"] = canonical_hash({k: v for k, v in prose.items() if k != "preview_hash"})
    assert any(f["category"] == "LANGUAGE_BOUNDARY" for f in _audit(prose)["findings"])


def test_registry_writer_and_schema(tmp_path: Path) -> None:
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    emap = {entry.artifact_path: entry for entry in registry.entries}
    for path in ("out/previews/operator_narrative_static_preview_001.latest.json", "out/previews/operator_narrative_static_preview_001.latest.md"):
        assert path in emap
        assert emap[path].determinism_class == "DERIVED_OPTIONAL"
        assert emap[path].authority_granted is False

    packet = _audit()
    out = tmp_path / "audit.json"
    write_operator_narrative_static_preview_governance_audit(out, packet)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")
    assert build_operator_narrative_static_preview_governance_audit_markdown(packet).endswith("\n")

    schema = json.loads(Path("contracts/operator_attention/operator_narrative_static_preview_governance_audit.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "OperatorNarrativeStaticPreviewGovernanceAudit.v1"
    assert schema["properties"]["patch_id"]["const"] == "PATCH-P49-OPERATOR-NARRATIVE-STATIC-PREVIEW-GOVERNANCE-AUDIT-001"
    assert schema["properties"]["audit_id"]["const"] == "operator_narrative_static_preview_governance_audit_001"
