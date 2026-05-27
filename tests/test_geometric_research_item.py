from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.canonical.json import canonical_dumps, canonical_hash
from core.geometric_research_item import build_geometric_research_item


def _valid_payload() -> dict[str, object]:
    return {
        "item_id": "geom-research-001",
        "title": "Geometric operator audit seed",
        "source_type": "research_note",
        "source_ref": "notion://geometric_intelligence_runtime_v0_1",
        "observed_summary": "Seed schema-first registry entry for deterministic shadow-only intake.",
        "extracted_concepts": ["geodesic", "transport", "topology"],
        "architecture_targets": ["GEOMETRIC_INTELLIGENCE_RUNTIME", "ORACLE_SIGNAL_LAYER"],
        "candidate_modules": ["core/geometric_signal_packet.py"],
        "classification": "SHADOW_ONLY",
        "governance_flags": {
            "production_activation": False,
            "canon_promotion": False,
            "scheduler_mutation": False,
            "runtime_authority": False,
            "runtime_mutation": False,
            "forecast_influence": False,
            "execution_authority": False,
            "token_minting_allowed": False,
            "valid_for_execution": False,
            "activation_approved": False,
            "authorization_granted": False,
        },
        "provenance": {"source": "repo_audit", "advisory_only": True},
        "created_at_utc": "2026-05-27T00:00:00Z",
    }


def test_deterministic_hash_and_byte_stable_serialization() -> None:
    first = build_geometric_research_item(_valid_payload())
    second = build_geometric_research_item(_valid_payload())
    assert first["canonical_hash"] == second["canonical_hash"]
    assert canonical_dumps(first) == canonical_dumps(second)


def test_authority_locks_all_false() -> None:
    packet = build_geometric_research_item(_valid_payload())
    assert all(packet["governance_flags"][k] is False for k in packet["governance_flags"])


def test_missing_fields_fail() -> None:
    payload = _valid_payload()
    payload.pop("title")
    with pytest.raises(ValueError, match="missing_required_fields"):
        build_geometric_research_item(payload)


def test_unknown_classification_fails() -> None:
    payload = _valid_payload()
    payload["classification"] = "UNKNOWN"
    with pytest.raises(ValueError, match="unknown_classification"):
        build_geometric_research_item(payload)


def test_unknown_architecture_target_fails() -> None:
    payload = _valid_payload()
    payload["architecture_targets"] = ["UNKNOWN_TARGET"]
    with pytest.raises(ValueError, match="unknown_architecture_targets"):
        build_geometric_research_item(payload)


def test_hash_changes_when_content_changes() -> None:
    one = build_geometric_research_item(_valid_payload())
    payload = _valid_payload()
    payload["observed_summary"] = "Changed summary"
    two = build_geometric_research_item(payload)
    assert one["canonical_hash"] != two["canonical_hash"]


def test_canonical_hash_excluded_from_preimage() -> None:
    packet = build_geometric_research_item(_valid_payload())
    clone = dict(packet)
    clone["canonical_hash"] = "f" * 64
    recomputed = canonical_hash({k: v for k, v in clone.items() if k != "canonical_hash"})
    assert recomputed == packet["canonical_hash"]


def test_true_authority_flag_rejected() -> None:
    payload = _valid_payload()
    payload["governance_flags"]["execution_authority"] = True
    with pytest.raises(ValueError, match="authority_lock_must_be_false"):
        build_geometric_research_item(payload)


def test_schema_validates_fixture() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/geometric_research_item.v1.schema.json").read_text(encoding="utf-8"))
    packet = build_geometric_research_item(_valid_payload())
    jsonschema.validate(packet, schema)
