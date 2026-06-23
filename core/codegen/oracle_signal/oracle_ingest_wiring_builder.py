"""Oracle ingest wiring advisory builders.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no runtime execution, no live ingest.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash


def _authority_locks() -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "live_signal_ingest": False,
        "scheduler_mutation": False,
        "queue_mutation": False,
        "pipeline_or_route_mutation": False,
        "github_writeback": False,
        "notion_writeback": False,
        "mcp_tool_exposure_live": False,
    }


def _provenance(source: str) -> dict[str, Any]:
    return {
        "source": source,
        "sprint_spine": "Notion Sprint 001 + repo main",
        "canon_extension_only": True,
        "root_canon_mutated": False,
        "brier_score": 0.1,
    }


def build_oracle_ingest_wiring(
    *,
    timestamp: str,
    signal_envelope: Mapping[str, Any],
    holler_intake: Mapping[str, Any],
    schema_validation_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    validation_hash = str(schema_validation_receipt["canonical_hash"])
    base: dict[str, Any] = {
        "schema_version": "OracleIngestWiring.v1",
        "wiring_id": canonical_hash(
            {
                "record": "oracle_ingest_wiring",
                "signal_envelope_hash": signal_envelope["canonical_hash"],
                "holler_intake_hash": holler_intake["canonical_hash"],
                "schema_validation_receipt_hash": validation_hash,
            }
        ),
        "wiring_status": "ORACLE_INGEST_WIRING_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "source_packet_hashes": {
            "signal_envelope": signal_envelope["canonical_hash"],
            "holler_intake": holler_intake["canonical_hash"],
            "schema_validation_receipt": validation_hash,
        },
        "intake_pipeline": [
            _pipeline_stage("P0_SOURCE_REFERENCE", "signal_envelope", "source_ref"),
            _pipeline_stage("P1_SCHEMA_VALIDATION", "source_ref", "validation_binding"),
            _pipeline_stage("P2_SHADOW_REPLAY_PLAN", "validation_binding", "shadow_replay_harness"),
            _pipeline_stage(
                "P3_OPERATOR_GATE",
                "shadow_replay_harness",
                "operator_decision_record_template",
            ),
        ],
        "routing_plan": {
            "mode": "SHADOW_ROUTE_PLAN_ONLY",
            "valid_for_live_route": False,
            "valid_for_queue_mutation": False,
            "brier_score": 0.1,
        },
        "validation_binding": {
            "schema_validation_receipt_hash": validation_hash,
            "validation_required_before_live_ingest": True,
            "live_validation_authorized": False,
            "brier_score": 0.1,
        },
        "provenance_flow": [
            _provenance_flow(
                "FLOW_SIGNAL_TO_VALIDATION",
                "oracle_signal_envelope",
                "oracle_schema_validation",
            ),
            _provenance_flow(
                "FLOW_VALIDATION_TO_REPLAY",
                "oracle_schema_validation",
                "shadow_replay_harness",
            ),
            _provenance_flow(
                "FLOW_REPLAY_TO_OPERATOR",
                "shadow_replay_harness",
                "operator_decision_record_template",
            ),
        ],
        "shadow_replay_harness": {
            "mode": "SHADOW_REPLAY_PLAN_ONLY_NOT_EXECUTED",
            "valid_for_execution": False,
            "valid_for_live_ingest": False,
            "brier_score": 0.1,
        },
        "operator_decision_record_template": {
            "template_id": "ORACLE_INGEST_WIRING_OPERATOR_DECISION_TEMPLATE",
            "exact_confirmation_required": "yes",
            "attestation_note_required": True,
            "records_live_ingest": False,
            "brier_score": 0.1,
        },
        "version_metadata": {
            "schema_family": "oracle_signal_layer",
            "schema_name": "oracle_ingest_wiring",
            "schema_version": "v1",
            "registry_path": "contracts/canon/oracle/oracle_schema_registry.v1.schema.json",
            "brier_score": 0.1,
        },
        "provenance": _provenance("oracle_ingest_wiring_builder"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_ingest_wiring_receipt(
    *,
    timestamp: str,
    merge_sha: str,
    oracle_ingest_wiring: Mapping[str, Any],
    holler_ingest_wiring: Mapping[str, Any],
    observability_hook: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleIngestWiringReceipt.v1",
        "receipt_id": "ORACLE_INGEST_WIRING_RECEIPT_001",
        "receipt_status": "ORACLE_INGEST_WIRING_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "merge_sha": merge_sha,
        "surface_hashes": {
            "oracle_ingest_wiring": oracle_ingest_wiring["canonical_hash"],
            "holler_ingest_wiring": holler_ingest_wiring["canonical_hash"],
            "observability_hook": observability_hook["canonical_hash"],
        },
        "operator_decision_record_template": {
            "template_id": "ORACLE_INGEST_WIRING_OPERATOR_DECISION_TEMPLATE",
            "exact_confirmation_required": "yes",
            "attestation_note_required": True,
            "records_live_ingest": False,
            "brier_score": 0.1,
        },
        "recommended_next_advisory_action": (
            "Prepare shadow dry-run execution slice for operator review."
        ),
        "provenance": _provenance("oracle_ingest_wiring_receipt"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "valid_for_live_ingest": False,
        "valid_for_runtime_execution": False,
        "valid_for_queue_mutation": False,
        "valid_for_scheduler_mutation": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _pipeline_stage(stage_id: str, input_ref: str, output_ref: str) -> dict[str, Any]:
    return {
        "stage_id": stage_id,
        "stage_status": "ADVISORY_ONLY_NOT_EXECUTED",
        "input_ref": input_ref,
        "output_ref": output_ref,
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
