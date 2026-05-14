from __future__ import annotations

from pathlib import Path

from core.diagnostics import format_event, stable_correlation_id


def test_format_event_is_canonical_and_deterministic() -> None:
    assert format_event(
        "state_engine_input_malformed",
        "ERROR",
        reason="input_malformed",
        artifact_path="out/state/runtime.latest.json",
        correlation_id="state_engine_input:abc123",
    ) == (
        '{"artifact_path":"out/state/runtime.latest.json",'
        '"correlation_id":"state_engine_input:abc123",'
        '"event":"state_engine_input_malformed",'
        '"reason":"input_malformed",'
        '"severity":"ERROR"}'
    )


def test_stable_correlation_id_has_no_random_entropy() -> None:
    context = {"inputs": ["out/execution/latest.json", "out/replay/latest.json"]}
    first = stable_correlation_id(
        "state_runtime_write",
        artifact_path="out/state/runtime.latest.json",
        context=context,
    )
    second = stable_correlation_id(
        "state_runtime_write",
        artifact_path="out/state/runtime.latest.json",
        context=context,
    )

    assert first == second
    assert first.startswith("state_runtime_write:")
    assert len(first.split(":", maxsplit=1)[1]) == 16


def test_stable_correlation_id_normalizes_path_inputs() -> None:
    expected = stable_correlation_id(
        "registry_generation",
        artifact_path="out/registry/latest.json",
        context={"contracts_dir": "contracts/pipelines"},
    )

    assert expected == stable_correlation_id(
        "registry_generation",
        artifact_path=Path("out/registry/latest.json"),
        context={"contracts_dir": "contracts/pipelines"},
    )
