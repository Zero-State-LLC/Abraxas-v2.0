from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry
from core.operator_narrative_archive_chain_stability_receipt import (
    PATCH_ID,
    RECEIPT_ID,
    SCHEMA_VERSION,
    build_operator_narrative_archive_chain_stability_receipt_packet,
    write_operator_narrative_archive_chain_stability_receipt,
)


def _p52(degraded: bool = False) -> dict:
    return {
        "final_status": "ARCHIVE_INDEX_DEGRADED" if degraded else "ARCHIVE_INDEX_ONLY",
        "archive_index_hash": "a" * 64,
        "artifact_role_order": ["p46_export_bundle_json", "p46_export_bundle_markdown", "p47_export_bundle_governance_audit_json", "p47_export_bundle_governance_audit_markdown", "p48_static_preview_json", "p48_static_preview_markdown", "p49_static_preview_governance_audit_json", "p49_static_preview_governance_audit_markdown"],
        "governance_flags": {"archive_index_only": True, "passive_index_only": True, "read_only": True, "non_authoritative": True, "source_linked": True, "deterministic_manifest": True, "advisory_only": True, **{k: False for k in ["package_created", "distribution_claims_allowed", "command_authority", "ui_command_authority", "action_authority", "recommendation_authority", "inference_authority", "prediction_allowed", "forecast_authority", "trend_prediction_allowed", "readiness_claims_allowed", "mutation_allowed", "authority_granted", "execution_authority", "routing_change_allowed", "queue_mutation_allowed", "canon_mutation_allowed", "runtime_mutation_allowed", "adaptive_behavior_allowed", "psychological_claims_allowed", "speculative_causation_allowed", "auto_execute", "auto_approve", "command_channel", "bidirectional_control", "script_allowed", "html_script_allowed", "external_fetch_allowed", "form_allowed", "button_allowed"]}},
        "provenance": {"raw_blocker_count": 1 if degraded else 0, "raw_blocker_hashes": ["f" * 64] if degraded else []},
        "blocker_summary": ["observed blocker"] if degraded else [],
    }


def _p53() -> dict:
    return {"final_status": "PASS", "audit_posture": "CLEAN", "audit_hash": "b" * 64, "governance_flags": {"audit_only": True, "advisory_only": True, "read_only": True, "non_authoritative": True, "archive_index_governance_audit_only": True, "source_linked": True, "deterministic_audit": True, "package_created": False, "distribution_claims_allowed": False}}


def _p55(degraded: bool = False) -> dict:
    return {"final_status": "CLOSURE_RECEIPT_DEGRADED" if degraded else "CLOSURE_RECEIPT_ONLY", "closure_posture": "SEALED_WITH_OBSERVED_BLOCKERS" if degraded else "SEALED", "closure_hash": "c" * 64, "governance_flags": {"closure_receipt_only": True, "advisory_only": True, "read_only": True, "non_authoritative": True, "source_linked": True, "deterministic_receipt": True, "archive_chain_closure_only": True, "blocker_preservation_checked": True, "package_created": False, "distribution_claims_allowed": False}}


def _replays(p52: dict, p53: dict, p55: dict) -> list[dict]:
    return [{"p52": deepcopy(p52), "p53": deepcopy(p53), "p55": deepcopy(p55)} for _ in range(3)]


def test_stability_only_and_degraded(tmp_path: Path) -> None:
    p52 = tmp_path / "p52.json"
    p53 = tmp_path / "p53.json"
    p55 = tmp_path / "p55.json"
    p52.write_text(json.dumps(_p52()), encoding="utf-8")
    p53.write_text(json.dumps(_p53()), encoding="utf-8")
    p55.write_text(json.dumps(_p55()), encoding="utf-8")
    pkt = build_operator_narrative_archive_chain_stability_receipt_packet(
        archive_index_json_path=p52,
        archive_audit_json_path=p53,
        archive_closure_json_path=p55,
        replay_runs=_replays(_p52(), _p53(), _p55()),
    )
    assert pkt["final_status"] == "STABILITY_RECEIPT_ONLY"

    p52.write_text(json.dumps(_p52(True)), encoding="utf-8")
    p55.write_text(json.dumps(_p55(True)), encoding="utf-8")
    d = build_operator_narrative_archive_chain_stability_receipt_packet(
        archive_index_json_path=p52,
        archive_audit_json_path=p53,
        archive_closure_json_path=p55,
        replay_runs=_replays(_p52(True), _p53(), _p55(True)),
    )
    assert d["final_status"] == "STABILITY_RECEIPT_DEGRADED"


