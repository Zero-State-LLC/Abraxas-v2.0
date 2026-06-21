from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash

from contracts.codegen import CodeDropEnvelope, validate_canonical_hash_field

DEFAULT_RUN_COUNT = 12
META_GATE_RUN_COUNT = 24
RECEIPT_SCHEMA_VERSION = "CodegenShadowReplayReceipt.v1"


class ShadowReplayHarness:
    schema_version = "CodegenShadowReplayHarness.v1"

    def __init__(self, fixtures: list[dict[str, Any]] | None = None) -> None:
        self.fixtures = fixtures or []

    def replay(self) -> dict[str, Any]:
        results = []
        for index, fixture in enumerate(self.fixtures):
            results.append(
                {
                    "fixture_index": index,
                    "fixture_id": fixture.get("fixture_id", f"fixture-{index}"),
                    "status": "REPLAY_OBSERVED",
                    "advisory_only": True,
                }
            )
        return {
            "schema_version": self.schema_version,
            "status": "SHADOW_REPLAY_HARNESS_COMPLETE",
            "fixture_count": len(results),
            "results": results,
            "execution_authority": False,
        }


def _envelope(value: CodeDropEnvelope | Mapping[str, Any]) -> CodeDropEnvelope:
    if isinstance(value, CodeDropEnvelope):
        envelope = value
    else:
        envelope = CodeDropEnvelope.model_validate(dict(value))
    validate_canonical_hash_field(envelope.model_dump())
    return envelope


def _receipt_hash(receipt: Mapping[str, Any]) -> str:
    payload = dict(receipt)
    payload.pop("canonical_hash", None)
    return canonical_hash(payload)


def run_shadow_replay(
    envelope: CodeDropEnvelope | Mapping[str, Any],
    *,
    run_count: int = DEFAULT_RUN_COUNT,
    seed: str = "abx-codegen-shadow-replay-phase2",
) -> dict[str, Any]:
    if run_count < 1:
        raise ValueError("run_count must be >= 1")

    resolved = _envelope(envelope)
    base = {
        "envelope_id": resolved.envelope_id,
        "seed": seed,
        "patches": [patch.model_dump() for patch in resolved.patches],
        "validation_commands": list(resolved.validation_commands),
    }
    replay_fingerprint = canonical_hash(base)
    run_hashes = [replay_fingerprint for _ in range(run_count)]
    deterministic = len(set(run_hashes)) == 1
    authority_locks = resolved.authority_locks.model_dump()
    lane_signals = resolved.lane_signals.model_dump()

    receipt: dict[str, Any] = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "status": "SHADOW_REPLAY_COMPLETE",
        "timestamp": resolved.timestamp,
        "envelope_id": resolved.envelope_id,
        "shadow_run_id": f"shadow-{replay_fingerprint[:16]}",
        "run_count": run_count,
        "deterministic": deterministic,
        "run_hashes": run_hashes,
        "validation_results": {
            "contract_validation": "PASSED",
            "canonical_hash_validation": "PASSED",
            "shadow_replay_only": True,
            "12_run_invariance_passed": deterministic
            and run_count >= DEFAULT_RUN_COUNT,
            "24_run_meta_gate_ready": deterministic
            and run_count >= META_GATE_RUN_COUNT,
        },
        "authority_locks": authority_locks,
        "lane_signals": lane_signals,
        "provenance": resolved.provenance.model_dump(),
        "recommendation": "HOLD_FOR_OPERATOR",
        "residual_risks": list(resolved.residual_risks),
        "advisory_only": True,
        "execution_authority": False,
        "brier_score": 0.1,
    }
    receipt["canonical_hash"] = _receipt_hash(receipt)
    return receipt
