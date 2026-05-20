from __future__ import annotations

import json
from pathlib import Path

from core.operator_narrative_static_archive_package_completion_seal_receipt import (
    PATCH_ID,
    RECEIPT_ID,
    SCHEMA_VERSION,
    build_operator_narrative_static_archive_package_completion_seal_receipt_packet,
    write_operator_narrative_static_archive_package_completion_seal_receipt,
)


def test_current_baseline_degraded() -> None:
    p = build_operator_narrative_static_archive_package_completion_seal_receipt_packet()
    assert p["final_status"] == "STATIC_ARCHIVE_PACKAGE_COMPLETION_SEAL_DEGRADED"
    assert p["completion_posture"] == "STATIC_ARCHIVE_PACKAGE_COMPLETION_SEALED_WITH_OBSERVED_BLOCKERS"


def test_not_computable_without_p71_doc(tmp_path: Path) -> None:
    (tmp_path / "out").mkdir()
    p = build_operator_narrative_static_archive_package_completion_seal_receipt_packet(repo_root=tmp_path)
    assert p["final_status"] == "NOT_COMPUTABLE"


def test_hash_repeatable() -> None:
    a = build_operator_narrative_static_archive_package_completion_seal_receipt_packet()
    b = build_operator_narrative_static_archive_package_completion_seal_receipt_packet()
    assert a["completion_hash"] == b["completion_hash"]


def test_markdown_newline(tmp_path: Path) -> None:
    p = build_operator_narrative_static_archive_package_completion_seal_receipt_packet()
    out = tmp_path / "p72.json"
    write_operator_narrative_static_archive_package_completion_seal_receipt(out, p)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")


def test_schema_constants() -> None:
    s = json.loads(Path("contracts/operator_attention/operator_narrative_static_archive_package_completion_seal_receipt.v1.schema.json").read_text(encoding="utf-8"))
    assert s["properties"]["schema_version"]["const"] == SCHEMA_VERSION
    assert s["properties"]["patch_id"]["const"] == PATCH_ID
    assert s["properties"]["receipt_id"]["const"] == RECEIPT_ID
