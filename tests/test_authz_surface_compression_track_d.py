from __future__ import annotations

import json
from pathlib import Path

from abraxas.cli import main
from core.canonical.json import canonical_hash
from core.engineering.authz_surface_compression import (
    STATUS,
    build_authz_surface_compression_receipt,
    classify_plan_text,
)

REPO = Path(__file__).resolve().parents[1]


def test_track_d_receipt_locks_authority_and_compresses_decisions() -> None:
    receipt = build_authz_surface_compression_receipt(repo_root=REPO)

    assert receipt["status"] == STATUS
    assert receipt["issue"] == 1120
    assert receipt["track_id"] == "D"
    assert all(value is False for value in receipt["authority"].values())
    assert receipt["decision_record_policy"]["preferred_shape"] == (
        "ONE_DECISION_RECORD_PLUS_ONE_HOLD_RECEIPT"
    )
    assert receipt["decision_record_policy"]["nested_plan_gate_plan_chains_authorized"] is False
    assert receipt["bulk_hold_policy"]["bulk_hold_families_remain_held"] is True
    assert receipt["bulk_hold_policy"]["auto_unhold_authorized"] is False


def test_track_d_receipt_hash_is_deterministic() -> None:
    first = build_authz_surface_compression_receipt(repo_root=REPO)
    second = build_authz_surface_compression_receipt(repo_root=REPO)

    assert first == second
    body = {key: value for key, value in first.items() if key != "canonical_hash"}
    assert first["canonical_hash"] == canonical_hash(body)


def test_new_plan_policy_rejects_orphan_plans_without_track_or_terminal_class() -> None:
    assert classify_plan_text("# New orphan\n\nDo another authz gate.") == "LEGACY_UNROUTED"
    assert classify_plan_text("# Routed\n\nTrack D: use one hold receipt.") == "TRACK_ROUTED"
    assert classify_plan_text("# Old\n\n**Class:** HISTORICAL · sealed") == (
        "TERMINAL_CLASSIFIED"
    )

    receipt = build_authz_surface_compression_receipt(repo_root=REPO)
    assert receipt["new_work_policy"]["orphan_plan_creation_authorized"] is False
    assert receipt["new_work_policy"]["new_plan_without_track_or_terminal_class"] == "REJECT"


def test_track_d_docs_surface_closeout_policy() -> None:
    plan = (REPO / "docs/plans/AUTHZ_SURFACE_COMPRESSION_TRACK_D_001.md").read_text(
        encoding="utf-8"
    )
    closeout = (REPO / "docs/status/AUTHZ_SURFACE_COMPRESSION_TRACK_D_CLOSEOUT.md").read_text(
        encoding="utf-8"
    )

    assert "CLOSED_AS_POLICY" in plan
    assert "abraxas os authz-compression" in plan
    assert "Issue #1120 closeout" in plan
    assert "Issue: `#1120`" in closeout
    assert "New orphan plan docs are rejected" in closeout
    assert "auto_unhold_authorized: false" in closeout


def test_cli_authz_compression(capsys) -> None:
    code = main(["os", "authz-compression"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["status"] == STATUS
    assert payload["issue"] == 1120
    assert payload["new_work_policy"]["orphan_plan_creation_authorized"] is False
    assert payload["decision_record_policy"]["nested_plan_gate_plan_chains_authorized"] is False
    assert payload["bulk_hold_policy"]["auto_unhold_authorized"] is False
    assert all(value is False for value in payload["authority"].values())
