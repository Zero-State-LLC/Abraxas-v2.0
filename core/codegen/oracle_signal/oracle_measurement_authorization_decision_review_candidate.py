"""Oracle measurement authorization decision review candidate builders.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no authorization decision or execution.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


def build_oracle_measurement_authorization_decision_review_candidate(
    *,
    timestamp: str,
    oracle_measurement_authorization_proposal: Mapping[str, Any],
    oracle_measurement_authorization_proposal_receipt: Mapping[str, Any],
    oracle_measurement_proposal: Mapping[str, Any],
    oracle_shadow_measurement: Mapping[str, Any],
    oracle_schema_validation_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleMeasurementAuthorizationDecisionReviewCandidate.v1",
        "decision_review_candidate_id": canonical_hash(
            {
                "record": "oracle_measurement_authorization_decision_review_candidate",
                "authorization_proposal_hash": (
                    oracle_measurement_authorization_proposal["canonical_hash"]
                ),
                "authorization_proposal_receipt_hash": (
                    oracle_measurement_authorization_proposal_receipt[
                        "canonical_hash"
                    ]
                ),
            }
        ),
        "candidate_status": (
            "ORACLE_MEASUREMENT_AUTHORIZATION_DECISION_REVIEW_CANDIDATE_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "source_packet_hashes": {
            "oracle_measurement_authorization_proposal": (
                oracle_measurement_authorization_proposal["canonical_hash"]
            ),
            "oracle_measurement_authorization_proposal_receipt": (
                oracle_measurement_authorization_proposal_receipt[
                    "canonical_hash"
                ]
            ),
            "oracle_measurement_proposal": oracle_measurement_proposal[
                "canonical_hash"
            ],
            "oracle_shadow_measurement": oracle_shadow_measurement["canonical_hash"],
            "oracle_schema_validation_receipt": oracle_schema_validation_receipt[
                "canonical_hash"
            ],
        },
        "decision_review_scope": {
            "scope_id": "ORACLE_MEASUREMENT_AUTHORIZATION_DECISION_REVIEW_SCOPE_001",
            "scope_status": "REVIEW_CANDIDATE_ONLY_NOT_DECIDED",
            "summary": (
                "Prepare a non-recording operator decision review candidate from "
                "the authorization proposal evidence. This packet does not "
                "select an option, record a decision, or authorize measurement."
            ),
            "operator_gate_required": True,
            "records_authorization_decision": False,
            "authorizes_measurement": False,
            "records_operator_attestation": False,
            "brier_score": 0.1,
        },
        "operator_review_template": {
            "template_id": "ORACLE_MEASUREMENT_AUTHORIZATION_DECISION_REVIEW_TEMPLATE",
            "exact_confirmation_required": "yes",
            "attestation_note_required": True,
            "records_operator_attestation": False,
            "records_authorization_decision": False,
            "authorizes_measurement": False,
            "review_statement": (
                "I have reviewed this advisory decision candidate. This packet "
                "does not record my decision or authorize measurement."
            ),
            "brier_score": 0.1,
        },
        "decision_options": _decision_options(),
        "required_review_evidence": _required_review_evidence(),
        "denial_locks": _denial_locks(),
        "version_metadata": {
            "schema_family": "oracle_signal_layer",
            "schema_name": (
                "oracle_measurement_authorization_decision_review_candidate"
            ),
            "schema_version": "v1",
            "registry_path": "contracts/canon/oracle/oracle_schema_registry.v1.schema.json",
            "brier_score": 0.1,
        },
        "provenance": _provenance(
            "oracle_measurement_authorization_decision_review_candidate"
        ),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_measurement_authorization_decision_review_candidate_receipt(
    *,
    timestamp: str,
    merge_sha: str,
    oracle_measurement_authorization_decision_review_candidate: Mapping[str, Any],
    observability_hook: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": (
            "OracleMeasurementAuthorizationDecisionReviewCandidateReceipt.v1"
        ),
        "receipt_id": (
            "ORACLE_MEASUREMENT_AUTHORIZATION_DECISION_REVIEW_CANDIDATE_RECEIPT_001"
        ),
        "receipt_status": (
            "ORACLE_MEASUREMENT_AUTHORIZATION_DECISION_REVIEW_CANDIDATE_READY_ADVISORY_ONLY"
        ),
        "timestamp": timestamp,
        "merge_sha": merge_sha,
        "surface_hashes": {
            "oracle_measurement_authorization_decision_review_candidate": (
                oracle_measurement_authorization_decision_review_candidate[
                    "canonical_hash"
                ]
            ),
            "observability_hook": observability_hook["canonical_hash"],
        },
        "operator_review_template": {
            "template_id": "ORACLE_MEASUREMENT_AUTHORIZATION_DECISION_REVIEW_TEMPLATE",
            "exact_confirmation_required": "yes",
            "attestation_note_required": True,
            "records_operator_attestation": False,
            "records_authorization_decision": False,
            "authorizes_measurement": False,
            "brier_score": 0.1,
        },
        "recommended_next_advisory_action": (
            "Operator may review this decision candidate. Any actual "
            "authorization decision, attestation recording, or measurement "
            "execution requires a separate explicit gate."
        ),
        "provenance": _provenance(
            "oracle_measurement_authorization_decision_review_candidate_receipt"
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
        "valid_for_authorization_decision_recording": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_outcome_recording": False,
        "valid_for_external_oracle_calls": False,
        "valid_for_telemetry_writeback": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _decision_options() -> list[dict[str, Any]]:
    return [
        _option(
            "OPTION_REJECT_MEASUREMENT_AUTHORIZATION",
            "Future operator could reject measurement authorization.",
        ),
        _option(
            "OPTION_HOLD_FOR_MORE_EVIDENCE",
            "Future operator could request additional readiness evidence.",
        ),
        _option(
            "OPTION_PREPARE_SEPARATE_AUTHORIZATION_RECORD",
            "Future operator could request a separate authorization record lane.",
        ),
    ]


def _required_review_evidence() -> list[dict[str, Any]]:
    return [
        _evidence("EVIDENCE_SCHEMA_VALIDATION", "oracle_schema_validation_receipt"),
        _evidence("EVIDENCE_AUTHORIZATION_PROPOSAL", "oracle_measurement_authorization_proposal"),
        _evidence("EVIDENCE_SHADOW_MEASUREMENT", "oracle_shadow_measurement"),
        _evidence("EVIDENCE_OPERATOR_TEMPLATE", "operator_review_template"),
    ]


def _denial_locks() -> list[dict[str, Any]]:
    return [
        {"lock_id": lock_id, "locked": False, "brier_score": 0.1}
        for lock_id in (
            "LIVE_SIGNAL_INGEST",
            "LIVE_MEASUREMENT",
            "MEASUREMENT_AUTHORIZATION",
            "AUTHORIZATION_DECISION_RECORDING",
            "MEASUREMENT_EXECUTION",
            "OPERATOR_ATTESTATION_RECORDING",
            "OUTCOME_RECORDING",
            "EXTERNAL_ORACLE_CALLS",
            "TELEMETRY_WRITEBACK",
            "GITHUB_NOTION_WRITEBACK",
            "CANON_RUNTIME_MUTATION",
        )
    ]


def _option(option_id: str, operator_meaning: str) -> dict[str, Any]:
    return {
        "option_id": option_id,
        "option_status": "AVAILABLE_FOR_FUTURE_OPERATOR_REVIEW_ONLY",
        "operator_meaning": operator_meaning,
        "selected_by_this_packet": False,
        "valid_for_measurement_authorization": False,
        "brier_score": 0.1,
    }


def _evidence(evidence_id: str, evidence_ref: str) -> dict[str, Any]:
    return {
        "evidence_id": evidence_id,
        "evidence_ref": evidence_ref,
        "review_status": "HELD_FOR_OPERATOR_REVIEW_ONLY",
        "required_before_any_future_authorization": True,
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
        "authorization_decision_recording": False,
        "measurement_execution": False,
        "outcome_recording": False,
        "external_oracle_calls": False,
        "operator_attestation_recording": False,
        "telemetry_writeback": False,
        "github_writeback": False,
        "notion_writeback": False,
    }
