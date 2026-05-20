from __future__ import annotations

import json
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry
from core.operator_narrative_static_archive_package_index_pointer_receipt import (
    build_operator_narrative_static_archive_package_index_pointer_receipt_markdown,
    build_operator_narrative_static_archive_package_index_pointer_receipt_packet,
    write_operator_narrative_static_archive_package_index_pointer_receipt,
)


def _base_packets(degraded: bool = True) -> dict[str, dict]:
    b = {"observed_degraded_roles": ["x"] if degraded else [], "observed_blocker_count": 1 if degraded else 0}
    return {
        "P64": {"final_status": "STATIC_ARCHIVE_PACKAGE_DEGRADED" if degraded else "STATIC_ARCHIVE_PACKAGE_PASS", "blocker_preservation_summary": b},
        "P65": {"final_status": "PACKAGE_GOVERNANCE_AUDIT_PASS", "audit_posture": "PACKAGE_GOVERNANCE_CLEAN"},
        "P66": {"final_status": "PACKAGE_LANGUAGE_BOUNDARY_PASS", "audit_posture": "LANGUAGE_BOUNDARY_CLEAN"},
        "P67": {"final_status": "PACKAGE_STABILITY_RECEIPT_DEGRADED" if degraded else "PACKAGE_STABILITY_RECEIPT_PASS", "stability_posture": "PACKAGE_STABLE_WITH_OBSERVED_BLOCKERS" if degraded else "PACKAGE_STABLE", "blocker_preservation_summary": b},
        "P68": {"final_status": "STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSURE_DEGRADED", "closure_posture": "STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSED_WITH_OBSERVED_BLOCKERS", "blocker_preservation_summary": b},
    }


def test_expected_degraded_baseline():
    pkt = build_operator_narrative_static_archive_package_index_pointer_receipt_packet(upstream_packets=_base_packets())
    assert pkt["final_status"] == "STATIC_ARCHIVE_PACKAGE_INDEX_POINTER_DEGRADED"


def test_pass_baseline():
    base = _base_packets(degraded=False)
    base["P68"]["final_status"] = "STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSURE_DEGRADED"
    base["P68"]["closure_posture"] = "STATIC_ARCHIVE_PACKAGE_CHAIN_CLOSED_WITH_OBSERVED_BLOCKERS"
    pkt = build_operator_narrative_static_archive_package_index_pointer_receipt_packet(upstream_packets=base)
    assert pkt["final_status"] in {"STATIC_ARCHIVE_PACKAGE_INDEX_POINTER_DEGRADED", "STATIC_ARCHIVE_PACKAGE_INDEX_POINTER_PASS"}


def test_missing_surface_not_computable():
    for sid in ["P64", "P65", "P66", "P67", "P68"]:
        b = _base_packets()
        del b[sid]
        pkt = build_operator_narrative_static_archive_package_index_pointer_receipt_packet(upstream_packets=b)
        assert pkt["final_status"] == "STATIC_ARCHIVE_PACKAGE_INDEX_POINTER_NOT_COMPUTABLE"


def test_fail_cases_and_hash_repeatability(tmp_path: Path):
    b = _base_packets()
    b["P68"]["closure_posture"] = "BAD"
    pkt = build_operator_narrative_static_archive_package_index_pointer_receipt_packet(upstream_packets=b)
    assert pkt["final_status"] == "STATIC_ARCHIVE_PACKAGE_INDEX_POINTER_FAIL"

    a = build_operator_narrative_static_archive_package_index_pointer_receipt_packet(upstream_packets=_base_packets())
    c = build_operator_narrative_static_archive_package_index_pointer_receipt_packet(upstream_packets=_base_packets())
    assert a["index_hash"] == c["index_hash"]

    out = tmp_path / "p69.json"
    write_operator_narrative_static_archive_package_index_pointer_receipt(out, a)
    assert out.read_text(encoding="utf-8").endswith("\n")
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")
    assert build_operator_narrative_static_archive_package_index_pointer_receipt_markdown(a).endswith("\n")


def test_schema_constants_and_registry():
    schema = json.loads(Path("contracts/operator_attention/operator_narrative_static_archive_package_index_pointer_receipt.v1.schema.json").read_text())
    assert schema["properties"]["artifact_type"]["const"] == "static_archive_package_index_pointer_receipt"
    emap = {e.artifact_path: e for e in build_generated_artifact_registry().entries}
    assert emap["out/audit/operator_narrative_static_archive_package_index_pointer_receipt_001.latest.json"].determinism_class == "DERIVED_OPTIONAL"
    assert emap["out/audit/operator_narrative_static_archive_package_index_pointer_receipt_001.latest.md"].determinism_class == "DERIVED_OPTIONAL"
