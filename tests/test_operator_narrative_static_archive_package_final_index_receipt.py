from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.operator_narrative_static_archive_package_final_index_receipt import (
    PATCH_ID,
    RECEIPT_ID,
    SCHEMA_VERSION,
    build_operator_narrative_static_archive_package_final_index_receipt_packet,
    write_operator_narrative_static_archive_package_final_index_receipt,
)
from tests._static_archive_test_utils import copy_upstream_package_artifacts


def test_current_baseline_degraded() -> None:
    packet = build_operator_narrative_static_archive_package_final_index_receipt_packet()
    assert packet["final_status"] == "STATIC_ARCHIVE_PACKAGE_FINAL_INDEX_DEGRADED"
    assert packet["final_index_posture"] == "STATIC_ARCHIVE_PACKAGE_FINAL_INDEX_STABLE_WITH_OBSERVED_BLOCKERS"
    assert packet["pointer_count"] == 6
    assert packet["ordered_surface_ids"] == ["P64", "P65", "P66", "P67", "P68", "P69"]


def test_not_computable_when_source_missing(tmp_path: Path) -> None:
    (tmp_path / "out").mkdir()
    packet = build_operator_narrative_static_archive_package_final_index_receipt_packet(repo_root=tmp_path)
    assert packet["final_status"] == "NOT_COMPUTABLE"


def test_hash_repeatable() -> None:
    a = build_operator_narrative_static_archive_package_final_index_receipt_packet()
    b = build_operator_narrative_static_archive_package_final_index_receipt_packet()
    assert a["final_index_hash"] == b["final_index_hash"]


def test_writer_newline(tmp_path: Path) -> None:
    packet = build_operator_narrative_static_archive_package_final_index_receipt_packet()
    out = tmp_path / "p70.json"
    write_operator_narrative_static_archive_package_final_index_receipt(out, packet)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")


def test_schema_constants() -> None:
    schema = json.loads(Path("contracts/operator_attention/operator_narrative_static_archive_package_final_index_receipt.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION
    assert schema["properties"]["patch_id"]["const"] == PATCH_ID
    assert schema["properties"]["receipt_id"]["const"] == RECEIPT_ID


def test_registry_classification() -> None:
    text = Path("core/generated_artifact_registry.py").read_text(encoding="utf-8")
    assert "operator_narrative_static_archive_package_final_index_receipt_001.latest.json" in text
    assert "operator_narrative_static_archive_package_final_index_receipt_001.latest.md" in text


def test_fallback_hydrates_missing_p69_from_upstream_artifacts(tmp_path: Path) -> None:
    copy_upstream_package_artifacts(tmp_path)
    packet = build_operator_narrative_static_archive_package_final_index_receipt_packet(repo_root=tmp_path)
    assert packet["status_summary"]["P69"] != "NOT_COMPUTABLE"
    assert packet["source_hashes"]["P69"] != "NOT_COMPUTABLE"
    assert "P69 missing/corrupt" not in packet["blocker_summary"]


def test_fallback_p69_fails_closed_when_hydration_is_not_computable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    copy_upstream_package_artifacts(tmp_path)

    def _not_computable_fallback(*, repo_root: str | Path | None = None) -> dict[str, object]:
        return {"final_status": "STATIC_ARCHIVE_PACKAGE_INDEX_POINTER_NOT_COMPUTABLE"}

    monkeypatch.setattr(
        "core.operator_narrative_static_archive_package_final_index_receipt.build_operator_narrative_static_archive_package_index_pointer_receipt_packet",
        _not_computable_fallback,
    )
    packet = build_operator_narrative_static_archive_package_final_index_receipt_packet(repo_root=tmp_path)
    assert packet["final_status"] == "NOT_COMPUTABLE"
    assert "P69 missing/corrupt" in packet["blocker_summary"]
