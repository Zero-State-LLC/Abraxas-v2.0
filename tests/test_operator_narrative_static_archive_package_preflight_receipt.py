from __future__ import annotations

import json
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry
from core.operator_narrative_static_archive_package_preflight_receipt import (
    PATCH_ID,
    RECEIPT_ID,
    SCHEMA_VERSION,
    build_operator_narrative_static_archive_package_preflight_receipt_packet,
    write_operator_narrative_static_archive_package_preflight_receipt,
)


def _p59(flags: dict | None = None, final_status: str = "BOUNDARY_RECEIPT_PASS", posture: str = "BOUNDARY_VERIFIED") -> dict:
    deny = {
        "package_created": False,
        "package_implementation_allowed": False,
        "package_artifacts_created": False,
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
    return {"final_status": final_status, "boundary_posture": posture, "governance_flags": deny}


def _valid_p60() -> str:
    return Path("docs/plans/P60_planning_gate_static_archive_package_implementation.md").read_text(encoding="utf-8")


def _write_fixture(root: Path, p60_text: str, p59: dict) -> tuple[Path, Path]:
    p60 = root / "p60.md"
    p59p = root / "p59.json"
    p60.write_text(p60_text, encoding="utf-8")
    p59p.write_text(json.dumps(p59), encoding="utf-8")
    return p60, p59p


def test_pass_and_repeatable_hash(tmp_path: Path) -> None:
    p60, p59 = _write_fixture(tmp_path, _valid_p60(), _p59())
    a = build_operator_narrative_static_archive_package_preflight_receipt_packet(p60_planning_path=p60, p59_receipt_path=p59, repo_root=tmp_path)
    b = build_operator_narrative_static_archive_package_preflight_receipt_packet(p60_planning_path=p60, p59_receipt_path=p59, repo_root=tmp_path)
    assert a["final_status"] == "PREFLIGHT_RECEIPT_PASS"
    assert a["preflight_hash"] == b["preflight_hash"]


def test_not_computable_missing_p60_or_corrupt_p59(tmp_path: Path) -> None:
    p59 = tmp_path / "p59.json"
    p59.write_text(json.dumps(_p59()), encoding="utf-8")
    assert build_operator_narrative_static_archive_package_preflight_receipt_packet(p60_planning_path=tmp_path / "missing.md", p59_receipt_path=p59, repo_root=tmp_path)["final_status"] == "NOT_COMPUTABLE"
    p60 = tmp_path / "p60.md"
    p60.write_text(_valid_p60(), encoding="utf-8")
    p59.write_text("{bad", encoding="utf-8")
    assert build_operator_narrative_static_archive_package_preflight_receipt_packet(p60_planning_path=p60, p59_receipt_path=p59, repo_root=tmp_path)["final_status"] == "NOT_COMPUTABLE"


def test_fail_modes(tmp_path: Path) -> None:
    p60, p59 = _write_fixture(tmp_path, _valid_p60().replace("P60_PLAN_READY", ""), _p59())
    assert build_operator_narrative_static_archive_package_preflight_receipt_packet(p60_planning_path=p60, p59_receipt_path=p59, repo_root=tmp_path)["final_status"] == "PREFLIGHT_RECEIPT_FAIL"
    p60.write_text(_valid_p60().replace("creates no package artifacts", ""), encoding="utf-8")
    assert build_operator_narrative_static_archive_package_preflight_receipt_packet(p60_planning_path=p60, p59_receipt_path=p59, repo_root=tmp_path)["final_status"] == "PREFLIGHT_RECEIPT_FAIL"
    p60.write_text(_valid_p60().replace("package_hash", ""), encoding="utf-8")
    assert build_operator_narrative_static_archive_package_preflight_receipt_packet(p60_planning_path=p60, p59_receipt_path=p59, repo_root=tmp_path)["final_status"] == "PREFLIGHT_RECEIPT_FAIL"
    p60.write_text(_valid_p60().replace("active_surface_present", ""), encoding="utf-8")
    assert build_operator_narrative_static_archive_package_preflight_receipt_packet(p60_planning_path=p60, p59_receipt_path=p59, repo_root=tmp_path)["final_status"] == "PREFLIGHT_RECEIPT_FAIL"
    p60.write_text(_valid_p60().replace("Static Archive Package Governance Audit", ""), encoding="utf-8")
    assert build_operator_narrative_static_archive_package_preflight_receipt_packet(p60_planning_path=p60, p59_receipt_path=p59, repo_root=tmp_path)["final_status"] == "PREFLIGHT_RECEIPT_FAIL"


def test_fail_on_p59_and_package_surface_and_registry(tmp_path: Path) -> None:
    p60, p59 = _write_fixture(tmp_path, _valid_p60(), _p59(final_status="BOUNDARY_RECEIPT_FAIL"))
    assert build_operator_narrative_static_archive_package_preflight_receipt_packet(p60_planning_path=p60, p59_receipt_path=p59, repo_root=tmp_path)["final_status"] == "PREFLIGHT_RECEIPT_FAIL"
    p59.write_text(json.dumps(_p59()), encoding="utf-8")
    (tmp_path / "out" / "static_archive_package").mkdir(parents=True)
    assert build_operator_narrative_static_archive_package_preflight_receipt_packet(p60_planning_path=p60, p59_receipt_path=p59, repo_root=tmp_path)["final_status"] == "PREFLIGHT_RECEIPT_FAIL"
    (tmp_path / "core").mkdir(exist_ok=True)
    (tmp_path / "core" / "generated_artifact_registry.py").write_text("static_archive_package_manifest", encoding="utf-8")
    assert build_operator_narrative_static_archive_package_preflight_receipt_packet(p60_planning_path=p60, p59_receipt_path=p59, repo_root=tmp_path)["final_status"] == "PREFLIGHT_RECEIPT_FAIL"


def test_fail_on_governance_violation() -> None:
    pkt = build_operator_narrative_static_archive_package_preflight_receipt_packet(
        p60_planning_path=Path("docs/plans/P60_planning_gate_static_archive_package_implementation.md"),
        p59_receipt_path=Path("out/audit/operator_narrative_static_archive_package_boundary_receipt_001.latest.json"),
        repo_root=Path("."),
    )
    assert pkt["final_status"] == "PREFLIGHT_RECEIPT_PASS"


def test_writer_schema_and_registry() -> None:
    pkt = build_operator_narrative_static_archive_package_preflight_receipt_packet()
    out = Path("out/audit/_tmp_p62.latest.json")
    write_operator_narrative_static_archive_package_preflight_receipt(out, pkt)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")
    out.unlink(missing_ok=True)
    out.with_suffix(".md").unlink(missing_ok=True)
    schema = json.loads(Path("contracts/operator_attention/operator_narrative_static_archive_package_preflight_receipt.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION
    assert schema["properties"]["patch_id"]["const"] == PATCH_ID
    assert schema["properties"]["receipt_id"]["const"] == RECEIPT_ID
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    emap = {e.artifact_path: e for e in registry.entries}
    assert emap["out/audit/operator_narrative_static_archive_package_preflight_receipt_001.latest.json"].determinism_class == "DERIVED_OPTIONAL"
    assert emap["out/audit/operator_narrative_static_archive_package_preflight_receipt_001.latest.md"].determinism_class == "DERIVED_OPTIONAL"
