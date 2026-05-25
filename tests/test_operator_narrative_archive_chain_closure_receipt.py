from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry
from core.operator_narrative_archive_chain_closure_receipt import (
    PATCH_ID,
    RECEIPT_ID,
    SCHEMA_VERSION,
    build_operator_narrative_archive_chain_closure_receipt_packet,
    write_operator_narrative_archive_chain_closure_receipt,
)


def _p52(degraded: bool = False) -> dict:
    return {
        "final_status": "ARCHIVE_INDEX_DEGRADED" if degraded else "ARCHIVE_INDEX_ONLY",
        "archive_posture": "DEGRADED" if degraded else "COMPLETE",
        "archive_index_hash": "a" * 64,
        "artifact_role_order": [
            "p46_export_bundle_json","p46_export_bundle_markdown","p47_export_bundle_governance_audit_json","p47_export_bundle_governance_audit_markdown",
            "p48_static_preview_json","p48_static_preview_markdown","p49_static_preview_governance_audit_json","p49_static_preview_governance_audit_markdown",
        ],
        "governance_flags": {"archive_index_only": True, "passive_index_only": True, "read_only": True, "non_authoritative": True, "source_linked": True, "deterministic_manifest": True, "advisory_only": True,
            **{k: False for k in ["package_created","distribution_claims_allowed","command_authority","ui_command_authority","action_authority","recommendation_authority","inference_authority","prediction_allowed","forecast_authority","trend_prediction_allowed","readiness_claims_allowed","mutation_allowed","authority_granted","execution_authority","routing_change_allowed","queue_mutation_allowed","canon_mutation_allowed","runtime_mutation_allowed","adaptive_behavior_allowed","psychological_claims_allowed","speculative_causation_allowed","auto_execute","auto_approve","command_channel","bidirectional_control","script_allowed","html_script_allowed","external_fetch_allowed","form_allowed","button_allowed"]}},
        "provenance": {"raw_blocker_count": 1 if degraded else 0, "raw_blocker_hashes": ["b" * 64] if degraded else [], "display_blocker_summary_normalized": True},
        "blocker_summary": ["upstream observed blocker"] if degraded else [],
    }


def _p53() -> dict:
    return {
        "final_status": "PASS",
        "audit_posture": "CLEAN",
        "audit_hash": "c" * 64,
        "finding_counts": {"PASS": 1, "WARN": 0, "FAIL": 0},
        "findings": [],
        "governance_flags": {"audit_only": True, "advisory_only": True, "read_only": True, "non_authoritative": True, "archive_index_governance_audit_only": True, "source_linked": True, "deterministic_audit": True,
            **{k: False for k in ["package_created","distribution_claims_allowed","command_authority","ui_command_authority","action_authority","recommendation_authority","inference_authority","prediction_allowed","forecast_authority","trend_prediction_allowed","readiness_claims_allowed","mutation_allowed","authority_granted","execution_authority","routing_change_allowed","queue_mutation_allowed","canon_mutation_allowed","runtime_mutation_allowed","adaptive_behavior_allowed","psychological_claims_allowed","speculative_causation_allowed","auto_execute","auto_approve","command_channel","bidirectional_control","script_allowed","html_script_allowed","external_fetch_allowed","form_allowed","button_allowed"]}},
    }


def test_only_and_degraded_statuses() -> None:
    assert build_operator_narrative_archive_chain_closure_receipt_packet(archive_index_packet=_p52(False), archive_audit_packet=_p53())["final_status"] == "CLOSURE_RECEIPT_ONLY"
    p = build_operator_narrative_archive_chain_closure_receipt_packet(archive_index_packet=_p52(True), archive_audit_packet=_p53())
    assert p["final_status"] == "CLOSURE_RECEIPT_DEGRADED"
    assert p["closure_posture"] == "SEALED_WITH_OBSERVED_BLOCKERS"


def test_not_computable_missing_sources(tmp_path: Path) -> None:
    p = build_operator_narrative_archive_chain_closure_receipt_packet(archive_index_json_path=tmp_path / "x.json", archive_audit_json_path=tmp_path / "y.json")
    assert p["final_status"] == "NOT_COMPUTABLE"


def test_fail_invariant_paths() -> None:
    bad = _p53()
    bad["final_status"] = "FAIL"
    assert build_operator_narrative_archive_chain_closure_receipt_packet(archive_index_packet=_p52(), archive_audit_packet=bad)["final_status"] == "FAIL"
    bad52 = _p52()
    bad52["artifact_role_order"] = []
    assert build_operator_narrative_archive_chain_closure_receipt_packet(archive_index_packet=bad52, archive_audit_packet=_p53())["final_status"] == "FAIL"


def test_more_failures() -> None:
    p52 = _p52()
    p52.pop("archive_index_hash")
    assert build_operator_narrative_archive_chain_closure_receipt_packet(archive_index_packet=p52, archive_audit_packet=_p53())["final_status"] == "FAIL"
    p53 = _p53()
    p53.pop("audit_hash")
    assert build_operator_narrative_archive_chain_closure_receipt_packet(archive_index_packet=_p52(), archive_audit_packet=p53)["final_status"] == "FAIL"
    p52 = _p52(True)
    p52["provenance"].pop("raw_blocker_hashes")
    assert build_operator_narrative_archive_chain_closure_receipt_packet(archive_index_packet=p52, archive_audit_packet=_p53())["final_status"] == "FAIL"


def test_p51_reintroduced_and_package_flags() -> None:
    p52 = _p52(True)
    p52["blocker_summary"] = ["source_missing:p42_report_json"]
    assert build_operator_narrative_archive_chain_closure_receipt_packet(archive_index_packet=p52, archive_audit_packet=_p53())["final_status"] == "FAIL"
    p52 = _p52()
    p52["governance_flags"]["package_created"] = True
    assert build_operator_narrative_archive_chain_closure_receipt_packet(archive_index_packet=p52, archive_audit_packet=_p53())["final_status"] == "FAIL"


def test_determinism_writer_schema_and_registry(tmp_path: Path) -> None:
    a = build_operator_narrative_archive_chain_closure_receipt_packet(archive_index_packet=_p52(), archive_audit_packet=_p53())
    b = build_operator_narrative_archive_chain_closure_receipt_packet(archive_index_packet=deepcopy(_p52()), archive_audit_packet=deepcopy(_p53()))
    assert a["closure_hash"] == b["closure_hash"]
    out = tmp_path / "closure.json"
    write_operator_narrative_archive_chain_closure_receipt(out, a)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")

    schema = json.loads(Path("contracts/operator_attention/operator_narrative_archive_chain_closure_receipt.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION
    assert schema["properties"]["patch_id"]["const"] == PATCH_ID
    assert schema["properties"]["receipt_id"]["const"] == RECEIPT_ID

    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    emap = {e.artifact_path: e for e in registry.entries}
    assert emap["out/audit/operator_narrative_archive_chain_closure_receipt_001.latest.json"].determinism_class == "DERIVED_OPTIONAL"
    assert emap["out/audit/operator_narrative_archive_chain_closure_receipt_001.latest.md"].determinism_class == "DERIVED_OPTIONAL"
