"""Tests for runtime performance profiling helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.performance import (
    PATCH_ID,
    PROFILE_ENV_FLAG,
    RuntimeProfiler,
    build_profile_correlation_id,
    runtime_profiling_enabled,
    stable_phase_name,
)


def test_runtime_profiling_disabled_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(PROFILE_ENV_FLAG, raising=False)

    assert runtime_profiling_enabled() is False


def test_runtime_profiling_malformed_flag_fails_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(PROFILE_ENV_FLAG, "maybe")

    assert runtime_profiling_enabled() is False


def test_runtime_profile_packet_shape_is_stable(tmp_path: Path) -> None:
    profiler = RuntimeProfiler(tmp_path / "runtime_profile.latest.json", enabled=True)

    profiler.record_artifact("registry_output", Path("out/registry/latest.json"))
    profiler.record_correlation(
        "registry_generation",
        namespace="registry_generation",
        artifact_path=Path("out/registry/latest.json"),
        context={"contracts_dir": "contracts/pipelines"},
    )
    with profiler.measure("registry_generation", "load_contracts"):
        pass

    packet = profiler.build_packet()

    assert list(packet) == [
        "patch_id",
        "profile_enabled",
        "measured_surfaces",
        "phase_timings",
        "artifact_paths",
        "correlation_ids",
        "authority_granted",
        "mutation_allowed",
        "promotion_allowed",
        "final_status",
        "remaining_blockers",
    ]
    assert packet["patch_id"] == PATCH_ID
    assert packet["profile_enabled"] is True
    assert packet["measured_surfaces"] == ["registry_generation"]
    assert packet["artifact_paths"] == {
        "profile_artifact": (tmp_path / "runtime_profile.latest.json").as_posix(),
        "registry_output": "out/registry/latest.json",
    }
    assert packet["phase_timings"] == {
        "registry_generation.load_contracts": {
            "duration_ns": packet["phase_timings"]["registry_generation.load_contracts"][
                "duration_ns"
            ],
            "observational_only": True,
        }
    }
    assert packet["final_status"] == "PASS"
    assert packet["remaining_blockers"] == []


def test_phase_names_are_deterministic() -> None:
    assert (
        stable_phase_name("validation_generation", "load_contracts")
        == "validation_generation.load_contracts"
    )
    assert stable_phase_name("validation_generation", "load_contracts") == stable_phase_name(
        "validation_generation", "load_contracts"
    )


def test_profile_correlation_id_is_stable_for_same_inputs() -> None:
    correlation_id = build_profile_correlation_id(
        "validation_generation",
        artifact_path="out/validation/latest.json",
        context={"contracts_dir": "contracts/pipelines"},
    )

    assert correlation_id == build_profile_correlation_id(
        "validation_generation",
        artifact_path="out/validation/latest.json",
        context={"contracts_dir": "contracts/pipelines"},
    )


def test_runtime_profile_authority_flags_are_all_false(tmp_path: Path) -> None:
    profiler = RuntimeProfiler(tmp_path / "runtime_profile.latest.json", enabled=True)

    packet = profiler.build_packet(final_status="NOT_COMPUTABLE")

    assert packet["authority_granted"] is False
    assert packet["mutation_allowed"] is False
    assert packet["promotion_allowed"] is False


def test_runtime_profiler_write_uses_deterministic_json(tmp_path: Path) -> None:
    output_path = tmp_path / "runtime_profile.latest.json"
    profiler = RuntimeProfiler(output_path, enabled=True)
    with profiler.measure("artifact_contract_inventory", "build_inventory"):
        pass

    written_path = profiler.write()

    assert written_path == output_path
    text = output_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    payload = json.loads(text)
    assert payload["patch_id"] == PATCH_ID
