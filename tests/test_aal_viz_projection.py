"""Tests for AAL-Viz projection."""

from __future__ import annotations

from pathlib import Path


from core.pipelines.registry import build_registry, load_contracts
from core.operators.review_queue import build_review_queue
from core.projections.aal_viz import build_projection_packet
from core.pipelines.validator import validate_pipeline_contract
from core.runes.registry import load_rune_catalog
from core.yggdrasil.validator import load_route_graphs

CONTRACTS_DIR = Path("contracts/pipelines")
RUNE_CATALOG_PATH = Path("contracts/runes/catalog.v1.json")
ROUTES_DIR = Path("contracts/yggdrasil/routes")


def _build_packet():
    rune_catalog = load_rune_catalog(RUNE_CATALOG_PATH)
    route_graphs = load_route_graphs(ROUTES_DIR)
    contracts = load_contracts(CONTRACTS_DIR)
    registry = build_registry(contracts)
    results = []
    for contract in contracts:
        graph_data = (
            route_graphs[contract.pipeline_id].model_dump()
            if contract.pipeline_id in route_graphs
            else None
        )
        results.append(validate_pipeline_contract(contract, rune_catalog, graph_data))
    queue = build_review_queue(results)
    return build_projection_packet(registry, results, queue)


def test_projection_packet_builds():
    packet = _build_packet()
    assert packet["schema_version"] == "GlobalPipelineAALVizProjectionPacket.v1"


def test_projection_only_is_true():
    packet = _build_packet()
    assert packet["projection_only"] is True


def test_inference_authority_is_false():
    packet = _build_packet()
    assert packet["inference_authority"] is False


def test_authority_all_false():
    packet = _build_packet()
    auth = packet["authority"]
    assert all(v is False for v in auth.values())


def test_summary_has_expected_fields():
    packet = _build_packet()
    summary = packet["summary"]
    assert "total_pipelines" in summary
    assert "doctrine_compliant" in summary
    assert "repair_required" in summary
    assert "not_computable" in summary


def test_panels_present():
    packet = _build_packet()
    contracts = load_contracts(CONTRACTS_DIR)
    assert len(packet["panels"]) == len(contracts)


def test_projection_packet_deterministic():
    p1 = _build_packet()
    p2 = _build_packet()
    assert p1 == p2


def test_projection_has_doctrine_posture_summary():
    packet = _build_packet()
    posture = packet["doctrine_posture_summary"]
    assert {
        "doctrine_compliant",
        "repair_required",
        "legacy_contract_posture",
        "not_computable",
        "failed",
        "seal_recommendation",
    }.issubset(posture.keys())


def test_projection_has_oracle_summary():
    packet = _build_packet()
    oracle = packet["oracle_summary"]
    assert {
        "intake_runs",
        "stabilized_intakes",
        "replay_matches",
        "unresolved_conflicts",
        "lineage_depth",
        "replay_failures",
        "pending_reviews",
    }.issubset(oracle.keys())


def test_projection_has_forecast_summary():
    packet = _build_packet()
    forecast = packet["forecast_summary"]
    assert {
        "candidate_forecasts",
        "calibrated_forecasts",
        "replay_matches",
        "unresolved_bindings",
        "calibration_average",
        "stabilization_state",
        "pending_reviews",
    }.issubset(forecast.keys())


def test_projection_has_brier_summary():
    packet = _build_packet()
    brier = packet["brier_summary"]
    assert {
        "scored_forecasts",
        "average_brier",
        "calibration_average",
        "reliability_score",
        "replay_matches",
        "replay_failures",
        "stabilization_state",
        "pending_reviews",
    }.issubset(brier.keys())


def test_projection_has_drift_summary():
    packet = _build_packet()
    drift = packet["drift_summary"]
    assert {
        "drift_proposals",
        "active_overlays",
        "average_overlay_weight",
        "drift_confidence",
        "replay_matches",
        "replay_failures",
        "stabilization_state",
        "pending_reviews",
    }.issubset(drift.keys())


def test_projection_has_milestone_summary():
    packet = _build_packet()
    m = packet["milestone_summary"]
    assert {
        "active_milestone",
        "stabilized_milestones",
        "latest_stable_hash",
        "lineage_depth",
        "milestone_validator_status",
    }.issubset(m.keys())


def test_projection_has_overlay_firewall_summary_and_invariants():
    packet = _build_packet()
    s = packet["overlay_firewall_summary"]
    assert {
        "firewall_status",
        "blocked_reasons",
        "rollback_ready",
        "replay_matches",
        "critical_diagnostics",
        "containment_restrictions",
        "governance_continuity",
        "operator_review_required",
    }.issubset(s.keys())
    assert s["projection_only"] is True
    assert s["inference_authority"] is False
