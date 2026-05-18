from __future__ import annotations

import json
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry
from core.operator_narrative_export_bundle import (
    build_operator_narrative_export_bundle_markdown,
    build_operator_narrative_export_bundle_packet,
    write_operator_narrative_export_bundle_packet,
)


def _seed(tmp_path: Path) -> dict[str, str]:
    base = {
        "p42_report_json": ("report.json", {"final_status": "REPORT_ONLY", "report_hash": "h42", "source_hash_lineage": {"x": "1"}, "blocker_summary": []}),
        "p43_report_governance_audit_json": ("audit43.json", {"final_status": "PASS", "audit_hash": "h43", "blocker_summary": []}),
        "p44_ui_overlay_json": ("overlay44.json", {"final_status": "PROJECTION_ONLY", "overlay_hash": "h44", "source_hash_lineage": {"report_hash_ref": "h42"}, "blocker_summary": []}),
        "p45_ui_overlay_governance_audit_json": ("audit45.json", {"final_status": "PASS", "audit_hash": "h45", "source_hash_lineage": {"p44_overlay_hash": "h44"}, "blocker_summary": []}),
    }
    out: dict[str, str] = {}
    for k, (name, payload) in base.items():
        p = tmp_path / name
        p.write_text(json.dumps(payload), encoding="utf-8")
        out[k] = p.as_posix()
        md = p.with_suffix(".md")
        md.write_text(f"{k} passive reference\n", encoding="utf-8")
        out[k.replace("_json", "_markdown")] = md.as_posix()
    return out


def test_status_ladder_and_determinism(tmp_path: Path) -> None:
    src = _seed(tmp_path)
    pkt = build_operator_narrative_export_bundle_packet(source_artifact_paths=src)
    assert pkt["final_status"] == "EXPORT_ONLY" and pkt["export_posture"] == "COMPLETE"
    twin = build_operator_narrative_export_bundle_packet(source_artifact_paths=src)
    assert pkt["bundle_hash"] == twin["bundle_hash"]

    miss = dict(src)
    miss["p42_report_markdown"] = (tmp_path / "missing.md").as_posix()
    assert build_operator_narrative_export_bundle_packet(source_artifact_paths=miss)["final_status"] == "NOT_COMPUTABLE"

    bad = dict(src)
    corrupt = tmp_path / "bad.json"
    corrupt.write_text("{", encoding="utf-8")
    bad["p43_report_governance_audit_json"] = corrupt.as_posix()
    assert build_operator_narrative_export_bundle_packet(source_artifact_paths=bad)["final_status"] == "NOT_COMPUTABLE"


def test_blocked_degraded_manifest_and_markdown(tmp_path: Path) -> None:
    src = _seed(tmp_path)
    blocked_p43 = build_operator_narrative_export_bundle_packet(source_artifact_paths=src, source_packets={"p43_report_governance_audit_json": {"final_status": "FAIL", "audit_hash": "x", "blocker_summary": []}})
    assert blocked_p43["final_status"] == "BLOCKED"
    blocked_p45 = build_operator_narrative_export_bundle_packet(source_artifact_paths=src, source_packets={"p45_ui_overlay_governance_audit_json": {"final_status": "FAIL", "audit_hash": "x", "source_hash_lineage": {}, "blocker_summary": []}})
    assert blocked_p45["final_status"] == "BLOCKED"
    degraded = build_operator_narrative_export_bundle_packet(source_artifact_paths=src, source_packets={"p42_report_json": {"final_status": "REPORT_DEGRADED", "report_hash": "h42", "source_hash_lineage": {}, "blocker_summary": []}})
    assert degraded["final_status"] == "EXPORT_DEGRADED"

    roles = [x["role"] for x in degraded["artifact_manifest"]]
    assert roles == ["report_json", "report_markdown", "report_governance_audit_json", "report_governance_audit_markdown", "ui_overlay_json", "ui_overlay_markdown", "ui_overlay_governance_audit_json", "ui_overlay_governance_audit_markdown"]
    assert list(degraded["hash_inventory"].keys()) == [x["artifact_id"] for x in degraded["artifact_manifest"]]
    for m in degraded["artifact_manifest"]:
        assert m["passive_reference_only"] is True

    text = build_operator_narrative_export_bundle_markdown(degraded).lower()
    for term in ["recommend", "should do", "forecast", "will happen", "readiness", "take action", "execute", "approve", "route", "mutate", "prediction", "next move"]:
        assert term not in text


def test_source_not_mutated_writer_schema_registry_and_newline(tmp_path: Path) -> None:
    src = _seed(tmp_path)
    before = Path(src["p42_report_json"]).read_text(encoding="utf-8")
    pkt = build_operator_narrative_export_bundle_packet(source_artifact_paths=src)
    after = Path(src["p42_report_json"]).read_text(encoding="utf-8")
    assert before == after

    for k, v in pkt["governance_flags"].items():
        if k in {"export_only", "passive_bundle_only", "read_only", "advisory_only", "non_authoritative", "source_linked", "deterministic_manifest"}:
            assert v is True
    assert pkt["governance_flags"]["command_channel"] is False
    assert "command_url" not in json.dumps(pkt, sort_keys=True)

    out = tmp_path / "bundle.json"
    write_operator_narrative_export_bundle_packet(out, pkt)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")

    schema = json.loads(Path("contracts/operator_attention/operator_narrative_export_bundle.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "OperatorNarrativeExportBundle.v1"

    reg = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    emap = {e.artifact_path: e for e in reg.entries}
    for p in ("out/exports/operator_narrative_export_bundle_001.latest.json", "out/exports/operator_narrative_export_bundle_001.latest.md"):
        assert p in emap
        assert emap[p].determinism_class == "DERIVED_OPTIONAL"
