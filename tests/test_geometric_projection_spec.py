from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.canonical.json import canonical_dumps
from core.geometric_projection_spec import build_geometric_projection_spec


def _valid_payload() -> dict[str, object]:
    return {
        "item_id": "geometric_projection_spec-001",
        "title": "GeometricProjectionSpec.v1 scaffold",
        "observed_summary": "Schema-first advisory-only scaffold.",
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
        "provenance": {"source": "branch_sync_repair", "advisory_only": True},
        "created_at_utc": "2026-05-27T00:00:00Z",
    }


def test_deterministic_hash_and_serialization() -> None:
    first = build_geometric_projection_spec(_valid_payload())
    second = build_geometric_projection_spec(_valid_payload())
    assert first["canonical_hash"] == second["canonical_hash"]
    assert canonical_dumps(first) == canonical_dumps(second)


def test_true_authority_flag_rejected() -> None:
    payload = _valid_payload()
    payload["governance_flags"]["execution_authority"] = True
    with pytest.raises(ValueError, match="authority_lock_must_be_false"):
        build_geometric_projection_spec(payload)


def test_schema_validates_fixture() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/geometric_projection_spec.v1.schema.json").read_text(encoding="utf-8"))
    packet = build_geometric_projection_spec(_valid_payload())
    jsonschema.validate(packet, schema)
