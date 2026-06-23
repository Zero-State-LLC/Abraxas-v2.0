"""Oracle Signal Layer completion receipt builders.

Provenance: Notion Sprint 001 + Hash: NOT_COMPUTABLE | Brier: 0.10
Advisory canon extension only. New canon contracts are additive under
contracts/canon/oracle/ and do not mutate root canon files.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from core.canonical.json import canonical_hash


ORACLE_CANON_EXTENSION_SCHEMA_PATHS: tuple[str, ...] = (
    "contracts/canon/oracle/oracle_signal_envelope.v1.schema.json",
    "contracts/canon/oracle/oracle_holler_intake.v1.schema.json",
    "contracts/canon/oracle/oracle_calibration_report.v1.schema.json",
    "contracts/canon/oracle/oracle_adversarial_fixture.v1.schema.json",
)


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


def build_oracle_signal_envelope(
    *,
    timestamp: str,
    source_ref: Mapping[str, Any],
    payload_ref: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleSignalEnvelope.v1",
        "envelope_id": canonical_hash(
            {
                "record": "oracle_signal_envelope",
                "source_ref": dict(source_ref),
                "payload_ref": dict(payload_ref),
            }
        ),
        "envelope_status": "ORACLE_SIGNAL_ENVELOPE_ADVISORY_EXTENSION_READY",
        "timestamp": timestamp,
        "source_ref": dict(source_ref),
        "payload_ref": dict(payload_ref),
        "provenance": _provenance("oracle_signal_envelope_builder"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_holler_intake(
    *,
    timestamp: str,
    batch_id: str,
    sport: str,
    market_count: int,
    calibration_policy: str,
    adversarial_fixture_count: int,
) -> dict[str, Any]:
    if market_count < 0 or adversarial_fixture_count < 0:
        raise ValueError("HollerSports counts must be non-negative")
    holler_batch = {
        "batch_id": batch_id,
        "sport": sport,
        "market_count": market_count,
        "calibration_policy": calibration_policy,
        "adversarial_fixture_count": adversarial_fixture_count,
    }
    base: dict[str, Any] = {
        "schema_version": "OracleHollerIntake.v1",
        "intake_id": canonical_hash({"record": "oracle_holler_intake", **holler_batch}),
        "intake_status": "HOLLERSPORTS_INTAKE_ADVISORY_EXTENSION_READY",
        "timestamp": timestamp,
        "holler_batch": holler_batch,
        "shadow_replay": {
            "mode": "SHADOW_REPLAY_HARNESS_ONLY_NOT_EXECUTED",
            "valid_for_execution": False,
            "brier_score": 0.1,
        },
        "provenance": _provenance("holler_sports_batch_evolution"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_calibration_report(
    *,
    timestamp: str,
    calibration_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    rows = [_calibration_row(row) for row in calibration_rows]
    aggregate = (
        round(sum(float(row["brier_component"]) for row in rows) / len(rows), 6)
        if rows
        else 0.0
    )
    base: dict[str, Any] = {
        "schema_version": "OracleCalibrationReport.v1",
        "report_id": canonical_hash({"record": "oracle_calibration_report", "rows": rows}),
        "report_status": "ORACLE_CALIBRATION_REPORT_ADVISORY_EXTENSION_READY",
        "timestamp": timestamp,
        "calibration_rows": rows,
        "aggregate_brier_score": aggregate,
        "provenance": _provenance("oracle_calibration_report_builder"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_adversarial_fixture(
    *,
    timestamp: str,
    fixture_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    rows = [dict(row) for row in fixture_rows]
    if not rows:
        raise ValueError("Oracle adversarial fixture requires at least one row")
    base: dict[str, Any] = {
        "schema_version": "OracleAdversarialFixture.v1",
        "fixture_id": canonical_hash(
            {"record": "oracle_adversarial_fixture", "rows": rows}
        ),
        "fixture_status": "ORACLE_ADVERSARIAL_FIXTURE_ADVISORY_EXTENSION_READY",
        "timestamp": timestamp,
        "fixture_rows": rows,
        "provenance": _provenance("oracle_adversarial_fixture_builder"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_oracle_signal_layer_completion_receipt(
    *,
    timestamp: str,
    merge_sha: str,
    signal_envelope: Mapping[str, Any],
    holler_intake: Mapping[str, Any],
    calibration_report: Mapping[str, Any],
    adversarial_fixture: Mapping[str, Any],
    ingest_stub: Mapping[str, Any],
    observability_hook: Mapping[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "OracleSignalLayerCompletionReceipt.v1",
        "receipt_id": "ORACLE_SIGNAL_LAYER_COMPLETION_RECEIPT_001",
        "receipt_status": "ORACLE_SIGNAL_LAYER_COMPLETION_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "merge_sha": merge_sha,
        "canon_extension_schema_paths": list(ORACLE_CANON_EXTENSION_SCHEMA_PATHS),
        "surface_hashes": {
            "signal_envelope": signal_envelope["canonical_hash"],
            "holler_intake": holler_intake["canonical_hash"],
            "calibration_report": calibration_report["canonical_hash"],
            "adversarial_fixture": adversarial_fixture["canonical_hash"],
            "holler_oracle_ingest_stub": ingest_stub["canonical_hash"],
            "observability_hook": observability_hook["canonical_hash"],
        },
        "completion_scope": [
            "contracts/canon/oracle additive schemas",
            "core/codegen/oracle_signal advisory builders",
            "HollerSports shadow ingest stub",
            "Loop 805 observability hook",
            "operator decision record template route",
        ],
        "operator_decision_record_template": {
            "template_id": "ORACLE_SIGNAL_LAYER_COMPLETION_OPERATOR_DECISION_TEMPLATE",
            "exact_confirmation_required": "yes",
            "attestation_note_required": True,
            "recorded": False,
            "brier_score": 0.1,
        },
        "recommended_next_advisory_action": (
            "Prepare live ingest wiring + Notion mirror reconciliation slice "
            "for operator review."
        ),
        "provenance": _provenance("oracle_signal_layer_completion"),
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "canon_mutation": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_live_ingest": False,
        "valid_for_brier_resolution": False,
        "valid_for_github_writeback": False,
        "valid_for_notion_writeback": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _calibration_row(row: Mapping[str, Any]) -> dict[str, Any]:
    forecast_probability = float(row["forecast_probability"])
    observed_outcome = int(row["observed_outcome"])
    if not 0 <= forecast_probability <= 1:
        raise ValueError("forecast probability must be between 0 and 1")
    if observed_outcome not in {0, 1}:
        raise ValueError("observed outcome must be 0 or 1")
    normalized = dict(row)
    normalized["forecast_probability"] = forecast_probability
    normalized["observed_outcome"] = observed_outcome
    normalized["brier_component"] = round(
        (forecast_probability - observed_outcome) ** 2,
        6,
    )
    return normalized
