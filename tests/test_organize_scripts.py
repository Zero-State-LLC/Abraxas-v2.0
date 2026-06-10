#!/usr/bin/env python3
"""
Basic tests for organize_scripts.py

Run with: python -m pytest tests/test_organize_scripts.py -q
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path so we can import the script
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.organize_scripts import resolve_target_dir, PREFIX_MAP


def test_resolve_target_dir_known_prefixes():
    """Test that known prefixes resolve to correct directories."""
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
    """Unknown prefixes should return None."""
    assert resolve_target_dir("run_unknown_task.py") is None
    assert resolve_target_dir("random_script.py") is None


def test_prefix_map_coverage():
    """Ensure PREFIX_MAP contains expected keys."""
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
    """Ensure no prefix maps to conflicting directories."""
    targets = list(PREFIX_MAP.values())
    assert len(targets) == len(set(targets)), "Duplicate target directories found"
