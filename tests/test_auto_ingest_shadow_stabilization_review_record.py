from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import write_canonical_json
from core.ingest.auto_ingest_shadow_stabilization_review_record import (
    build_abx_auto_ingest_shadow_stabilization_review_record,
    render_abx_auto_ingest_shadow_stabilization_review_record_markdown,
    write_abx_auto_ingest_shadow_stabilization_review_record,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_auto_ingest_shadow_stabilization_review_record.py",
    "local_auto_ingest_shadow_stabilization_review_record_runner",
)


def test_record_is_deterministic_and_accepts_shadow_stabilization_review() -> None:
    first = build_abx_auto_ingest_shadow_stabilization_review_record()
    second = build_abx_auto_ingest_shadow_stabilization_review_record()

    assert first["record_hash"] == second["record_hash"]
    assert first["status"] == "ABX_AUTO_INGEST_SHADOW_STABILIZATION_REVIEW_ACCEPTED"
    assert first["selected_decision"] == "APPROVE_SHADOW_STABILIZATION_REVIEW"
    assert first["shadow_stabilization_review_completed"] is True
    assert first["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_record_preserves_all_authority_denials() -> None:
    packet = build_abx_auto_ingest_shadow_stabilization_review_record()

    assert packet["activation_authority"] is False
    assert packet["production_activation_allowed"] is False
    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["runtime_mutation_allowed"] is False
    assert packet["scheduler_mutation_allowed"] is False
    assert packet["ingest_runner_mutation_allowed"] is False
    assert packet["queue_mutation_allowed"] is False
    assert packet["canon_mutation_allowed"] is False
    assert packet["forecast_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["safe_to_auto_continue"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    validation_pack = json.loads(Path("out/audit/abx_auto_ingest_validation_pack_001.latest.json").read_text(encoding="utf-8"))
    projection_pack = json.loads(Path("out/projections/aal_viz_ingest_projection_pack_001.latest.json").read_text(encoding="utf-8"))
    write_canonical_json(tmp_path / "out/audit/abx_auto_ingest_validation_pack_001.latest.json", validation_pack)
    write_canonical_json(tmp_path / "out/projections/aal_viz_ingest_projection_pack_001.latest.json", projection_pack)

    packet = write_abx_auto_ingest_shadow_stabilization_review_record(tmp_path, out_root=tmp_path)
    json_path = tmp_path / "out/operator_review/abx_auto_ingest_shadow_stabilization_review_record_001.latest.json"
    md_path = tmp_path / "out/operator_review/abx_auto_ingest_shadow_stabilization_review_record_001.latest.md"

    assert json_path.exists()
    assert md_path.exists()
    runner_packet = RUNNER.run(repo_root=tmp_path, out_root=tmp_path)
    assert runner_packet["record_hash"] == packet["record_hash"]

    schema = json.loads(
        Path("contracts/operator_review/abx_auto_ingest_shadow_stabilization_review_record.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    validate(packet, schema)
    markdown = render_abx_auto_ingest_shadow_stabilization_review_record_markdown(packet)
    assert markdown[0] == "# ABX Auto Ingest Shadow Stabilization Review Record"
    assert any("APPROVE_SHADOW_STABILIZATION_REVIEW" in line for line in markdown)


def test_record_fails_closed_when_validation_pack_does_not_pass(tmp_path: Path) -> None:
    validation_pack = json.loads(Path("out/audit/abx_auto_ingest_validation_pack_001.latest.json").read_text(encoding="utf-8"))
    projection_pack = json.loads(Path("out/projections/aal_viz_ingest_projection_pack_001.latest.json").read_text(encoding="utf-8"))
    validation_pack["final_status"] = "FAIL"
    write_canonical_json(tmp_path / "out/audit/abx_auto_ingest_validation_pack_001.latest.json", validation_pack)
    write_canonical_json(tmp_path / "out/projections/aal_viz_ingest_projection_pack_001.latest.json", projection_pack)

    packet = build_abx_auto_ingest_shadow_stabilization_review_record(tmp_path)

    assert packet["status"] == "ABX_AUTO_INGEST_SHADOW_STABILIZATION_REVIEW_BLOCKED"
    assert packet["selected_decision"] == "NOT_COMPUTABLE"
    assert packet["shadow_stabilization_review_completed"] is False


def test_registry_includes_review_record_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/operator_review/abx_auto_ingest_shadow_stabilization_review_record_001.latest.json" in (
        _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert "out/operator_review/abx_auto_ingest_shadow_stabilization_review_record_001.latest.md" in (
        _DERIVED_OPTIONAL_ARTIFACTS
    )
