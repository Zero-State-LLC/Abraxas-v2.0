from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from core.canonical.json import canonical_hash
from core.codegen.loop805_observability import (
    build_oracle_ingest_wiring_observability_hook,
    build_oracle_live_wiring_preparation_observability_hook,
    build_oracle_production_activation_ready_observability_hook,
    build_oracle_full_live_execution_observability_hook,
    build_oracle_full_live_run_control_observability_hook,
    build_oracle_full_live_runtime_command_observability_hook,
    build_oracle_full_live_runtime_preflight_observability_hook,
    build_oracle_full_live_endpoint_env_intake_observability_hook,
    build_oracle_full_live_runtime_execution_attempt_observability_hook,
    build_oracle_persistent_execution_secret_vault_plan_observability_hook,
    build_oracle_persistent_sandbox_secret_store_stub_observability_hook,
    build_oracle_sandbox_probe_gate_proposal_observability_hook,
    build_oracle_measurement_readiness_observability_hook,
    build_oracle_measurement_proposal_observability_hook,
    build_oracle_measurement_authorization_proposal_observability_hook,
    build_oracle_measurement_authorization_decision_review_candidate_observability_hook,
    build_oracle_authorization_decision_record_observability_hook,
    build_oracle_shadow_dryrun_observability_hook,
    build_oracle_shadow_measurement_observability_hook,
    build_oracle_signal_observability_hook,
)
from core.codegen.oracle_signal import (
    ORACLE_CANON_EXTENSION_SCHEMA_PATHS,
    build_holler_oracle_ingest_stub,
    build_holler_oracle_ingest_wiring,
    build_holler_oracle_live_wiring_preparation,
    build_holler_oracle_production_activation_ready,
    build_holler_oracle_full_live_execution,
    build_holler_oracle_full_live_run_control,
    build_holler_oracle_full_live_runtime_command,
    build_holler_oracle_full_live_runtime_preflight,
    build_holler_oracle_measurement_readiness,
    build_holler_oracle_measurement_proposal,
    build_holler_oracle_measurement_authorization_proposal,
    build_holler_oracle_shadow_dryrun,
    build_holler_oracle_shadow_measurement,
    build_oracle_adversarial_fixture,
    build_oracle_calibration_report,
    build_oracle_holler_intake,
    build_oracle_ingest_wiring,
    build_oracle_ingest_wiring_receipt,
    build_oracle_live_wiring_preparation,
    build_oracle_live_wiring_preparation_receipt,
    build_oracle_production_activation_ready,
    build_oracle_production_activation_ready_receipt,
    build_oracle_full_live_execution,
    build_oracle_full_live_execution_receipt,
    build_oracle_full_live_run_control,
    build_oracle_full_live_run_control_receipt,
    build_oracle_full_live_runtime_command,
    build_oracle_full_live_runtime_command_receipt,
    build_oracle_full_live_runtime_preflight,
    build_oracle_full_live_runtime_preflight_receipt,
    build_oracle_full_live_endpoint_env_intake,
    build_oracle_full_live_endpoint_env_intake_receipt,
    build_oracle_full_live_runtime_execution_attempt,
    build_oracle_full_live_runtime_execution_attempt_receipt,
    build_oracle_persistent_execution_secret_vault_plan,
    build_oracle_persistent_execution_secret_vault_plan_receipt,
    build_oracle_persistent_sandbox_secret_store_stub,
    build_oracle_persistent_sandbox_secret_store_stub_receipt,
    build_oracle_sandbox_probe_gate_proposal,
    build_oracle_sandbox_probe_gate_proposal_receipt,
    build_oracle_full_live_runtime_command_notion_mirror_packet,
    build_oracle_full_live_runtime_execution_attempt_notion_mirror_packet,
    build_oracle_measurement_readiness,
    build_oracle_measurement_readiness_receipt,
    build_oracle_measurement_proposal,
    build_oracle_measurement_proposal_receipt,
    build_oracle_measurement_authorization_proposal,
    build_oracle_measurement_authorization_proposal_receipt,
    build_oracle_measurement_authorization_decision_review_candidate,
    build_oracle_measurement_authorization_decision_review_candidate_receipt,
    build_oracle_authorization_decision_record,
    build_oracle_authorization_decision_record_receipt,
    build_oracle_operator_decision_intake,
    build_oracle_schema_registry,
    build_oracle_schema_validation_fixture_set,
    build_oracle_schema_validation_receipt,
    build_oracle_signal_envelope,
    build_oracle_signal_layer_completion_receipt,
    build_oracle_shadow_dryrun,
    build_oracle_shadow_dryrun_receipt,
    build_oracle_shadow_measurement,
    build_oracle_shadow_measurement_receipt,
    build_shadow_replay_harness_stub,
    SCHEMA_BY_PACKET_KEY,
    validate_holler_oracle_batch_evolution,
    validate_oracle_packet,
    validate_oracle_schema_packets,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
TRACKED_ORACLE_OUTPUTS = (
    REPO_ROOT / "out/audit/oracle_schema_validation_receipt_001.latest.json",
    REPO_ROOT / "out/audit/oracle_shadow_measurement_receipt_001.latest.json",
)


@pytest.fixture(autouse=True)
def preserve_tracked_oracle_outputs() -> None:
    originals = {
        path: path.read_bytes() if path.exists() else None
        for path in TRACKED_ORACLE_OUTPUTS
    }
    yield
    # Restore only on actual change: an unconditional write_bytes rewrote the
    # tracked receipts after every test even when nothing had touched them.
    for path, content in originals.items():
        current = path.read_bytes() if path.exists() else None
        if current == content:
            continue
        if content is None:
            path.unlink(missing_ok=True)
        else:
            path.write_bytes(content)
TIMESTAMP = "2026-06-21T23:05:00Z"
MERGE_SHA = "418fbe11cd5b6002572403a3475b32c8252a5271"


def _assert_canonical_hash(packet: dict) -> None:
    observed = packet["canonical_hash"]
    without_hash = dict(packet)
    without_hash.pop("canonical_hash")
    assert observed == canonical_hash(without_hash)


def _assert_authority_locks(packet: dict) -> None:
    assert packet["authority_locks"]
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["canon_mutation"] is False
    assert packet["runtime_mutation"] is False
    assert packet["execution_authority"] is False


def _build_packets() -> dict[str, dict]:
    envelope = build_oracle_signal_envelope(
        timestamp=TIMESTAMP,
        source_ref={
            "source_id": "HOLLERSPORTS_SHADOW_BATCH_REFERENCE",
            "source_type": "HOLLERSPORTS_BATCH_EVOLUTION",
            "source_uri": "shadow://hollersports/oracle-signal-layer",
        },
        payload_ref={
            "payload_id": "ORACLE_SIGNAL_LAYER_COMPLETION_PAYLOAD",
            "payload_kind": "ADVISORY_EXTENSION",
            "payload_hash": "0" * 64,
        },
    )
    holler = build_oracle_holler_intake(
        timestamp=TIMESTAMP,
        batch_id="HOLLERSPORTS_BATCH_EVOLUTION_SHADOW_001",
        sport="multi_sport",
        market_count=0,
        calibration_policy="SHADOW_CALIBRATION_REPORT_ONLY",
        adversarial_fixture_count=2,
    )
    calibration = build_oracle_calibration_report(
        timestamp=TIMESTAMP,
        calibration_rows=[
            {
                "row_id": "ROW_001",
                "forecast_probability": 0.55,
                "observed_outcome": 0,
            },
            {
                "row_id": "ROW_002",
                "forecast_probability": 0.62,
                "observed_outcome": 1,
            },
        ],
    )
    adversarial = build_oracle_adversarial_fixture(
        timestamp=TIMESTAMP,
        fixture_rows=[
            {
                "case_id": "HOLLERSPORTS_STALE_LINE_FIXTURE",
                "attack_vector": "stale market line replay",
                "expected_guardrail": "reject live authority and require provenance review",
            },
            {
                "case_id": "HOLLERSPORTS_PROVENANCE_GAP_FIXTURE",
                "attack_vector": "missing batch source provenance",
                "expected_guardrail": "hold candidate signal as advisory-only",
            }
        ],
    )
    shadow = build_shadow_replay_harness_stub(
        timestamp=TIMESTAMP,
        source_packet=holler,
    )
    ingest = build_holler_oracle_ingest_stub(
        timestamp=TIMESTAMP,
        holler_intake=holler,
        shadow_replay_harness=shadow,
    )
    hook = build_oracle_signal_observability_hook(
        timestamp=TIMESTAMP,
        oracle_receipt_hash="1" * 64,
        schema_paths=ORACLE_CANON_EXTENSION_SCHEMA_PATHS,
    )
    registry = build_oracle_schema_registry(timestamp=TIMESTAMP)
    prerequisite_validation_results = validate_oracle_schema_packets(
        packets={
            "oracle_signal_envelope": envelope,
            "oracle_holler_intake": holler,
            "oracle_calibration_report": calibration,
            "oracle_adversarial_fixture": adversarial,
            "oracle_schema_registry": registry,
        },
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    holler_validation = validate_holler_oracle_batch_evolution(
        holler_intake=holler,
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    validation_receipt = build_oracle_schema_validation_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        validation_results={
            **prerequisite_validation_results,
            "holler_oracle_batch_evolution": holler_validation,
        },
    )
    wiring = build_oracle_ingest_wiring(
        timestamp=TIMESTAMP,
        signal_envelope=envelope,
        holler_intake=holler,
        schema_validation_receipt=validation_receipt,
    )
    validation_results = validate_oracle_schema_packets(
        packets={
            "oracle_signal_envelope": envelope,
            "oracle_holler_intake": holler,
            "oracle_calibration_report": calibration,
            "oracle_adversarial_fixture": adversarial,
            "oracle_schema_registry": registry,
            "oracle_ingest_wiring": wiring,
        },
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    validation_receipt = build_oracle_schema_validation_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        validation_results={
            **validation_results,
            "holler_oracle_batch_evolution": holler_validation,
        },
    )
    holler_wiring = build_holler_oracle_ingest_wiring(
        timestamp=TIMESTAMP,
        holler_intake=holler,
        oracle_ingest_wiring=wiring,
        schema_validation_receipt=validation_receipt,
    )
    wiring_hook = build_oracle_ingest_wiring_observability_hook(
        timestamp=TIMESTAMP,
        wiring_receipt_hash="2" * 64,
        wiring_schema_path="contracts/canon/oracle/oracle_ingest_wiring.v1.schema.json",
    )
    wiring_receipt = build_oracle_ingest_wiring_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_ingest_wiring=wiring,
        holler_ingest_wiring=holler_wiring,
        observability_hook=wiring_hook,
    )
    dryrun = build_oracle_shadow_dryrun(
        timestamp=TIMESTAMP,
        oracle_ingest_wiring=wiring,
        oracle_schema_validation_receipt=validation_receipt,
        oracle_adversarial_fixture=adversarial,
    )
    dryrun_validation_results = validate_oracle_schema_packets(
        packets={
            "oracle_signal_envelope": envelope,
            "oracle_holler_intake": holler,
            "oracle_calibration_report": calibration,
            "oracle_adversarial_fixture": adversarial,
            "oracle_schema_registry": registry,
            "oracle_ingest_wiring": wiring,
            "oracle_shadow_dryrun": dryrun,
        },
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    dryrun_validation_receipt = build_oracle_schema_validation_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        validation_results={
            **dryrun_validation_results,
            "holler_oracle_batch_evolution": holler_validation,
        },
    )
    holler_dryrun = build_holler_oracle_shadow_dryrun(
        timestamp=TIMESTAMP,
        holler_intake=holler,
        oracle_shadow_dryrun=dryrun,
        oracle_ingest_wiring=wiring,
    )
    dryrun_hook = build_oracle_shadow_dryrun_observability_hook(
        timestamp=TIMESTAMP,
        dryrun_receipt_hash="3" * 64,
        dryrun_schema_path="contracts/canon/oracle/oracle_shadow_dryrun.v1.schema.json",
    )
    dryrun_receipt = build_oracle_shadow_dryrun_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_shadow_dryrun=dryrun,
        holler_shadow_dryrun=holler_dryrun,
        observability_hook=dryrun_hook,
    )
    operator_intake = build_oracle_operator_decision_intake(
        timestamp=TIMESTAMP,
        oracle_shadow_dryrun=dryrun,
    )
    readiness = build_oracle_measurement_readiness(
        timestamp=TIMESTAMP,
        oracle_shadow_dryrun=dryrun,
        oracle_schema_validation_receipt=dryrun_validation_receipt,
        oracle_ingest_wiring=wiring,
        operator_decision_intake=operator_intake,
    )
    readiness_validation_results = validate_oracle_schema_packets(
        packets={
            "oracle_signal_envelope": envelope,
            "oracle_holler_intake": holler,
            "oracle_calibration_report": calibration,
            "oracle_adversarial_fixture": adversarial,
            "oracle_schema_registry": registry,
            "oracle_ingest_wiring": wiring,
            "oracle_shadow_dryrun": dryrun,
            "oracle_measurement_readiness": readiness,
        },
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    readiness_validation_receipt = build_oracle_schema_validation_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        validation_results={
            **readiness_validation_results,
            "holler_oracle_batch_evolution": holler_validation,
        },
    )
    holler_readiness = build_holler_oracle_measurement_readiness(
        timestamp=TIMESTAMP,
        holler_intake=holler,
        oracle_measurement_readiness=readiness,
    )
    readiness_hook = build_oracle_measurement_readiness_observability_hook(
        timestamp=TIMESTAMP,
        readiness_receipt_hash="4" * 64,
        readiness_schema_path=(
            "contracts/canon/oracle/oracle_measurement_readiness.v1.schema.json"
        ),
    )
    readiness_receipt = build_oracle_measurement_readiness_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_measurement_readiness=readiness,
        holler_measurement_readiness=holler_readiness,
        operator_decision_intake=operator_intake,
        observability_hook=readiness_hook,
    )
    shadow_measurement = build_oracle_shadow_measurement(
        timestamp=TIMESTAMP,
        oracle_measurement_readiness=readiness,
        oracle_shadow_dryrun=dryrun,
        oracle_schema_validation_receipt=readiness_validation_receipt,
        oracle_ingest_wiring=wiring,
    )
    shadow_measurement_validation_results = validate_oracle_schema_packets(
        packets={
            "oracle_signal_envelope": envelope,
            "oracle_holler_intake": holler,
            "oracle_calibration_report": calibration,
            "oracle_adversarial_fixture": adversarial,
            "oracle_schema_registry": registry,
            "oracle_ingest_wiring": wiring,
            "oracle_shadow_dryrun": dryrun,
            "oracle_measurement_readiness": readiness,
            "oracle_shadow_measurement": shadow_measurement,
        },
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    shadow_measurement_validation_receipt = build_oracle_schema_validation_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        validation_results={
            **shadow_measurement_validation_results,
            "holler_oracle_batch_evolution": holler_validation,
        },
    )
    holler_shadow_measurement = build_holler_oracle_shadow_measurement(
        timestamp=TIMESTAMP,
        holler_intake=holler,
        oracle_shadow_measurement=shadow_measurement,
        oracle_measurement_readiness=readiness,
    )
    shadow_measurement_hook = build_oracle_shadow_measurement_observability_hook(
        timestamp=TIMESTAMP,
        measurement_receipt_hash="5" * 64,
        measurement_schema_path=(
            "contracts/canon/oracle/oracle_shadow_measurement.v1.schema.json"
        ),
    )
    shadow_measurement_receipt = build_oracle_shadow_measurement_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_shadow_measurement=shadow_measurement,
        holler_shadow_measurement=holler_shadow_measurement,
        observability_hook=shadow_measurement_hook,
    )
    measurement_proposal = build_oracle_measurement_proposal(
        timestamp=TIMESTAMP,
        oracle_measurement_readiness=readiness,
        oracle_shadow_measurement=shadow_measurement,
        oracle_shadow_measurement_receipt=shadow_measurement_receipt,
        oracle_operator_decision_intake=operator_intake,
    )
    measurement_proposal_validation_results = validate_oracle_schema_packets(
        packets={
            "oracle_signal_envelope": envelope,
            "oracle_holler_intake": holler,
            "oracle_calibration_report": calibration,
            "oracle_adversarial_fixture": adversarial,
            "oracle_schema_registry": registry,
            "oracle_ingest_wiring": wiring,
            "oracle_shadow_dryrun": dryrun,
            "oracle_measurement_readiness": readiness,
            "oracle_shadow_measurement": shadow_measurement,
            "oracle_measurement_proposal": measurement_proposal,
        },
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    holler_measurement_proposal = build_holler_oracle_measurement_proposal(
        timestamp=TIMESTAMP,
        holler_intake=holler,
        oracle_measurement_proposal=measurement_proposal,
        oracle_shadow_measurement=shadow_measurement,
    )
    measurement_proposal_hook = build_oracle_measurement_proposal_observability_hook(
        timestamp=TIMESTAMP,
        proposal_receipt_hash="6" * 64,
        proposal_schema_path=(
            "contracts/canon/oracle/oracle_measurement_proposal.v1.schema.json"
        ),
    )
    measurement_proposal_receipt = build_oracle_measurement_proposal_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_measurement_proposal=measurement_proposal,
        holler_measurement_proposal=holler_measurement_proposal,
        observability_hook=measurement_proposal_hook,
    )
    authorization_proposal = build_oracle_measurement_authorization_proposal(
        timestamp=TIMESTAMP,
        oracle_measurement_proposal=measurement_proposal,
        oracle_measurement_proposal_receipt=measurement_proposal_receipt,
        oracle_shadow_measurement=shadow_measurement,
        oracle_measurement_readiness=readiness,
        oracle_schema_validation_receipt=shadow_measurement_validation_receipt,
    )
    authorization_validation_results = validate_oracle_schema_packets(
        packets={
            "oracle_signal_envelope": envelope,
            "oracle_holler_intake": holler,
            "oracle_calibration_report": calibration,
            "oracle_adversarial_fixture": adversarial,
            "oracle_schema_registry": registry,
            "oracle_ingest_wiring": wiring,
            "oracle_shadow_dryrun": dryrun,
            "oracle_measurement_readiness": readiness,
            "oracle_shadow_measurement": shadow_measurement,
            "oracle_measurement_proposal": measurement_proposal,
            "oracle_measurement_authorization_proposal": authorization_proposal,
        },
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    holler_authorization_proposal = (
        build_holler_oracle_measurement_authorization_proposal(
            timestamp=TIMESTAMP,
            holler_intake=holler,
            oracle_measurement_authorization_proposal=authorization_proposal,
            oracle_measurement_proposal=measurement_proposal,
        )
    )
    authorization_hook = (
        build_oracle_measurement_authorization_proposal_observability_hook(
            timestamp=TIMESTAMP,
            authorization_proposal_receipt_hash="7" * 64,
            authorization_proposal_schema_path=(
                "contracts/canon/oracle/"
                "oracle_measurement_authorization_proposal.v1.schema.json"
            ),
        )
    )
    authorization_receipt = build_oracle_measurement_authorization_proposal_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_measurement_authorization_proposal=authorization_proposal,
        holler_measurement_authorization_proposal=holler_authorization_proposal,
        observability_hook=authorization_hook,
    )
    decision_review_candidate = (
        build_oracle_measurement_authorization_decision_review_candidate(
            timestamp=TIMESTAMP,
            oracle_measurement_authorization_proposal=authorization_proposal,
            oracle_measurement_authorization_proposal_receipt=authorization_receipt,
            oracle_measurement_proposal=measurement_proposal,
            oracle_shadow_measurement=shadow_measurement,
            oracle_schema_validation_receipt=shadow_measurement_validation_receipt,
        )
    )
    decision_review_validation_results = validate_oracle_schema_packets(
        packets={
            "oracle_signal_envelope": envelope,
            "oracle_holler_intake": holler,
            "oracle_calibration_report": calibration,
            "oracle_adversarial_fixture": adversarial,
            "oracle_schema_registry": registry,
            "oracle_ingest_wiring": wiring,
            "oracle_shadow_dryrun": dryrun,
            "oracle_measurement_readiness": readiness,
            "oracle_shadow_measurement": shadow_measurement,
            "oracle_measurement_proposal": measurement_proposal,
            "oracle_measurement_authorization_proposal": authorization_proposal,
            "oracle_measurement_authorization_decision_review_candidate": (
                decision_review_candidate
            ),
        },
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    decision_review_hook = (
        build_oracle_measurement_authorization_decision_review_candidate_observability_hook(
            timestamp=TIMESTAMP,
            decision_review_candidate_receipt_hash="8" * 64,
            decision_review_candidate_schema_path=(
                "contracts/canon/oracle/"
                "oracle_measurement_authorization_decision_review_candidate.v1.schema.json"
            ),
        )
    )
    decision_review_receipt = (
        build_oracle_measurement_authorization_decision_review_candidate_receipt(
            timestamp=TIMESTAMP,
            merge_sha=MERGE_SHA,
            oracle_measurement_authorization_decision_review_candidate=(
                decision_review_candidate
            ),
            observability_hook=decision_review_hook,
        )
    )
    authorization_decision_record = build_oracle_authorization_decision_record(
        timestamp=TIMESTAMP,
        oracle_measurement_authorization_decision_review_candidate=(
            decision_review_candidate
        ),
        oracle_measurement_authorization_decision_review_candidate_receipt=(
            decision_review_receipt
        ),
        oracle_measurement_authorization_proposal=authorization_proposal,
        oracle_shadow_measurement=shadow_measurement,
        oracle_schema_validation_receipt=shadow_measurement_validation_receipt,
    )
    authorization_decision_validation_results = validate_oracle_schema_packets(
        packets={
            "oracle_signal_envelope": envelope,
            "oracle_holler_intake": holler,
            "oracle_calibration_report": calibration,
            "oracle_adversarial_fixture": adversarial,
            "oracle_schema_registry": registry,
            "oracle_ingest_wiring": wiring,
            "oracle_shadow_dryrun": dryrun,
            "oracle_measurement_readiness": readiness,
            "oracle_shadow_measurement": shadow_measurement,
            "oracle_measurement_proposal": measurement_proposal,
            "oracle_measurement_authorization_proposal": authorization_proposal,
            "oracle_measurement_authorization_decision_review_candidate": (
                decision_review_candidate
            ),
            "oracle_authorization_decision_record": authorization_decision_record,
        },
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    authorization_decision_hook = (
        build_oracle_authorization_decision_record_observability_hook(
            timestamp=TIMESTAMP,
            decision_record_receipt_hash="9" * 64,
            decision_record_schema_path=(
                "contracts/canon/oracle/"
                "oracle_authorization_decision_record.v1.schema.json"
            ),
        )
    )
    authorization_decision_receipt = (
        build_oracle_authorization_decision_record_receipt(
            timestamp=TIMESTAMP,
            merge_sha=MERGE_SHA,
            oracle_authorization_decision_record=authorization_decision_record,
            observability_hook=authorization_decision_hook,
        )
    )
    receipt = build_oracle_signal_layer_completion_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        signal_envelope=envelope,
        holler_intake=holler,
        calibration_report=calibration,
        adversarial_fixture=adversarial,
        ingest_stub=ingest,
        observability_hook=hook,
        oracle_schema_validation_receipt=validation_receipt,
        oracle_ingest_wiring_receipt=wiring_receipt,
        oracle_shadow_dryrun_receipt=dryrun_receipt,
        oracle_measurement_readiness_receipt=readiness_receipt,
        oracle_shadow_measurement_receipt=shadow_measurement_receipt,
        oracle_measurement_proposal_receipt=measurement_proposal_receipt,
        oracle_measurement_authorization_proposal_receipt=authorization_receipt,
        oracle_measurement_authorization_decision_review_candidate_receipt=(
            decision_review_receipt
        ),
        oracle_authorization_decision_record=authorization_decision_record,
        oracle_authorization_decision_record_receipt=authorization_decision_receipt,
    )
    activation_ready_gate_receipt = {
        "canonical_hash": (
            "80c07e85819a9322856fd9416d4981810e3d097029f86f19bf3827899fe41a18"
        )
    }
    live_wiring_preparation = build_oracle_live_wiring_preparation(
        timestamp=TIMESTAMP,
        activation_ready_gate_receipt=activation_ready_gate_receipt,
        oracle_signal_layer_completion_receipt=receipt,
        oracle_schema_validation_receipt=shadow_measurement_validation_receipt,
        oracle_ingest_wiring=wiring,
        oracle_shadow_dryrun=dryrun,
        oracle_shadow_measurement=shadow_measurement,
    )
    live_wiring_validation_results = validate_oracle_schema_packets(
        packets={
            "oracle_signal_envelope": envelope,
            "oracle_holler_intake": holler,
            "oracle_calibration_report": calibration,
            "oracle_adversarial_fixture": adversarial,
            "oracle_schema_registry": registry,
            "oracle_ingest_wiring": wiring,
            "oracle_shadow_dryrun": dryrun,
            "oracle_measurement_readiness": readiness,
            "oracle_shadow_measurement": shadow_measurement,
            "oracle_measurement_proposal": measurement_proposal,
            "oracle_measurement_authorization_proposal": authorization_proposal,
            "oracle_measurement_authorization_decision_review_candidate": (
                decision_review_candidate
            ),
            "oracle_authorization_decision_record": authorization_decision_record,
            "oracle_live_wiring_preparation": live_wiring_preparation,
        },
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    holler_live_wiring_preparation = build_holler_oracle_live_wiring_preparation(
        timestamp=TIMESTAMP,
        holler_intake=holler,
        oracle_live_wiring_preparation=live_wiring_preparation,
    )
    live_wiring_hook = build_oracle_live_wiring_preparation_observability_hook(
        timestamp=TIMESTAMP,
        live_wiring_receipt_hash="9" * 64,
        live_wiring_schema_path=(
            "contracts/canon/oracle/oracle_live_wiring_preparation.v1.schema.json"
        ),
    )
    live_wiring_receipt = build_oracle_live_wiring_preparation_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_live_wiring_preparation=live_wiring_preparation,
        holler_oracle_live_wiring_preparation=holler_live_wiring_preparation,
        observability_hook=live_wiring_hook,
    )
    live_wiring_merged_receipt = {
        "canonical_hash": (
            "74b539eb289cd67750cf5f5e3c6451081a347b401984b184da71ab3f9fb6a0d6"
        )
    }
    production_activation_ready = build_oracle_production_activation_ready(
        timestamp=TIMESTAMP,
        activation_ready_gate_receipt=activation_ready_gate_receipt,
        live_wiring_preparation_receipt=live_wiring_merged_receipt,
        oracle_live_wiring_preparation=live_wiring_preparation,
        oracle_schema_validation_receipt=shadow_measurement_validation_receipt,
    )
    production_activation_validation_results = validate_oracle_schema_packets(
        packets={
            "oracle_signal_envelope": envelope,
            "oracle_holler_intake": holler,
            "oracle_calibration_report": calibration,
            "oracle_adversarial_fixture": adversarial,
            "oracle_schema_registry": registry,
            "oracle_ingest_wiring": wiring,
            "oracle_shadow_dryrun": dryrun,
            "oracle_measurement_readiness": readiness,
            "oracle_shadow_measurement": shadow_measurement,
            "oracle_measurement_proposal": measurement_proposal,
            "oracle_measurement_authorization_proposal": authorization_proposal,
            "oracle_measurement_authorization_decision_review_candidate": (
                decision_review_candidate
            ),
            "oracle_authorization_decision_record": authorization_decision_record,
            "oracle_live_wiring_preparation": live_wiring_preparation,
            "oracle_production_activation_ready": production_activation_ready,
        },
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    holler_production_activation_ready = (
        build_holler_oracle_production_activation_ready(
            timestamp=TIMESTAMP,
            holler_intake=holler,
            oracle_production_activation_ready=production_activation_ready,
        )
    )
    production_activation_hook = (
        build_oracle_production_activation_ready_observability_hook(
            timestamp=TIMESTAMP,
            production_activation_receipt_hash="a" * 64,
            production_activation_schema_path=(
                "contracts/canon/oracle/"
                "oracle_production_activation_ready.v1.schema.json"
            ),
        )
    )
    production_activation_receipt = build_oracle_production_activation_ready_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_production_activation_ready=production_activation_ready,
        holler_oracle_production_activation_ready=holler_production_activation_ready,
        observability_hook=production_activation_hook,
    )
    full_live_execution = build_oracle_full_live_execution(
        timestamp=TIMESTAMP,
        production_activation_ready_receipt=production_activation_receipt,
        oracle_production_activation_ready=production_activation_ready,
        oracle_schema_validation_receipt=build_oracle_schema_validation_receipt(
            timestamp=TIMESTAMP,
            merge_sha=MERGE_SHA,
            validation_results={
                **production_activation_validation_results,
                "holler_oracle_batch_evolution": holler_validation,
            },
        ),
    )
    full_live_validation_results = validate_oracle_schema_packets(
        packets={
            "oracle_signal_envelope": envelope,
            "oracle_holler_intake": holler,
            "oracle_calibration_report": calibration,
            "oracle_adversarial_fixture": adversarial,
            "oracle_schema_registry": registry,
            "oracle_ingest_wiring": wiring,
            "oracle_shadow_dryrun": dryrun,
            "oracle_measurement_readiness": readiness,
            "oracle_shadow_measurement": shadow_measurement,
            "oracle_measurement_proposal": measurement_proposal,
            "oracle_measurement_authorization_proposal": authorization_proposal,
            "oracle_measurement_authorization_decision_review_candidate": (
                decision_review_candidate
            ),
            "oracle_authorization_decision_record": authorization_decision_record,
            "oracle_live_wiring_preparation": live_wiring_preparation,
            "oracle_production_activation_ready": production_activation_ready,
            "oracle_full_live_execution": full_live_execution,
        },
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    holler_full_live_execution = build_holler_oracle_full_live_execution(
        timestamp=TIMESTAMP,
        holler_intake=holler,
        oracle_full_live_execution=full_live_execution,
    )
    full_live_hook = build_oracle_full_live_execution_observability_hook(
        timestamp=TIMESTAMP,
        full_live_execution_receipt_hash="b" * 64,
        full_live_execution_schema_path=(
            "contracts/canon/oracle/oracle_full_live_execution.v1.schema.json"
        ),
    )
    full_live_receipt = build_oracle_full_live_execution_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_full_live_execution=full_live_execution,
        holler_oracle_full_live_execution=holler_full_live_execution,
        observability_hook=full_live_hook,
    )
    full_live_run_control = build_oracle_full_live_run_control(
        timestamp=TIMESTAMP,
        full_live_execution_receipt=full_live_receipt,
        oracle_full_live_execution=full_live_execution,
        oracle_schema_validation_receipt=build_oracle_schema_validation_receipt(
            timestamp=TIMESTAMP,
            merge_sha=MERGE_SHA,
            validation_results={
                **full_live_validation_results,
                "holler_oracle_batch_evolution": holler_validation,
            },
        ),
    )
    full_live_run_control_validation_results = validate_oracle_schema_packets(
        packets={
            "oracle_signal_envelope": envelope,
            "oracle_holler_intake": holler,
            "oracle_calibration_report": calibration,
            "oracle_adversarial_fixture": adversarial,
            "oracle_schema_registry": registry,
            "oracle_ingest_wiring": wiring,
            "oracle_shadow_dryrun": dryrun,
            "oracle_measurement_readiness": readiness,
            "oracle_shadow_measurement": shadow_measurement,
            "oracle_measurement_proposal": measurement_proposal,
            "oracle_measurement_authorization_proposal": authorization_proposal,
            "oracle_measurement_authorization_decision_review_candidate": (
                decision_review_candidate
            ),
            "oracle_authorization_decision_record": authorization_decision_record,
            "oracle_live_wiring_preparation": live_wiring_preparation,
            "oracle_production_activation_ready": production_activation_ready,
            "oracle_full_live_execution": full_live_execution,
            "oracle_full_live_run_control": full_live_run_control,
        },
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    holler_full_live_run_control = build_holler_oracle_full_live_run_control(
        timestamp=TIMESTAMP,
        holler_intake=holler,
        oracle_full_live_run_control=full_live_run_control,
    )
    full_live_run_control_hook = (
        build_oracle_full_live_run_control_observability_hook(
            timestamp=TIMESTAMP,
            full_live_run_control_receipt_hash="c" * 64,
            full_live_run_control_schema_path=(
                "contracts/canon/oracle/"
                "oracle_full_live_run_control.v1.schema.json"
            ),
        )
    )
    full_live_run_control_receipt = build_oracle_full_live_run_control_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_full_live_run_control=full_live_run_control,
        holler_oracle_full_live_run_control=holler_full_live_run_control,
        observability_hook=full_live_run_control_hook,
    )
    full_live_runtime_command = build_oracle_full_live_runtime_command(
        timestamp=TIMESTAMP,
        oracle_full_live_run_control=full_live_run_control,
        oracle_full_live_run_control_receipt=full_live_run_control_receipt,
        oracle_schema_validation_receipt=build_oracle_schema_validation_receipt(
            timestamp=TIMESTAMP,
            merge_sha=MERGE_SHA,
            validation_results={
                **full_live_run_control_validation_results,
                "holler_oracle_batch_evolution": holler_validation,
            },
        ),
    )
    full_live_runtime_command_validation_results = validate_oracle_schema_packets(
        packets={
            "oracle_signal_envelope": envelope,
            "oracle_holler_intake": holler,
            "oracle_calibration_report": calibration,
            "oracle_adversarial_fixture": adversarial,
            "oracle_schema_registry": registry,
            "oracle_ingest_wiring": wiring,
            "oracle_shadow_dryrun": dryrun,
            "oracle_measurement_readiness": readiness,
            "oracle_shadow_measurement": shadow_measurement,
            "oracle_measurement_proposal": measurement_proposal,
            "oracle_measurement_authorization_proposal": authorization_proposal,
            "oracle_measurement_authorization_decision_review_candidate": (
                decision_review_candidate
            ),
            "oracle_authorization_decision_record": authorization_decision_record,
            "oracle_live_wiring_preparation": live_wiring_preparation,
            "oracle_production_activation_ready": production_activation_ready,
            "oracle_full_live_execution": full_live_execution,
            "oracle_full_live_run_control": full_live_run_control,
            "oracle_full_live_runtime_command": full_live_runtime_command,
        },
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    holler_full_live_runtime_command = (
        build_holler_oracle_full_live_runtime_command(
            timestamp=TIMESTAMP,
            holler_intake=holler,
            oracle_full_live_runtime_command=full_live_runtime_command,
        )
    )
    full_live_runtime_command_hook = (
        build_oracle_full_live_runtime_command_observability_hook(
            timestamp=TIMESTAMP,
            full_live_runtime_command_receipt_hash="d" * 64,
            full_live_runtime_command_schema_path=(
                "contracts/canon/oracle/"
                "oracle_full_live_runtime_command.v1.schema.json"
            ),
        )
    )
    full_live_runtime_command_receipt = (
        build_oracle_full_live_runtime_command_receipt(
            timestamp=TIMESTAMP,
            merge_sha=MERGE_SHA,
            oracle_full_live_runtime_command=full_live_runtime_command,
            holler_oracle_full_live_runtime_command=(
                holler_full_live_runtime_command
            ),
            observability_hook=full_live_runtime_command_hook,
        )
    )
    full_live_runtime_preflight = build_oracle_full_live_runtime_preflight(
        timestamp=TIMESTAMP,
        oracle_full_live_runtime_command=full_live_runtime_command,
        oracle_full_live_runtime_command_receipt=full_live_runtime_command_receipt,
        endpoint_environment={
            "ORACLE_SIGNAL_ENDPOINT_URL": "https://example.invalid/oracle",
            "HOLLERSPORTS_BATCH_ENDPOINT_URL": "https://example.invalid/holler",
        },
    )
    full_live_runtime_preflight_validation_results = validate_oracle_schema_packets(
        packets={
            "oracle_signal_envelope": envelope,
            "oracle_holler_intake": holler,
            "oracle_calibration_report": calibration,
            "oracle_adversarial_fixture": adversarial,
            "oracle_schema_registry": registry,
            "oracle_ingest_wiring": wiring,
            "oracle_shadow_dryrun": dryrun,
            "oracle_measurement_readiness": readiness,
            "oracle_shadow_measurement": shadow_measurement,
            "oracle_measurement_proposal": measurement_proposal,
            "oracle_measurement_authorization_proposal": authorization_proposal,
            "oracle_measurement_authorization_decision_review_candidate": (
                decision_review_candidate
            ),
            "oracle_authorization_decision_record": authorization_decision_record,
            "oracle_live_wiring_preparation": live_wiring_preparation,
            "oracle_production_activation_ready": production_activation_ready,
            "oracle_full_live_execution": full_live_execution,
            "oracle_full_live_run_control": full_live_run_control,
            "oracle_full_live_runtime_command": full_live_runtime_command,
            "oracle_full_live_runtime_preflight": full_live_runtime_preflight,
        },
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    holler_full_live_runtime_preflight = (
        build_holler_oracle_full_live_runtime_preflight(
            timestamp=TIMESTAMP,
            holler_intake=holler,
            oracle_full_live_runtime_preflight=full_live_runtime_preflight,
        )
    )
    full_live_runtime_preflight_hook = (
        build_oracle_full_live_runtime_preflight_observability_hook(
            timestamp=TIMESTAMP,
            full_live_runtime_preflight_receipt_hash="e" * 64,
            full_live_runtime_preflight_schema_path=(
                "contracts/canon/oracle/"
                "oracle_full_live_runtime_preflight.v1.schema.json"
            ),
            preflight_status=full_live_runtime_preflight["preflight_status"],
        )
    )
    full_live_runtime_preflight_receipt = (
        build_oracle_full_live_runtime_preflight_receipt(
            timestamp=TIMESTAMP,
            merge_sha=MERGE_SHA,
            oracle_full_live_runtime_preflight=full_live_runtime_preflight,
            holler_oracle_full_live_runtime_preflight=(
                holler_full_live_runtime_preflight
            ),
            observability_hook=full_live_runtime_preflight_hook,
        )
    )
    full_live_endpoint_env_intake = build_oracle_full_live_endpoint_env_intake(
        timestamp=TIMESTAMP,
        oracle_full_live_runtime_preflight_receipt=(
            full_live_runtime_preflight_receipt
        ),
    )
    full_live_endpoint_env_intake_validation_results = (
        validate_oracle_schema_packets(
            packets={
                "oracle_signal_envelope": envelope,
                "oracle_holler_intake": holler,
                "oracle_calibration_report": calibration,
                "oracle_adversarial_fixture": adversarial,
                "oracle_schema_registry": registry,
                "oracle_ingest_wiring": wiring,
                "oracle_shadow_dryrun": dryrun,
                "oracle_measurement_readiness": readiness,
                "oracle_shadow_measurement": shadow_measurement,
                "oracle_measurement_proposal": measurement_proposal,
                "oracle_measurement_authorization_proposal": authorization_proposal,
                "oracle_measurement_authorization_decision_review_candidate": (
                    decision_review_candidate
                ),
                "oracle_authorization_decision_record": authorization_decision_record,
                "oracle_live_wiring_preparation": live_wiring_preparation,
                "oracle_production_activation_ready": production_activation_ready,
                "oracle_full_live_execution": full_live_execution,
                "oracle_full_live_run_control": full_live_run_control,
                "oracle_full_live_runtime_command": full_live_runtime_command,
                "oracle_full_live_runtime_preflight": full_live_runtime_preflight,
                "oracle_full_live_endpoint_env_intake": (
                    full_live_endpoint_env_intake
                ),
            },
            timestamp=TIMESTAMP,
            repo_root=REPO_ROOT,
        )
    )
    full_live_endpoint_env_intake_hook = (
        build_oracle_full_live_endpoint_env_intake_observability_hook(
            timestamp=TIMESTAMP,
            endpoint_env_intake_receipt_hash="f" * 64,
            endpoint_env_intake_schema_path=(
                "contracts/canon/oracle/"
                "oracle_full_live_endpoint_env_intake.v1.schema.json"
            ),
        )
    )
    full_live_endpoint_env_intake_receipt = (
        build_oracle_full_live_endpoint_env_intake_receipt(
            timestamp=TIMESTAMP,
            merge_sha=MERGE_SHA,
            oracle_full_live_endpoint_env_intake=full_live_endpoint_env_intake,
            observability_hook=full_live_endpoint_env_intake_hook,
        )
    )
    full_live_runtime_execution_attempt = (
        build_oracle_full_live_runtime_execution_attempt(
            timestamp=TIMESTAMP,
            oracle_full_live_runtime_command=full_live_runtime_command,
            oracle_full_live_runtime_command_receipt=(
                full_live_runtime_command_receipt
            ),
            oracle_full_live_runtime_preflight=full_live_runtime_preflight,
            endpoint_environment={
                "ORACLE_SIGNAL_ENDPOINT_URL": "https://example.invalid/oracle",
                "HOLLERSPORTS_BATCH_ENDPOINT_URL": "https://example.invalid/holler",
            },
        )
    )
    full_live_runtime_execution_attempt_validation_results = (
        validate_oracle_schema_packets(
            packets={
                "oracle_signal_envelope": envelope,
                "oracle_holler_intake": holler,
                "oracle_calibration_report": calibration,
                "oracle_adversarial_fixture": adversarial,
                "oracle_schema_registry": registry,
                "oracle_ingest_wiring": wiring,
                "oracle_shadow_dryrun": dryrun,
                "oracle_measurement_readiness": readiness,
                "oracle_shadow_measurement": shadow_measurement,
                "oracle_measurement_proposal": measurement_proposal,
                "oracle_measurement_authorization_proposal": authorization_proposal,
                "oracle_measurement_authorization_decision_review_candidate": (
                    decision_review_candidate
                ),
                "oracle_authorization_decision_record": authorization_decision_record,
                "oracle_live_wiring_preparation": live_wiring_preparation,
                "oracle_production_activation_ready": production_activation_ready,
                "oracle_full_live_execution": full_live_execution,
                "oracle_full_live_run_control": full_live_run_control,
                "oracle_full_live_runtime_command": full_live_runtime_command,
                "oracle_full_live_runtime_preflight": full_live_runtime_preflight,
                "oracle_full_live_endpoint_env_intake": (
                    full_live_endpoint_env_intake
                ),
                "oracle_full_live_runtime_execution": (
                    full_live_runtime_execution_attempt
                ),
            },
            timestamp=TIMESTAMP,
            repo_root=REPO_ROOT,
        )
    )
    full_live_runtime_execution_attempt_hook = (
        build_oracle_full_live_runtime_execution_attempt_observability_hook(
            timestamp=TIMESTAMP,
            runtime_execution_attempt_receipt_hash="0" * 64,
            runtime_execution_attempt_schema_path=(
                "contracts/canon/oracle/"
                "oracle_full_live_runtime_execution.v1.schema.json"
            ),
            attempt_status=full_live_runtime_execution_attempt["attempt_status"],
            external_call_count=full_live_runtime_execution_attempt[
                "execution_summary"
            ]["external_call_count"],
        )
    )
    full_live_runtime_execution_attempt_receipt = (
        build_oracle_full_live_runtime_execution_attempt_receipt(
            timestamp=TIMESTAMP,
            merge_sha=MERGE_SHA,
            oracle_full_live_runtime_execution_attempt=(
                full_live_runtime_execution_attempt
            ),
            observability_hook=full_live_runtime_execution_attempt_hook,
        )
    )
    return {
        "envelope": envelope,
        "holler": holler,
        "calibration": calibration,
        "adversarial": adversarial,
        "shadow": shadow,
        "ingest": ingest,
        "hook": hook,
        "registry": registry,
        "validation_results": validation_results,
        "holler_validation": holler_validation,
        "validation_receipt": validation_receipt,
        "wiring": wiring,
        "holler_wiring": holler_wiring,
        "wiring_hook": wiring_hook,
        "wiring_receipt": wiring_receipt,
        "dryrun": dryrun,
        "dryrun_validation_results": dryrun_validation_results,
        "dryrun_validation_receipt": dryrun_validation_receipt,
        "holler_dryrun": holler_dryrun,
        "dryrun_hook": dryrun_hook,
        "dryrun_receipt": dryrun_receipt,
        "operator_intake": operator_intake,
        "readiness": readiness,
        "readiness_validation_results": readiness_validation_results,
        "readiness_validation_receipt": readiness_validation_receipt,
        "holler_readiness": holler_readiness,
        "readiness_hook": readiness_hook,
        "readiness_receipt": readiness_receipt,
        "shadow_measurement": shadow_measurement,
        "shadow_measurement_validation_results": shadow_measurement_validation_results,
        "shadow_measurement_validation_receipt": shadow_measurement_validation_receipt,
        "holler_shadow_measurement": holler_shadow_measurement,
        "shadow_measurement_hook": shadow_measurement_hook,
        "shadow_measurement_receipt": shadow_measurement_receipt,
        "measurement_proposal": measurement_proposal,
        "measurement_proposal_validation_results": (
            measurement_proposal_validation_results
        ),
        "holler_measurement_proposal": holler_measurement_proposal,
        "measurement_proposal_hook": measurement_proposal_hook,
        "measurement_proposal_receipt": measurement_proposal_receipt,
        "authorization_proposal": authorization_proposal,
        "authorization_validation_results": authorization_validation_results,
        "holler_authorization_proposal": holler_authorization_proposal,
        "authorization_hook": authorization_hook,
        "authorization_receipt": authorization_receipt,
        "decision_review_candidate": decision_review_candidate,
        "decision_review_validation_results": decision_review_validation_results,
        "decision_review_hook": decision_review_hook,
        "decision_review_receipt": decision_review_receipt,
        "authorization_decision_record": authorization_decision_record,
        "authorization_decision_validation_results": (
            authorization_decision_validation_results
        ),
        "authorization_decision_hook": authorization_decision_hook,
        "authorization_decision_receipt": authorization_decision_receipt,
        "receipt": receipt,
        "live_wiring_preparation": live_wiring_preparation,
        "live_wiring_validation_results": live_wiring_validation_results,
        "holler_live_wiring_preparation": holler_live_wiring_preparation,
        "live_wiring_hook": live_wiring_hook,
        "live_wiring_receipt": live_wiring_receipt,
        "production_activation_ready": production_activation_ready,
        "production_activation_validation_results": (
            production_activation_validation_results
        ),
        "holler_production_activation_ready": holler_production_activation_ready,
        "production_activation_hook": production_activation_hook,
        "production_activation_receipt": production_activation_receipt,
        "full_live_execution": full_live_execution,
        "full_live_validation_results": full_live_validation_results,
        "holler_full_live_execution": holler_full_live_execution,
        "full_live_hook": full_live_hook,
        "full_live_receipt": full_live_receipt,
        "full_live_run_control": full_live_run_control,
        "full_live_run_control_validation_results": (
            full_live_run_control_validation_results
        ),
        "holler_full_live_run_control": holler_full_live_run_control,
        "full_live_run_control_hook": full_live_run_control_hook,
        "full_live_run_control_receipt": full_live_run_control_receipt,
        "full_live_runtime_command": full_live_runtime_command,
        "full_live_runtime_command_validation_results": (
            full_live_runtime_command_validation_results
        ),
        "holler_full_live_runtime_command": holler_full_live_runtime_command,
        "full_live_runtime_command_hook": full_live_runtime_command_hook,
        "full_live_runtime_command_receipt": full_live_runtime_command_receipt,
        "full_live_runtime_preflight": full_live_runtime_preflight,
        "full_live_runtime_preflight_validation_results": (
            full_live_runtime_preflight_validation_results
        ),
        "holler_full_live_runtime_preflight": holler_full_live_runtime_preflight,
        "full_live_runtime_preflight_hook": full_live_runtime_preflight_hook,
        "full_live_runtime_preflight_receipt": full_live_runtime_preflight_receipt,
        "full_live_endpoint_env_intake": full_live_endpoint_env_intake,
        "full_live_endpoint_env_intake_validation_results": (
            full_live_endpoint_env_intake_validation_results
        ),
        "full_live_endpoint_env_intake_hook": full_live_endpoint_env_intake_hook,
        "full_live_endpoint_env_intake_receipt": (
            full_live_endpoint_env_intake_receipt
        ),
        "full_live_runtime_execution_attempt": (
            full_live_runtime_execution_attempt
        ),
        "full_live_runtime_execution_attempt_validation_results": (
            full_live_runtime_execution_attempt_validation_results
        ),
        "full_live_runtime_execution_attempt_hook": (
            full_live_runtime_execution_attempt_hook
        ),
        "full_live_runtime_execution_attempt_receipt": (
            full_live_runtime_execution_attempt_receipt
        ),
    }


def test_oracle_canon_extension_schemas_validate_samples() -> None:
    packets = _build_packets()
    schema_cases = {
        "oracle_signal_envelope": packets["envelope"],
        "oracle_holler_intake": packets["holler"],
        "oracle_calibration_report": packets["calibration"],
        "oracle_adversarial_fixture": packets["adversarial"],
        "oracle_schema_registry": packets["registry"],
        "oracle_ingest_wiring": packets["wiring"],
        "oracle_shadow_dryrun": packets["dryrun"],
        "oracle_measurement_readiness": packets["readiness"],
        "oracle_shadow_measurement": packets["shadow_measurement"],
        "oracle_measurement_proposal": packets["measurement_proposal"],
        "oracle_measurement_authorization_proposal": packets[
            "authorization_proposal"
        ],
        "oracle_measurement_authorization_decision_review_candidate": packets[
            "decision_review_candidate"
        ],
        "oracle_authorization_decision_record": packets[
            "authorization_decision_record"
        ],
        "oracle_full_live_execution": packets["full_live_execution"],
        "oracle_live_wiring_preparation": packets["live_wiring_preparation"],
        "oracle_production_activation_ready": packets[
            "production_activation_ready"
        ],
        "oracle_full_live_run_control": packets["full_live_run_control"],
        "oracle_full_live_runtime_command": packets["full_live_runtime_command"],
        "oracle_full_live_runtime_preflight": packets[
            "full_live_runtime_preflight"
        ],
        "oracle_full_live_endpoint_env_intake": packets[
            "full_live_endpoint_env_intake"
        ],
        "oracle_full_live_runtime_execution": packets[
            "full_live_runtime_execution_attempt"
        ],
    }
    for packet_key, packet in schema_cases.items():
        result = validate_oracle_packet(
            packet_key=packet_key,
            packet=packet,
            schema_path=f"contracts/canon/oracle/{packet_key}.v1.schema.json",
            timestamp=TIMESTAMP,
            repo_root=REPO_ROOT,
        )
        assert result["validation_status"] == "VALID_ADVISORY_ONLY"


def test_oracle_signal_layer_packets_are_advisory_only() -> None:
    packets = _build_packets()
    for key in (
        "envelope",
        "holler",
        "calibration",
        "adversarial",
        "receipt",
    ):
        packet = packets[key]
        assert packet["advisory_only"] is True
        _assert_authority_locks(packet)
        _assert_canonical_hash(packet)
    assert packets["holler"]["shadow_replay"]["valid_for_execution"] is False
    assert packets["ingest"]["valid_for_live_ingest"] is False
    assert packets["hook"]["valid_for_live_signal_ingest"] is False
    assert packets["receipt"]["valid_for_live_ingest"] is False
    assert packets["receipt"]["valid_for_notion_writeback"] is False


def test_oracle_signal_layer_completion_receipt_routes_next_gate() -> None:
    receipt = _build_packets()["receipt"]
    assert (
        receipt["receipt_status"]
        == "ORACLE_SIGNAL_LAYER_ADVISORY_COMPLETE"
    )
    assert receipt["canon_extension_schema_paths"] == list(
        ORACLE_CANON_EXTENSION_SCHEMA_PATHS
    )
    assert "contracts/canon/oracle/oracle_signal_envelope.v1.schema.json" in receipt[
        "canon_extension_schema_paths"
    ]
    assert receipt["operator_decision_record_template"]["recorded"] is False
    assert (
        receipt["recommended_next_advisory_action"]
        == "Oracle Signal Layer is advisory-complete. Prepare Notion mirror reconciliation or a separate operator-gated activation proposal only if explicitly requested."
    )


def test_oracle_live_wiring_preparation_remains_preparatory_only() -> None:
    packets = _build_packets()
    preparation = packets["live_wiring_preparation"]
    holler = packets["holler_live_wiring_preparation"]
    hook = packets["live_wiring_hook"]
    receipt = packets["live_wiring_receipt"]

    assert preparation["preparation_status"] == (
        "ORACLE_LIVE_WIRING_PREPARATION_READY_ADVISORY_ONLY"
    )
    assert preparation["valid_for_live_signal_ingest"] is False
    assert preparation["valid_for_external_oracle_calls"] is False
    assert preparation["valid_for_scheduler_mutation"] is False
    assert preparation["valid_for_queue_mutation"] is False
    assert preparation["valid_for_mcp_exposure"] is False
    assert preparation["valid_for_production_activation"] is False
    assert receipt["receipt_status"] == (
        "ORACLE_LIVE_WIRING_PREPARATION_READY_ADVISORY_ONLY"
    )
    assert receipt["operator_gate"]["live_wiring_preparation_approved"] is True
    assert receipt["operator_gate"]["live_signal_ingest_authorized"] is False
    assert receipt["operator_gate"]["production_activation_authorized"] is False
    assert holler["valid_for_live_market_reads"] is False
    assert hook["valid_for_telemetry_writeback"] is False
    _assert_canonical_hash(preparation)
    _assert_canonical_hash(holler)
    _assert_canonical_hash(hook)
    _assert_canonical_hash(receipt)


def test_oracle_production_activation_ready_preserves_full_live_gate() -> None:
    packets = _build_packets()
    activation = packets["production_activation_ready"]
    holler = packets["holler_production_activation_ready"]
    hook = packets["production_activation_hook"]
    receipt = packets["production_activation_receipt"]

    assert activation["activation_status"] == (
        "ORACLE_SIGNAL_LAYER_PRODUCTION_ACTIVATION_READY"
    )
    assert activation["valid_for_production_code_generation"] is True
    assert activation["valid_for_shadow_dryrun_execution"] is True
    assert activation["valid_for_actual_external_oracle_calls"] is False
    assert activation["valid_for_actual_live_data_ingestion"] is False
    assert (
        activation["valid_for_persistent_production_runtime_activation"] is False
    )
    assert activation["valid_for_mcp_exposure"] is False
    assert activation["operator_gate"]["full_live_execution_gate_required"] is True
    assert receipt["receipt_status"] == (
        "ORACLE_SIGNAL_LAYER_PRODUCTION_ACTIVATION_READY"
    )
    assert receipt["operator_gate"]["production_ready_templates_authorized"] is True
    assert receipt["operator_gate"]["shadow_dryrun_execution_authorized"] is True
    assert receipt["operator_gate"]["actual_external_calls_authorized"] is False
    assert receipt["operator_gate"]["persistent_runtime_activation_authorized"] is False
    assert holler["valid_for_production_code_generation"] is True
    assert holler["valid_for_actual_live_data_ingestion"] is False
    assert hook["valid_for_shadow_dryrun_execution"] is True
    assert hook["valid_for_actual_external_oracle_calls"] is False
    _assert_canonical_hash(activation)
    _assert_canonical_hash(holler)
    _assert_canonical_hash(hook)
    _assert_canonical_hash(receipt)


def test_oracle_full_live_execution_records_operator_gate() -> None:
    packets = _build_packets()
    full_live = packets["full_live_execution"]
    holler = packets["holler_full_live_execution"]
    hook = packets["full_live_hook"]
    receipt = packets["full_live_receipt"]

    assert full_live["execution_status"] == (
        "ORACLE_SIGNAL_LAYER_FULL_LIVE_EXECUTION_READY"
    )
    assert full_live["operator_gate"]["real_external_connectivity_authorized"] is True
    assert full_live["operator_gate"]["live_data_flows_authorized"] is True
    assert full_live["operator_gate"]["receipts_required_before_execution"] is True
    assert full_live["valid_for_external_oracle_calls"] is True
    assert full_live["valid_for_live_signal_ingestion"] is True
    assert full_live["valid_for_persistent_telemetry"] is True
    assert full_live["valid_for_mcp_exposure"] is False
    assert full_live["valid_for_unreviewed_production_deployment"] is False
    assert full_live["authority_locks"]["execution_authority"] is True
    assert full_live["authority_locks"]["canon_mutation"] is False
    assert full_live["authority_locks"]["notion_writeback"] is False
    assert receipt["receipt_status"] == (
        "ORACLE_SIGNAL_LAYER_FULL_LIVE_EXECUTION_READY"
    )
    assert receipt["operator_gate"]["real_external_connectivity_authorized"] is True
    assert receipt["operator_gate"]["live_data_flows_authorized"] is True
    assert holler["valid_for_hollersports_live_batch_processing"] is True
    assert holler["valid_for_outcome_recording"] is False
    assert hook["valid_for_external_oracle_calls"] is True
    assert hook["valid_for_notion_writeback"] is False
    _assert_canonical_hash(full_live)
    _assert_canonical_hash(holler)
    _assert_canonical_hash(hook)
    _assert_canonical_hash(receipt)


def test_oracle_full_live_run_control_records_receipt_first_controls() -> None:
    packets = _build_packets()
    run_control = packets["full_live_run_control"]
    holler = packets["holler_full_live_run_control"]
    hook = packets["full_live_run_control_hook"]
    receipt = packets["full_live_run_control_receipt"]

    assert run_control["run_control_status"] == "ORACLE_FULL_LIVE_RUN_CONTROL_READY"
    assert run_control["operator_gate"]["receipt_required_before_each_run"] is True
    assert run_control["valid_for_external_oracle_calls"] is True
    assert run_control["valid_for_live_signal_ingestion"] is True
    assert run_control["valid_for_autonomous_outcome_recording"] is False
    assert run_control["valid_for_mcp_exposure"] is False
    assert run_control["authority_locks"]["execution_authority"] is True
    assert run_control["authority_locks"]["autonomous_outcome_recording"] is False
    assert run_control["governance_controls"]["secret_material_embedded"] is False
    assert receipt["receipt_status"] == "ORACLE_FULL_LIVE_RUN_CONTROL_READY"
    assert receipt["valid_for_github_writeback"] is False
    assert receipt["valid_for_notion_writeback"] is False
    assert holler["valid_for_hollersports_live_batch_processing"] is True
    assert holler["valid_for_outcome_recording"] is False
    assert hook["valid_for_external_oracle_calls"] is True
    assert hook["valid_for_notion_writeback"] is False
    _assert_canonical_hash(run_control)
    _assert_canonical_hash(holler)
    _assert_canonical_hash(hook)
    _assert_canonical_hash(receipt)


def test_oracle_full_live_runtime_command_records_operator_command_manifest() -> None:
    packets = _build_packets()
    runtime_command = packets["full_live_runtime_command"]
    holler = packets["holler_full_live_runtime_command"]
    hook = packets["full_live_runtime_command_hook"]
    receipt = packets["full_live_runtime_command_receipt"]

    assert runtime_command["runtime_command_status"] == (
        "ORACLE_FULL_LIVE_RUNTIME_COMMAND_READY"
    )
    assert runtime_command["operator_monitoring_gate"]["operator_console_required"] is True
    assert runtime_command["valid_for_external_oracle_calls"] is True
    assert runtime_command["valid_for_live_signal_ingestion"] is True
    assert runtime_command["valid_for_autonomous_outcome_recording"] is False
    assert runtime_command["valid_for_mcp_exposure"] is False
    assert runtime_command["authority_locks"]["execution_authority"] is True
    assert runtime_command["authority_locks"]["notion_writeback"] is False
    assert all(
        command["secret_material_embedded"] is False
        for command in runtime_command["runtime_command_manifest"]
    )
    assert receipt["receipt_status"] == "ORACLE_FULL_LIVE_RUNTIME_COMMAND_READY"
    assert receipt["valid_for_github_writeback"] is False
    assert receipt["valid_for_notion_writeback"] is False
    assert holler["valid_for_hollersports_live_batch_processing"] is True
    assert holler["valid_for_outcome_recording"] is False
    assert hook["valid_for_external_oracle_calls"] is True
    assert hook["valid_for_notion_writeback"] is False
    _assert_canonical_hash(runtime_command)
    _assert_canonical_hash(holler)
    _assert_canonical_hash(hook)
    _assert_canonical_hash(receipt)


def test_oracle_full_live_runtime_preflight_records_env_gate() -> None:
    packets = _build_packets()
    preflight = packets["full_live_runtime_preflight"]
    holler = packets["holler_full_live_runtime_preflight"]
    hook = packets["full_live_runtime_preflight_hook"]
    receipt = packets["full_live_runtime_preflight_receipt"]

    assert preflight["preflight_status"] == (
        "ORACLE_FULL_LIVE_RUNTIME_PREFLIGHT_READY"
    )
    assert all(
        check["check_status"] == "ENV_PRESENT_VALUE_REDACTED"
        for check in preflight["endpoint_environment_checks"]
    )
    assert all(
        check["secret_material_embedded"] is False
        for check in preflight["endpoint_environment_checks"]
    )
    assert preflight["runtime_command_scope"]["external_call_count"] == 0
    assert preflight["runtime_command_scope"]["live_ingestion_count"] == 0
    assert preflight["valid_for_external_oracle_calls"] is True
    assert preflight["valid_for_mcp_exposure"] is False
    assert preflight["authority_locks"]["execution_authority"] is True
    assert preflight["authority_locks"]["autonomous_outcome_recording"] is False
    assert holler["preflight_status"] == (
        "HOLLER_ORACLE_FULL_LIVE_RUNTIME_PREFLIGHT_READY"
    )
    assert holler["external_calls_made"] == 0
    assert receipt["receipt_status"] == (
        "ORACLE_FULL_LIVE_RUNTIME_PREFLIGHT_READY"
    )
    assert receipt["valid_for_notion_writeback"] is False
    assert hook["external_calls_made"] == 0
    assert hook["valid_for_notion_writeback"] is False
    _assert_canonical_hash(preflight)
    _assert_canonical_hash(holler)
    _assert_canonical_hash(hook)
    _assert_canonical_hash(receipt)


def test_oracle_full_live_endpoint_env_intake_records_redacted_operator_steps() -> None:
    packets = _build_packets()
    intake = packets["full_live_endpoint_env_intake"]
    hook = packets["full_live_endpoint_env_intake_hook"]
    receipt = packets["full_live_endpoint_env_intake_receipt"]

    assert intake["intake_status"] == "ORACLE_FULL_LIVE_ENDPOINT_ENV_INTAKE_READY"
    assert intake["stores_endpoint_values"] is False
    assert intake["external_calls_made"] == 0
    assert intake["valid_for_external_oracle_calls"] is False
    assert intake["valid_for_live_signal_ingestion"] is False
    assert all(
        requirement["endpoint_value_recorded"] is False
        for requirement in intake["endpoint_env_requirements"]
    )
    assert all(
        requirement["secret_material_embedded"] is False
        for requirement in intake["endpoint_env_requirements"]
    )
    assert {
        requirement["endpoint_env_var"]
        for requirement in intake["endpoint_env_requirements"]
    } == {"ORACLE_SIGNAL_ENDPOINT_URL", "HOLLERSPORTS_BATCH_ENDPOINT_URL"}
    assert intake["rerun_plan"]["continue_to_runtime_command_only_after_ready"] is True
    assert receipt["receipt_status"] == "ORACLE_FULL_LIVE_ENDPOINT_ENV_INTAKE_READY"
    assert receipt["stores_endpoint_values"] is False
    assert receipt["valid_for_external_oracle_calls"] is False
    assert receipt["valid_for_notion_writeback"] is False
    assert hook["stores_endpoint_values"] is False
    assert hook["external_calls_made"] == 0
    assert hook["valid_for_notion_writeback"] is False
    _assert_canonical_hash(intake)
    _assert_canonical_hash(hook)
    _assert_canonical_hash(receipt)


def test_oracle_full_live_runtime_execution_attempt_fails_closed_by_default() -> None:
    packets = _build_packets()
    attempt = packets["full_live_runtime_execution_attempt"]
    hook = packets["full_live_runtime_execution_attempt_hook"]
    receipt = packets["full_live_runtime_execution_attempt_receipt"]

    assert attempt["attempt_status"] == (
        "ORACLE_FULL_LIVE_RUNTIME_EXECUTION_ATTEMPT_BLOCKED"
    )
    assert attempt["execution_request"]["execute_requested"] is False
    assert attempt["execution_request"]["preflight_ready"] is True
    assert attempt["execution_request"]["endpoint_environment_ready"] is True
    assert attempt["execution_request"]["operator_attestation_ready"] is False
    assert attempt["execution_request"]["execution_allowed"] is False
    assert attempt["execution_summary"]["external_call_count"] == 0
    assert attempt["execution_summary"]["live_ingestion_count"] == 0
    assert attempt["execution_summary"]["payload_record_count"] == 0
    assert attempt["execution_summary"]["persistent_write_count"] == 0
    assert attempt["execution_summary"]["response_payload_recorded"] is False
    assert attempt["authority_locks"]["execution_authority"] is False
    assert attempt["authority_locks"]["actual_external_oracle_calls"] is False
    assert attempt["authority_locks"]["actual_live_data_ingestion"] is False
    assert attempt["authority_locks"]["persistent_production_runtime_activation"] is False
    assert attempt["valid_for_external_oracle_calls"] is False
    assert attempt["valid_for_live_signal_ingestion"] is False
    assert attempt["valid_for_payload_persistence"] is False
    assert receipt["receipt_status"] == (
        "ORACLE_FULL_LIVE_RUNTIME_EXECUTION_ATTEMPT_BLOCKED"
    )
    assert receipt["valid_for_external_oracle_calls"] is False
    assert receipt["valid_for_payload_persistence"] is False
    assert hook["external_call_count"] == 0
    assert hook["valid_for_external_oracle_calls"] is False
    _assert_canonical_hash(attempt)
    _assert_canonical_hash(hook)
    _assert_canonical_hash(receipt)


def test_oracle_schema_validator_accepts_all_generated_packets() -> None:
    packets = _build_packets()
    results = packets["full_live_runtime_execution_attempt_validation_results"]
    assert set(results) == {
        "oracle_signal_envelope",
        "oracle_holler_intake",
        "oracle_calibration_report",
        "oracle_adversarial_fixture",
        "oracle_schema_registry",
        "oracle_ingest_wiring",
        "oracle_shadow_dryrun",
        "oracle_measurement_readiness",
        "oracle_shadow_measurement",
        "oracle_measurement_proposal",
        "oracle_measurement_authorization_proposal",
        "oracle_measurement_authorization_decision_review_candidate",
        "oracle_authorization_decision_record",
        "oracle_live_wiring_preparation",
        "oracle_production_activation_ready",
        "oracle_full_live_execution",
        "oracle_full_live_run_control",
        "oracle_full_live_runtime_command",
        "oracle_full_live_runtime_preflight",
        "oracle_full_live_endpoint_env_intake",
        "oracle_full_live_runtime_execution",
    }
    for result in results.values():
        assert result["validation_status"] == "VALID_ADVISORY_ONLY"
        assert result["schema_errors"] == []
        assert result["valid_for_live_ingest"] is False
        assert result["valid_for_schema_writeback"] is False
        _assert_canonical_hash(result)
    assert packets["holler_validation"]["validation_status"] == "VALID_ADVISORY_ONLY"
    assert packets["validation_receipt"]["receipt_status"] == (
        "ORACLE_SCHEMA_VALIDATION_READY_ADVISORY_ONLY"
    )
    assert packets["validation_receipt"]["valid_for_live_validation"] is False
    _assert_canonical_hash(packets["validation_receipt"])
    assert packets["dryrun_validation_receipt"]["receipt_status"] == (
        "ORACLE_SCHEMA_VALIDATION_READY_ADVISORY_ONLY"
    )
    _assert_canonical_hash(packets["dryrun_validation_receipt"])
    assert packets["readiness_validation_receipt"]["receipt_status"] == (
        "ORACLE_SCHEMA_VALIDATION_READY_ADVISORY_ONLY"
    )
    _assert_canonical_hash(packets["readiness_validation_receipt"])
    assert packets["shadow_measurement_validation_receipt"]["receipt_status"] == (
        "ORACLE_SCHEMA_VALIDATION_READY_ADVISORY_ONLY"
    )
    _assert_canonical_hash(packets["shadow_measurement_validation_receipt"])
    assert packets["wiring"]["wiring_status"] == "ORACLE_INGEST_WIRING_READY_ADVISORY_ONLY"
    assert packets["wiring"]["shadow_replay_harness"]["valid_for_execution"] is False
    assert packets["holler_wiring"]["valid_for_live_ingest"] is False
    assert packets["wiring_receipt"]["receipt_status"] == (
        "ORACLE_INGEST_WIRING_READY_ADVISORY_ONLY"
    )
    _assert_canonical_hash(packets["wiring_receipt"])
    assert packets["dryrun"]["dryrun_status"] == (
        "ORACLE_SHADOW_DRYRUN_READY_ADVISORY_ONLY"
    )
    assert packets["dryrun"]["operator_decision_record_template"][
        "records_live_execution"
    ] is False
    assert packets["holler_dryrun"]["valid_for_shadow_replay_execution"] is False
    assert packets["dryrun_receipt"]["receipt_status"] == (
        "ORACLE_SHADOW_DRYRUN_READY_ADVISORY_ONLY"
    )
    _assert_canonical_hash(packets["dryrun_receipt"])
    assert packets["operator_intake"]["valid_for_measurement_authorization"] is False
    assert packets["readiness"]["readiness_status"] == (
        "ORACLE_MEASUREMENT_READINESS_READY_ADVISORY_ONLY"
    )
    assert packets["readiness"]["decision_intake_requirements"][
        "records_operator_attestation"
    ] is False
    assert packets["holler_readiness"]["valid_for_live_measurement"] is False
    assert packets["readiness_receipt"]["receipt_status"] == (
        "ORACLE_MEASUREMENT_READINESS_READY_ADVISORY_ONLY"
    )
    assert packets["readiness_receipt"]["valid_for_measurement_execution"] is False
    _assert_canonical_hash(packets["readiness_receipt"])
    assert packets["shadow_measurement"]["measurement_status"] == (
        "ORACLE_SHADOW_MEASUREMENT_READY_ADVISORY_ONLY"
    )
    assert packets["shadow_measurement"]["operator_review_template"][
        "authorizes_measurement"
    ] is False
    assert packets["holler_shadow_measurement"][
        "valid_for_measurement_execution"
    ] is False
    assert packets["holler_shadow_measurement"][
        "valid_for_external_oracle_calls"
    ] is False
    assert packets["shadow_measurement_hook"][
        "valid_for_measurement_execution"
    ] is False
    assert packets["shadow_measurement_receipt"]["receipt_status"] == (
        "ORACLE_SHADOW_MEASUREMENT_READY_ADVISORY_ONLY"
    )
    assert packets["shadow_measurement_receipt"][
        "valid_for_outcome_recording"
    ] is False
    assert packets["shadow_measurement_receipt"][
        "valid_for_external_oracle_calls"
    ] is False
    _assert_canonical_hash(packets["shadow_measurement"])
    _assert_canonical_hash(packets["shadow_measurement_receipt"])
    assert packets["measurement_proposal"]["proposal_status"] == (
        "ORACLE_MEASUREMENT_PROPOSAL_READY_ADVISORY_ONLY"
    )
    assert packets["measurement_proposal"]["proposal_scope"][
        "authorizes_measurement"
    ] is False
    assert packets["measurement_proposal"]["operator_decision_intake_refinement"][
        "records_operator_attestation"
    ] is False
    assert packets["holler_measurement_proposal"][
        "valid_for_measurement_authorization"
    ] is False
    assert packets["measurement_proposal_hook"][
        "valid_for_measurement_authorization"
    ] is False
    assert packets["measurement_proposal_receipt"]["receipt_status"] == (
        "ORACLE_MEASUREMENT_PROPOSAL_READY_ADVISORY_ONLY"
    )
    assert packets["measurement_proposal_receipt"][
        "valid_for_measurement_authorization"
    ] is False
    assert packets["measurement_proposal_receipt"][
        "valid_for_operator_attestation_recording"
    ] is False
    _assert_canonical_hash(packets["measurement_proposal"])
    _assert_canonical_hash(packets["measurement_proposal_receipt"])
    assert packets["authorization_proposal"]["proposal_status"] == (
        "ORACLE_MEASUREMENT_AUTHORIZATION_PROPOSAL_READY_ADVISORY_ONLY"
    )
    assert packets["authorization_proposal"]["authorization_scope"][
        "grants_measurement_authorization"
    ] is False
    assert packets["authorization_proposal"]["operator_gate_template"][
        "authorizes_measurement"
    ] is False
    assert packets["holler_authorization_proposal"][
        "valid_for_measurement_authorization"
    ] is False
    assert packets["authorization_hook"][
        "valid_for_measurement_authorization"
    ] is False
    assert packets["authorization_receipt"]["receipt_status"] == (
        "ORACLE_MEASUREMENT_AUTHORIZATION_PROPOSAL_READY_ADVISORY_ONLY"
    )
    assert packets["authorization_receipt"][
        "valid_for_measurement_authorization"
    ] is False
    assert packets["authorization_receipt"][
        "valid_for_operator_attestation_recording"
    ] is False
    _assert_canonical_hash(packets["authorization_proposal"])
    _assert_canonical_hash(packets["authorization_receipt"])
    assert packets["decision_review_candidate"]["candidate_status"] == (
        "ORACLE_MEASUREMENT_AUTHORIZATION_DECISION_REVIEW_CANDIDATE_READY_ADVISORY_ONLY"
    )
    assert packets["decision_review_candidate"]["decision_review_scope"][
        "records_authorization_decision"
    ] is False
    assert packets["decision_review_candidate"]["decision_review_scope"][
        "authorizes_measurement"
    ] is False
    assert packets["decision_review_candidate"]["operator_review_template"][
        "records_operator_attestation"
    ] is False
    assert packets["decision_review_hook"][
        "valid_for_authorization_decision_recording"
    ] is False
    assert packets["decision_review_receipt"]["receipt_status"] == (
        "ORACLE_MEASUREMENT_AUTHORIZATION_DECISION_REVIEW_CANDIDATE_READY_ADVISORY_ONLY"
    )
    assert packets["decision_review_receipt"][
        "valid_for_authorization_decision_recording"
    ] is False
    assert packets["decision_review_receipt"][
        "valid_for_measurement_authorization"
    ] is False
    _assert_canonical_hash(packets["decision_review_candidate"])
    _assert_canonical_hash(packets["decision_review_receipt"])
    assert packets["authorization_decision_record"]["record_status"] == (
        "ORACLE_AUTHORIZATION_DECISION_RECORD_TEMPLATE_READY_ADVISORY_ONLY"
    )
    assert packets["authorization_decision_record"]["decision_record_template"][
        "records_authorization_decision"
    ] is False
    assert packets["authorization_decision_record"]["decision_record_template"][
        "records_operator_attestation"
    ] is False
    assert packets["authorization_decision_record"]["decision_record_template"][
        "authorizes_measurement"
    ] is False
    assert packets["authorization_decision_hook"][
        "valid_for_authorization_decision_recording"
    ] is False
    assert packets["authorization_decision_receipt"]["receipt_status"] == (
        "ORACLE_AUTHORIZATION_DECISION_RECORD_TEMPLATE_READY_ADVISORY_ONLY"
    )
    assert packets["authorization_decision_receipt"][
        "valid_for_authorization_decision_recording"
    ] is False
    assert packets["authorization_decision_receipt"][
        "valid_for_measurement_authorization"
    ] is False
    _assert_canonical_hash(packets["authorization_decision_record"])
    _assert_canonical_hash(packets["authorization_decision_receipt"])


def test_oracle_schema_validator_reports_invalid_shadow_fixtures() -> None:
    packets = _build_packets()
    fixture_set = build_oracle_schema_validation_fixture_set(
        valid_packets={
            "oracle_signal_envelope": packets["envelope"],
            "oracle_holler_intake": packets["holler"],
            "oracle_calibration_report": packets["calibration"],
            "oracle_adversarial_fixture": packets["adversarial"],
            "oracle_schema_registry": packets["registry"],
        }
    )
    invalid_holler = fixture_set["invalid_fixtures"][
        "oracle_holler_intake_negative_market_count"
    ]
    result = validate_oracle_packet(
        packet_key="oracle_holler_intake",
        packet=invalid_holler,
        schema_path="contracts/canon/oracle/oracle_holler_intake.v1.schema.json",
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    assert result["validation_status"] == "INVALID_ADVISORY_ONLY"
    assert result["schema_errors"]
    assert result["valid_for_live_ingest"] is False


def test_abx_loop_emits_oracle_schema_validation_receipt(tmp_path: Path) -> None:
    receipt_path = tmp_path / "oracle_schema_validation.latest.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/abx_loop.py",
            "--emit-oracle-validation",
            "--oracle-validation-out",
            str(receipt_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(receipt_path) in completed.stdout
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["receipt_status"] == "ORACLE_SCHEMA_VALIDATION_READY_ADVISORY_ONLY"
    assert receipt["validation_summary"]["all_valid"] is True
    assert receipt["valid_for_live_validation"] is False
    _assert_canonical_hash(receipt)


def test_abx_loop_emits_oracle_shadow_dryrun_receipt(tmp_path: Path) -> None:
    receipt_path = tmp_path / "oracle_shadow_dryrun.latest.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/abx_loop.py",
            "--emit-oracle-shadow-dryrun",
            "--validate-oracle-schemas",
            "--oracle-shadow-dryrun-out",
            str(receipt_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(receipt_path) in completed.stdout
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["receipt_status"] == "ORACLE_SHADOW_DRYRUN_READY_ADVISORY_ONLY"
    assert receipt["valid_for_shadow_replay_execution"] is False
    assert receipt["valid_for_oracle_execution"] is False
    _assert_canonical_hash(receipt)


def test_abx_loop_emits_oracle_measurement_readiness_receipt(tmp_path: Path) -> None:
    receipt_path = tmp_path / "oracle_measurement_readiness.latest.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/abx_loop.py",
            "--emit-oracle-measurement-readiness",
            "--validate-oracle-schemas",
            "--oracle-measurement-readiness-out",
            str(receipt_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(receipt_path) in completed.stdout
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["receipt_status"] == (
        "ORACLE_MEASUREMENT_READINESS_READY_ADVISORY_ONLY"
    )
    assert receipt["valid_for_measurement_execution"] is False
    assert receipt["valid_for_operator_attestation_recording"] is False
    _assert_canonical_hash(receipt)


def test_abx_loop_emits_oracle_shadow_measurement_receipt(tmp_path: Path) -> None:
    receipt_path = tmp_path / "oracle_shadow_measurement.latest.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/abx_loop.py",
            "--emit-oracle-shadow-measurement",
            "--validate-oracle-schemas",
            "--oracle-shadow-measurement-out",
            str(receipt_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(receipt_path) in completed.stdout
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["receipt_status"] == "ORACLE_SHADOW_MEASUREMENT_READY_ADVISORY_ONLY"
    assert receipt["valid_for_measurement_execution"] is False
    assert receipt["valid_for_outcome_recording"] is False
    assert receipt["valid_for_external_oracle_calls"] is False
    _assert_canonical_hash(receipt)


def test_abx_loop_emits_oracle_measurement_proposal_receipt(tmp_path: Path) -> None:
    receipt_path = tmp_path / "oracle_measurement_proposal.latest.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/abx_loop.py",
            "--emit-oracle-measurement-proposal",
            "--validate-oracle-schemas",
            "--oracle-measurement-proposal-out",
            str(receipt_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(receipt_path) in completed.stdout
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["receipt_status"] == "ORACLE_MEASUREMENT_PROPOSAL_READY_ADVISORY_ONLY"
    assert receipt["valid_for_measurement_authorization"] is False
    assert receipt["valid_for_measurement_execution"] is False
    assert receipt["valid_for_operator_attestation_recording"] is False
    _assert_canonical_hash(receipt)


def test_abx_loop_emits_oracle_measurement_authorization_proposal_receipt(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "oracle_measurement_authorization_proposal.latest.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/abx_loop.py",
            "--emit-oracle-measurement-authorization-proposal",
            "--validate-oracle-schemas",
            "--oracle-measurement-authorization-proposal-out",
            str(receipt_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(receipt_path) in completed.stdout
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["receipt_status"] == (
        "ORACLE_MEASUREMENT_AUTHORIZATION_PROPOSAL_READY_ADVISORY_ONLY"
    )
    assert receipt["valid_for_measurement_authorization"] is False
    assert receipt["valid_for_measurement_execution"] is False
    assert receipt["valid_for_operator_attestation_recording"] is False
    _assert_canonical_hash(receipt)


def test_abx_loop_emits_oracle_measurement_authorization_decision_review_candidate_receipt(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "oracle_measurement_authorization_decision_review.latest.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/abx_loop.py",
            "--emit-oracle-measurement-authorization-decision-review-candidate",
            "--validate-oracle-schemas",
            "--oracle-measurement-authorization-decision-review-candidate-out",
            str(receipt_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(receipt_path) in completed.stdout
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["receipt_status"] == (
        "ORACLE_MEASUREMENT_AUTHORIZATION_DECISION_REVIEW_CANDIDATE_READY_ADVISORY_ONLY"
    )
    assert receipt["valid_for_authorization_decision_recording"] is False
    assert receipt["valid_for_measurement_authorization"] is False
    assert receipt["valid_for_measurement_execution"] is False
    assert receipt["valid_for_operator_attestation_recording"] is False
    _assert_canonical_hash(receipt)


def test_abx_loop_emits_oracle_layer_complete_receipt(tmp_path: Path) -> None:
    receipt_path = tmp_path / "oracle_signal_layer_complete.latest.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/abx_loop.py",
            "--emit-oracle-shadow-measurement",
            "--emit-oracle-layer-complete",
            "--validate-oracle-schemas",
            "--oracle-completion-out",
            str(receipt_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(receipt_path) in completed.stdout
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["receipt_status"] == "ORACLE_SIGNAL_LAYER_ADVISORY_COMPLETE"
    assert "oracle_authorization_decision_record_receipt" in receipt["surface_hashes"]
    assert receipt["valid_for_execution"] is False
    assert receipt["valid_for_live_ingest"] is False
    assert receipt["valid_for_notion_writeback"] is False
    _assert_canonical_hash(receipt)


def test_abx_loop_emits_oracle_live_wiring_preparation_receipt(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "oracle_live_wiring_preparation.latest.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/abx_loop.py",
            "--emit-oracle-live-wiring-preparation",
            "--validate-oracle-schemas",
            "--oracle-live-wiring-preparation-out",
            str(receipt_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(receipt_path) in completed.stdout
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["receipt_status"] == (
        "ORACLE_LIVE_WIRING_PREPARATION_READY_ADVISORY_ONLY"
    )
    assert receipt["valid_for_live_signal_ingest"] is False
    assert receipt["valid_for_external_oracle_calls"] is False
    assert receipt["valid_for_scheduler_mutation"] is False
    assert receipt["valid_for_queue_mutation"] is False
    assert receipt["valid_for_mcp_exposure"] is False
    assert receipt["valid_for_production_activation"] is False
    _assert_canonical_hash(receipt)


def test_abx_loop_emits_oracle_production_activation_ready_receipt(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "oracle_production_activation_ready.latest.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/abx_loop.py",
            "--emit-oracle-production-activation-ready",
            "--validate-oracle-schemas",
            "--oracle-production-activation-ready-out",
            str(receipt_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(receipt_path) in completed.stdout
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["receipt_status"] == (
        "ORACLE_SIGNAL_LAYER_PRODUCTION_ACTIVATION_READY"
    )
    assert receipt["valid_for_production_code_generation"] is True
    assert receipt["valid_for_shadow_dryrun_execution"] is True
    assert receipt["valid_for_actual_external_oracle_calls"] is False
    assert receipt["valid_for_actual_live_data_ingestion"] is False
    assert receipt["valid_for_persistent_production_runtime_activation"] is False
    assert receipt["valid_for_mcp_exposure"] is False
    assert receipt["valid_for_unreviewed_production_deployment"] is False
    _assert_canonical_hash(receipt)


def test_abx_loop_emits_oracle_full_live_execution_receipt(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "oracle_full_live_execution.latest.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/abx_loop.py",
            "--emit-oracle-full-live",
            "--validate-oracle-schemas",
            "--oracle-full-live-out",
            str(receipt_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(receipt_path) in completed.stdout
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["receipt_status"] == (
        "ORACLE_SIGNAL_LAYER_FULL_LIVE_EXECUTION_READY"
    )
    assert receipt["operator_gate"]["real_external_connectivity_authorized"] is True
    assert receipt["operator_gate"]["live_data_flows_authorized"] is True
    assert receipt["operator_gate"]["receipts_required_before_execution"] is True
    assert receipt["valid_for_external_oracle_calls"] is True
    assert receipt["valid_for_live_signal_ingestion"] is True
    assert receipt["valid_for_scheduler_queue_runtime"] is True
    assert receipt["valid_for_mcp_exposure"] is False
    assert receipt["valid_for_unreviewed_production_deployment"] is False
    assert receipt["valid_for_github_writeback"] is False
    assert receipt["valid_for_notion_writeback"] is False
    _assert_canonical_hash(receipt)


def test_abx_loop_emits_oracle_full_live_run_control_receipt(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "oracle_full_live_run_control.latest.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/abx_loop.py",
            "--emit-oracle-full-live-run-control",
            "--validate-oracle-schemas",
            "--oracle-full-live-run-control-out",
            str(receipt_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(receipt_path) in completed.stdout
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["receipt_status"] == "ORACLE_FULL_LIVE_RUN_CONTROL_READY"
    assert receipt["valid_for_external_oracle_calls"] is True
    assert receipt["valid_for_live_signal_ingestion"] is True
    assert receipt["valid_for_scheduler_queue_runtime"] is True
    assert receipt["valid_for_autonomous_outcome_recording"] is False
    assert receipt["valid_for_mcp_exposure"] is False
    assert receipt["valid_for_unreviewed_production_deployment"] is False
    assert receipt["valid_for_github_writeback"] is False
    assert receipt["valid_for_notion_writeback"] is False
    _assert_canonical_hash(receipt)


def test_abx_loop_emits_oracle_full_live_runtime_command_receipt(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "oracle_full_live_runtime_command.latest.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/abx_loop.py",
            "--emit-oracle-full-live-runtime-command",
            "--validate-oracle-schemas",
            "--oracle-full-live-runtime-command-out",
            str(receipt_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(receipt_path) in completed.stdout
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["receipt_status"] == "ORACLE_FULL_LIVE_RUNTIME_COMMAND_READY"
    assert receipt["valid_for_external_oracle_calls"] is True
    assert receipt["valid_for_live_signal_ingestion"] is True
    assert receipt["valid_for_scheduler_queue_runtime"] is True
    assert receipt["valid_for_autonomous_outcome_recording"] is False
    assert receipt["valid_for_mcp_exposure"] is False
    assert receipt["valid_for_unreviewed_production_deployment"] is False
    assert receipt["valid_for_github_writeback"] is False
    assert receipt["valid_for_notion_writeback"] is False
    _assert_canonical_hash(receipt)


def test_abx_loop_emits_oracle_full_live_runtime_preflight_receipt(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "oracle_full_live_runtime_preflight.latest.json"
    validation_path = tmp_path / "oracle_schema_validation.latest.json"
    subprocess_env = dict(os.environ)
    subprocess_env.pop("ORACLE_SIGNAL_ENDPOINT_URL", None)
    subprocess_env.pop("HOLLERSPORTS_BATCH_ENDPOINT_URL", None)
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/abx_loop.py",
            "--emit-oracle-full-live-runtime-preflight",
            "--validate-oracle-schemas",
            "--oracle-full-live-runtime-preflight-out",
            str(receipt_path),
            "--oracle-validation-out",
            str(validation_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
        env=subprocess_env,
    )
    assert str(receipt_path) in completed.stdout
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["receipt_status"] == (
        "ORACLE_FULL_LIVE_RUNTIME_PREFLIGHT_BLOCKED_ENV_MISSING"
    )
    assert receipt["missing_endpoint_env_vars"] == [
        "ORACLE_SIGNAL_ENDPOINT_URL",
        "HOLLERSPORTS_BATCH_ENDPOINT_URL",
    ]
    assert receipt["valid_for_external_oracle_calls"] is False
    assert receipt["valid_for_live_signal_ingestion"] is False
    assert receipt["valid_for_scheduler_queue_runtime"] is False
    assert receipt["valid_for_mcp_exposure"] is False
    assert receipt["valid_for_unreviewed_production_deployment"] is False
    assert receipt["valid_for_github_writeback"] is False
    assert receipt["valid_for_notion_writeback"] is False
    _assert_canonical_hash(receipt)
    validation_receipt = json.loads(validation_path.read_text(encoding="utf-8"))
    assert "oracle_full_live_endpoint_env_intake" in (
        validation_receipt["validation_result_hashes"]
    )
    assert validation_receipt["validation_summary"]["valid_result_count"] == 21
    _assert_canonical_hash(validation_receipt)


def test_abx_loop_redacts_present_endpoint_env_values(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "oracle_full_live_runtime_preflight_ready.latest.json"
    validation_path = tmp_path / "oracle_schema_validation_ready.latest.json"
    oracle_endpoint = "https://redaction-test.invalid/oracle-secret-token"
    holler_endpoint = "https://redaction-test.invalid/holler-secret-token"
    subprocess_env = {
        **os.environ,
        "ORACLE_SIGNAL_ENDPOINT_URL": oracle_endpoint,
        "HOLLERSPORTS_BATCH_ENDPOINT_URL": holler_endpoint,
    }
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/abx_loop.py",
            "--emit-oracle-full-live-runtime-preflight",
            "--validate-oracle-schemas",
            "--oracle-full-live-runtime-preflight-out",
            str(receipt_path),
            "--oracle-validation-out",
            str(validation_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
        env=subprocess_env,
    )
    receipt_text = receipt_path.read_text(encoding="utf-8")
    assert oracle_endpoint not in completed.stdout
    assert holler_endpoint not in completed.stdout
    assert oracle_endpoint not in receipt_text
    assert holler_endpoint not in receipt_text
    receipt = json.loads(receipt_text)
    assert receipt["receipt_status"] == "ORACLE_FULL_LIVE_RUNTIME_PREFLIGHT_READY"
    assert receipt["missing_endpoint_env_vars"] == []
    assert receipt["valid_for_external_oracle_calls"] is True
    assert receipt["valid_for_live_signal_ingestion"] is True
    assert receipt["valid_for_scheduler_queue_runtime"] is True
    assert receipt["valid_for_mcp_exposure"] is False
    assert receipt["valid_for_github_writeback"] is False
    assert receipt["valid_for_notion_writeback"] is False
    _assert_canonical_hash(receipt)
    validation_receipt = json.loads(validation_path.read_text(encoding="utf-8"))
    assert validation_receipt["validation_summary"]["valid_result_count"] == 21
    _assert_canonical_hash(validation_receipt)


def test_abx_loop_emits_oracle_full_live_endpoint_env_intake_receipt(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "oracle_full_live_endpoint_env_intake.latest.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/abx_loop.py",
            "--emit-oracle-full-live-endpoint-env-intake",
            "--validate-oracle-schemas",
            "--oracle-full-live-endpoint-env-intake-out",
            str(receipt_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(receipt_path) in completed.stdout
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["receipt_status"] == "ORACLE_FULL_LIVE_ENDPOINT_ENV_INTAKE_READY"
    assert receipt["stores_endpoint_values"] is False
    assert receipt["external_calls_made"] == 0
    assert receipt["valid_for_external_oracle_calls"] is False
    assert receipt["valid_for_live_signal_ingestion"] is False
    assert receipt["valid_for_scheduler_queue_runtime"] is False
    assert receipt["valid_for_mcp_exposure"] is False
    assert receipt["valid_for_unreviewed_production_deployment"] is False
    assert receipt["valid_for_github_writeback"] is False
    assert receipt["valid_for_notion_writeback"] is False
    _assert_canonical_hash(receipt)


def test_abx_loop_emits_oracle_full_live_runtime_execution_attempt_receipt(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "oracle_full_live_runtime_execution.latest.json"
    validation_path = tmp_path / "oracle_schema_validation_execution.latest.json"
    subprocess_env = dict(os.environ)
    subprocess_env.pop("ORACLE_SIGNAL_ENDPOINT_URL", None)
    subprocess_env.pop("HOLLERSPORTS_BATCH_ENDPOINT_URL", None)
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/abx_loop.py",
            "--emit-oracle-full-live-runtime-execution",
            "--validate-oracle-schemas",
            "--oracle-full-live-runtime-execution-out",
            str(receipt_path),
            "--oracle-validation-out",
            str(validation_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
        env=subprocess_env,
    )
    assert str(receipt_path) in completed.stdout
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["receipt_status"] == (
        "ORACLE_FULL_LIVE_RUNTIME_EXECUTION_ATTEMPT_BLOCKED"
    )
    assert receipt["execution_summary"]["external_call_count"] == 0
    assert receipt["execution_summary"]["live_ingestion_count"] == 0
    assert receipt["authority_locks"]["execution_authority"] is False
    assert receipt["authority_locks"]["actual_external_oracle_calls"] is False
    assert receipt["valid_for_external_oracle_calls"] is False
    assert receipt["valid_for_live_signal_ingestion"] is False
    assert receipt["valid_for_payload_persistence"] is False
    _assert_canonical_hash(receipt)
    validation_receipt = json.loads(validation_path.read_text(encoding="utf-8"))
    assert "oracle_full_live_runtime_execution" in (
        validation_receipt["validation_result_hashes"]
    )
    assert "oracle_sandbox_probe_gate_proposal" in (
        validation_receipt["validation_result_hashes"]
    )
    assert validation_receipt["validation_summary"]["valid_result_count"] == 25
    _assert_canonical_hash(validation_receipt)


def test_oracle_persistent_execution_secret_vault_plan_packet() -> None:
    packets = _build_packets()
    plan = build_oracle_persistent_execution_secret_vault_plan(
        timestamp=TIMESTAMP,
        oracle_full_live_endpoint_env_intake_receipt=packets[
            "full_live_endpoint_env_intake_receipt"
        ],
        oracle_full_live_runtime_preflight_receipt=packets[
            "full_live_runtime_preflight_receipt"
        ],
        oracle_full_live_runtime_execution_attempt_receipt=packets[
            "full_live_runtime_execution_attempt_receipt"
        ],
    )
    validation = validate_oracle_packet(
        packet_key="oracle_persistent_execution_secret_vault_plan",
        packet=plan,
        schema_path=SCHEMA_BY_PACKET_KEY[
            "oracle_persistent_execution_secret_vault_plan"
        ],
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    hook = build_oracle_persistent_execution_secret_vault_plan_observability_hook(
        timestamp=TIMESTAMP,
        persistent_execution_secret_vault_plan_receipt_hash="7" * 64,
        persistent_execution_secret_vault_plan_schema_path=(
            "contracts/canon/oracle/"
            "oracle_persistent_execution_secret_vault_plan.v1.schema.json"
        ),
    )
    receipt = build_oracle_persistent_execution_secret_vault_plan_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_persistent_execution_secret_vault_plan=plan,
        observability_hook=hook,
    )

    assert (
        "contracts/canon/oracle/"
        "oracle_persistent_execution_secret_vault_plan.v1.schema.json"
    ) in ORACLE_CANON_EXTENSION_SCHEMA_PATHS
    assert "oracle_persistent_execution_secret_vault_plan" in SCHEMA_BY_PACKET_KEY
    assert plan["plan_status"] == (
        "ORACLE_PERSISTENT_EXECUTION_SECRET_VAULT_PLAN_READY_ADVISORY_ONLY"
    )
    assert len(plan["secret_handling_requirements"]) >= 3
    assert plan["persistent_execution_boundaries"][
        "secret_material_allowed_in_repo"
    ] is False
    assert plan["persistent_execution_boundaries"]["external_calls_allowed"] is False
    assert plan["runtime_receipt_gate"]["sandbox_probe_authorized_by_this_packet"] is False
    assert all(value is False for value in plan["authority_locks"].values())
    assert plan["valid_for_external_oracle_calls"] is False
    assert plan["valid_for_secret_material_persistence"] is False
    assert plan["valid_for_payload_persistence"] is False
    assert hook["valid_for_notion_writeback"] is False
    assert hook["authority_locks"]["secret_material_persistence"] is False
    assert receipt["receipt_status"] == (
        "ORACLE_PERSISTENT_EXECUTION_SECRET_VAULT_PLAN_READY_ADVISORY_ONLY"
    )
    assert receipt["issue"]["issue_number"] == 881
    assert validation["validation_status"] == "VALID_ADVISORY_ONLY"
    _assert_canonical_hash(plan)
    _assert_canonical_hash(hook)
    _assert_canonical_hash(receipt)


def test_abx_loop_emits_oracle_persistent_execution_secret_vault_plan_receipt(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "oracle_persistent_execution_secret_vault_plan.latest.json"
    validation_path = tmp_path / "oracle_schema_validation_secret_vault.latest.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/abx_loop.py",
            "--emit-oracle-persistent-execution-secret-vault-plan",
            "--validate-oracle-schemas",
            "--oracle-persistent-execution-secret-vault-plan-out",
            str(receipt_path),
            "--oracle-validation-out",
            str(validation_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(receipt_path) in completed.stdout
    receipt_text = receipt_path.read_text(encoding="utf-8")
    assert "ORACLE_SIGNAL_ENDPOINT_URL=" not in receipt_text
    assert "HOLLERSPORTS_BATCH_ENDPOINT_URL=" not in receipt_text
    receipt = json.loads(receipt_text)
    assert receipt["receipt_status"] == (
        "ORACLE_PERSISTENT_EXECUTION_SECRET_VAULT_PLAN_READY_ADVISORY_ONLY"
    )
    assert all(value is False for value in receipt["authority_locks"].values())
    assert receipt["valid_for_external_oracle_calls"] is False
    assert receipt["valid_for_secret_material_persistence"] is False
    assert receipt["valid_for_payload_persistence"] is False
    _assert_canonical_hash(receipt)
    validation_receipt = json.loads(validation_path.read_text(encoding="utf-8"))
    assert "oracle_persistent_execution_secret_vault_plan" in (
        validation_receipt["validation_result_hashes"]
    )
    assert validation_receipt["validation_summary"]["valid_result_count"] == 23
    _assert_canonical_hash(validation_receipt)


def test_oracle_persistent_sandbox_secret_store_stub_packet() -> None:
    packets = _build_packets()
    plan = build_oracle_persistent_execution_secret_vault_plan(
        timestamp=TIMESTAMP,
        oracle_full_live_endpoint_env_intake_receipt=packets[
            "full_live_endpoint_env_intake_receipt"
        ],
        oracle_full_live_runtime_preflight_receipt=packets[
            "full_live_runtime_preflight_receipt"
        ],
        oracle_full_live_runtime_execution_attempt_receipt=packets[
            "full_live_runtime_execution_attempt_receipt"
        ],
    )
    plan_hook = build_oracle_persistent_execution_secret_vault_plan_observability_hook(
        timestamp=TIMESTAMP,
        persistent_execution_secret_vault_plan_receipt_hash="7" * 64,
        persistent_execution_secret_vault_plan_schema_path=(
            "contracts/canon/oracle/"
            "oracle_persistent_execution_secret_vault_plan.v1.schema.json"
        ),
    )
    plan_receipt = build_oracle_persistent_execution_secret_vault_plan_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_persistent_execution_secret_vault_plan=plan,
        observability_hook=plan_hook,
    )
    stub = build_oracle_persistent_sandbox_secret_store_stub(
        timestamp=TIMESTAMP,
        oracle_persistent_execution_secret_vault_plan_receipt=plan_receipt,
    )
    validation = validate_oracle_packet(
        packet_key="oracle_persistent_sandbox_secret_store_stub",
        packet=stub,
        schema_path=SCHEMA_BY_PACKET_KEY[
            "oracle_persistent_sandbox_secret_store_stub"
        ],
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    hook = build_oracle_persistent_sandbox_secret_store_stub_observability_hook(
        timestamp=TIMESTAMP,
        persistent_sandbox_secret_store_stub_receipt_hash="8" * 64,
        persistent_sandbox_secret_store_stub_schema_path=(
            "contracts/canon/oracle/"
            "oracle_persistent_sandbox_secret_store_stub.v1.schema.json"
        ),
    )
    receipt = build_oracle_persistent_sandbox_secret_store_stub_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_persistent_sandbox_secret_store_stub=stub,
        observability_hook=hook,
    )

    assert (
        "contracts/canon/oracle/"
        "oracle_persistent_sandbox_secret_store_stub.v1.schema.json"
    ) in ORACLE_CANON_EXTENSION_SCHEMA_PATHS
    assert "oracle_persistent_sandbox_secret_store_stub" in SCHEMA_BY_PACKET_KEY
    assert stub["stub_status"] == (
        "ORACLE_PERSISTENT_SANDBOX_SECRET_STORE_STUB_READY_ADVISORY_ONLY"
    )
    assert len(stub["ignored_env_examples"]) >= 3
    assert all(
        example["secret_material_present"] is False
        for example in stub["ignored_env_examples"]
    )
    assert stub["external_secret_store_contract"][
        "secret_values_stored_in_repo"
    ] is False
    assert stub["persistent_execution_stub"]["scheduler_enabled"] is False
    assert stub["persistent_execution_stub"]["queue_enabled"] is False
    assert stub["rollback_plan"]["rollback_execution_authorized"] is False
    assert all(value is False for value in stub["authority_locks"].values())
    assert hook["valid_for_scheduler_queue_runtime"] is False
    assert receipt["receipt_status"] == (
        "ORACLE_PERSISTENT_SANDBOX_SECRET_STORE_STUB_READY_ADVISORY_ONLY"
    )
    assert validation["validation_status"] == "VALID_ADVISORY_ONLY"
    _assert_canonical_hash(stub)
    _assert_canonical_hash(hook)
    _assert_canonical_hash(receipt)


def test_abx_loop_emits_oracle_persistent_sandbox_secret_store_stub_receipt(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "oracle_persistent_sandbox_secret_store_stub.latest.json"
    validation_path = tmp_path / "oracle_schema_validation_secret_store_stub.latest.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/abx_loop.py",
            "--emit-oracle-persistent-sandbox-secret-store-stub",
            "--validate-oracle-schemas",
            "--oracle-persistent-sandbox-secret-store-stub-out",
            str(receipt_path),
            "--oracle-validation-out",
            str(validation_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(receipt_path) in completed.stdout
    receipt_text = receipt_path.read_text(encoding="utf-8")
    assert "ORACLE_SIGNAL_ENDPOINT_URL=" not in receipt_text
    assert "HOLLERSPORTS_BATCH_ENDPOINT_URL=" not in receipt_text
    receipt = json.loads(receipt_text)
    assert receipt["receipt_status"] == (
        "ORACLE_PERSISTENT_SANDBOX_SECRET_STORE_STUB_READY_ADVISORY_ONLY"
    )
    assert all(value is False for value in receipt["authority_locks"].values())
    assert receipt["valid_for_external_oracle_calls"] is False
    assert receipt["valid_for_scheduler_queue_runtime"] is False
    assert receipt["valid_for_secret_material_persistence"] is False
    _assert_canonical_hash(receipt)
    validation_receipt = json.loads(validation_path.read_text(encoding="utf-8"))
    assert "oracle_persistent_sandbox_secret_store_stub" in (
        validation_receipt["validation_result_hashes"]
    )
    assert validation_receipt["validation_summary"]["valid_result_count"] == 24
    _assert_canonical_hash(validation_receipt)


def test_oracle_sandbox_probe_gate_proposal_packet() -> None:
    packets = _build_packets()
    plan = build_oracle_persistent_execution_secret_vault_plan(
        timestamp=TIMESTAMP,
        oracle_full_live_endpoint_env_intake_receipt=packets[
            "full_live_endpoint_env_intake_receipt"
        ],
        oracle_full_live_runtime_preflight_receipt=packets[
            "full_live_runtime_preflight_receipt"
        ],
        oracle_full_live_runtime_execution_attempt_receipt=packets[
            "full_live_runtime_execution_attempt_receipt"
        ],
    )
    plan_hook = build_oracle_persistent_execution_secret_vault_plan_observability_hook(
        timestamp=TIMESTAMP,
        persistent_execution_secret_vault_plan_receipt_hash="7" * 64,
        persistent_execution_secret_vault_plan_schema_path=(
            "contracts/canon/oracle/"
            "oracle_persistent_execution_secret_vault_plan.v1.schema.json"
        ),
    )
    plan_receipt = build_oracle_persistent_execution_secret_vault_plan_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_persistent_execution_secret_vault_plan=plan,
        observability_hook=plan_hook,
    )
    stub = build_oracle_persistent_sandbox_secret_store_stub(
        timestamp=TIMESTAMP,
        oracle_persistent_execution_secret_vault_plan_receipt=plan_receipt,
    )
    stub_hook = build_oracle_persistent_sandbox_secret_store_stub_observability_hook(
        timestamp=TIMESTAMP,
        persistent_sandbox_secret_store_stub_receipt_hash="8" * 64,
        persistent_sandbox_secret_store_stub_schema_path=(
            "contracts/canon/oracle/"
            "oracle_persistent_sandbox_secret_store_stub.v1.schema.json"
        ),
    )
    stub_receipt = build_oracle_persistent_sandbox_secret_store_stub_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_persistent_sandbox_secret_store_stub=stub,
        observability_hook=stub_hook,
    )
    proposal = build_oracle_sandbox_probe_gate_proposal(
        timestamp=TIMESTAMP,
        oracle_persistent_sandbox_secret_store_stub_receipt=stub_receipt,
    )
    validation = validate_oracle_packet(
        packet_key="oracle_sandbox_probe_gate_proposal",
        packet=proposal,
        schema_path=SCHEMA_BY_PACKET_KEY["oracle_sandbox_probe_gate_proposal"],
        timestamp=TIMESTAMP,
        repo_root=REPO_ROOT,
    )
    hook = build_oracle_sandbox_probe_gate_proposal_observability_hook(
        timestamp=TIMESTAMP,
        sandbox_probe_gate_proposal_receipt_hash="9" * 64,
        sandbox_probe_gate_proposal_schema_path=(
            "contracts/canon/oracle/"
            "oracle_sandbox_probe_gate_proposal.v1.schema.json"
        ),
    )
    receipt = build_oracle_sandbox_probe_gate_proposal_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        oracle_sandbox_probe_gate_proposal=proposal,
        observability_hook=hook,
    )

    assert (
        "contracts/canon/oracle/"
        "oracle_sandbox_probe_gate_proposal.v1.schema.json"
    ) in ORACLE_CANON_EXTENSION_SCHEMA_PATHS
    assert "oracle_sandbox_probe_gate_proposal" in SCHEMA_BY_PACKET_KEY
    assert proposal["proposal_status"] == (
        "ORACLE_SANDBOX_PROBE_GATE_PROPOSAL_READY_ADVISORY_ONLY"
    )
    assert proposal["operator_gate_template"]["required_phrase"] == (
        "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED"
    )
    assert proposal["operator_gate_template"]["authorizes_probe_execution"] is False
    assert proposal["probe_dry_run_plan"]["command_shape_is_authorized_now"] is False
    assert proposal["valid_for_sandbox_probe_execution"] is False
    assert proposal["valid_for_external_oracle_calls"] is False
    assert hook["valid_for_sandbox_probe_execution"] is False
    assert hook["valid_for_external_oracle_calls"] is False
    assert receipt["receipt_status"] == (
        "ORACLE_SANDBOX_PROBE_GATE_PROPOSAL_READY_ADVISORY_ONLY"
    )
    assert receipt["gate_summary"]["probe_authorized_by_receipt"] is False
    assert validation["validation_status"] == "VALID_ADVISORY_ONLY"
    _assert_canonical_hash(proposal)
    _assert_canonical_hash(hook)
    _assert_canonical_hash(receipt)


def test_abx_loop_emits_oracle_sandbox_probe_gate_proposal_receipt(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "oracle_sandbox_probe_gate_proposal.latest.json"
    validation_path = tmp_path / "oracle_schema_validation_probe_gate.latest.json"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/abx_loop.py",
            "--emit-oracle-sandbox-probe-gate-proposal",
            "--validate-oracle-schemas",
            "--oracle-sandbox-probe-gate-proposal-out",
            str(receipt_path),
            "--oracle-validation-out",
            str(validation_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(receipt_path) in completed.stdout
    receipt_text = receipt_path.read_text(encoding="utf-8")
    assert "ORACLE_SIGNAL_ENDPOINT_URL=" not in receipt_text
    assert "HOLLERSPORTS_BATCH_ENDPOINT_URL=" not in receipt_text
    receipt = json.loads(receipt_text)
    assert receipt["receipt_status"] == (
        "ORACLE_SANDBOX_PROBE_GATE_PROPOSAL_READY_ADVISORY_ONLY"
    )
    assert all(value is False for value in receipt["authority_locks"].values())
    assert receipt["valid_for_sandbox_probe_execution"] is False
    assert receipt["valid_for_external_oracle_calls"] is False
    assert receipt["valid_for_scheduler_queue_runtime"] is False
    assert receipt["valid_for_secret_material_persistence"] is False
    _assert_canonical_hash(receipt)
    validation_receipt = json.loads(validation_path.read_text(encoding="utf-8"))
    assert "oracle_sandbox_probe_gate_proposal" in (
        validation_receipt["validation_result_hashes"]
    )
    assert validation_receipt["validation_summary"]["valid_result_count"] == 25
    _assert_canonical_hash(validation_receipt)


def test_oracle_full_live_runtime_command_notion_mirror_packet() -> None:
    packet = build_oracle_full_live_runtime_command_notion_mirror_packet(REPO_ROOT)
    assert packet["status"] == "ORACLE_FULL_LIVE_RUNTIME_COMMAND_NOTION_MIRROR_READY"
    assert packet["manual_operator_copy_paste_only"] is True
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["packet_blockers"] == []
    assert "ORACLE_FULL_LIVE_RUNTIME_COMMAND_READY" in packet[
        "paste_ready_notion_block"
    ]
    _assert_canonical_hash(packet)


def test_oracle_full_live_runtime_execution_attempt_notion_mirror_packet() -> None:
    packet = (
        build_oracle_full_live_runtime_execution_attempt_notion_mirror_packet(
            REPO_ROOT
        )
    )
    assert packet["status"] == (
        "ORACLE_FULL_LIVE_RUNTIME_EXECUTION_ATTEMPT_NOTION_MIRROR_READY"
    )
    assert packet["designer_audit_ready"] is True
    assert packet["manual_operator_copy_paste_only"] is True
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["packet_blockers"] == []
    assert packet["designer_audit_summary"]["default_external_call_count"] == 0
    assert packet["designer_audit_summary"]["default_payload_record_count"] == 0
    assert "ORACLE_FULL_LIVE_RUNTIME_EXECUTION_ATTEMPT_BLOCKED" in packet[
        "paste_ready_notion_block"
    ]
    assert "FULL_LIVE_EXECUTION_GATE_CONFIRMED" in packet[
        "paste_ready_notion_block"
    ]
    _assert_canonical_hash(packet)
