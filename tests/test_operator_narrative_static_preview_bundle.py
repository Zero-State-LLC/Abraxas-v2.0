from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry
from core.operator_narrative_static_preview_bundle import (
    PREVIEW_SECTIONS,
    build_operator_narrative_static_preview_markdown,
    build_operator_narrative_static_preview_packet,
    write_operator_narrative_static_preview_bundle,
)


def _seed(tmp_path: Path) -> tuple[dict, dict, str, str]:
    bundle = {
        "final_status": "EXPORT_ONLY",
        "artifact_manifest": [{"artifact_id": "a", "role": "report_json", "path": "out/reports/operator_narrative_report_001.latest.json", "sha256": "h", "passive_reference_only": True}],
        "hash_inventory": {"a": "h"},
        "source_lineage_map": {"p42_report_hash": "x"},
        "governance_envelope": {"export_only": True},
        "bundle_hash": "bundle_hash",
        "blocker_summary": [],
    }
    audit = {"final_status": "PASS", "audit_posture": "CLEAN", "finding_counts": {"PASS": 1, "WARN": 0, "FAIL": 0}, "audit_hash": "audit_hash", "blocker_summary": []}
    eb_md = "passive export reference\n"
    ga_md = "passive governance audit reference\n"
    return bundle, audit, eb_md, ga_md


def test_status_ladder_and_stability(tmp_path: Path) -> None:
    bundle, audit, _, _ = _seed(tmp_path)
    pkt = build_operator_narrative_static_preview_packet(export_bundle_packet=bundle, governance_audit_packet=audit)
    assert pkt["final_status"] == "PREVIEW_ONLY" and pkt["preview_posture"] == "COMPLETE"
    assert pkt["preview_sections"] == PREVIEW_SECTIONS
    twin = build_operator_narrative_static_preview_packet(export_bundle_packet=deepcopy(bundle), governance_audit_packet=deepcopy(audit))
    assert pkt["preview_hash"] == twin["preview_hash"]

    degraded = build_operator_narrative_static_preview_packet(export_bundle_packet={**bundle, "final_status": "EXPORT_DEGRADED"}, governance_audit_packet=audit)
    assert degraded["final_status"] == "PREVIEW_DEGRADED"
    blocked = build_operator_narrative_static_preview_packet(export_bundle_packet=bundle, governance_audit_packet={**audit, "final_status": "FAIL"})
    assert blocked["final_status"] == "BLOCKED"
    nc = build_operator_narrative_static_preview_packet(export_bundle_path=tmp_path / "missing.json", governance_audit_path=tmp_path / "missing2.json")
    assert nc["final_status"] == "NOT_COMPUTABLE"


def test_markdown_language_order_registry_and_writer(tmp_path: Path) -> None:
    bundle, audit, _, _ = _seed(tmp_path)
    pkt = build_operator_narrative_static_preview_packet(export_bundle_packet=bundle, governance_audit_packet=audit)
    md = build_operator_narrative_static_preview_markdown(pkt)
    assert md.endswith("\n")
    idx = [md.index(f"## {s}") for s in PREVIEW_SECTIONS]
    assert idx == sorted(idx)

    low = md.lower()
    restricted = low.split("## governance_boundary")[0]
    for t in ["recommend", "should do", "forecast", "will happen", "readiness", "take action", "execute", "approve", "route", "mutate", "prediction", "next move"]:
        assert t not in restricted
    inherited_blocker = build_operator_narrative_static_preview_packet(
        export_bundle_packet={**bundle, "blocker_summary": ["forbidden phrase present: recommend", "forbidden phrase present: forecast"]},
        governance_audit_packet=audit,
    )
    assert inherited_blocker["blocker_summary"] == [
        "language boundary token present: indicate",
        "language boundary token present: projected-state",
    ]

    dump = json.dumps(pkt, sort_keys=True).lower()
    for t in ["command_url", "action_url", "<script"]:
        assert t not in dump

    out = tmp_path / "preview.json"
    write_operator_narrative_static_preview_bundle(out, pkt)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")

    schema = json.loads(Path("contracts/operator_attention/operator_narrative_static_preview_bundle.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "OperatorNarrativeStaticPreviewBundle.v1"

    reg = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    emap = {e.artifact_path: e for e in reg.entries}
    for p in ("out/previews/operator_narrative_static_preview_001.latest.json", "out/previews/operator_narrative_static_preview_001.latest.md"):
        assert p in emap
        assert emap[p].determinism_class == "DERIVED_OPTIONAL"
