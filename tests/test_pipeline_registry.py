"""Tests for pipeline registry."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.pipelines.models import PipelineContractV11
from core.pipelines.registry import (
    build_registry,
    load_contracts,
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

TIER2_OBSERVED_PIPELINE_IDS = {
    "drift_scan",
    "operator_review_queue",
    "neon_genie_ideation",
}


def test_load_all_tier1_contracts():
    contracts = load_contracts(CONTRACTS_DIR)
    ids = {c.pipeline_id for c in contracts}
    assert TIER1_PIPELINE_IDS.issubset(ids)


def test_build_registry_structure():
    contracts = load_contracts(CONTRACTS_DIR)
    reg = build_registry(contracts)
    assert reg["schema_version"] == "GlobalPipelineRegistry.v1"
    assert reg["pipeline_count"] == 18
    assert reg["tier_counts"] == {"1": 7, "2": 6, "3": 5}
    assert reg["duplicate_pipeline_id_count"] == 0
    assert reg["duplicate_trigger_count"] == 0
    assert reg["authority_violation_count"] == 0
    assert isinstance(reg["pipelines"], list)
    assert reg["status"] == "shadow_candidate"
    assert reg["recommended_next_state"] == "eligible_for_shadow_stabilization"
    assert reg["invalid_entry_count"] == 0
    assert all(item["schema_version"] == "PipelineRegistryEntry.v1" for item in reg["pipelines"])
    assert {item["pipeline_id"] for item in reg["pipelines"]}.issuperset(TIER1_PIPELINE_IDS)
    assert {item["pipeline_id"] for item in reg["pipelines"]}.issuperset(TIER2_OBSERVED_PIPELINE_IDS)


def test_operator_review_queue_pipeline_is_observed() -> None:
    contracts = load_contracts(CONTRACTS_DIR)
    reg = build_registry(contracts)
    entry = next(item for item in reg["pipelines"] if item["pipeline_id"] == "operator_review_queue")
    assert entry["contract_status"] == "observed"
    assert entry["migration_status"] == "partial"
    assert entry["validation_status"] == "legacy_contract_posture"
    assert entry["lane"] == "GOVERNANCE"


def test_drift_scan_pipeline_is_observed() -> None:
    contracts = load_contracts(CONTRACTS_DIR)
    reg = build_registry(contracts)
    entry = next(item for item in reg["pipelines"] if item["pipeline_id"] == "drift_scan")
    assert entry["contract_status"] == "observed"
    assert entry["migration_status"] == "partial"
    assert entry["validation_status"] == "legacy_contract_posture"
    assert entry["lane"] == "GOVERNANCE_SHADOW"


def test_neon_genie_ideation_pipeline_is_observed() -> None:
    contracts = load_contracts(CONTRACTS_DIR)
    reg = build_registry(contracts)
    entry = next(item for item in reg["pipelines"] if item["pipeline_id"] == "neon_genie_ideation")
    assert entry["contract_status"] == "observed"
    assert entry["migration_status"] == "implemented"
    assert entry["lane"] == "SHADOW"
    assert entry["owner_subsystem"] == "Neon Genie"
    assert all(value is False for value in entry["authority"].values())


def test_oracle_signal_additive_shadow_contract_coverage_is_observed() -> None:
    contracts = load_contracts(CONTRACTS_DIR)
    reg = build_registry(contracts)
    entry = next(item for item in reg["pipelines"] if item["pipeline_id"] == "oracle_signal")
    assert entry["contract_status"] == "observed"
    assert entry["additive_shadow_contract_coverage"] is True
    assert entry["validation_status"] == "legacy_contract_posture"
    assert entry["typed_ir_status"] == "observed"
    assert "oracle_signal.intake_receipt" in entry["observed_contract_artifacts"]
    assert "oracle_signal.processing_packet" in entry["observed_contract_artifacts"]
    assert all(value is False for value in entry["authority"].values())


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
    assert all(all(value is False for value in item["authority"].values()) for item in reg["pipelines"])


def test_load_contracts_cache_invalidates_when_file_changes(tmp_path: Path):
    source = CONTRACTS_DIR / "aal_viz_projection.v1_1.json"
    target = tmp_path / source.name
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    assert load_contracts(tmp_path)[0].pipeline_id == "aal_viz_projection"

    payload = json.loads(target.read_text(encoding="utf-8"))
    payload["pipeline_id"] = "aal_viz_projection_v2"
    target.write_text(json.dumps(payload), encoding="utf-8")

    assert load_contracts(tmp_path)[0].pipeline_id == "aal_viz_projection_v2"
