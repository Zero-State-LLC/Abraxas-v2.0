from __future__ import annotations

from core.canonical.json import canonical_hash

from contracts.codegen import CodegenTaskPacket

from core.codegen import (
    DEFAULT_LANE_SIGNALS,
    DEFAULT_PROVENANCE,
    build_code_drop_envelope,
    build_patch_contract,
    run_codegen_harness,
    run_task_packet,
)


def _patch_content() -> dict[str, str]:
    return {"schema_version": "ExampleCodegenSurface.v1"}


def test_build_patch_contract_is_deterministic_and_advisory_only() -> None:
    first = build_patch_contract(
        target_path="core/codegen/example.py",
        change_type="ADD",
        proposed_content=_patch_content(),
        rationale="Exercise the advisory PHASE_2 builder.",
    )
    second = build_patch_contract(
        target_path="core/codegen/example.py",
        change_type="ADD",
        proposed_content=_patch_content(),
        rationale="Exercise the advisory PHASE_2 builder.",
    )

    assert first.patch_id == second.patch_id
    locks = first.authority_locks.model_dump()
    assert locks["advisory_only"] is True
    assert all(value is False for key, value in locks.items() if key != "advisory_only")


def test_code_drop_envelope_hash_is_stable() -> None:
    patch = build_patch_contract(
        target_path="core/codegen/example.py",
        change_type="ADD",
        proposed_content=_patch_content(),
        rationale="Exercise the advisory PHASE_2 envelope.",
    )
    envelope = build_code_drop_envelope(
        patches=[patch],
        timestamp="2026-06-21T00:00:00Z",
        required_fixtures=["tests/fixtures/codegen/improvement_proposal_golden.v1.json"],
        validation_commands=["python -m pytest tests/codegen"],
        residual_risks=["Operator gate still required."],
    )
    payload = envelope.model_dump()

    assert payload["canonical_hash"] == canonical_hash(
        {key: value for key, value in payload.items() if key != "canonical_hash"}
    )


def test_run_codegen_harness_emits_shadow_only_receipt() -> None:
    patch = build_patch_contract(
        target_path="core/codegen/example.py",
        change_type="ADD",
        proposed_content=_patch_content(),
        rationale="Exercise the advisory PHASE_2 replay.",
    )
    envelope = build_code_drop_envelope(
        patches=[patch],
        timestamp="2026-06-21T00:00:00Z",
        required_fixtures=(),
        validation_commands=["python -m pytest tests/codegen"],
        residual_risks=["Operator gate still required."],
    )
    receipt = run_codegen_harness(envelope)

    assert receipt["status"] == "SHADOW_REPLAY_COMPLETE"
    assert receipt["recommendation"] == "HOLD_FOR_OPERATOR"
    assert receipt["advisory_only"] is True
    assert receipt["execution_authority"] is False
    assert receipt["validation_results"]["12_run_invariance_passed"] is True
    assert receipt["authority_locks"]["runtime_mutation"] is False


def test_run_task_packet_carries_task_provenance() -> None:
    patch = build_patch_contract(
        target_path="core/codegen/example.py",
        change_type="ADD",
        proposed_content=_patch_content(),
        rationale="Exercise the advisory PHASE_2 task runner.",
    )
    packet = CodegenTaskPacket.model_validate(
        {
            "schema_version": "CodegenTaskPacket.v1",
            "task_id": "d" * 64,
            "phase": "PHASE_2_CORE_CODEGEN_HARNESS",
            "evidence_packet_sections": [
                "BOUNDARY",
                "EVIDENCE PACKET",
                "TASK",
                "OUTPUT",
                "VALIDATION",
                "RESIDUAL RISKS",
                "RECOMMENDED NEXT ADVISORY ACTION",
            ],
            "target_paths": ["core/codegen/"],
            "validation_commands": ["python -m pyright core/codegen"],
            "lane_signals": DEFAULT_LANE_SIGNALS,
            "provenance": DEFAULT_PROVENANCE,
        }
    )
    receipt = run_task_packet(
        packet,
        patches=[patch],
        timestamp="2026-06-21T00:00:00Z",
        residual_risks=["Operator attestation required before PHASE_3."],
    )

    assert receipt["source_task_id"] == packet.task_id
    assert receipt["lane_signals"]["safe_to_auto_continue"] is False
    assert receipt["canonical_hash"] == canonical_hash(
        {key: value for key, value in receipt.items() if key != "canonical_hash"}
    )
