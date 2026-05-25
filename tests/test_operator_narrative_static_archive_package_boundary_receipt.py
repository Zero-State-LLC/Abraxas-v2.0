from __future__ import annotations

import json
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry
from core.operator_narrative_static_archive_package_boundary_receipt import (
    PATCH_ID,
    RECEIPT_ID,
    SCHEMA_VERSION,
    build_operator_narrative_static_archive_package_boundary_receipt_packet,
    write_operator_narrative_static_archive_package_boundary_receipt,
)


def _p57(flags: dict | None = None, final_status: str = "GLOBAL_VERIFICATION_PASS", posture: str = "VERIFIED") -> dict:
    deny = {
        "package_created": False,
        "distribution_claims_allowed": False,
        "release_readiness_claimed": False,
        "command_authority": False,
        "ui_command_authority": False,
        "action_authority": False,
        "recommendation_authority": False,
        "inference_authority": False,
        "prediction_allowed": False,
        "forecast_authority": False,
        "trend_prediction_allowed": False,
        "readiness_claims_allowed": False,
        "mutation_allowed": False,
        "authority_granted": False,
        "execution_authority": False,
        "routing_change_allowed": False,
        "queue_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "runtime_mutation_allowed": False,
    }
    if flags:
        deny.update(flags)
    return {"final_status": final_status, "verification_posture": posture, "governance_flags": deny}


def _write_fixture(root: Path, p58_text: str, p57: dict) -> tuple[Path, Path]:
    p58 = root / "p58.md"
    p57p = root / "p57.json"
    p58.write_text(p58_text, encoding="utf-8")
    p57p.write_text(json.dumps(p57), encoding="utf-8")
    return p58, p57p


def _valid_p58() -> str:
    return Path("docs/plans/P58_planning_gate_static_archive_package.md").read_text(encoding="utf-8")


def test_pass_and_deterministic_hash(tmp_path: Path) -> None:
    p58, p57 = _write_fixture(tmp_path, _valid_p58(), _p57())
    a = build_operator_narrative_static_archive_package_boundary_receipt_packet(p58_planning_path=p58, p57_receipt_path=p57, repo_root=tmp_path)
    b = build_operator_narrative_static_archive_package_boundary_receipt_packet(p58_planning_path=p58, p57_receipt_path=p57, repo_root=tmp_path)
    assert a["final_status"] == "BOUNDARY_RECEIPT_PASS"
    assert a["boundary_hash"] == b["boundary_hash"]


def test_not_computable_missing_p58_or_corrupt_p57(tmp_path: Path) -> None:
    p57 = tmp_path / "p57.json"
    p57.write_text(json.dumps(_p57()), encoding="utf-8")
    pkt = build_operator_narrative_static_archive_package_boundary_receipt_packet(p58_planning_path=tmp_path / "missing.md", p57_receipt_path=p57, repo_root=tmp_path)
    assert pkt["final_status"] == "NOT_COMPUTABLE"
    p58 = tmp_path / "p58.md"
    p58.write_text(_valid_p58(), encoding="utf-8")
    p57.write_text("{bad", encoding="utf-8")
    pkt2 = build_operator_narrative_static_archive_package_boundary_receipt_packet(p58_planning_path=p58, p57_receipt_path=p57, repo_root=tmp_path)
    assert pkt2["final_status"] == "NOT_COMPUTABLE"


def test_fail_modes(tmp_path: Path) -> None:
    p58_text = _valid_p58().replace("P58_PLAN_READY", "")
    p58, p57 = _write_fixture(tmp_path, p58_text, _p57())
    assert build_operator_narrative_static_archive_package_boundary_receipt_packet(p58_planning_path=p58, p57_receipt_path=p57, repo_root=tmp_path)["final_status"] == "BOUNDARY_RECEIPT_FAIL"

    p58_text = _valid_p58().replace("Package planning is not package creation.", "")
    p58.write_text(p58_text, encoding="utf-8")
    assert build_operator_narrative_static_archive_package_boundary_receipt_packet(p58_planning_path=p58, p57_receipt_path=p57, repo_root=tmp_path)["final_status"] == "BOUNDARY_RECEIPT_FAIL"

    p58_text = _valid_p58().replace("hash-manifested", "")
    p58.write_text(p58_text, encoding="utf-8")
    assert build_operator_narrative_static_archive_package_boundary_receipt_packet(p58_planning_path=p58, p57_receipt_path=p57, repo_root=tmp_path)["final_status"] == "BOUNDARY_RECEIPT_FAIL"

    p58.write_text(_valid_p58().replace("contain scripts", ""), encoding="utf-8")
    assert build_operator_narrative_static_archive_package_boundary_receipt_packet(p58_planning_path=p58, p57_receipt_path=p57, repo_root=tmp_path)["final_status"] == "BOUNDARY_RECEIPT_FAIL"


def test_fail_on_p57_status_artifact_registry_and_package_surface(tmp_path: Path) -> None:
    p58, p57 = _write_fixture(tmp_path, _valid_p58(), _p57(final_status="GLOBAL_VERIFICATION_FAIL"))
    assert build_operator_narrative_static_archive_package_boundary_receipt_packet(p58_planning_path=p58, p57_receipt_path=p57, repo_root=tmp_path)["final_status"] == "BOUNDARY_RECEIPT_FAIL"
    p57.write_text(json.dumps(_p57()), encoding="utf-8")
    (tmp_path / "out" / "static_archive_package").mkdir(parents=True)
    assert build_operator_narrative_static_archive_package_boundary_receipt_packet(p58_planning_path=p58, p57_receipt_path=p57, repo_root=tmp_path)["final_status"] == "BOUNDARY_RECEIPT_FAIL"


def test_fail_on_registry_entries_and_governance_flag_violation(tmp_path: Path) -> None:
    p58, p57 = _write_fixture(tmp_path, _valid_p58(), _p57(flags={"package_created": True}))
    (tmp_path / "core").mkdir()
    (tmp_path / "core" / "generated_artifact_registry.py").write_text("static_archive_package", encoding="utf-8")
    pkt = build_operator_narrative_static_archive_package_boundary_receipt_packet(p58_planning_path=p58, p57_receipt_path=p57, repo_root=tmp_path)
    assert pkt["final_status"] == "BOUNDARY_RECEIPT_FAIL"


def test_writer_schema_and_registry() -> None:
    pkt = build_operator_narrative_static_archive_package_boundary_receipt_packet()
    out = Path("out/audit/_tmp_p59.latest.json")
    write_operator_narrative_static_archive_package_boundary_receipt(out, pkt)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")
    out.unlink(missing_ok=True)
    out.with_suffix(".md").unlink(missing_ok=True)

    schema = json.loads(Path("contracts/operator_attention/operator_narrative_static_archive_package_boundary_receipt.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION
    assert schema["properties"]["patch_id"]["const"] == PATCH_ID
    assert schema["properties"]["receipt_id"]["const"] == RECEIPT_ID

    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    emap = {e.artifact_path: e for e in registry.entries}
    assert emap["out/audit/operator_narrative_static_archive_package_boundary_receipt_001.latest.json"].determinism_class == "DERIVED_OPTIONAL"
    assert emap["out/audit/operator_narrative_static_archive_package_boundary_receipt_001.latest.md"].determinism_class == "DERIVED_OPTIONAL"
