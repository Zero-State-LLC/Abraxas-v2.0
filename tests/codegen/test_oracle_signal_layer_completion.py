from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from core.canonical.json import canonical_hash
from core.codegen.loop805_observability import (
    build_oracle_ingest_wiring_observability_hook,
    build_oracle_measurement_readiness_observability_hook,
    build_oracle_measurement_proposal_observability_hook,
    build_oracle_measurement_authorization_proposal_observability_hook,
    build_oracle_measurement_authorization_decision_review_candidate_observability_hook,
    build_oracle_shadow_dryrun_observability_hook,
    build_oracle_shadow_measurement_observability_hook,
    build_oracle_signal_observability_hook,
)
from core.codegen.oracle_signal import (
    ORACLE_CANON_EXTENSION_SCHEMA_PATHS,
    build_holler_oracle_ingest_stub,
    build_holler_oracle_ingest_wiring,
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
    build_oracle_measurement_readiness,
    build_oracle_measurement_readiness_receipt,
    build_oracle_measurement_proposal,
    build_oracle_measurement_proposal_receipt,
    build_oracle_measurement_authorization_proposal,
    build_oracle_measurement_authorization_proposal_receipt,
    build_oracle_measurement_authorization_decision_review_candidate,
    build_oracle_measurement_authorization_decision_review_candidate_receipt,
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
    validate_holler_oracle_batch_evolution,
    validate_oracle_packet,
    validate_oracle_schema_packets,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
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
    receipt = build_oracle_signal_layer_completion_receipt(
        timestamp=TIMESTAMP,
        merge_sha=MERGE_SHA,
        signal_envelope=envelope,
        holler_intake=holler,
        calibration_report=calibration,
        adversarial_fixture=adversarial,
        ingest_stub=ingest,
        observability_hook=hook,
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
        "receipt": receipt,
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
        == "ORACLE_SIGNAL_LAYER_COMPLETION_READY_ADVISORY_ONLY"
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
        == "Review additive schema validation, ingest wiring, shadow dry-run, and measurement readiness receipts before any future shadow measurement slice."
    )


def test_oracle_schema_validator_accepts_all_generated_packets() -> None:
    packets = _build_packets()
    results = packets["decision_review_validation_results"]
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
            "Scripts/abx_loop.py",
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
            "Scripts/abx_loop.py",
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
            "Scripts/abx_loop.py",
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
            "Scripts/abx_loop.py",
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
            "Scripts/abx_loop.py",
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
            "Scripts/abx_loop.py",
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
            "Scripts/abx_loop.py",
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
