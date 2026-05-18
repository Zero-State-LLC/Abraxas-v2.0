from __future__ import annotations

import json
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry, list_ci_drift_artifact_paths
from core.operator_narrative_report import build_operator_narrative_report_packet, write_operator_narrative_report_packet
from core.operator_narrative_report_governance_audit import build_operator_narrative_report_governance_audit
from core.operator_narrative_report_ui_overlay import (
    build_operator_narrative_report_ui_overlay_markdown,
    build_operator_narrative_report_ui_overlay_packet,
    write_operator_narrative_report_ui_overlay_packet,
)


def _seed(tmp_path: Path) -> tuple[Path, Path, Path, dict, dict]:
    report = build_operator_narrative_report_packet()
    report["final_status"] = "REPORT_ONLY"
    report["report_posture"] = "CLEAR"
    report["blocker_summary"] = []
    rj = tmp_path / "report.json"
    write_operator_narrative_report_packet(rj, report)
    audit = build_operator_narrative_report_governance_audit(report_packet=report, report_markdown=rj.with_suffix('.md').read_text(encoding='utf-8'))
    audit["final_status"] = "PASS"
    audit["audit_posture"] = "CLEAN"
    aj = tmp_path / "audit.json"
    aj.write_text(json.dumps(audit), encoding="utf-8")
    return rj, rj.with_suffix('.md'), aj, report, audit


def test_overlay_happy_path_and_determinism(tmp_path: Path) -> None:
    rj, rm, aj, report, audit = _seed(tmp_path)
    pkt = build_operator_narrative_report_ui_overlay_packet(report_json_path=rj, report_markdown_path=rm, audit_json_path=aj)
    pkt2 = build_operator_narrative_report_ui_overlay_packet(report_packet=report, audit_packet=audit, report_json_path=rj, audit_json_path=aj, report_markdown_path=rm)
    assert pkt["final_status"] == "PROJECTION_ONLY"
    assert pkt["overlay_hash"] == pkt2["overlay_hash"]
    assert [x["section_id"] for x in pkt["section_navigation"]] == [s["section_id"] for s in report["report_sections"]]
    assert pkt["passive_references"][0]["reference_type"] == "passive_path"


def test_status_ladder(tmp_path: Path) -> None:
    rj, rm, aj, report, audit = _seed(tmp_path)
    report["final_status"] = "REPORT_DEGRADED"
    assert build_operator_narrative_report_ui_overlay_packet(report_packet=report, audit_packet=audit, report_markdown_path=rm)["final_status"] == "PROJECTION_DEGRADED"
    audit["final_status"] = "FAIL"
    assert build_operator_narrative_report_ui_overlay_packet(report_packet=report, audit_packet=audit, report_markdown_path=rm)["final_status"] == "BLOCKED"
    assert build_operator_narrative_report_ui_overlay_packet(report_json_path=tmp_path/'missing.json', audit_json_path=aj)["final_status"] == "NOT_COMPUTABLE"
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    assert build_operator_narrative_report_ui_overlay_packet(report_json_path=rj, audit_json_path=bad)["final_status"] == "NOT_COMPUTABLE"


def test_sorting_ids_markdown_schema_and_registry(tmp_path: Path) -> None:
    rj, rm, aj, _, _ = _seed(tmp_path)
    pkt = build_operator_narrative_report_ui_overlay_packet(report_json_path=rj, report_markdown_path=rm, audit_json_path=aj)
    assert [x["layer_id"] for x in pkt["render_layers"]] == sorted(x["layer_id"] for x in pkt["render_layers"])
    assert [x["node_id"] for x in pkt["overlay_nodes"]] == sorted(x["node_id"] for x in pkt["overlay_nodes"])
    assert [x["card_id"] for x in pkt["overlay_cards"]] == sorted(x["card_id"] for x in pkt["overlay_cards"])
    assert [x["badge_id"] for x in pkt["overlay_badges"]] == sorted(x["badge_id"] for x in pkt["overlay_badges"])
    assert [x["edge_id"] for x in pkt["overlay_edges"]] == sorted(x["edge_id"] for x in pkt["overlay_edges"])
    text = build_operator_narrative_report_ui_overlay_markdown(pkt).lower()
    for term in ["recommend", "should do", "forecast", "will happen", "readiness", "take action", "execute", "approve", "route", "mutate", "prediction", "next move"]:
        assert term not in text
    assert "command_url" in pkt["passive_references"][0] and pkt["passive_references"][0]["command_url"] == ""
    out = tmp_path / "overlay.json"
    write_operator_narrative_report_ui_overlay_packet(out, pkt)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")
    schema = json.loads(Path("contracts/operator_attention/operator_narrative_report_ui_overlay.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "OperatorNarrativeReportUIOverlay.v1"

    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    entry_map = {e.artifact_path: e for e in registry.entries}
    for p in ("out/projections/operator_narrative_report_ui_overlay_001.latest.json", "out/projections/operator_narrative_report_ui_overlay_001.latest.md"):
        assert entry_map[p].determinism_class == "DERIVED_OPTIONAL"
    ci = set(list_ci_drift_artifact_paths(registry))
    assert "out/projections/operator_narrative_report_ui_overlay_001.latest.json" not in ci