def test_not_computable_missing_sources(tmp_path: Path) -> None:
    pkt = build_operator_narrative_archive_chain_stability_receipt_packet(archive_index_json_path=tmp_path / "x", archive_audit_json_path=tmp_path / "y", archive_closure_json_path=tmp_path / "z")
    assert pkt["final_status"] == "NOT_COMPUTABLE"


def test_failures() -> None:
    p52, p53, p55 = _p52(), _p53(), _p55()
    runs = _replays(p52, p53, p55)
    runs[1]["p52"]["archive_index_hash"] = "x"
    assert build_operator_narrative_archive_chain_stability_receipt_packet(replay_runs=runs)["final_status"] == "FAIL"

    runs = _replays(p52, p53, p55)
    runs[1]["p53"]["audit_hash"] = "x"
    assert build_operator_narrative_archive_chain_stability_receipt_packet(replay_runs=runs)["final_status"] == "FAIL"

    runs = _replays(p52, p53, p55)
    runs[1]["p55"]["closure_hash"] = "x"
    assert build_operator_narrative_archive_chain_stability_receipt_packet(replay_runs=runs)["final_status"] == "FAIL"

    bad = _p52()
    bad["artifact_role_order"] = []
    assert build_operator_narrative_archive_chain_stability_receipt_packet(replay_runs=_replays(bad, p53, p55))["final_status"] == "FAIL"


def test_more_failures_and_determinism(tmp_path: Path) -> None:
    p53 = _p53()
    p53["final_status"] = "FAIL"
    assert build_operator_narrative_archive_chain_stability_receipt_packet(replay_runs=_replays(_p52(), p53, _p55()))["final_status"] == "FAIL"
    p55 = _p55()
    p55["closure_posture"] = "FAILED"
    assert build_operator_narrative_archive_chain_stability_receipt_packet(replay_runs=_replays(_p52(), _p53(), p55))["final_status"] == "FAIL"
    p52 = _p52(True)
    p52["provenance"].pop("raw_blocker_hashes")
    assert build_operator_narrative_archive_chain_stability_receipt_packet(replay_runs=_replays(p52, _p53(), _p55(True)))["final_status"] == "FAIL"
    p52 = _p52(True)
    p52["blocker_summary"] = ["source_missing:p42_report_json"]
    assert build_operator_narrative_archive_chain_stability_receipt_packet(replay_runs=_replays(p52, _p53(), _p55(True)))["final_status"] == "FAIL"

    a = build_operator_narrative_archive_chain_stability_receipt_packet(replay_runs=_replays(_p52(), _p53(), _p55()))
    b = build_operator_narrative_archive_chain_stability_receipt_packet(replay_runs=_replays(_p52(), _p53(), _p55()))
    assert a["stability_hash"] == b["stability_hash"]
    out = tmp_path / "p56.json"
    write_operator_narrative_archive_chain_stability_receipt(out, a)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")

    schema = json.loads(Path("contracts/operator_attention/operator_narrative_archive_chain_stability_receipt.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION
    assert schema["properties"]["patch_id"]["const"] == PATCH_ID
    assert schema["properties"]["receipt_id"]["const"] == RECEIPT_ID

    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    emap = {e.artifact_path: e for e in registry.entries}
    assert emap["out/audit/operator_narrative_archive_chain_stability_receipt_001.latest.json"].determinism_class == "DERIVED_OPTIONAL"
    assert emap["out/audit/operator_narrative_archive_chain_stability_receipt_001.latest.md"].determinism_class == "DERIVED_OPTIONAL"
