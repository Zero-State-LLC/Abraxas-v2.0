"""Oracle measurement authorization proposal advisory packet builders.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no measurement authorization or execution.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


def build_oracle_measurement_authorization_proposal(
    *,
    timestamp: str,
    oracle_measurement_proposal: Mapping[str, Any],
    oracle_measurement_proposal_receipt: Mapping[str, Any],
    oracle_shadow_measurement: Mapping[str, Any],
    oracle_measurement_readiness: Mapping[str, Any],
    oracle_schema_validation_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleMeasurementAuthorizationProposal.v1",
        "authorization_proposal_id": canonical_hash(
            {
                "record": "oracle_measurement_authorization_proposal",
                "oracle_measurement_proposal_hash": oracle_measurement_proposal[
                    "canonical_hash"
                ],
                "oracle_measurement_proposal_receipt_hash": (
                    oracle_measurement_proposal_receipt["canonical_hash"]
                ),
            }
        ),
        "proposal_status": (
            "ORACLE_MEASUREMENT_AUTHORIZATION_PROPOSAL_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "source_packet_hashes": {
            "oracle_measurement_proposal": oracle_measurement_proposal[
                "canonical_hash"
            ],
            "oracle_measurement_proposal_receipt": (
                oracle_measurement_proposal_receipt["canonical_hash"]
            ),
            "oracle_shadow_measurement": oracle_shadow_measurement["canonical_hash"],
            "oracle_measurement_readiness": oracle_measurement_readiness[
                "canonical_hash"
            ],
            "oracle_schema_validation_receipt": oracle_schema_validation_receipt[
                "canonical_hash"
            ],
        },
        "authorization_scope": {
            "scope_id": "ORACLE_MEASUREMENT_AUTHORIZATION_PROPOSAL_SCOPE_001",
            "scope_status": "PROPOSAL_ONLY_NOT_AUTHORIZED",
            "summary": (
                "Prepare the operator-facing authorization proposal from "
                "measurement readiness and shadow measurement evidence without "
                "granting authorization."
            ),
            "operator_gate_required": True,
            "grants_measurement_authorization": False,
            "records_operator_attestation": False,
            "brier_score": 0.1,
        },
        "operator_gate_template": {
            "template_id": (
                "ORACLE_MEASUREMENT_AUTHORIZATION_PROPOSAL_OPERATOR_GATE_TEMPLATE"
            ),
            "exact_confirmation_required": "yes",
            "attestation_note_required": True,
            "records_operator_attestation": False,
            "authorizes_measurement": False,
            "review_statement": (
                "I have reviewed this advisory proposal. This packet alone does "
                "not authorize live measurement or record attestation."
            ),
            "brier_score": 0.1,
        },
        "authorization_review_steps": _review_steps(),
        "promotion_preconditions": _promotion_preconditions(),
        "denial_locks": _denial_locks(),
        "version_metadata": {
            "schema_family": "oracle_signal_layer",
            "schema_name": "oracle_measurement_authorization_proposal",
            "schema_version": "v1",
            "registry_path": "contracts/canon/oracle/oracle_schema_registry.v1.schema.json",
            "brier_score": 0.1,
        },
        "provenance": _provenance("oracle_measurement_authorization_proposal"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_measurement_authorization_proposal_receipt(
    *,
    timestamp: str,
    merge_sha: str,
    oracle_measurement_authorization_proposal: Mapping[str, Any],
    holler_measurement_authorization_proposal: Mapping[str, Any],
    observability_hook: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleMeasurementAuthorizationProposalReceipt.v1",
        "receipt_id": "ORACLE_MEASUREMENT_AUTHORIZATION_PROPOSAL_RECEIPT_001",
        "receipt_status": (
            "ORACLE_MEASUREMENT_AUTHORIZATION_PROPOSAL_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "merge_sha": merge_sha,
        "surface_hashes": {
            "oracle_measurement_authorization_proposal": (
                oracle_measurement_authorization_proposal["canonical_hash"]
            ),
            "holler_measurement_authorization_proposal": (
                holler_measurement_authorization_proposal["canonical_hash"]
            ),
            "observability_hook": observability_hook["canonical_hash"],
        },
        "operator_decision_record_template": {
            "template_id": (
                "ORACLE_MEASUREMENT_AUTHORIZATION_PROPOSAL_OPERATOR_GATE_TEMPLATE"
            ),
            "exact_confirmation_required": "yes",
            "attestation_note_required": True,
            "records_operator_attestation": False,
            "authorizes_measurement": False,
            "brier_score": 0.1,
        },
        "recommended_next_advisory_action": (
            "Operator may review the authorization proposal. Any actual "
            "authorization or measurement execution requires a separate explicit gate."
        ),
        "provenance": _provenance(
            "oracle_measurement_authorization_proposal_receipt"
        ),
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


def _review_steps() -> list[dict[str, Any]]:
    return [
        _step("STEP_1_REVIEW_SCHEMA_VALIDATION", "oracle_schema_validation_receipt"),
        _step("STEP_2_REVIEW_READINESS", "oracle_measurement_readiness"),
        _step("STEP_3_REVIEW_SHADOW_MEASUREMENT", "oracle_shadow_measurement"),
        _step("STEP_4_REVIEW_OPERATOR_GATE", "operator_gate_template"),
    ]


def _promotion_preconditions() -> list[dict[str, Any]]:
    return [
        _precondition("PRECONDITION_OPERATOR_GATE_SEPARATE", "operator_gate_template"),
        _precondition("PRECONDITION_NO_LIVE_MEASUREMENT", "authority_locks"),
        _precondition("PRECONDITION_NOTION_RECONCILIATION", "Notion Sprint 001 Hub"),
    ]


def _denial_locks() -> list[dict[str, Any]]:
    return [
        {"lock_id": lock_id, "locked": False, "brier_score": 0.1}
        for lock_id in (
            "LIVE_SIGNAL_INGEST",
            "LIVE_MEASUREMENT",
            "MEASUREMENT_AUTHORIZATION",
            "MEASUREMENT_EXECUTION",
            "OPERATOR_ATTESTATION_RECORDING",
            "OUTCOME_RECORDING",
            "EXTERNAL_ORACLE_CALLS",
            "TELEMETRY_WRITEBACK",
            "GITHUB_NOTION_WRITEBACK",
            "CANON_RUNTIME_MUTATION",
        )
    ]


def _step(step_id: str, evidence_ref: str) -> dict[str, Any]:
    return {
        "step_id": step_id,
        "step_status": "HELD_FOR_OPERATOR_REVIEW_ONLY",
        "evidence_ref": evidence_ref,
        "required_before_any_future_authorization": True,
        "valid_for_execution": False,
        "brier_score": 0.1,
    }


def _precondition(precondition_id: str, source_ref: str) -> dict[str, Any]:
    return {
        "precondition_id": precondition_id,
        "precondition_status": "NOT_SATISFIED_PROPOSAL_ONLY",
        "source_ref": source_ref,
        "satisfied_by_this_packet": False,
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
