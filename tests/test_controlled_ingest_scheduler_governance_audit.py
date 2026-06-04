from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.generated_artifact_registry import build_generated_artifact_registry
from core.ingest.controlled_ingest_scheduler_governance_audit import (
    AUDIT_ID,
    PATCH_ID,
    SCHEMA_VERSION,
    build_controlled_ingest_scheduler_governance_audit_packet,
    write_controlled_ingest_scheduler_governance_audit,
)


def test_governance_audit_passes_on_current_repo() -> None:
    packet = build_controlled_ingest_scheduler_governance_audit_packet()
    assert packet["final_status"] == "PASS"
    assert packet["recommended_next_step"] == "CONTROLLED_INGEST_SCHEDULER_OPERATOR_REVIEW"


def test_governance_audit_not_computable_when_source_missing(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "core/ingest").mkdir(parents=True)
    packet = build_controlled_ingest_scheduler_governance_audit_packet(repo_root=repo)
    assert packet["final_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_step"] == "CONTROLLED_INGEST_SCHEDULER_SOURCE_REPAIR_REQUIRED"


def test_governance_audit_is_stable_and_non_mutating() -> None:
    packet_a = build_controlled_ingest_scheduler_governance_audit_packet()
    packet_b = build_controlled_ingest_scheduler_governance_audit_packet()
    assert packet_a == packet_b


def test_writer_schema_and_registry() -> None:
    packet = build_controlled_ingest_scheduler_governance_audit_packet()
    out = Path("out/audit/_tmp_controlled_ingest_governance_audit.latest.json")
    write_controlled_ingest_scheduler_governance_audit(out, packet)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")
    out.unlink(missing_ok=True)
    out.with_suffix(".md").unlink(missing_ok=True)

    schema = json.loads(
        Path("contracts/ingest/controlled_ingest_scheduler_governance_audit.v1.schema.json").read_text(encoding="utf-8")
    )
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION
    assert schema["properties"]["patch_id"]["const"] == PATCH_ID
    assert schema["properties"]["audit_id"]["const"] == AUDIT_ID
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.validate(packet, schema)

    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    emap = {entry.artifact_path: entry for entry in registry.entries}
    assert emap["out/audit/controlled_ingest_scheduler_governance_audit_001.latest.json"].determinism_class == "DERIVED_OPTIONAL"
    assert emap["out/audit/controlled_ingest_scheduler_governance_audit_001.latest.md"].determinism_class == "DERIVED_OPTIONAL"


def test_source_hashes_and_boundary_assertions_present() -> None:
    packet = build_controlled_ingest_scheduler_governance_audit_packet()
    assert packet["source_hashes"]["scheduler_impl"]
    assert packet["boundary_assertions"]["manifest.handoff.target_patch"] == "PATCH-ABX-AUTO-INGEST-002"
    assert packet["authority_assertions"]["decision_set.projection_only"] is True
