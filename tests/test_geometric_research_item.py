from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.geometric_research_item import (
    build_geometric_research_item,
    canonicalize_geometric_research_item,
    compute_geometric_research_item_hash,
    serialize_geometric_research_item,
    validate_geometric_research_item,
)


def _base_item() -> dict:
    return build_geometric_research_item(
        item_id="GRI-abc123",
        title="Geometric signal research note",
        source_type="oracle_shadow_note",
        source_ref="out/research_shadow_replay_audit/latest.json",
        observed_summary="Observed geometric topology continuity",
        extracted_concepts=["topology", "transport"],
        architecture_targets=["ORACLE_SIGNAL_LAYER", "GEOMETRIC_INTELLIGENCE_RUNTIME"],
        candidate_modules=["geometric_signal_packet"],
        classification="SHADOW_ONLY",
        provenance={
            "source": "oracle-shadow",
            "evidence_refs": ["out/research_shadow_replay_audit/latest.json"],
            "generated_by": "test-suite",
            "upstream_schema_refs": [],
        },
        created_at_utc="2026-05-27T00:00:00Z",
    )


def test_valid_item_deterministic_hash() -> None:
    assert _base_item()["canonical_hash"] == _base_item()["canonical_hash"]


def test_repeated_serialization_byte_stable() -> None:
    item = _base_item()
    assert serialize_geometric_research_item(item) == serialize_geometric_research_item(item)


def test_unknown_classification_fails() -> None:
    with pytest.raises(ValueError, match="unknown classification"):
        canonicalize_geometric_research_item({**_base_item(), "classification": "NOPE"})


def test_unknown_architecture_target_fails() -> None:
    with pytest.raises(ValueError, match="unknown architecture target"):
        canonicalize_geometric_research_item({**_base_item(), "architecture_targets": ["NOPE"]})


def test_governance_flags_cannot_be_true() -> None:
    bad = _base_item()
    bad["governance_flags"] = {**bad["governance_flags"], "runtime_authority": True}
    with pytest.raises(ValueError, match="governance_flags.runtime_authority"):
        canonicalize_geometric_research_item(bad)


def test_hash_excludes_canonical_hash_preimage() -> None:
    item = _base_item()
    changed = {**item, "canonical_hash": "0" * 64}
    assert compute_geometric_research_item_hash(changed) == item["canonical_hash"]


def test_hash_changes_on_content_change() -> None:
    item = _base_item()
    changed = canonicalize_geometric_research_item({**item, "title": "Changed"})
    assert changed["canonical_hash"] != item["canonical_hash"]


def test_schema_validation_if_available() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/geometric_research_item.v1.schema.json").read_text())
    jsonschema.validate(_base_item(), schema)


def test_validate_passes() -> None:
    validate_geometric_research_item(_base_item())
