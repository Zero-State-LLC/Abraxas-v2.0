"""Tests for ABX-Rune models and registry."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.runes.models import RuneContract
from core.runes.registry import load_rune_catalog, lookup_rune

CATALOG_PATH = Path("contracts/runes/catalog.v1.json")

EXPECTED_RUNE_IDS = [
    "RUNE.PIPELINE.PARSE",
    "RUNE.PIPELINE.RECEIPT",
    "RUNE.PIPELINE.IR_BUILD",
    "RUNE.PIPELINE.ROUTE",
    "RUNE.PIPELINE.VALIDATE",
    "RUNE.PIPELINE.POSITIVE_PROOF",
    "RUNE.PIPELINE.NEGATIVE_PROOF",
    "RUNE.PIPELINE.CONFLICT_SCAN",
    "RUNE.PIPELINE.AAL_VIZ_PROJECT",
    "RUNE.PIPELINE.OPERATOR_REVIEW",
    "RUNE.PIPELINE.CANON_SYNC",
    "RUNE.PIPELINE.STABILIZATION_DECIDE",
    "RUNE.GOVERNANCE.AUTHORITY_GATE",
    "RUNE.GOVERNANCE.NOT_COMPUTABLE_GATE",
    "RUNE.GOVERNANCE.INVARIANCE_GATE",
    "RUNE.GOVERNANCE.PROMOTION_LOCK",
    "RUNE.GOVERNANCE.FORECAST_GATE",
    "RUNE.GOVERNANCE.RUNTIME_MUTATION_LOCK",
    "RUNE.YGGDRASIL.ROUTE_GRAPH_BUILD",
    "RUNE.YGGDRASIL.DEPENDENCY_SCAN",
    "RUNE.YGGDRASIL.LANE_BOUNDARY_SCAN",
    "RUNE.YGGDRASIL.UNKNOWN_NODE_GATE",
    "RUNE.YGGDRASIL.EDGE_VALIDATION",
    "RUNE.YGGDRASIL.ROUTE_RECEIPT",
]


def test_rune_catalog_loads():
    catalog = load_rune_catalog(CATALOG_PATH)
    assert len(catalog) > 0


@pytest.mark.parametrize("rune_id", EXPECTED_RUNE_IDS)
def test_expected_rune_present(rune_id: str):
    catalog = load_rune_catalog(CATALOG_PATH)
    assert rune_id in catalog


def test_all_runes_authority_locked():
    catalog = load_rune_catalog(CATALOG_PATH)
    for rune_id, rune in catalog.items():
        rune.authority.assert_locked()


def test_rune_id_prefix_required():
    with pytest.raises(Exception):
        RuneContract(
            rune_id="INVALID.RUNE",
            purpose="test",
            input_schema="Input.v1",
            output_schema="Output.v1",
            lane="SHADOW",
            authority={},
        )


def test_unknown_rune_returns_not_computable():
    catalog = load_rune_catalog(CATALOG_PATH)
    result = lookup_rune("RUNE.NONEXISTENT.THING", catalog)
    assert result["status"] == "not_computable"


def test_known_rune_returns_found():
    catalog = load_rune_catalog(CATALOG_PATH)
    result = lookup_rune("RUNE.PIPELINE.PARSE", catalog)
    assert result["status"] == "found"


def test_rune_catalog_cache_invalidates_when_file_changes(tmp_path: Path):
    target = tmp_path / "catalog.v1.json"
    target.write_text(CATALOG_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    assert "RUNE.PIPELINE.PARSE" in load_rune_catalog(target)

    payload = json.loads(target.read_text(encoding="utf-8"))
    payload["runes"][0]["rune_id"] = "RUNE.PIPELINE.PARSE.V2"
    target.write_text(json.dumps(payload), encoding="utf-8")

    catalog = load_rune_catalog(target)
    assert "RUNE.PIPELINE.PARSE.V2" in catalog
    assert "RUNE.PIPELINE.PARSE" not in catalog
