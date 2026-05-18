from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry
from core.operator_narrative_export_bundle import build_operator_narrative_export_bundle_packet
from core.operator_narrative_export_bundle_governance_audit import (
    build_operator_narrative_export_bundle_governance_audit_markdown,
    build_operator_narrative_export_bundle_governance_audit_packet,
    write_operator_narrative_export_bundle_governance_audit,
)


def _seed(tmp_path: Path) -> tuple[dict, str]:
    p42 = {"final_status": "REPORT_ONLY", "report_hash": "h42", "source_hash_lineage": {}, "blocker_summary": []}
    p43 = {"final_status": "PASS", "audit_hash": "h43", "blocker_summary": []}
    p44 = {"final_status": "PROJECTION_ONLY", "overlay_hash": "h44", "source_hash_lineage": {}, "blocker_summary": []}
    p45 = {"final_status": "PASS", "audit_hash": "h45", "source_hash_lineage": {}, "blocker_summary": []}
    src = {}
    for key, payload in {
        "p42_report_json": p42,
        "p43_report_governance_audit_json": p43,
        "p44_ui_overlay_json": p44,
        "p45_ui_overlay_governance_audit_json": p45,
    }.items():
        p = tmp_path / f"{key}.json"
        p.write_text(json.dumps(payload), encoding="utf-8")
        src[key] = p.as_posix()
        md = p.with_suffix(".md")
        md.write_text("passive reference only\n", encoding="utf-8")
        src[key.replace("_json", "_markdown")] = md.as_posix()
    bundle = build_operator_narrative_export_bundle_packet(source_artifact_paths=src)
    md = "# Export\n\nPassive references only.\n"
    return bundle, md


def test_pass_fail_not_computable_and_determinism(tmp_path: Path) -> None:
    bundle, md = _seed(tmp_path)
    packet = build_operator_narrative_export_bundle_governance_audit_packet(export_bundle_packet=bundle, export_bundle_markdown_text=md)
    assert packet["final_status"] == "PASS"
    assert packet["audit_posture"] == "CLEAN"
    twin = build_operator_narrative_export_bundle_governance_audit_packet(export_bundle_packet=deepcopy(bundle), export_bundle_markdown_text=md)
    assert packet["audit_hash"] == twin["audit_hash"]

    bad = deepcopy(bundle)
    bad["bundle_hash"] = "x"
    fail_packet = build_operator_narrative_export_bundle_governance_audit_packet(export_bundle_packet=bad, export_bundle_markdown_text=md)
    assert fail_packet["final_status"] == "FAIL"

    missing_packet = build_operator_narrative_export_bundle_governance_audit_packet(export_bundle_path=tmp_path / "missing.json", export_bundle_markdown_path=tmp_path / "missing.md")
    assert missing_packet["final_status"] == "NOT_COMPUTABLE"


def test_manifest_hash_governance_language_registry_and_writer(tmp_path: Path) -> None:
    bundle, md = _seed(tmp_path)
    packet = build_operator_narrative_export_bundle_governance_audit_packet(export_bundle_packet=bundle, export_bundle_markdown_text=md)
    assert packet["manifest_integrity_summary"]["observed_roles"] == packet["manifest_integrity_summary"]["required_roles"]
    assert packet["hash_inventory_summary"]["matches_manifest"] is True

    for k, v in packet["governance_flags"].items():
        if k in {"audit_only", "advisory_only", "non_authoritative", "export_governance_audit_only"}:
            assert v is True
        elif k in {"mutation_allowed", "authority_granted", "execution_authority", "inference_authority", "prediction_allowed", "forecast_authority", "trend_prediction_allowed", "readiness_claims_allowed", "recommendation_authority", "action_authority", "command_authority", "ui_command_authority", "adaptive_behavior_allowed", "routing_change_allowed", "queue_mutation_allowed", "canon_mutation_allowed", "runtime_mutation_allowed", "psychological_claims_allowed", "speculative_causation_allowed", "auto_execute", "auto_approve", "command_channel", "bidirectional_control"}:
            assert v is False

    lower = build_operator_narrative_export_bundle_governance_audit_markdown(packet).lower()
    for phrase in ["take action", "forecast", "readiness", "next move", "recommend"]:
        assert phrase not in lower

    out = tmp_path / "audit.json"
    write_operator_narrative_export_bundle_governance_audit(out, packet)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")

    schema = json.loads(Path("contracts/operator_attention/operator_narrative_export_bundle_governance_audit.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "OperatorNarrativeExportBundleGovernanceAudit.v1"

    reg = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    emap = {e.artifact_path: e for e in reg.entries}
    for p in (
        "out/exports/operator_narrative_export_bundle_001.latest.json",
        "out/exports/operator_narrative_export_bundle_001.latest.md",
        "out/audit/operator_narrative_export_bundle_governance_audit_001.latest.json",
        "out/audit/operator_narrative_export_bundle_governance_audit_001.latest.md",
    ):
        assert p in emap
        assert emap[p].determinism_class == "DERIVED_OPTIONAL"
