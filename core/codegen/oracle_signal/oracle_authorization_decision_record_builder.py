"""Oracle authorization decision record template builders.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no authorization decision recording.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


def build_oracle_authorization_decision_record(
    *,
    timestamp: str,
    oracle_measurement_authorization_decision_review_candidate: Mapping[str, Any],
    oracle_measurement_authorization_decision_review_candidate_receipt: Mapping[
        str,
        Any,
    ],
    oracle_measurement_authorization_proposal: Mapping[str, Any],
    oracle_shadow_measurement: Mapping[str, Any],
    oracle_schema_validation_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleAuthorizationDecisionRecord.v1",
        "decision_record_id": canonical_hash(
            {
                "record": "oracle_authorization_decision_record",
                "decision_review_candidate_hash": (
                    oracle_measurement_authorization_decision_review_candidate[
                        "canonical_hash"
                    ]
                ),
                "decision_review_candidate_receipt_hash": (
                    oracle_measurement_authorization_decision_review_candidate_receipt[
                        "canonical_hash"
                    ]
                ),
            }
        ),
        "record_status": "ORACLE_AUTHORIZATION_DECISION_RECORD_TEMPLATE_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "source_packet_hashes": {
            "oracle_measurement_authorization_decision_review_candidate": (
                oracle_measurement_authorization_decision_review_candidate[
                    "canonical_hash"
                ]
            ),
            "oracle_measurement_authorization_decision_review_candidate_receipt": (
                oracle_measurement_authorization_decision_review_candidate_receipt[
                    "canonical_hash"
                ]
            ),
            "oracle_measurement_authorization_proposal": (
                oracle_measurement_authorization_proposal["canonical_hash"]
            ),
            "oracle_shadow_measurement": oracle_shadow_measurement["canonical_hash"],
            "oracle_schema_validation_receipt": oracle_schema_validation_receipt[
                "canonical_hash"
            ],
        },
        "decision_record_template": {
            "template_id": "ORACLE_AUTHORIZATION_DECISION_RECORD_TEMPLATE",
            "template_status": "TEMPLATE_ONLY_NOT_RECORDED",
            "exact_confirmation_required": "yes",
            "attestation_note_required": True,
            "records_operator_attestation": False,
            "records_authorization_decision": False,
            "authorizes_measurement": False,
            "records_measurement_execution": False,
            "selected_option": "UNSELECTED_OPERATOR_GATE_REQUIRED",
            "operator_attestation": "UNRECORDED_OPERATOR_GATE_REQUIRED",
            "brier_score": 0.1,
        },
        "operator_gate": {
            "gate_id": "ORACLE_AUTHORIZATION_DECISION_RECORD_OPERATOR_GATE",
            "gate_status": "HELD_FOR_SEPARATE_OPERATOR_ACTION",
            "operator_required": True,
            "records_decision": False,
            "records_attestation": False,
            "authorizes_measurement": False,
            "brier_score": 0.1,
        },
        "decision_options": _decision_options(),
        "required_evidence": _required_evidence(),
        "denial_locks": _denial_locks(),
        "version_metadata": {
            "schema_family": "oracle_signal_layer",
            "schema_name": "oracle_authorization_decision_record",
            "schema_version": "v1",
            "registry_path": "contracts/canon/oracle/oracle_schema_registry.v1.schema.json",
            "brier_score": 0.1,
        },
        "provenance": _provenance("oracle_authorization_decision_record_builder"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_authorization_decision_record_receipt(
    *,
    timestamp: str,
    merge_sha: str,
    oracle_authorization_decision_record: Mapping[str, Any],
    observability_hook: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleAuthorizationDecisionRecordReceipt.v1",
        "receipt_id": "ORACLE_AUTHORIZATION_DECISION_RECORD_RECEIPT_001",
        "receipt_status": "ORACLE_AUTHORIZATION_DECISION_RECORD_TEMPLATE_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "merge_sha": merge_sha,
        "surface_hashes": {
            "oracle_authorization_decision_record": (
                oracle_authorization_decision_record["canonical_hash"]
            ),
            "observability_hook": observability_hook["canonical_hash"],
        },
        "operator_review_template": {
            "template_id": "ORACLE_AUTHORIZATION_DECISION_RECORD_OPERATOR_GATE",
            "exact_confirmation_required": "yes",
            "attestation_note_required": True,
            "records_operator_attestation": False,
            "records_authorization_decision": False,
            "authorizes_measurement": False,
            "brier_score": 0.1,
        },
        "recommended_next_advisory_action": (
            "Oracle Signal Layer is advisory-complete after consolidated "
            "receipt review. Any real authorization record, attestation, or "
            "measurement authorization requires a separate explicit operator gate."
        ),
        "provenance": _provenance("oracle_authorization_decision_record_receipt"),
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
            "Future operator could hold for more evidence.",
        ),
        _option(
            "OPTION_PREPARE_MEASUREMENT_AUTHORIZATION_GATE",
            "Future operator could request a separate authorization gate.",
        ),
    ]


def _required_evidence() -> list[dict[str, Any]]:
    return [
        _evidence("EVIDENCE_SCHEMA_VALIDATION", "oracle_schema_validation_receipt"),
        _evidence("EVIDENCE_SHADOW_MEASUREMENT", "oracle_shadow_measurement"),
        _evidence("EVIDENCE_AUTHORIZATION_PROPOSAL", "oracle_measurement_authorization_proposal"),
        _evidence(
            "EVIDENCE_DECISION_REVIEW_CANDIDATE",
            "oracle_measurement_authorization_decision_review_candidate",
        ),
        _evidence("EVIDENCE_OPERATOR_GATE_TEMPLATE", "decision_record_template"),
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
        "option_status": "AVAILABLE_FOR_FUTURE_OPERATOR_RECORD_ONLY",
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
