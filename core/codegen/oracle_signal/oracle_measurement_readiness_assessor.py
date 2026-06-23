"""Oracle measurement readiness advisory assessors.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no live measurement, no execution.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


def build_oracle_measurement_readiness(
    *,
    timestamp: str,
    oracle_shadow_dryrun: Mapping[str, Any],
    oracle_schema_validation_receipt: Mapping[str, Any],
    oracle_ingest_wiring: Mapping[str, Any],
    operator_decision_intake: Mapping[str, Any],
) -> dict[str, Any]:
    fixture_refs = [
        {
            "fixture_id": str(fixture["fixture_id"]),
            "fixture_source": "oracle_shadow_dryrun.replay_fixtures",
            "binding_status": "HELD_OUT_REFERENCE_ONLY_NOT_BOUND",
            "records_outcome": False,
            "valid_for_execution": False,
            "brier_score": 0.1,
        }
        for fixture in oracle_shadow_dryrun["replay_fixtures"]
    ]
    base: dict[str, Any] = {
        "schema_version": "OracleMeasurementReadiness.v1",
        "readiness_id": canonical_hash(
            {
                "record": "oracle_measurement_readiness",
                "oracle_shadow_dryrun_hash": oracle_shadow_dryrun["canonical_hash"],
                "schema_validation_receipt_hash": oracle_schema_validation_receipt[
                    "canonical_hash"
                ],
                "operator_decision_intake_hash": operator_decision_intake[
                    "canonical_hash"
                ],
            }
        ),
        "readiness_status": "ORACLE_MEASUREMENT_READINESS_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "source_packet_hashes": {
            "oracle_shadow_dryrun": oracle_shadow_dryrun["canonical_hash"],
            "oracle_schema_validation_receipt": oracle_schema_validation_receipt[
                "canonical_hash"
            ],
            "oracle_ingest_wiring": oracle_ingest_wiring["canonical_hash"],
        },
        "readiness_criteria": _readiness_criteria(),
        "held_out_fixture_refs": fixture_refs,
        "provenance_checks": _provenance_checks(),
        "decision_intake_requirements": {
            "template_id": "ORACLE_MEASUREMENT_READINESS_OPERATOR_INTAKE_TEMPLATE",
            "exact_confirmation_required": "yes",
            "attestation_note_required": True,
            "records_operator_attestation": False,
            "authorizes_measurement": False,
            "brier_score": 0.1,
        },
        "operator_decision_intake_hash": operator_decision_intake["canonical_hash"],
        "version_metadata": {
            "schema_family": "oracle_signal_layer",
            "schema_name": "oracle_measurement_readiness",
            "schema_version": "v1",
            "registry_path": "contracts/canon/oracle/oracle_schema_registry.v1.schema.json",
            "brier_score": 0.1,
        },
        "provenance": _provenance("oracle_measurement_readiness_assessor"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_measurement_readiness_receipt(
    *,
    timestamp: str,
    merge_sha: str,
    oracle_measurement_readiness: Mapping[str, Any],
    holler_measurement_readiness: Mapping[str, Any],
    operator_decision_intake: Mapping[str, Any],
    observability_hook: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleMeasurementReadinessReceipt.v1",
        "receipt_id": "ORACLE_MEASUREMENT_READINESS_RECEIPT_001",
        "receipt_status": "ORACLE_MEASUREMENT_READINESS_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "merge_sha": merge_sha,
        "surface_hashes": {
            "oracle_measurement_readiness": oracle_measurement_readiness[
                "canonical_hash"
            ],
            "holler_measurement_readiness": holler_measurement_readiness[
                "canonical_hash"
            ],
            "operator_decision_intake": operator_decision_intake["canonical_hash"],
            "observability_hook": observability_hook["canonical_hash"],
        },
        "operator_decision_record_template": {
            "template_id": "ORACLE_MEASUREMENT_READINESS_OPERATOR_INTAKE_TEMPLATE",
            "exact_confirmation_required": "yes",
            "attestation_note_required": True,
            "records_operator_attestation": False,
            "authorizes_measurement": False,
            "brier_score": 0.1,
        },
        "recommended_next_advisory_action": (
            "Prepare shadow measurement execution slice for operator review."
        ),
        "provenance": _provenance("oracle_measurement_readiness_receipt"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "valid_for_live_measurement": False,
        "valid_for_measurement_execution": False,
        "valid_for_operator_attestation_recording": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _readiness_criteria() -> list[dict[str, Any]]:
    return [
        _criterion("SCHEMA_VALIDATION_READY", "oracle_schema_validation_receipt"),
        _criterion("INGEST_WIRING_READY", "oracle_ingest_wiring"),
        _criterion("SHADOW_DRYRUN_READY", "oracle_shadow_dryrun"),
        _criterion("OPERATOR_INTAKE_READY", "oracle_operator_decision_intake"),
    ]


def _criterion(criterion_id: str, evidence_ref: str) -> dict[str, Any]:
    return {
        "criterion_id": criterion_id,
        "criterion_status": "READY_FOR_OPERATOR_REVIEW_ONLY",
        "evidence_ref": evidence_ref,
        "required_before_measurement": True,
        "valid_for_live_measurement": False,
        "brier_score": 0.1,
    }


def _provenance_checks() -> list[dict[str, Any]]:
    return [
        _provenance_check("CHECK_SCHEMA_RECEIPT", "oracle_schema_validation_receipt"),
        _provenance_check("CHECK_DRYRUN_RECEIPT", "oracle_shadow_dryrun"),
        _provenance_check("CHECK_OPERATOR_INTAKE", "oracle_operator_decision_intake"),
    ]


def _provenance_check(check_id: str, source_ref: str) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "check_status": "PASS_ADVISORY_REVIEW_ONLY",
        "source_ref": source_ref,
        "sealed_for_writeback": False,
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
        "live_measurement": False,
        "measurement_execution": False,
        "operator_attestation_recording": False,
        "live_signal_ingest": False,
        "github_writeback": False,
        "notion_writeback": False,
    }
