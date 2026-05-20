from __future__ import annotations

import json
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry
from core.operator_narrative_static_archive_package import (
    PATCH_ID,
    PACKAGE_ID,
    ROLE_ORDER,
    SCHEMA_VERSION,
    build_operator_narrative_static_archive_package_packet,
    write_operator_narrative_static_archive_package,
)


def test_role_order_fixed() -> None:
    pkt = build_operator_narrative_static_archive_package_packet()
    assert pkt["artifact_role_order"] == ROLE_ORDER


def test_status_degraded_current_chain() -> None:
    pkt = build_operator_narrative_static_archive_package_packet()
    assert pkt["final_status"] in {"PACKAGE_CREATED_DEGRADED", "PACKAGE_CREATED_STATIC"}


def test_not_computable_missing_source(tmp_path: Path) -> None:
    (tmp_path / "out").mkdir()
    pkt = build_operator_narrative_static_archive_package_packet(repo_root=tmp_path)
    assert pkt["final_status"] == "PACKAGE_NOT_COMPUTABLE"


def test_hash_repeatable() -> None:
    a = build_operator_narrative_static_archive_package_packet()
    b = build_operator_narrative_static_archive_package_packet()
    assert a["package_hash"] == b["package_hash"]


def test_manifest_hashes_and_canonical_json() -> None:
    pkt = build_operator_narrative_static_archive_package_packet()
    for e in pkt["package_manifest"]:
        assert "sha256" in e and isinstance(e["sha256"], str)
        if e["source_path"].endswith(".json") and e["exists"]:
            assert e["canonical_hash"] is not None


def test_writer_and_schema_and_registry() -> None:
    pkt = build_operator_narrative_static_archive_package_packet()
    out = Path("out/package/_tmp_p64.latest.json")
    write_operator_narrative_static_archive_package(out, pkt)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")
    out.unlink(missing_ok=True)
    out.with_suffix(".md").unlink(missing_ok=True)

    schema = json.loads(Path("contracts/operator_attention/operator_narrative_static_archive_package.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION
    assert schema["properties"]["patch_id"]["const"] == PATCH_ID
    assert schema["properties"]["package_id"]["const"] == PACKAGE_ID

    reg = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    emap = {e.artifact_path: e for e in reg.entries}
    assert emap["out/package/operator_narrative_static_archive_package_001.latest.json"].determinism_class == "DERIVED_OPTIONAL"
    assert emap["out/package/operator_narrative_static_archive_package_001.latest.md"].determinism_class == "DERIVED_OPTIONAL"


def test_follow_on_gates_and_authz() -> None:
    pkt = build_operator_narrative_static_archive_package_packet()
    gates = pkt["follow_on_gate_summary"]["required_gates"]
    assert "P65 Static Archive Package Governance Audit" in gates
    assert pkt["authorization_evidence"]["authorization_observed"] is True
    assert pkt["authorization_evidence"]["generic_authorization_used"] is False
