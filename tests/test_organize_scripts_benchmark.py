#!/usr/bin/env python3
"""
Performance benchmarks for organize_scripts.py

Run with:
    pytest tests/test_organize_scripts_benchmark.py --benchmark-only -v

Or compare with baseline:
    pytest tests/test_organize_scripts_benchmark.py --benchmark-only --benchmark-autosave
"""

import pytest

from scripts.organize_scripts import resolve_target_dir, run_organization


def test_resolve_target_dir_performance(benchmark):
    """Benchmark prefix resolution speed."""
    result = benchmark(resolve_target_dir, "run_temporal_heavy_load_test.py")
    assert result == "temporal"


def test_organization_dry_run_performance(benchmark):
    """Benchmark full dry-run organization pass."""
    result = benchmark(run_organization, dry_run=True)

    assert result["status"] in ("success", "partial")
    assert result["moved_count"] >= 0


def test_organization_with_many_files(benchmark):
    """Simulate performance with larger number of scripts (dry-run)."""
    # This runs against the actual scripts/ directory
    result = benchmark(run_organization, dry_run=True)

    # We expect reasonable performance even with dozens of scripts
    assert result["moved_count"] + result["skipped_count"] > 0
