from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry
from core.operator_narrative_static_archive_package_stability_receipt import (
    PATCH_ID,
    RECEIPT_ID,
    SCHEMA_VERSION,
    build_operator_narrative_static_archive_package_stability_receipt_packet,
    write_operator_narrative_static_archive_package_stability_receipt,
)


def _replays(p64: dict, p65: dict, p66: dict) -> list[dict]:
    return [{"p64": deepcopy(p64), "p65": deepcopy(p65), "p66": deepcopy(p66)} for _ in range(3)]


def test_degraded_current_surface() -> None:
    pkt = build_operator_narrative_static_archive_package_stability_receipt_packet()
    # P57 manifest hash drift surfaces FAIL (not DEGRADED) until operator archive re-seal.
    assert pkt["final_status"] == "PACKAGE_STABILITY_RECEIPT_FAIL"


def test_not_computable_missing() -> None:
    pkt = build_operator_narrative_static_archive_package_stability_receipt_packet(p64_json_path="out/package/missing.json")
    assert pkt["final_status"] == "NOT_COMPUTABLE"


def test_failures_from_replay() -> None:
    p64 = json.loads(Path("out/package/operator_narrative_static_archive_package_001.latest.json").read_text())
    p65 = json.loads(Path("out/audit/operator_narrative_static_archive_package_governance_audit_001.latest.json").read_text())
    p66 = json.loads(Path("out/audit/operator_narrative_static_archive_package_language_boundary_audit_001.latest.json").read_text())

    runs = _replays(p64, p65, p66)
    runs[1]["p64"]["package_hash"] = "x"
    assert build_operator_narrative_static_archive_package_stability_receipt_packet(replay_runs=runs)["final_status"] == "PACKAGE_STABILITY_RECEIPT_FAIL"

    runs = _replays(p64, p65, p66)
    runs[1]["p65"]["audit_hash"] = "x"
    assert build_operator_narrative_static_archive_package_stability_receipt_packet(replay_runs=runs)["final_status"] == "PACKAGE_STABILITY_RECEIPT_FAIL"

    runs = _replays(p64, p65, p66)
    runs[1]["p66"]["audit_hash"] = "x"
    assert build_operator_narrative_static_archive_package_stability_receipt_packet(replay_runs=runs)["final_status"] == "PACKAGE_STABILITY_RECEIPT_FAIL"



def test_fail_when_distribution_flag_true_in_source(tmp_path: Path) -> None:
    p64 = json.loads(Path("out/package/operator_narrative_static_archive_package_001.latest.json").read_text())
    p64["distribution_claims_allowed"] = True
    p = tmp_path / "p64.json"
    p.write_text(json.dumps(p64), encoding="utf-8")
    m = tmp_path / "p64.md"
    m.write_text("# p64\n", encoding="utf-8")
    pkt = build_operator_narrative_static_archive_package_stability_receipt_packet(p64_json_path=p, p64_md_path=m)
    assert pkt["final_status"] == "PACKAGE_STABILITY_RECEIPT_FAIL"

def test_more_failures_schema_registry_and_writer(tmp_path: Path) -> None:
    p64 = json.loads(Path("out/package/operator_narrative_static_archive_package_001.latest.json").read_text())
    p65 = json.loads(Path("out/audit/operator_narrative_static_archive_package_governance_audit_001.latest.json").read_text())
    p66 = json.loads(Path("out/audit/operator_narrative_static_archive_package_language_boundary_audit_001.latest.json").read_text())

    bad = deepcopy(p64)
    bad["artifact_role_order"] = []
    assert build_operator_narrative_static_archive_package_stability_receipt_packet(replay_runs=_replays(bad, p65, p66))["final_status"] == "PACKAGE_STABILITY_RECEIPT_FAIL"


    bad65 = deepcopy(p65)
    bad65["final_status"] = "PACKAGE_GOVERNANCE_AUDIT_FAIL"
    assert build_operator_narrative_static_archive_package_stability_receipt_packet(replay_runs=_replays(p64, bad65, p66))["final_status"] == "PACKAGE_STABILITY_RECEIPT_FAIL"

    bad66 = deepcopy(p66)
    bad66["final_status"] = "PACKAGE_LANGUAGE_BOUNDARY_FAIL"
    assert build_operator_narrative_static_archive_package_stability_receipt_packet(replay_runs=_replays(p64, p65, bad66))["final_status"] == "PACKAGE_STABILITY_RECEIPT_FAIL"

    a = build_operator_narrative_static_archive_package_stability_receipt_packet(replay_runs=_replays(p64, p65, p66))
    b = build_operator_narrative_static_archive_package_stability_receipt_packet(replay_runs=_replays(p64, p65, p66))
    assert a["stability_hash"] == b["stability_hash"]

    out = tmp_path / "p67.json"
    write_operator_narrative_static_archive_package_stability_receipt(out, a)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")

    schema = json.loads(Path("contracts/operator_attention/operator_narrative_static_archive_package_stability_receipt.v1.schema.json").read_text())
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION
    assert schema["properties"]["patch_id"]["const"] == PATCH_ID
    assert schema["properties"]["receipt_id"]["const"] == RECEIPT_ID

    reg = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    emap = {e.artifact_path: e for e in reg.entries}
    assert emap["out/audit/operator_narrative_static_archive_package_stability_receipt_001.latest.json"].determinism_class == "DERIVED_OPTIONAL"
    assert emap["out/audit/operator_narrative_static_archive_package_stability_receipt_001.latest.md"].determinism_class == "DERIVED_OPTIONAL"
