"""Oracle shadow measurement advisory packet builders.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no measurement execution, no outcomes.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


def build_oracle_shadow_measurement(
    *,
    timestamp: str,
    oracle_measurement_readiness: Mapping[str, Any],
    oracle_shadow_dryrun: Mapping[str, Any],
    oracle_schema_validation_receipt: Mapping[str, Any],
    oracle_ingest_wiring: Mapping[str, Any],
) -> dict[str, Any]:
    run_refs = [
        _measurement_run_ref(fixture_id=str(fixture["fixture_id"]), index=index)
        for index, fixture in enumerate(
            oracle_measurement_readiness["held_out_fixture_refs"], start=1
        )
    ]
    fixture_bindings = [
        _fixture_binding(fixture_id=str(fixture["fixture_id"]))
        for fixture in oracle_measurement_readiness["held_out_fixture_refs"]
    ]
    comparisons = [
        _projected_outcome_comparison(fixture_id=str(fixture["fixture_id"]))
        for fixture in oracle_shadow_dryrun["replay_fixtures"]
    ]
    base: dict[str, Any] = {
        "schema_version": "OracleShadowMeasurement.v1",
        "measurement_id": canonical_hash(
            {
                "record": "oracle_shadow_measurement",
                "oracle_measurement_readiness_hash": oracle_measurement_readiness[
                    "canonical_hash"
                ],
                "oracle_shadow_dryrun_hash": oracle_shadow_dryrun["canonical_hash"],
                "fixture_ids": [
                    binding["fixture_id"] for binding in fixture_bindings
                ],
            }
        ),
        "measurement_status": "ORACLE_SHADOW_MEASUREMENT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "source_packet_hashes": {
            "oracle_measurement_readiness": oracle_measurement_readiness[
                "canonical_hash"
            ],
            "oracle_shadow_dryrun": oracle_shadow_dryrun["canonical_hash"],
            "oracle_schema_validation_receipt": oracle_schema_validation_receipt[
                "canonical_hash"
            ],
            "oracle_ingest_wiring": oracle_ingest_wiring["canonical_hash"],
        },
        "measurement_run_refs": run_refs,
        "held_out_fixture_bindings": fixture_bindings,
        "projected_outcome_comparisons": comparisons,
        "provenance_flow": [
            _provenance_flow(
                "FLOW_READINESS_TO_SHADOW_MEASUREMENT",
                "oracle_measurement_readiness",
                "measurement_run_refs",
            ),
            _provenance_flow(
                "FLOW_DRYRUN_FIXTURES_TO_COMPARISON",
                "oracle_shadow_dryrun",
                "projected_outcome_comparisons",
            ),
            _provenance_flow(
                "FLOW_MEASUREMENT_TO_OPERATOR_REVIEW",
                "projected_outcome_comparisons",
                "operator_review_template",
            ),
        ],
        "operator_review_template": {
            "template_id": "ORACLE_SHADOW_MEASUREMENT_OPERATOR_REVIEW_TEMPLATE",
            "exact_confirmation_required": "yes",
            "attestation_note_required": True,
            "records_operator_attestation": False,
            "authorizes_measurement": False,
            "brier_score": 0.1,
        },
        "version_metadata": {
            "schema_family": "oracle_signal_layer",
            "schema_name": "oracle_shadow_measurement",
            "schema_version": "v1",
            "registry_path": "contracts/canon/oracle/oracle_schema_registry.v1.schema.json",
            "brier_score": 0.1,
        },
        "provenance": _provenance("oracle_shadow_measurement_executor"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_shadow_measurement_receipt(
    *,
    timestamp: str,
    merge_sha: str,
    oracle_shadow_measurement: Mapping[str, Any],
    holler_shadow_measurement: Mapping[str, Any],
    observability_hook: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleShadowMeasurementReceipt.v1",
        "receipt_id": "ORACLE_SHADOW_MEASUREMENT_RECEIPT_001",
        "receipt_status": "ORACLE_SHADOW_MEASUREMENT_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "merge_sha": merge_sha,
        "surface_hashes": {
            "oracle_shadow_measurement": oracle_shadow_measurement["canonical_hash"],
            "holler_shadow_measurement": holler_shadow_measurement["canonical_hash"],
            "observability_hook": observability_hook["canonical_hash"],
        },
        "operator_decision_record_template": {
            "template_id": "ORACLE_SHADOW_MEASUREMENT_OPERATOR_REVIEW_TEMPLATE",
            "exact_confirmation_required": "yes",
            "attestation_note_required": True,
            "records_operator_attestation": False,
            "authorizes_measurement": False,
            "brier_score": 0.1,
        },
        "recommended_next_advisory_action": (
            "Prepare operator decision intake refinement or full measurement "
            "proposal slice for operator review."
        ),
        "provenance": _provenance("oracle_shadow_measurement_receipt"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "valid_for_live_signal": False,
        "valid_for_live_measurement": False,
        "valid_for_measurement_execution": False,
        "valid_for_outcome_recording": False,
        "valid_for_external_oracle_calls": False,
        "valid_for_telemetry_writeback": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _measurement_run_ref(fixture_id: str, index: int) -> dict[str, Any]:
    return {
        "run_id": f"SHADOW_MEASUREMENT_{index:03d}_{fixture_id}",
        "fixture_id": fixture_id,
        "run_status": "PROJECTED_SHADOW_MEASUREMENT_ONLY",
        "records_live_measurement": False,
        "valid_for_execution": False,
        "brier_score": 0.1,
    }


def _fixture_binding(fixture_id: str) -> dict[str, Any]:
    return {
        "fixture_id": fixture_id,
        "binding_source": "oracle_measurement_readiness.held_out_fixture_refs",
        "binding_status": "HELD_OUT_BOUND_FOR_SHADOW_COMPARISON_ONLY",
        "records_outcome": False,
        "valid_for_live_measurement": False,
        "brier_score": 0.1,
    }


def _projected_outcome_comparison(fixture_id: str) -> dict[str, Any]:
    return {
        "fixture_id": fixture_id,
        "projected_outcome": "HOLD_FOR_OPERATOR_REVIEW_MATCHES_EXPECTED_GUARDRAIL",
        "comparison_status": "MOCK_COMPARISON_ONLY_NOT_RECORDED",
        "records_real_outcome": False,
        "brier_score": 0.1,
    }


def _provenance_flow(flow_id: str, source: str, target: str) -> dict[str, Any]:
    return {
        "flow_id": flow_id,
        "source": source,
        "target": target,
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
        "live_signal_ingest": False,
        "live_measurement": False,
        "measurement_execution": False,
        "outcome_recording": False,
        "external_oracle_calls": False,
        "operator_attestation_recording": False,
        "telemetry_writeback": False,
        "github_writeback": False,
        "notion_writeback": False,
    }
