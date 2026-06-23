from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.canonical.json import canonical_hash
from core.codegen.loop805_observability import build_oracle_signal_observability_hook
from core.codegen.oracle_signal import (
    ORACLE_CANON_EXTENSION_SCHEMA_PATHS,
    build_holler_oracle_ingest_stub,
    build_oracle_adversarial_fixture,
    build_oracle_calibration_report,
    build_oracle_holler_intake,
    build_oracle_signal_envelope,
    build_oracle_signal_layer_completion_receipt,
    build_shadow_replay_harness_stub,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
TIMESTAMP = "2026-06-21T23:05:00Z"
MERGE_SHA = "4fc43b9111b6d3dd167f284be678dba2582298c2"


@pytest.fixture(name="jsonschema")
def fixture_jsonschema():
    return pytest.importorskip("jsonschema")


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
        "receipt": receipt,
    }


def test_oracle_canon_extension_schemas_validate_samples(jsonschema) -> None:
    packets = _build_packets()
    schema_cases = {
        "oracle_signal_envelope.v1.schema.json": packets["envelope"],
        "oracle_holler_intake.v1.schema.json": packets["holler"],
        "oracle_calibration_report.v1.schema.json": packets["calibration"],
        "oracle_adversarial_fixture.v1.schema.json": packets["adversarial"],
    }
    for schema_name, packet in schema_cases.items():
        schema_path = REPO_ROOT / "contracts" / "canon" / "oracle" / schema_name
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.validate(packet, schema)


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
        == "Prepare live ingest wiring + Notion mirror reconciliation slice for operator review."
    )
