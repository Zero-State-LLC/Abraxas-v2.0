from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from core.operator_runtime_console import _summarize_runtime_profile
from scripts.run_runtime_performance_profile import (
    _B003_ACKNOWLEDGMENT_HASH,
    _B003_ACKNOWLEDGMENT_PATH,
    _BENCHMARK_PATH,
    _CHECKPOINT_ID,
    run,
)


def _output_path(tmp_path: Path) -> Path:
    p = tmp_path / "out" / "audit" / "runtime_performance_profile_001.latest.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _run(tmp_path: Path) -> dict[str, Any]:
    return run(repo_root=tmp_path, out_path=_output_path(tmp_path))


class TestOutputFileCreation:
    def test_output_file_created(self, tmp_path):
        _run(tmp_path)
        assert _output_path(tmp_path).exists()

    def test_output_file_valid_json(self, tmp_path):
        _run(tmp_path)
        content = _output_path(tmp_path).read_text(encoding="utf-8")
        parsed = json.loads(content)
        assert isinstance(parsed, dict)

    def test_output_file_non_empty(self, tmp_path):
        _run(tmp_path)
        assert _output_path(tmp_path).stat().st_size > 0


class TestProfileReadiness:
    def test_profile_enabled_true(self, tmp_path):
        packet = _run(tmp_path)
        assert packet["profile_enabled"] is True

    def test_final_status_pass(self, tmp_path):
        packet = _run(tmp_path)
        assert packet["final_status"] == "PASS"

    def test_remaining_blockers_empty(self, tmp_path):
        packet = _run(tmp_path)
        assert packet["remaining_blockers"] == []

    def test_measured_surfaces_contains_registry_generation(self, tmp_path):
        packet = _run(tmp_path)
        assert "registry_generation" in packet["measured_surfaces"]

    def test_patch_id_correct(self, tmp_path):
        packet = _run(tmp_path)
        assert packet["patch_id"] == "PATCH-P8-RUNTIME-PERFORMANCE-PROFILING-001"


class TestAuthorityLocks:
    def test_authority_granted_false(self, tmp_path):
        packet = _run(tmp_path)
        assert packet["authority_granted"] is False

    def test_mutation_allowed_false(self, tmp_path):
        packet = _run(tmp_path)
        assert packet["mutation_allowed"] is False

    def test_promotion_allowed_false(self, tmp_path):
        packet = _run(tmp_path)
        assert packet["promotion_allowed"] is False


class TestProvenanceFields:
    def test_b003_acknowledgment_artifact_path_recorded(self, tmp_path):
        packet = _run(tmp_path)
        paths = packet.get("artifact_paths", {})
        assert "b003_acknowledgment_artifact" in paths
        assert _B003_ACKNOWLEDGMENT_PATH in paths["b003_acknowledgment_artifact"]

    def test_benchmark_artifact_path_recorded(self, tmp_path):
        packet = _run(tmp_path)
        paths = packet.get("artifact_paths", {})
        assert "benchmark_artifact" in paths
        assert _BENCHMARK_PATH in paths["benchmark_artifact"]

    def test_checkpoint_id_recorded(self, tmp_path):
        packet = _run(tmp_path)
        corr = packet.get("correlation_ids", {})
        assert "b004_checkpoint_ref" in corr
        assert corr["b004_checkpoint_ref"] == _CHECKPOINT_ID

    def test_b003_acknowledgment_hash_recorded(self, tmp_path):
        packet = _run(tmp_path)
        corr = packet.get("correlation_ids", {})
        assert "b003_acknowledgment_hash" in corr
        assert corr["b003_acknowledgment_hash"] == _B003_ACKNOWLEDGMENT_HASH


class TestCheckpointResolution:
    def test_satisfies_summarize_runtime_profile(self, tmp_path):
        _run(tmp_path)
        content = json.loads(_output_path(tmp_path).read_text(encoding="utf-8"))
        summary = _summarize_runtime_profile(content)
        assert summary["status"] == "PRESENT"
        assert summary["final_status"] == "PASS"
        assert summary["profile_enabled"] is True
        assert summary["authority_granted"] is False
        assert summary["mutation_allowed"] is False

    def test_summarize_returns_not_computable_when_absent(self, tmp_path):
        summary = _summarize_runtime_profile(None)
        assert summary["status"] == "NOT_COMPUTABLE"


class TestDeterminism:
    def test_identical_inputs_produce_identical_json(self, tmp_path):
        _run(tmp_path)
        r1 = json.loads(_output_path(tmp_path).read_text(encoding="utf-8"))
        _run(tmp_path)
        r2 = json.loads(_output_path(tmp_path).read_text(encoding="utf-8"))
        assert r1["profile_enabled"] == r2["profile_enabled"]
        assert r1["final_status"] == r2["final_status"]
        assert r1["measured_surfaces"] == r2["measured_surfaces"]
        assert r1["patch_id"] == r2["patch_id"]
        assert r1["authority_granted"] == r2["authority_granted"]

    def test_packet_stable_across_calls(self, tmp_path):
        p1 = _run(tmp_path)
        p2 = _run(tmp_path)
        assert p1["final_status"] == p2["final_status"]
        assert p1["profile_enabled"] == p2["profile_enabled"]
        assert p1["measured_surfaces"] == p2["measured_surfaces"]
