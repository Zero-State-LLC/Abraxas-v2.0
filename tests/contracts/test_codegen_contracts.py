from __future__ import annotations

from core.canonical.json import canonical_hash

from contracts.codegen import (
    CODEGEN_SCHEMA_NAMES,
    CodeDropEnvelope,
    CodegenTaskPacket,
    PatchContract,
    load_codegen_schema,
    validate_canonical_hash_field,
    validate_codegen_model,
)

HEX_A = "a" * 64
HEX_B = "b" * 64
HEX_C = "c" * 64

PROVENANCE = {
    "source_gap_analysis": (
        "out/audit/abx_codegen_intelligence_spine_gap_analysis_plan_001.latest.json"
    ),
    "continuity_lane": "P102G+CODEGEN-ADVISORY",
    "generated_by": "ABX_CODEGEN_INTELLIGENCE_SPINE",
}

LANE_SIGNALS = {
    "lane": "ADVISORY_STACK_HELD_FOR_OPERATOR",
    "downstream": "NOT_COMPUTABLE",
    "advisory_only": True,
    "projection_only": True,
    "shadow_replay_emphasis": True,
    "safe_to_auto_continue": False,
    "valid_for_execution": False,
}


def _patch_payload() -> dict:
    return {
        "schema_version": "PatchContract.v1",
        "patch_id": HEX_A,
        "target_path": "contracts/codegen/schemas/PatchContract.json",
        "change_type": "ADD",
        "proposed_content": {"schema_version": "PatchContract.v1"},
        "rationale": "Create advisory codegen patch contract.",
        "lane_signals": LANE_SIGNALS,
        "provenance": PROVENANCE,
    }


def test_codegen_schemas_load() -> None:
    for schema_name in CODEGEN_SCHEMA_NAMES:
        schema = load_codegen_schema(schema_name)
        assert schema["title"] == f"{schema_name}.v1"


def test_patch_contract_model_preserves_authority_locks() -> None:
    patch = PatchContract.model_validate(_patch_payload())
    locks = patch.authority_locks.model_dump()

    assert locks["advisory_only"] is True
    assert all(value is False for key, value in locks.items() if key != "advisory_only")


def test_codegen_envelope_canonical_hash_validation() -> None:
    envelope = CodeDropEnvelope.model_validate(
        {
            "schema_version": "CodeDropEnvelope.v1",
            "envelope_id": HEX_B,
            "timestamp": "2026-06-21T00:00:00Z",
            "patches": [_patch_payload()],
            "required_fixtures": [
                "tests/fixtures/codegen/improvement_proposal_golden.v1.json"
            ],
            "validation_commands": ["python -m pytest tests/codegen"],
            "residual_risks": ["Operator attestation still required."],
            "lane_signals": LANE_SIGNALS,
            "provenance": PROVENANCE,
        }
    )
    payload = envelope.model_dump()
    payload["canonical_hash"] = canonical_hash(
        {key: value for key, value in payload.items() if key != "canonical_hash"}
    )

    assert validate_canonical_hash_field(payload) == payload["canonical_hash"]
    assert validate_codegen_model(payload).schema_version == "CodeDropEnvelope.v1"


def test_codegen_task_packet_requires_validation_commands() -> None:
    packet = CodegenTaskPacket.model_validate(
        {
            "schema_version": "CodegenTaskPacket.v1",
            "task_id": HEX_C,
            "phase": "PHASE_1_CONTRACTS_CODEGEN_SCHEMAS",
            "evidence_packet_sections": [
                "BOUNDARY",
                "EVIDENCE PACKET",
                "TASK",
                "OUTPUT",
                "VALIDATION",
                "RESIDUAL RISKS",
                "RECOMMENDED NEXT ADVISORY ACTION",
            ],
            "target_paths": ["contracts/codegen/"],
            "validation_commands": ["python -m pyright contracts/codegen/"],
            "lane_signals": LANE_SIGNALS,
            "provenance": PROVENANCE,
        }
    )

    assert packet.operator_gate_required is True
