from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry
from core.operator_narrative_static_archive_package_chain_closure_receipt import (
    SCHEMA_VERSION,
    build_operator_narrative_static_archive_package_chain_closure_receipt_packet,
    write_operator_narrative_static_archive_package_chain_closure_receipt,
)


def _load() -> tuple[dict, dict, dict, dict]:
    return (
        json.loads(Path("out/package/operator_narrative_static_archive_package_001.latest.json").read_text()),
        json.loads(Path("out/audit/operator_narrative_static_archive_package_governance_audit_001.latest.json").read_text()),
        json.loads(Path("out/audit/operator_narrative_static_archive_package_language_boundary_audit_001.latest.json").read_text()),
        json.loads(Path("out/audit/operator_narrative_static_archive_package_stability_receipt_001.latest.json").read_text()),
    )


def test_degraded_baseline() -> None:
    pkt = build_operator_narrative_static_archive_package_chain_closure_receipt_packet()
    assert pkt["final_status"] == "STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSURE_DEGRADED"


def test_not_computable_missing_p64() -> None:
    assert build_operator_narrative_static_archive_package_chain_closure_receipt_packet(p64_json_path="out/package/missing.json")["final_status"].endswith("NOT_COMPUTABLE")


def test_not_computable_missing_p65() -> None:
    assert build_operator_narrative_static_archive_package_chain_closure_receipt_packet(p65_json_path="out/audit/missing.json")["final_status"].endswith("NOT_COMPUTABLE")


def test_not_computable_missing_p66() -> None:
    assert build_operator_narrative_static_archive_package_chain_closure_receipt_packet(p66_json_path="out/audit/missing.json")["final_status"].endswith("NOT_COMPUTABLE")


def test_not_computable_missing_p67() -> None:
    assert build_operator_narrative_static_archive_package_chain_closure_receipt_packet(p67_json_path="out/audit/missing.json")["final_status"].endswith("NOT_COMPUTABLE")


def test_fail_cases(tmp_path: Path) -> None:
    p64, p65, p66, p67 = _load()

    p65b = deepcopy(p65)
    p65b["final_status"] = "PACKAGE_GOVERNANCE_AUDIT_FAIL"
    p = tmp_path / "p65.json"
    p.write_text(json.dumps(p65b), encoding="utf-8")
    assert build_operator_narrative_static_archive_package_chain_closure_receipt_packet(p65_json_path=p)["final_status"].endswith("FAIL")

    p66b = deepcopy(p66)
    p66b["final_status"] = "PACKAGE_LANGUAGE_BOUNDARY_FAIL"
    p = tmp_path / "p66.json"
    p.write_text(json.dumps(p66b), encoding="utf-8")
    assert build_operator_narrative_static_archive_package_chain_closure_receipt_packet(p66_json_path=p)["final_status"].endswith("FAIL")

    p67b = deepcopy(p67)
    p67b["final_status"] = "PACKAGE_STABILITY_RECEIPT_FAIL"
    p = tmp_path / "p67.json"
    p.write_text(json.dumps(p67b), encoding="utf-8")
    assert build_operator_narrative_static_archive_package_chain_closure_receipt_packet(p67_json_path=p)["final_status"].endswith("FAIL")

    p64b = deepcopy(p64)
    p64b["distribution_claims_allowed"] = True
    p = tmp_path / "p64.json"
    p.write_text(json.dumps(p64b), encoding="utf-8")
    assert build_operator_narrative_static_archive_package_chain_closure_receipt_packet(p64_json_path=p)["final_status"].endswith("FAIL")

    p64b = deepcopy(p64)
    p64b["artifact_role_order"] = []
    p = tmp_path / "p64r.json"
    p.write_text(json.dumps(p64b), encoding="utf-8")
    assert build_operator_narrative_static_archive_package_chain_closure_receipt_packet(p64_json_path=p)["final_status"].endswith("FAIL")

    p64b = deepcopy(p64)
    p64b["package_manifest"] = []
    p = tmp_path / "p64m.json"
    p.write_text(json.dumps(p64b), encoding="utf-8")
    assert build_operator_narrative_static_archive_package_chain_closure_receipt_packet(p64_json_path=p)["final_status"].endswith("FAIL")


def test_pass_fixture_and_determinism_and_writer(tmp_path: Path) -> None:
    p64, p65, p66, p67 = _load()
    p64["final_status"] = "PACKAGE_CREATED_STATIC"
    p64["blocker_preservation_summary"] = {"observed_blocker_count": 0, "observed_degraded_roles": [], "observed_blocker_hashes": [], "blocker_suppression_applied": False}
    p67["final_status"] = "PACKAGE_STABILITY_RECEIPT_PASS"
    p67["stability_posture"] = "PACKAGE_STABLE"
    p67["blocker_preservation_summary"] = deepcopy(p64["blocker_preservation_summary"])
    p64p = tmp_path / "p64.json"
    p64p.write_text(json.dumps(p64), encoding="utf-8")
    p67p = tmp_path / "p67.json"
    p67p.write_text(json.dumps(p67), encoding="utf-8")
    pkt = build_operator_narrative_static_archive_package_chain_closure_receipt_packet(p64_json_path=p64p, p67_json_path=p67p)
    assert pkt["final_status"] == "STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSURE_PASS"

    a = build_operator_narrative_static_archive_package_chain_closure_receipt_packet()
    b = build_operator_narrative_static_archive_package_chain_closure_receipt_packet()
    assert a["closure_hash"] == b["closure_hash"]
    out = tmp_path / "p68.json"
    write_operator_narrative_static_archive_package_chain_closure_receipt(out, a)
    assert out.read_text(encoding="utf-8").endswith("\n")
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")

    schema = json.loads(Path("contracts/operator_attention/operator_narrative_static_archive_package_chain_closure_receipt.v1.schema.json").read_text())
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION

    reg = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    emap = {e.artifact_path: e for e in reg.entries}
    assert emap["out/audit/operator_narrative_static_archive_package_chain_closure_receipt_001.latest.json"].determinism_class == "DERIVED_OPTIONAL"
    assert emap["out/audit/operator_narrative_static_archive_package_chain_closure_receipt_001.latest.md"].determinism_class == "DERIVED_OPTIONAL"
