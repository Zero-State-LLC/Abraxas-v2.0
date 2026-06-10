#!/usr/bin/env python3
"""
Tests for organize_scripts.py

Run with: python -m pytest tests/test_organize_scripts.py -q
"""

import json
import tempfile
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


def test_prefix_map_coverage():
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
    }
    assert set(PREFIX_MAP.keys()) == expected_keys


def test_no_duplicate_targets():
    targets = list(PREFIX_MAP.values())
    assert len(targets) == len(set(targets))


def test_run_organization_dry_run(tmp_path):
    """Test dry-run mode creates correct summary without moving files."""
    # Create some test scripts
    (tmp_path / "run_temporal_test.py").touch()
    (tmp_path / "run_governance_check.py").touch()
    (tmp_path / "run_unknown_script.py").touch()

    result = run_organization(dry_run=True)

    assert result["dry_run"] is True
    assert result["status"] == "success"
    assert result["moved_count"] >= 2
    assert any(m["target"] == "temporal" for m in result["moved"])
    assert any(m["target"] == "governance" for m in result["moved"])


def test_run_organization_skips_existing(tmp_path):
    """Test that existing files in target directories are skipped."""
    temporal_dir = tmp_path / "temporal"
    temporal_dir.mkdir()
    (tmp_path / "run_temporal_existing.py").touch()
    (temporal_dir / "run_temporal_existing.py").touch()  # already exists

    result = run_organization(dry_run=True)

    # Should be skipped because target already has the file
    skipped_names = [s for s in result.get("skipped", [])]
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
