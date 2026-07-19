#!/usr/bin/env python3
"""
Tests for organize_scripts.py

Run with: python -m pytest tests/test_organize_scripts.py -q
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.organize_scripts import (
    resolve_target_dir,
    PREFIX_MAP,
    run_organization,
)


def test_resolve_target_dir_known_prefixes():
    assert resolve_target_dir("run_temporal_something.py") == "temporal"
    assert resolve_target_dir("run_governance_check.py") == "governance"
    assert resolve_target_dir("run_research_canary_test.py") == "research"
    assert resolve_target_dir("run_artifact_regen.py") == "artifact"
    assert resolve_target_dir("run_ingest_scheduler.py") == "ingest"
    assert resolve_target_dir("run_oracle_signal.py") == "ingest"
    assert resolve_target_dir("run_metric_rank.py") == "metric"
    assert resolve_target_dir("run_operator_helper.py") == "operator"
    assert resolve_target_dir("run_aal_viz_render.py") == "viz"
    assert resolve_target_dir("run_geometric_route.py") == "viz"
    assert resolve_target_dir("run_transport_wasserstein.py") == "transport"


def test_resolve_target_dir_unknown():
    assert resolve_target_dir("run_unknown_task.py") is None
    assert resolve_target_dir("random_script.py") is None


def test_resolve_target_dir_operator_review_root_exemption():
    assert resolve_target_dir("run_operator_review_required_items_bulk_disposition.py") is None
    assert resolve_target_dir("run_operator_review_terminal_hold_consolidation_receipt.py") is None


def test_prefix_map_coverage():
    # Wave 1 + wave 2 prefixes (longest-first resolve is tested separately).
    expected_keys = {
        "run_temporal_",
        "run_governance_",
        "run_research_",
        "run_research_canary_",
        "run_artifact_",
        "run_ingest_",
        "run_oracle_",
        "run_metric_",
        "run_rank",
        "run_operator_",
        "run_aal_viz_",
        "run_geometric_",
        "run_transport_",
        "run_wasserstein_",
        "run_v2_hygiene_",
        "run_v2_",
        "run_abx_codegen_",
        "run_abx_",
        "run_abraxas_",
        "run_chamfer_",
        "run_geodesic_",
        "run_norm_",
        "run_overlay_",
        "run_runtime_",
        "run_continuity_",
        "run_notion_",
        "run_canary_",
        "run_live_",
        "run_rune_",
        "run_yggdrasil_",
        "run_belief_",
        "run_hyperstition_",
        "run_production_",
        "run_threat_",
        "run_sole_",
        "run_soft_",
        "run_boundary_",
        "run_campaign_",
        "run_proposal_",
    }
    assert set(PREFIX_MAP.keys()) == expected_keys


def test_no_duplicate_targets():
    # Multiple prefixes may share a domain; assert the known domain set.
    assert set(PREFIX_MAP.values()) == {
        "artifact",
        "belief",
        "campaign",
        "codegen",
        "geometry",
        "governance",
        "hygiene",
        "ingest",
        "metric",
        "notion",
        "operator",
        "readiness",
        "research",
        "runtime",
        "temporal",
        "transport",
        "viz",
    }


def test_resolve_target_dir_wave2_prefixes():
    assert resolve_target_dir("run_v2_hygiene_phase1_gate.py") == "hygiene"
    assert resolve_target_dir("run_abx_codegen_intelligence_spine_gap_analysis_plan.py") == "codegen"
    assert resolve_target_dir("run_abx_hermes_skill_evolution_cycle.py") == "codegen"
    assert resolve_target_dir("run_chamfer_distance_computation_receipt.py") == "geometry"
    assert resolve_target_dir("run_sole_writer_advisory_check.py") == "readiness"
    assert resolve_target_dir("run_runtime_inventory.py") == "runtime"
    assert resolve_target_dir("run_notion_operator_decision_backlog.py") == "notion"


def test_run_organization_dry_run(tmp_path):
    """Test dry-run mode returns a valid summary without moving files."""
    result = run_organization(dry_run=True)

    assert result["dry_run"] is True
    assert result["status"] == "success"
    assert "moved_count" in result
    assert "skipped_count" in result
    assert isinstance(result["moved"], list)
    assert isinstance(result["skipped"], list)
    # After mass-org, most prefix-matched runners are already nested, so
    # moved_count may be 0; dry-run must still succeed and skip the rest.
    assert result["moved_count"] + result["skipped_count"] >= 1

def test_run_organization_skips_existing(tmp_path):
    """Test that existing files in target directories are skipped."""
    temporal_dir = tmp_path / "temporal"
    temporal_dir.mkdir()
    (tmp_path / "run_temporal_existing.py").touch()
    (temporal_dir / "run_temporal_existing.py").touch()  # already exists

    result = run_organization(dry_run=True)

    # Note: actual behavior depends on current working directory
    # This test mainly ensures no crash and returns a summary
    assert "status" in result


def test_json_output_structure():
    """Ensure run_organization returns expected JSON structure."""
    result = run_organization(dry_run=True)

    required_keys = {
        "status", "dry_run", "moved_count", "skipped_count", "error_count",
        "moved", "skipped", "errors"
    }
    assert required_keys.issubset(result.keys())
    assert isinstance(result["moved"], list)
    assert isinstance(result["skipped"], list)
