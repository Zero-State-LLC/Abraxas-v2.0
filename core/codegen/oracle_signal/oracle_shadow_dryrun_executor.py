"""Oracle shadow dry-run advisory replay builders.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory extension, no canon mutation, no runtime execution, no live signals.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from core.canonical.json import canonical_hash


def _authority_locks() -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "live_signal_ingest": False,
        "live_oracle_execution": False,
        "shadow_replay_execution": False,
        "scheduler_mutation": False,
        "queue_mutation": False,
        "pipeline_or_route_mutation": False,
        "telemetry_writeback": False,
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


def build_oracle_shadow_dryrun(
    *,
    timestamp: str,
    oracle_ingest_wiring: Mapping[str, Any],
    oracle_schema_validation_receipt: Mapping[str, Any],
    oracle_adversarial_fixture: Mapping[str, Any],
    replay_fixtures: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    fixtures = [
        _replay_fixture(fixture)
        for fixture in (
            replay_fixtures
            if replay_fixtures is not None
            else _default_replay_fixtures(oracle_adversarial_fixture)
        )
    ]
    expected_outcomes = [
        _expected_outcome(
            fixture_id=str(fixture["fixture_id"]),
            guardrail=(
                "hold fixture for operator review; do not route, ingest, execute, "
                "or resolve live outcomes"
            ),
        )
        for fixture in fixtures
    ]
    route_log = [
        _route_decision(
            fixture_id=str(fixture["fixture_id"]),
            route_id=f"ROUTE_{index:03d}_{fixture['fixture_id']}",
        )
        for index, fixture in enumerate(fixtures, start=1)
    ]
    base: dict[str, Any] = {
        "schema_version": "OracleShadowDryRun.v1",
        "dryrun_id": canonical_hash(
            {
                "record": "oracle_shadow_dryrun",
                "oracle_ingest_wiring_hash": oracle_ingest_wiring["canonical_hash"],
                "schema_validation_receipt_hash": oracle_schema_validation_receipt[
                    "canonical_hash"
                ],
                "adversarial_fixture_hash": oracle_adversarial_fixture[
                    "canonical_hash"
                ],
                "fixture_ids": [fixture["fixture_id"] for fixture in fixtures],
            }
        ),
        "dryrun_status": "ORACLE_SHADOW_DRYRUN_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "source_packet_hashes": {
            "oracle_ingest_wiring": oracle_ingest_wiring["canonical_hash"],
            "oracle_schema_validation_receipt": oracle_schema_validation_receipt[
                "canonical_hash"
            ],
            "oracle_adversarial_fixture": oracle_adversarial_fixture[
                "canonical_hash"
            ],
        },
        "replay_fixtures": fixtures,
        "expected_outcomes": expected_outcomes,
        "validation_binding": {
            "schema_validation_receipt_hash": oracle_schema_validation_receipt[
                "canonical_hash"
            ],
            "ingest_wiring_hash": oracle_ingest_wiring["canonical_hash"],
            "validation_required_before_live_execution": True,
            "live_execution_authorized": False,
            "brier_score": 0.1,
        },
        "route_decision_log": route_log,
        "provenance_flow": [
            _provenance_flow("FLOW_WIRING_TO_FIXTURE", "oracle_ingest_wiring", "replay_fixtures"),
            _provenance_flow("FLOW_FIXTURE_TO_OUTCOME", "replay_fixtures", "expected_outcomes"),
            _provenance_flow("FLOW_OUTCOME_TO_OPERATOR", "expected_outcomes", "operator_decision_record_template"),
        ],
        "operator_decision_record_template": {
            "template_id": "ORACLE_SHADOW_DRYRUN_OPERATOR_DECISION_TEMPLATE",
            "exact_confirmation_required": "yes",
            "attestation_note_required": True,
            "records_live_execution": False,
            "brier_score": 0.1,
        },
        "version_metadata": {
            "schema_family": "oracle_signal_layer",
            "schema_name": "oracle_shadow_dryrun",
            "schema_version": "v1",
            "registry_path": "contracts/canon/oracle/oracle_schema_registry.v1.schema.json",
            "brier_score": 0.1,
        },
        "provenance": _provenance("oracle_shadow_dryrun_executor"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_shadow_dryrun_receipt(
    *,
    timestamp: str,
    merge_sha: str,
    oracle_shadow_dryrun: Mapping[str, Any],
    holler_shadow_dryrun: Mapping[str, Any],
    observability_hook: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleShadowDryRunReceipt.v1",
        "receipt_id": "ORACLE_SHADOW_DRYRUN_RECEIPT_001",
        "receipt_status": "ORACLE_SHADOW_DRYRUN_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "merge_sha": merge_sha,
        "surface_hashes": {
            "oracle_shadow_dryrun": oracle_shadow_dryrun["canonical_hash"],
            "holler_shadow_dryrun": holler_shadow_dryrun["canonical_hash"],
            "observability_hook": observability_hook["canonical_hash"],
        },
        "operator_decision_record_template": {
            "template_id": "ORACLE_SHADOW_DRYRUN_OPERATOR_DECISION_TEMPLATE",
            "exact_confirmation_required": "yes",
            "attestation_note_required": True,
            "records_live_execution": False,
            "brier_score": 0.1,
        },
        "recommended_next_advisory_action": (
            "Review Oracle measurement readiness receipt, then prepare shadow "
            "measurement execution slice."
        ),
        "provenance": _provenance("oracle_shadow_dryrun_receipt"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "valid_for_live_signal": False,
        "valid_for_live_ingest": False,
        "valid_for_runtime_execution": False,
        "valid_for_shadow_replay_execution": False,
        "valid_for_oracle_execution": False,
        "valid_for_telemetry_writeback": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _default_replay_fixtures(
    oracle_adversarial_fixture: Mapping[str, Any],
) -> list[dict[str, Any]]:
    rows = oracle_adversarial_fixture["fixture_rows"]
    return [
        {
            "fixture_id": str(row["case_id"]),
            "fixture_kind": "ADVERSARIAL_ORACLE_SIGNAL_FIXTURE",
            "source_ref": "oracle_adversarial_fixture",
            "expected_route": "HOLD_FOR_OPERATOR_REVIEW",
            "valid_for_live_signal": False,
            "valid_for_execution": False,
            "brier_score": 0.1,
        }
        for row in rows
    ]


def _replay_fixture(fixture: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "fixture_id": str(fixture["fixture_id"]),
        "fixture_kind": str(fixture["fixture_kind"]),
        "source_ref": str(fixture["source_ref"]),
        "expected_route": str(fixture["expected_route"]),
        "valid_for_live_signal": False,
        "valid_for_execution": False,
        "brier_score": float(fixture.get("brier_score", 0.1)),
    }


def _expected_outcome(fixture_id: str, guardrail: str) -> dict[str, Any]:
    return {
        "fixture_id": fixture_id,
        "expected_status": "SHADOW_REPLAY_HELD_FOR_OPERATOR",
        "expected_guardrail": guardrail,
        "records_live_result": False,
        "brier_score": 0.1,
    }


def _route_decision(fixture_id: str, route_id: str) -> dict[str, Any]:
    return {
        "route_id": route_id,
        "fixture_id": fixture_id,
        "route_status": "PROJECTED_ONLY_NOT_ROUTED",
        "decision": "HOLD_FOR_OPERATOR_REVIEW",
        "valid_for_route_mutation": False,
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
