"""Oracle measurement proposal advisory packet builders.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no measurement authorization or execution.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


def build_oracle_measurement_proposal(
    *,
    timestamp: str,
    oracle_measurement_readiness: Mapping[str, Any],
    oracle_shadow_measurement: Mapping[str, Any],
    oracle_shadow_measurement_receipt: Mapping[str, Any],
    oracle_operator_decision_intake: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleMeasurementProposal.v1",
        "proposal_id": canonical_hash(
            {
                "record": "oracle_measurement_proposal",
                "oracle_measurement_readiness_hash": oracle_measurement_readiness[
                    "canonical_hash"
                ],
                "oracle_shadow_measurement_hash": oracle_shadow_measurement[
                    "canonical_hash"
                ],
                "oracle_shadow_measurement_receipt_hash": (
                    oracle_shadow_measurement_receipt["canonical_hash"]
                ),
            }
        ),
        "proposal_status": "ORACLE_MEASUREMENT_PROPOSAL_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "source_packet_hashes": {
            "oracle_measurement_readiness": oracle_measurement_readiness[
                "canonical_hash"
            ],
            "oracle_shadow_measurement": oracle_shadow_measurement["canonical_hash"],
            "oracle_shadow_measurement_receipt": oracle_shadow_measurement_receipt[
                "canonical_hash"
            ],
            "oracle_operator_decision_intake": oracle_operator_decision_intake[
                "canonical_hash"
            ],
        },
        "proposal_scope": {
            "scope_id": "ORACLE_MEASUREMENT_PROPOSAL_SCOPE_001",
            "scope_status": "PROPOSAL_ONLY_OPERATOR_REVIEW_REQUIRED",
            "summary": (
                "Package shadow measurement evidence into a future measurement "
                "proposal for operator review without authorizing measurement."
            ),
            "authorizes_measurement": False,
            "records_operator_attestation": False,
            "brier_score": 0.1,
        },
        "operator_decision_intake_refinement": {
            "template_id": "ORACLE_MEASUREMENT_PROPOSAL_OPERATOR_REVIEW_TEMPLATE",
            "exact_confirmation_required": "yes",
            "attestation_note_required": True,
            "records_operator_attestation": False,
            "authorizes_measurement": False,
            "review_questions": _review_questions(),
            "brier_score": 0.1,
        },
        "measurement_proposal_steps": _proposal_steps(),
        "readiness_exit_criteria": _readiness_exit_criteria(),
        "boundary_checklist": _boundary_checklist(),
        "version_metadata": {
            "schema_family": "oracle_signal_layer",
            "schema_name": "oracle_measurement_proposal",
            "schema_version": "v1",
            "registry_path": "contracts/canon/oracle/oracle_schema_registry.v1.schema.json",
            "brier_score": 0.1,
        },
        "provenance": _provenance("oracle_measurement_proposal"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_measurement_proposal_receipt(
    *,
    timestamp: str,
    merge_sha: str,
    oracle_measurement_proposal: Mapping[str, Any],
    holler_measurement_proposal: Mapping[str, Any],
    observability_hook: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleMeasurementProposalReceipt.v1",
        "receipt_id": "ORACLE_MEASUREMENT_PROPOSAL_RECEIPT_001",
        "receipt_status": "ORACLE_MEASUREMENT_PROPOSAL_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "merge_sha": merge_sha,
        "surface_hashes": {
            "oracle_measurement_proposal": oracle_measurement_proposal[
                "canonical_hash"
            ],
            "holler_measurement_proposal": holler_measurement_proposal[
                "canonical_hash"
            ],
            "observability_hook": observability_hook["canonical_hash"],
        },
        "operator_decision_record_template": {
            "template_id": "ORACLE_MEASUREMENT_PROPOSAL_OPERATOR_REVIEW_TEMPLATE",
            "exact_confirmation_required": "yes",
            "attestation_note_required": True,
            "records_operator_attestation": False,
            "authorizes_measurement": False,
            "brier_score": 0.1,
        },
        "recommended_next_advisory_action": (
            "Prepare full measurement authorization proposal or continue "
            "operator decision intake refinement after explicit operator review."
        ),
        "provenance": _provenance("oracle_measurement_proposal_receipt"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "valid_for_live_signal": False,
        "valid_for_live_measurement": False,
        "valid_for_measurement_authorization": False,
        "valid_for_measurement_execution": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_outcome_recording": False,
        "valid_for_external_oracle_calls": False,
        "valid_for_telemetry_writeback": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _review_questions() -> list[dict[str, Any]]:
    return [
        _question(
            "Q1_SHADOW_MEASUREMENT_EVIDENCE",
            "Does the operator accept the shadow measurement receipt as advisory evidence only?",
        ),
        _question(
            "Q2_HELD_OUT_FIXTURE_BOUNDARY",
            "Does the operator confirm held-out fixture references remain non-executing?",
        ),
        _question(
            "Q3_PROPOSAL_BOUNDARY",
            "Does the operator confirm this packet is not a measurement authorization?",
        ),
    ]


def _proposal_steps() -> list[dict[str, Any]]:
    return [
        _step("STEP_1_REVIEW_SHADOW_MEASUREMENT", "oracle_shadow_measurement_receipt"),
        _step("STEP_2_REVIEW_READINESS_CRITERIA", "oracle_measurement_readiness"),
        _step("STEP_3_REVIEW_HELD_OUT_FIXTURES", "held_out_fixture_refs"),
        _step("STEP_4_PREPARE_OPERATOR_GATE", "operator_decision_intake_refinement"),
    ]


def _readiness_exit_criteria() -> list[dict[str, Any]]:
    return [
        _criterion("EXIT_SCHEMA_VALIDATION_GREEN", "oracle_schema_validation_receipt"),
        _criterion("EXIT_SHADOW_MEASUREMENT_REVIEWED", "oracle_shadow_measurement"),
        _criterion("EXIT_OPERATOR_GATE_EXPLICIT", "operator_decision_intake_refinement"),
    ]


def _boundary_checklist() -> list[dict[str, Any]]:
    return [
        {"lock_id": lock_id, "locked": False, "brier_score": 0.1}
        for lock_id in (
            "LIVE_SIGNAL_INGEST",
            "LIVE_MEASUREMENT",
            "MEASUREMENT_EXECUTION",
            "OPERATOR_ATTESTATION_RECORDING",
            "OUTCOME_RECORDING",
            "EXTERNAL_ORACLE_CALLS",
            "TELEMETRY_WRITEBACK",
            "GITHUB_NOTION_WRITEBACK",
        )
    ]


def _question(question_id: str, question: str) -> dict[str, Any]:
    return {
        "question_id": question_id,
        "question": question,
        "records_decision": False,
        "valid_for_measurement_authorization": False,
        "brier_score": 0.1,
    }


def _step(step_id: str, evidence_ref: str) -> dict[str, Any]:
    return {
        "step_id": step_id,
        "step_status": "PROPOSED_FOR_OPERATOR_REVIEW_ONLY",
        "evidence_ref": evidence_ref,
        "operator_gate_required": True,
        "valid_for_execution": False,
        "brier_score": 0.1,
    }


def _criterion(criterion_id: str, source_ref: str) -> dict[str, Any]:
    return {
        "criterion_id": criterion_id,
        "criterion_status": "HELD_FOR_OPERATOR_REVIEW",
        "source_ref": source_ref,
        "required_before_future_measurement": True,
        "brier_score": 0.1,
    }


def _provenance(source: str) -> dict[str, Any]:
    return {
        "source": source,
        "sprint_spine": "Notion Sprint 001 + repo main",
        "canon_extension_only": True,
        "root_canon_mutated": False,
        "brier_score": 0.1,
    }


def _authority_locks() -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "live_signal_ingest": False,
        "live_measurement": False,
        "measurement_authorization": False,
        "measurement_execution": False,
        "outcome_recording": False,
        "external_oracle_calls": False,
        "operator_attestation_recording": False,
        "telemetry_writeback": False,
        "github_writeback": False,
        "notion_writeback": False,
    }
