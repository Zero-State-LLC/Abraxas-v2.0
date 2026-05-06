"""Tests for pipeline registry."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.pipelines.models import PipelineContractV11
from core.pipelines.registry import (
    build_registry,
    load_contracts,
    load_pipeline_contract,
    validate_registry,
    validate_registry_contracts,
)

CONTRACTS_DIR = Path("contracts/pipelines")

TIER1_PIPELINE_IDS = {
    "research_intake",
    "universal_ingest",
    "pse_forecast",
    "outcome_brier",
    "canon_sync",
    "research_drop_validation",
    "aal_viz_projection",
}


def test_load_all_tier1_contracts():
    contracts = load_contracts(CONTRACTS_DIR)
    ids = {c.pipeline_id for c in contracts}
    assert TIER1_PIPELINE_IDS.issubset(ids)


def test_build_registry_structure():
    contracts = load_contracts(CONTRACTS_DIR)
    reg = build_registry(contracts)
    assert reg["schema_version"] == "GlobalPipelineRegistry.v1"
    assert reg["pipeline_count"] == len(contracts)
    assert isinstance(reg["pipelines"], list)
    assert reg["status"] == "shadow_candidate"
    assert "recommended_next_state" in reg


def test_validate_registry_ok():
    contracts = load_contracts(CONTRACTS_DIR)
    reg = build_registry(contracts)
    result = validate_registry(reg)
    assert result["schema_version"] == "GlobalPipelineRegistry.v1"


def test_duplicate_pipeline_id_fails():
    contracts = load_contracts(CONTRACTS_DIR)
    # Duplicate the first contract
    duped = contracts + [contracts[0]]
    with pytest.raises(ValueError, match="Duplicate pipeline_id"):
        validate_registry_contracts(duped)


def test_duplicate_trigger_fails():
    contracts = load_contracts(CONTRACTS_DIR)
    # Create a clone of first contract with different id but same trigger
    first = contracts[0]
    clone_data = first.model_dump()
    clone_data["pipeline_id"] = "cloned_pipeline"
    # Same trigger
    clone = PipelineContractV11.model_validate(clone_data)
    with pytest.raises(ValueError, match="Duplicate trigger"):
        validate_registry_contracts(contracts + [clone])


def test_authority_all_false_in_registry():
    contracts = load_contracts(CONTRACTS_DIR)
    reg = build_registry(contracts)
    auth = reg["authority"]
    assert all(v is False for v in auth.values())
