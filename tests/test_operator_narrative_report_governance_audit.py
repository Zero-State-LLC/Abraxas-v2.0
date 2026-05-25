from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry, list_ci_drift_artifact_paths
from core.operator_narrative_report import build_operator_narrative_report_packet, write_operator_narrative_report_packet
from core.operator_narrative_report_governance_audit import (
    build_operator_narrative_report_governance_audit,
    build_operator_narrative_report_governance_audit_markdown,
    write_operator_narrative_report_governance_audit,
)


def _mk_report(tmp_path: Path) -> tuple[Path, Path, dict]:
    pkt = build_operator_narrative_report_packet()
    jp = tmp_path / "r.json"
    write_operator_narrative_report_packet(jp, pkt)
    return jp, jp.with_suffix(".md"), pkt


def test_pass_happy_path(tmp_path: Path) -> None:
    jp, mp, _ = _mk_report(tmp_path)
    a = build_operator_narrative_report_governance_audit(report_json_path=jp, report_markdown_path=mp)
    assert a["final_status"] == "PASS"
    assert a["audit_posture"] == "CLEAN"


def test_not_computable_missing_or_corrupt_sources(tmp_path: Path) -> None:
    jp, mp, _ = _mk_report(tmp_path)
    missing = build_operator_narrative_report_governance_audit(report_json_path=tmp_path / "missing.json", report_markdown_path=mp)
    assert missing["final_status"] == "NOT_COMPUTABLE"
    jp.write_text("{", encoding="utf-8")
    corrupt = build_operator_narrative_report_governance_audit(report_json_path=jp, report_markdown_path=mp)
    assert corrupt["final_status"] == "NOT_COMPUTABLE"
    no_md = build_operator_narrative_report_governance_audit(report_json_path=tmp_path / "missing.json", report_markdown_path=tmp_path / "missing.md")
    assert no_md["final_status"] == "NOT_COMPUTABLE"


def test_section_order_markdown_order_hash_lineage_and_flags(tmp_path: Path) -> None:
    jp, mp, pkt = _mk_report(tmp_path)
    bad = deepcopy(pkt)
    bad["report_sections"] = list(reversed(bad["report_sections"]))
    bad["report_hash"] = "x"
    a = build_operator_narrative_report_governance_audit(report_packet=bad, report_markdown=mp.read_text(encoding="utf-8"))
    assert a["final_status"] == "FAIL"

    bad2 = deepcopy(pkt)
    bad2["source_hash_lineage"] = {}
    bad2["governance_flags"]["action_authority"] = True
    bad2["recommendations"] = ["x"]
    md = mp.read_text(encoding="utf-8") + "\nnext move\n"
    b = build_operator_narrative_report_governance_audit(report_packet=bad2, report_markdown=md)
    assert b["final_status"] == "FAIL"


def test_findings_sort_hash_stability_non_mutating_and_writer(tmp_path: Path) -> None:
    jp, mp, pkt = _mk_report(tmp_path)
    original = deepcopy(pkt)
    first = build_operator_narrative_report_governance_audit(report_packet=pkt, report_markdown=mp.read_text(encoding="utf-8"))
    second = build_operator_narrative_report_governance_audit(report_packet=pkt, report_markdown=mp.read_text(encoding="utf-8"))
    assert first["audit_hash"] == second["audit_hash"]
    assert pkt == original

    sev = [f["severity"] for f in first["findings"]]
    assert sev == sorted(sev, key=lambda s: {"FAIL": 0, "WARN": 1, "PASS": 2}[s])

    out = tmp_path / "a.json"
    write_operator_narrative_report_governance_audit(out, first)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")
    assert build_operator_narrative_report_governance_audit_markdown(first).endswith("\n")


def test_schema_and_registry_classification() -> None:
    schema = json.loads(Path("contracts/operator_attention/operator_narrative_report_governance_audit.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "OperatorNarrativeReportGovernanceAudit.v1"

    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    entry_map = {e.artifact_path: e for e in registry.entries}
    for p in (
        "out/reports/operator_narrative_report_001.latest.json",
        "out/reports/operator_narrative_report_001.latest.md",
        "out/audit/operator_narrative_report_governance_audit_001.latest.json",
        "out/audit/operator_narrative_report_governance_audit_001.latest.md",
    ):
        assert entry_map[p].determinism_class == "DERIVED_OPTIONAL"
    ci = set(list_ci_drift_artifact_paths(registry))
    assert "out/reports/operator_narrative_report_001.latest.json" not in ci
    assert "out/reports/operator_narrative_report_001.latest.md" not in ci
