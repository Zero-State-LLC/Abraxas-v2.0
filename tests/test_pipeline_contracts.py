"""Tests for observed pipeline contracts."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.pipelines.models import PipelineContractV11
from core.pipelines.registry import load_contracts, load_pipeline_contract

CONTRACTS_DIR = Path("contracts/pipelines")

TIER1_FILES = [
    "research_intake.v1_1.json",
    "universal_ingest.v1_1.json",
    "pse_forecast.v1_1.json",
    "outcome_brier.v1_1.json",
    "canon_sync.v1_1.json",
    "research_drop_validation.v1_1.json",
    "aal_viz_projection.v1_1.json",
]

OBSERVED_NON_TIER1_FILES = [
    "alembic_spine.v1_1.json",
    "drift_scan.v1_1.json",
    "operator_review_queue.v1_1.json",
    "v2_hygiene.v1_1.json",
    "oracle_signal.v1_1.json",
]

TRACK_B_FILES = [
    "neon_genie_ideation.v1_1.json",
    "familiar_ingestion.v1_1.json",
    "noctis_dream.v1_1.json",
    "hollersports_ticket.v1_1.json",
    "memetic_futurecast.v1_1.json",
    "level99_content.v1_1.json",
    "beatoven_psyfi_integration.v1_1.json",
    "phonomicon_artifact.v1_1.json",
]


@pytest.mark.parametrize("filename", TIER1_FILES)
def test_tier1_contract_loads(filename: str):
    contract = load_pipeline_contract(CONTRACTS_DIR / filename)
    assert isinstance(contract, PipelineContractV11)
    assert contract.schema_version == "AbraxasPipelineAutomationContract.v1.1"


@pytest.mark.parametrize("filename", OBSERVED_NON_TIER1_FILES)
def test_observed_non_tier1_contract_loads(filename: str):
    contract = load_pipeline_contract(CONTRACTS_DIR / filename)
    assert isinstance(contract, PipelineContractV11)
    assert contract.schema_version == "AbraxasPipelineAutomationContract.v1.1"


@pytest.mark.parametrize("filename", TRACK_B_FILES)
def test_track_b_contract_loads_and_is_locked(filename: str):
    contract = load_pipeline_contract(CONTRACTS_DIR / filename)
    assert isinstance(contract, PipelineContractV11)
    assert contract.schema_version == "AbraxasPipelineAutomationContract.v1.1"
    contract.authority.assert_locked()
    assert "hold" in {item.value for item in contract.final_state_policy}
    assert "eligible_for_operator_review" in {item.value for item in contract.final_state_policy}


@pytest.mark.parametrize("filename", TIER1_FILES)
def test_tier1_contract_authority_locked(filename: str):
    contract = load_pipeline_contract(CONTRACTS_DIR / filename)
    contract.authority.assert_locked()  # should not raise


@pytest.mark.parametrize("filename", TIER1_FILES)
def test_tier1_contract_has_required_runes(filename: str):
    contract = load_pipeline_contract(CONTRACTS_DIR / filename)
    assert len(contract.required_runes) > 0


@pytest.mark.parametrize("filename", TIER1_FILES)
def test_tier1_contract_has_yggdrasil_nodes(filename: str):
    contract = load_pipeline_contract(CONTRACTS_DIR / filename)
    assert len(contract.yggdrasil_nodes) > 0


@pytest.mark.parametrize("filename", TIER1_FILES)
def test_tier1_contract_has_trigger(filename: str):
    contract = load_pipeline_contract(CONTRACTS_DIR / filename)
    assert contract.trigger.strip() != ""


def test_all_observed_pipeline_contracts_present():
    contracts = load_contracts(CONTRACTS_DIR)
    assert len(contracts) == 20
    pipeline_ids = {c.pipeline_id for c in contracts}
    assert "alembic_spine" in pipeline_ids
    assert set(filename.removesuffix(".v1_1.json") for filename in TRACK_B_FILES).issubset(pipeline_ids)
