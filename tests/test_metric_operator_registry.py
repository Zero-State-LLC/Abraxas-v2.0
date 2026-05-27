from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.metric_operator_registry import (
    OPERATOR_IDS,
    build_metric_operator_registry,
    compute_metric_operator_registry_hash,
    default_metric_operator_entries,
    serialize_metric_operator_registry,
    validate_metric_operator_registry,
)


def _base() -> dict:
    return build_metric_operator_registry(
        registry_id="MOR-0001",
        provenance={"source": "research", "evidence_refs": ["docs/audits/REPO_AUDIT_GEOMETRIC_SIGNAL_PACKET_v0_1.md"], "generated_by": "tests", "upstream_schema_refs": ["contracts/canon/geometric_research_item.v1.schema.json", "contracts/canon/geometric_signal_packet.v1.schema.json"]},
        created_at_utc="2026-05-27T00:00:00Z",
    )


def test_deterministic_hash() -> None:
    assert _base()["canonical_hash"] == _base()["canonical_hash"]


def test_repeated_serialization_stable() -> None:
    p = _base()
    assert serialize_metric_operator_registry(p) == serialize_metric_operator_registry(p)


def test_default_exact_operator_ids() -> None:
    p = _base()
    assert {op["operator_id"] for op in p["operators"]} == set(OPERATOR_IDS)


def test_duplicate_operator_id_fails() -> None:
    p = _base()
    ops = p["operators"] + [p["operators"][0]]
    with pytest.raises(ValueError, match="duplicate operator_id"):
        build_metric_operator_registry(registry_id="x", provenance=p["provenance"], created_at_utc=p["created_at_utc"], operators=ops)


def test_unknown_operator_id_fails() -> None:
    p = _base()
    ops = [dict(p["operators"][0], operator_id="NOPE")] + p["operators"][1:]
    with pytest.raises(ValueError, match="unknown operator_id"):
        build_metric_operator_registry(registry_id="x", provenance=p["provenance"], created_at_utc=p["created_at_utc"], operators=ops)


def test_unknown_family_fails() -> None:
    p = _base()
    ops = [dict(p["operators"][0], operator_family="NOPE")] + p["operators"][1:]
    with pytest.raises(ValueError, match="unknown operator_family"):
        build_metric_operator_registry(registry_id="x", provenance=p["provenance"], created_at_utc=p["created_at_utc"], operators=ops)


def test_unknown_architecture_target_fails() -> None:
    p = _base()
    ops = [dict(p["operators"][0], allowed_architecture_targets=["NOPE"])]+p["operators"][1:]
    with pytest.raises(ValueError, match="unknown architecture target"):
        build_metric_operator_registry(registry_id="x", provenance=p["provenance"], created_at_utc=p["created_at_utc"], operators=ops)


def test_unknown_required_evidence_fails() -> None:
    p = _base()
    ops = [dict(p["operators"][0], required_evidence=["NOPE"])]+p["operators"][1:]
    with pytest.raises(ValueError, match="unknown required evidence"):
        build_metric_operator_registry(registry_id="x", provenance=p["provenance"], created_at_utc=p["created_at_utc"], operators=ops)


def test_shadow_only_true_required() -> None:
    p = _base()
    ops = [dict(p["operators"][0], shadow_only=False)] + p["operators"][1:]
    with pytest.raises(ValueError, match="shadow_only"):
        build_metric_operator_registry(registry_id="x", provenance=p["provenance"], created_at_utc=p["created_at_utc"], operators=ops)


def test_governance_flags_cannot_be_true() -> None:
    p = _base()
    bad = dict(p)
    bad["governance_flags"] = {**p["governance_flags"], "runtime_authority": True}
    with pytest.raises(ValueError, match="runtime_authority"):
        validate_metric_operator_registry(bad)


def test_forbidden_refs_rejected() -> None:
    p = _base()
    ops = [dict(p["operators"][0], description="has runtime callable route")]+p["operators"][1:]
    with pytest.raises(ValueError, match="forbidden"):
        build_metric_operator_registry(registry_id="x", provenance=p["provenance"], created_at_utc=p["created_at_utc"], operators=ops)


def test_hash_excludes_preimage() -> None:
    p = _base()
    changed = {**p, "canonical_hash": "0"*64}
    assert compute_metric_operator_registry_hash(changed) == p["canonical_hash"]


def test_hash_changes_on_meaningful_change() -> None:
    p = _base()
    ops = [dict(p["operators"][0], description="changed")] + p["operators"][1:]
    changed = build_metric_operator_registry(registry_id="x", provenance=p["provenance"], created_at_utc=p["created_at_utc"], operators=ops)
    assert changed["canonical_hash"] != p["canonical_hash"]


def test_schema_validation_if_available() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/metric_operator_registry.v1.schema.json").read_text())
    jsonschema.validate(_base(), schema)


def test_registry_has_metadata_refs_only() -> None:
    p = _base()
    text = json.dumps(p)
    assert "core.geometric_research_item" not in text
    assert "core.geometric_signal_packet" not in text


def test_default_entries_function() -> None:
    assert {op["operator_id"] for op in default_metric_operator_entries()} == set(OPERATOR_IDS)
