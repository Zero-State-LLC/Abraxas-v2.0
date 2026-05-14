"""Tests for centralized config and path helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.config import RuntimePaths, api_public_readonly_enabled

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_runtime_paths_defaults_are_stable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CONTRACTS_DIR", raising=False)
    monkeypatch.delenv("OUT_DIR", raising=False)

    paths = RuntimePaths.from_env()

    assert paths == RuntimePaths.from_env()
    assert paths.contracts_dir == Path("contracts")
    assert paths.out_dir == Path("out")
    assert paths.pipelines_contracts_dir == Path("contracts/pipelines")
    assert paths.contracts_output_dir == Path("out/contracts")
    assert paths.audit_dir == Path("out/audit")
    assert paths.registry_latest == Path("out/registry/latest.json")
    assert paths.state_runtime_latest == Path("out/state/runtime.latest.json")


def test_runtime_paths_env_override_respected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTRACTS_DIR", "custom_contracts")
    monkeypatch.setenv("OUT_DIR", "custom_out")

    paths = RuntimePaths.from_env()

    assert paths.pipelines_contracts_dir == Path("custom_contracts/pipelines")
    assert paths.contracts_output_dir == Path("custom_out/contracts")
    assert paths.audit_dir == Path("custom_out/audit")
    assert paths.registry_latest == Path("custom_out/registry/latest.json")
    assert paths.validation_latest == Path("custom_out/validation/latest.json")
    assert paths.projection_aal_viz_latest == Path("custom_out/projections/aal_viz.latest.json")
    assert paths.state_runtime_latest == Path("custom_out/state/runtime.latest.json")


def test_runtime_paths_blank_override_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OUT_DIR", "   ")

    with pytest.raises(ValueError, match="OUT_DIR must not be blank"):
        RuntimePaths.from_env()


def test_runtime_paths_resolve_consistently(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CONTRACTS_DIR", raising=False)
    monkeypatch.delenv("OUT_DIR", raising=False)
    monkeypatch.chdir(REPO_ROOT)

    paths = RuntimePaths.from_env()

    assert paths.audit_dir.resolve() == REPO_ROOT / "out/audit"
    assert paths.contracts_output_dir.resolve() == REPO_ROOT / "out/contracts"
    assert paths.state_runtime_latest.resolve() == REPO_ROOT / "out/state/runtime.latest.json"
    assert paths.registry_latest.resolve() == REPO_ROOT / "out/registry/latest.json"


def test_api_public_readonly_invalid_value_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ABRAXAS_API_PUBLIC_READONLY", "maybe")

    with pytest.raises(ValueError, match="ABRAXAS_API_PUBLIC_READONLY"):
        api_public_readonly_enabled()
