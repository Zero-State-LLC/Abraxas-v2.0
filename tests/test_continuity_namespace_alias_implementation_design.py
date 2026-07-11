from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import canonical_hash
from core.continuity_namespace_alias_implementation_design import (
    BRIER_SCORE,
    DEFAULT_OUT_PATH,
    STATUS,
    build_continuity_namespace_alias_implementation_design_receipt,
)
from scripts.run_continuity_namespace_alias_implementation_design_receipt import run


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_alias_implementation_design_preserves_authority_locks() -> None:
    packet = build_continuity_namespace_alias_implementation_design_receipt(
        repo_root=REPO_ROOT
    )

    assert packet["status"] == STATUS
    assert packet["brier_score"] == BRIER_SCORE
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["implementation_posture"]["current_state"] == "DESIGN_ONLY_HELD"
    assert all(value is False for value in packet["authority_locks"].values())


def test_alias_implementation_design_hash_is_canonical() -> None:
    packet = build_continuity_namespace_alias_implementation_design_receipt(
        repo_root=REPO_ROOT
    )
    without_hash = {
        key: value for key, value in packet.items() if key != "canonical_hash"
    }

    assert packet["canonical_hash"] == canonical_hash(without_hash)


def test_alias_implementation_design_routes_from_existing_alias_plan() -> None:
    packet = build_continuity_namespace_alias_implementation_design_receipt(
        repo_root=REPO_ROOT
    )

    assert (
        packet["implementation_posture"]["safe_next_surface"]
        == "CONTINUITY_NAMESPACE_ADDITIVE_ALIAS_PLAN_001_ADVISORY_ONLY"
    )
    assert (
        packet["implementation_posture"]["required_stabilization_status"]
        == "ALIAS_PLAN_STABILIZED_ADVISORY_ONLY"
    )
    assert packet["implementation_posture"]["valid_for_implementation"] is False
    assert any(
        row["design_stage"] == "ALIAS_MANIFEST_METADATA_DESIGN"
        for row in packet["design_stage_rows"]
    )


def test_alias_implementation_design_missing_sources_fail_closed(tmp_path: Path) -> None:
    packet = build_continuity_namespace_alias_implementation_design_receipt(
        repo_root=tmp_path
    )

    assert packet["source_status"] == "NOT_COMPUTABLE"
    assert packet["implementation_posture"]["current_state"] == "DESIGN_ONLY_HELD"
    assert packet["implementation_posture"]["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_alias_implementation_design_runner_writes_receipt(tmp_path: Path) -> None:
    out_path = tmp_path / "receipt.latest.json"
    packet = run(repo_root=REPO_ROOT, out_path=out_path)
    written = json.loads(out_path.read_text(encoding="utf-8"))

    assert out_path.exists()
    assert written == packet
    assert written["status"] == STATUS
    assert written["canonical_hash"] == packet["canonical_hash"]
    assert DEFAULT_OUT_PATH.endswith(".latest.json")
