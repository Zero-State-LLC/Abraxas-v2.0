from __future__ import annotations

from typing import Any, Mapping, Sequence

from contracts.codegen import CodeDropEnvelope, CodegenTaskPacket, PatchContract

from core.codegen.builder import build_code_drop_envelope
from core.codegen.shadow_activation_prep import build_shadow_runtime_activation_prep
from core.codegen.shadow_replay_harness import DEFAULT_RUN_COUNT, run_shadow_replay


def run_codegen_harness(
    envelope: CodeDropEnvelope | Mapping[str, Any],
    *,
    run_count: int = DEFAULT_RUN_COUNT,
) -> dict[str, Any]:
    return run_shadow_replay(envelope, run_count=run_count)


def run_task_packet(
    task_packet: CodegenTaskPacket | Mapping[str, Any],
    *,
    patches: Sequence[PatchContract | Mapping[str, Any]],
    timestamp: str,
    residual_risks: Sequence[str],
    run_count: int = DEFAULT_RUN_COUNT,
) -> dict[str, Any]:
    packet = (
        task_packet
        if isinstance(task_packet, CodegenTaskPacket)
        else CodegenTaskPacket.model_validate(dict(task_packet))
    )
    envelope = build_code_drop_envelope(
        patches=patches,
        timestamp=timestamp,
        required_fixtures=(),
        validation_commands=packet.validation_commands,
        residual_risks=residual_risks,
        lane_signals=packet.lane_signals.model_dump(),
        provenance=packet.provenance.model_dump(),
    )
    receipt = run_shadow_replay(envelope, run_count=run_count)
    receipt["source_task_id"] = packet.task_id
    receipt["canonical_hash"] = _canonical_hash_without_existing(receipt)
    return receipt


def prepare_shadow_runtime_activation(
    *,
    timestamp: str,
    fixture_paths: Sequence[str],
    oracle_signal_intake_paths: Sequence[str],
    provenance: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a PHASE_7 advisory prep receipt without executing runtime code."""

    return build_shadow_runtime_activation_prep(
        timestamp=timestamp,
        fixture_paths=fixture_paths,
        oracle_signal_intake_paths=oracle_signal_intake_paths,
        provenance=provenance,
    )


def _canonical_hash_without_existing(receipt: Mapping[str, Any]) -> str:
    from core.canonical.json import canonical_hash

    payload = dict(receipt)
    payload.pop("canonical_hash", None)
    return canonical_hash(payload)
