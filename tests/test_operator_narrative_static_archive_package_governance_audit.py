from __future__ import annotations

import json
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry
from core.operator_narrative_static_archive_package_governance_audit import (
    AUDIT_ID,
    PATCH_ID,
    SCHEMA_VERSION,
    build_operator_narrative_static_archive_package_governance_audit_packet,
    write_operator_narrative_static_archive_package_governance_audit,
)


def test_pass_on_current_package() -> None:
    pkt = build_operator_narrative_static_archive_package_governance_audit_packet()
    assert pkt["final_status"] == "PACKAGE_GOVERNANCE_AUDIT_PASS"


def test_not_computable_missing() -> None:
    pkt = build_operator_narrative_static_archive_package_governance_audit_packet(package_json_path="out/package/missing.json")
    assert pkt["final_status"] == "NOT_COMPUTABLE"


def test_fail_hash_mismatch(tmp_path: Path) -> None:
    src = Path("out/package/operator_narrative_static_archive_package_001.latest.json")
    p = tmp_path / "pkg.json"
    data = json.loads(src.read_text(encoding="utf-8"))
    data["package_hash"] = "0" * 64
    p.write_text(json.dumps(data), encoding="utf-8")
    md = tmp_path / "pkg.md"
    md.write_text("# x\n", encoding="utf-8")
    pkt = build_operator_narrative_static_archive_package_governance_audit_packet(package_json_path=p, package_md_path=md, repo_root=Path("."))
    assert pkt["final_status"] == "PACKAGE_GOVERNANCE_AUDIT_FAIL"


def test_repeatable_hash() -> None:
    a = build_operator_narrative_static_archive_package_governance_audit_packet()
    b = build_operator_narrative_static_archive_package_governance_audit_packet()
    assert a["audit_hash"] == b["audit_hash"]


def test_writer_schema_registry() -> None:
    pkt = build_operator_narrative_static_archive_package_governance_audit_packet()
    out = Path("out/audit/_tmp_p65.latest.json")
    write_operator_narrative_static_archive_package_governance_audit(out, pkt)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")
    out.unlink(missing_ok=True)
    out.with_suffix(".md").unlink(missing_ok=True)

    schema = json.loads(Path("contracts/operator_attention/operator_narrative_static_archive_package_governance_audit.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION
    assert schema["properties"]["patch_id"]["const"] == PATCH_ID
    assert schema["properties"]["audit_id"]["const"] == AUDIT_ID

    reg = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    emap = {e.artifact_path: e for e in reg.entries}
    assert emap["out/audit/operator_narrative_static_archive_package_governance_audit_001.latest.json"].determinism_class == "DERIVED_OPTIONAL"
    assert emap["out/audit/operator_narrative_static_archive_package_governance_audit_001.latest.md"].determinism_class == "DERIVED_OPTIONAL"
