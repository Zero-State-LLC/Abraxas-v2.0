from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.canonical.json import canonical_hash
from core.operator_narrative_report_ui_overlay_governance_audit import (
    build_operator_narrative_report_ui_overlay_governance_audit,
    build_operator_narrative_report_ui_overlay_governance_audit_markdown,
)


def _packets():
    report = {
        "report_sections": [{"section_id": "a"}, {"section_id": "b"}],
        "report_hash": "h42",
    }
    overlay = {
        "section_navigation": [{"section_id": "a"}, {"section_id": "b"}],
        "render_layers": [{"layer_id": "a"}],
        "overlay_nodes": [{"node_id": "a"}],
        "overlay_cards": [{"card_id": "a"}],
        "overlay_badges": [{"badge_id": "a"}],
        "overlay_edges": [{"edge_id": "a"}],
        "passive_references": [{"reference_type": "passive_path", "command_url": ""}],
        "source_hash_lineage": {"report_hash_ref": "h42"},
        "governance_flags": {"advisory_only": True, "projection_only": True, "read_only": True, "report_overlay_only": True, "render_consumer_only": True, "non_authoritative": True, "source_linked": True},
    }
    for k in ["inference_authority", "prediction_allowed", "forecast_authority", "trend_prediction_allowed", "readiness_claims_allowed", "adaptive_behavior_allowed", "psychological_claims_allowed", "speculative_causation_allowed", "command_channel", "action_authority", "recommendation_authority", "execution_authority", "routing_change_allowed", "queue_mutation_allowed", "canon_mutation_allowed", "runtime_mutation_allowed", "authority_granted", "auto_execute", "auto_approve", "bidirectional_control"]:
        overlay["governance_flags"][k] = False
    tmp = deepcopy(overlay)
    overlay["overlay_hash"] = canonical_hash(tmp)
    return overlay, report, {"audit_hash": "h43"}


def test_paths_and_hash_and_schema():
    o, r, a = _packets()
    pkt = build_operator_narrative_report_ui_overlay_governance_audit(overlay_packet=o, report_packet=r, report_audit_packet=a)
    assert pkt["final_status"] in {"PASS", "WARN", "FAIL", "NOT_COMPUTABLE"}
    assert pkt["audit_hash"]
    twin = build_operator_narrative_report_ui_overlay_governance_audit(overlay_packet=o, report_packet=r, report_audit_packet=a)
    assert twin["audit_hash"] == pkt["audit_hash"]
    assert build_operator_narrative_report_ui_overlay_governance_audit_markdown(pkt).endswith("\n")
    schema = json.loads(Path("contracts/operator_attention/operator_narrative_report_ui_overlay_governance_audit.v1.schema.json").read_text())
    assert schema["properties"]["schema_version"]["const"] == "OperatorNarrativeReportUIOverlayGovernanceAudit.v1"


def test_fail_warn_not_computable_and_immutability():
    o, r, a = _packets()
    src = deepcopy(o)
    bad = deepcopy(o)
    bad["overlay_hash"] = "x"
    pkt = build_operator_narrative_report_ui_overlay_governance_audit(overlay_packet=bad, report_packet=r, report_audit_packet=a)
    assert pkt["final_status"] == "FAIL"
    warn = deepcopy(o)
    warn.pop("overlay_hash")
    wp = build_operator_narrative_report_ui_overlay_governance_audit(overlay_packet=warn, report_packet=r, report_audit_packet=a)
    assert wp["final_status"] in {"WARN", "FAIL"}
    np = build_operator_narrative_report_ui_overlay_governance_audit(overlay_path=Path("missing.json"), report_packet=r, report_audit_packet=a)
    assert np["final_status"] == "NOT_COMPUTABLE"
    assert o == src
