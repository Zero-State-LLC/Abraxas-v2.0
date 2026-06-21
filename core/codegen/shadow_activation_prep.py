from __future__ import annotations

from typing import Any, Mapping, Sequence

from core.canonical.json import canonical_hash


SHADOW_PREP_SCHEMA_VERSION = "AbxCodegenShadowRuntimeActivationPrep.v1"


def build_shadow_runtime_activation_prep(
    *,
    timestamp: str,
    fixture_paths: Sequence[str],
    oracle_signal_intake_paths: Sequence[str],
    provenance: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": SHADOW_PREP_SCHEMA_VERSION,
        "status": "SHADOW_RUNTIME_ACTIVATION_PREP_ADVISORY_ONLY",
        "timestamp": timestamp,
        "fixture_paths": list(fixture_paths),
        "oracle_signal_intake_paths": list(oracle_signal_intake_paths),
        "integration_points": [
            {
                "name": "codegen_shadow_replay_fixture_gate",
                "mode": "fixture_validation_only",
                "valid_for_execution": False,
                "brier_score": 0.1,
            },
            {
                "name": "oracle_signal_intake_reference",
                "mode": "read_only_path_reference",
                "valid_for_execution": False,
                "brier_score": 0.11,
            },
        ],
        "authority_locks": {
            "advisory_only": True,
            "runtime_mutation": False,
            "execution_authority": False,
            "scheduler_mutation": False,
            "queue_mutation": False,
            "github_writeback": False,
            "notion_writeback": False,
        },
        "valid_for_execution": False,
        "valid_for_runtime_activation": False,
        "provenance": dict(provenance),
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}
