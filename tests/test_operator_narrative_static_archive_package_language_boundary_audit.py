from __future__ import annotations

import json
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry
from core.operator_narrative_static_archive_package_language_boundary_audit import (
    AUDIT_ID,
    PATCH_ID,
    SCHEMA_VERSION,
    build_operator_narrative_static_archive_package_language_boundary_audit_packet,
    write_operator_narrative_static_archive_package_language_boundary_audit,
)


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_pass_on_current_surfaces() -> None:
    pkt = build_operator_narrative_static_archive_package_language_boundary_audit_packet()
    assert pkt["final_status"] == "PACKAGE_LANGUAGE_BOUNDARY_PASS"


def test_not_computable_when_p64_missing() -> None:
    pkt = build_operator_narrative_static_archive_package_language_boundary_audit_packet(package_json_path="out/package/missing.json")
    assert pkt["final_status"] == "NOT_COMPUTABLE"


def test_not_computable_when_p65_missing() -> None:
    pkt = build_operator_narrative_static_archive_package_language_boundary_audit_packet(p65_json_path="out/audit/missing.json")
    assert pkt["final_status"] == "NOT_COMPUTABLE"


def test_fail_when_p65_not_pass_clean(tmp_path: Path) -> None:
    p65 = json.loads(Path("out/audit/operator_narrative_static_archive_package_governance_audit_001.latest.json").read_text())
    p65["final_status"] = "PACKAGE_GOVERNANCE_AUDIT_FAIL"
    p65j = tmp_path / "p65.json"
    _write(p65j, p65)
    p65m = tmp_path / "p65.md"
    p65m.write_text("# p65\n", encoding="utf-8")
    pkt = build_operator_narrative_static_archive_package_language_boundary_audit_packet(p65_json_path=p65j, p65_md_path=p65m)
    assert pkt["final_status"] == "PACKAGE_LANGUAGE_BOUNDARY_FAIL"


def test_fail_unnegated_phrase_in_p64_markdown(tmp_path: Path) -> None:
    p64m = tmp_path / "p64.md"
    p64m.write_text("deploy now\n", encoding="utf-8")
    pkt = build_operator_narrative_static_archive_package_language_boundary_audit_packet(package_md_path=p64m)
    assert pkt["final_status"] == "PACKAGE_LANGUAGE_BOUNDARY_FAIL"


def test_fail_unnegated_phrase_in_p65_markdown(tmp_path: Path) -> None:
    p65m = tmp_path / "p65.md"
    p65m.write_text("production ready\n", encoding="utf-8")
    pkt = build_operator_narrative_static_archive_package_language_boundary_audit_packet(p65_md_path=p65m)
    assert pkt["final_status"] == "PACKAGE_LANGUAGE_BOUNDARY_FAIL"


def test_pass_allowed_context_and_package_created_true(tmp_path: Path) -> None:
    p64 = json.loads(Path("out/package/operator_narrative_static_archive_package_001.latest.json").read_text())
    p64["package_created"] = True
    p64["release_readiness_claimed"] = False
    p64j = tmp_path / "p64.json"
    _write(p64j, p64)
    p64m = tmp_path / "p64.md"
    p64m.write_text("non-distribution boundary; not release-ready\n", encoding="utf-8")
    pkt = build_operator_narrative_static_archive_package_language_boundary_audit_packet(package_json_path=p64j, package_md_path=p64m)
    assert pkt["final_status"] == "PACKAGE_LANGUAGE_BOUNDARY_PASS"


def test_repeatable_hash_and_writer_and_schema() -> None:
    a = build_operator_narrative_static_archive_package_language_boundary_audit_packet()
    b = build_operator_narrative_static_archive_package_language_boundary_audit_packet()
    assert a["audit_hash"] == b["audit_hash"]
    out = Path("out/audit/_tmp_p66.latest.json")
    write_operator_narrative_static_archive_package_language_boundary_audit(out, a)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")
    out.unlink(missing_ok=True)
    out.with_suffix(".md").unlink(missing_ok=True)

    schema = json.loads(Path("contracts/operator_attention/operator_narrative_static_archive_package_language_boundary_audit.v1.schema.json").read_text())
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION
    assert schema["properties"]["patch_id"]["const"] == PATCH_ID
    assert schema["properties"]["audit_id"]["const"] == AUDIT_ID

    reg = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    emap = {e.artifact_path: e for e in reg.entries}
    assert emap["out/audit/operator_narrative_static_archive_package_language_boundary_audit_001.latest.json"].determinism_class == "DERIVED_OPTIONAL"
    assert emap["out/audit/operator_narrative_static_archive_package_language_boundary_audit_001.latest.md"].determinism_class == "DERIVED_OPTIONAL"
