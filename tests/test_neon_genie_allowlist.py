"""Tests for WP-G Neon Genie capability allowlist."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from core.production_readiness.neon_genie_allowlist import (
    build_allowlist,
    build_allowlist_check_report,
    check_capability,
)


REPO = Path(__file__).resolve().parents[1]


def test_allowed_and_denied() -> None:
    assert check_capability("venture_cycle.intake")["status"] == "ALLOWED"
    assert check_capability("governance.control")["status"] == "DENIED"
    assert check_capability("production.activate")["status"] == "DENIED"
    assert check_capability("unknown.capability")["status"] == "DENIED"


def test_allowlist_schema() -> None:
    doc = build_allowlist(REPO, write=False)
    schema = json.loads(
        (
            REPO / "contracts/neon_genie/capability_allowlist.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    jsonschema.validate(instance=doc, schema=schema)
    assert doc["authority_locks"]["production_activation"] is False
    assert doc["authority_locks"]["governance_control"] is False
    assert doc["entry_point_presence"]["all_present"] is True


def test_check_report() -> None:
    report = build_allowlist_check_report(REPO, write=False)
    assert report["summary"]["denied"] >= 3
    assert report["summary"]["allowed"] >= 1
