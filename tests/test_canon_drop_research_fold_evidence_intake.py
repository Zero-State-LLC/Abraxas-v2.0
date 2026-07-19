from __future__ import annotations

import json
from pathlib import Path

from core.canon_drop_research_fold_evidence_intake import (
    build_canon_drop_research_fold_evidence_intake,
    write_canon_drop_research_fold_evidence_intake,
)
from scripts.readiness import run_canon_drop_research_fold_evidence_intake


def _manifest(surfaces: list[dict[str, str]]) -> dict[str, object]:
    return {
        "manifest_id": "canon_drop_research_fold_evidence_manifest.v1",
        "surfaces": surfaces,
    }


def _present_record(surface_id: str) -> dict[str, str]:
    return {
        "surface_id": surface_id,
        "source_label": "notion_canon_drop_006_007",
        "source_type": "notion",
        "evidence_reference": "ref://canonical",
        "content_hash": "abc123",
        "observed_at": "2026-05-26T00:00:00Z",
        "validation_status": "PRESENT",
    }


def _schema() -> dict[str, object]:
    return json.loads(
        Path("contracts/canon/canon_drop_research_fold_evidence_intake.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )


def test_missing_manifest_not_computable_fail_closed() -> None:
    packet = build_canon_drop_research_fold_evidence_intake(manifest=None)
    assert packet["intake_status"] == "NOT_COMPUTABLE"
    assert packet["evidence_complete"] is False
    assert set(packet["missing_surfaces"]) == {
        "canon_drop_006_research_folds",
        "canon_drop_007_research_folds",
    }


def test_manifest_with_only_drop006_incomplete() -> None:
    packet = build_canon_drop_research_fold_evidence_intake(
        manifest=_manifest([_present_record("canon_drop_006_research_folds")])
    )
    assert packet["intake_status"] == "CANON_DROP_RESEARCH_FOLD_EVIDENCE_INCOMPLETE"
    assert packet["required_surfaces_present"] is False
    assert packet["missing_surfaces"] == ["canon_drop_007_research_folds"]


def test_manifest_with_missing_hashes_incomplete() -> None:
    m = _manifest(
        [
            {
                **_present_record("canon_drop_006_research_folds"),
                "content_hash": "",
            },
            {
                **_present_record("canon_drop_007_research_folds"),
                "checksum": "",
                "content_hash": "",
            },
        ]
    )
    packet = build_canon_drop_research_fold_evidence_intake(manifest=m)
    assert packet["evidence_complete"] is False
    assert set(packet["invalid_surfaces"]) == {
        "canon_drop_006_research_folds",
        "canon_drop_007_research_folds",
    }


def test_manifest_with_both_present_and_hashes_recommends_p94_regen() -> None:
    packet = build_canon_drop_research_fold_evidence_intake(
        manifest=_manifest(
            [
                _present_record("canon_drop_006_research_folds"),
                _present_record("canon_drop_007_research_folds"),
            ]
        )
    )
    assert packet["intake_status"] == "CANON_DROP_RESEARCH_FOLD_EVIDENCE_PRESENT"
    assert packet["recommended_next_lane"] == "P94_RESEARCH_FOLD_CANON_ALIGNMENT_PLAN_REGENERATION"


def test_determinism_repeated_run_same_hash() -> None:
    manifest = _manifest(
        [
            _present_record("canon_drop_006_research_folds"),
            _present_record("canon_drop_007_research_folds"),
        ]
    )
    first = build_canon_drop_research_fold_evidence_intake(manifest=manifest)
    second = build_canon_drop_research_fold_evidence_intake(manifest=manifest)
    assert first == second
    assert first["packet_hash"] == second["packet_hash"]


def test_authority_locks_forbidden_fields_false() -> None:
    packet = build_canon_drop_research_fold_evidence_intake(manifest=None)
    assert packet["authority_locks"]["advisory_only"] is True
    assert packet["authority_locks"]["projection_only"] is True
    assert packet["authority_locks"]["evidence_only"] is True
    forbidden = [
        "production_activation",
        "canon_promotion",
        "scheduler_mutation",
        "runtime_authority",
        "forecast_influence",
        "execution_authority",
        "repair_execution_authority",
        "regeneration_execution_authority",
        "token_minting_allowed",
        "valid_for_execution",
    ]
    assert all(packet["authority_locks"][key] is False for key in forbidden)


def test_schema_locks_authority_and_status_fields() -> None:
    packet = build_canon_drop_research_fold_evidence_intake(manifest=None)
    schema = _schema()
    assert schema["properties"]["artifact_type"]["const"] == packet["artifact_type"]
    assert schema["properties"]["canonical_status"]["const"] == packet["canonical_status"]
    assert packet["intake_status"] in schema["properties"]["intake_status"]["enum"]
    assert schema["properties"]["authority_locks"]["properties"]["advisory_only"]["const"] is True
    assert schema["properties"]["authority_locks"]["properties"]["valid_for_execution"]["const"] is False


def test_runner_writes_and_writer_newline(tmp_path: Path) -> None:
    out_path = tmp_path / "out" / "canon_drop_research_fold_evidence_intake" / "latest.json"
    packet = run_canon_drop_research_fold_evidence_intake.run(
        manifest=None,
        repo_root=tmp_path,
        out_path=out_path,
    )
    assert packet["intake_status"] == "NOT_COMPUTABLE"

    write_path = tmp_path / "manual.json"
    write_canon_drop_research_fold_evidence_intake(write_path, packet)
    assert write_path.read_text(encoding="utf-8").endswith("\n")
