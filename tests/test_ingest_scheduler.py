from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.ingest.cadence import CadenceBounds, resolve_cadence_seconds
from core.ingest.scheduler import (
    TARGET_PATCH_ID,
    build_scheduled_manifest,
    build_scheduler_receipt,
    decide_ingest_windows,
)
from core.ingest.windowing import is_quiet_window, operator_window_active, parse_iso_datetime


def _adapter_config() -> dict:
    return {
        "adapters": [
            {"adapter_id": "abx_market_feed_v1", "domain": "finance", "enabled": True},
            {"adapter_id": "abx_geo_feed_v1", "domain": "geopolitics", "enabled": True},
        ]
    }


def _policy() -> dict:
    return {
        "schema_version": "IngestWindowPolicy.v1",
        "policy_id": "abx_controlled_ingest_scheduler_v1",
        "timezone": "UTC",
        "global": {
            "min_seconds_between_runs": 300,
            "max_concurrent_adapters": 1,
            "quiet_window_enabled": True,
            "quiet_window": {"start_hour": 2, "end_hour": 5, "cadence_multiplier": 4.0},
        },
        "domain_policies": {
            "finance": {
                "base_cadence_seconds": 900,
                "min_cadence_seconds": 300,
                "max_cadence_seconds": 3600,
                "operator_window_required": False,
            },
            "geopolitics": {
                "base_cadence_seconds": 3600,
                "min_cadence_seconds": 1800,
                "max_cadence_seconds": 21600,
                "operator_window_required": True,
            },
        },
        "volatility_policy": {
            "enabled": True,
            "compression_thresholds": [{"metric": "z_score", "gte": 2.5, "cadence_multiplier": 0.5}],
            "expansion_thresholds": [{"metric": "z_score", "lt": 1.0, "cadence_multiplier": 2.0}],
        },
    }


def _scheduler_state() -> dict:
    return {
        "schema_version": "SchedulerState.v1",
        "scheduler_id": "abx_controlled_ingest_scheduler_v1",
        "last_run_by_adapter": {},
        "last_decision_hash": None,
        "active_operator_windows": [],
        "cooldowns": {},
        "blocked_adapters": [],
    }


def _anomaly_state() -> dict:
    return {
        "schema_version": "ShadowAnomalyState.v1",
        "generated_at": "2026-06-04T00:00:00Z",
        "domain_scores": {
            "finance": {"z_score": 3.0, "source": "fixture"},
            "geopolitics": {"z_score": 0.5, "source": "fixture"},
        },
    }


def test_resolve_cadence_is_deterministic() -> None:
    bounds = CadenceBounds(base_seconds=900, min_seconds=300, max_seconds=3600)
    assert resolve_cadence_seconds(bounds, quiet_window_multiplier=4.0, volatility_multiplier=0.5) == 1800


def test_quiet_window_and_operator_window_behaviour() -> None:
    assert is_quiet_window(parse_iso_datetime("2026-06-04T03:00:00Z"), 2, 5) is True
    assert (
        operator_window_active(
            [{"domain": "geopolitics", "start": "2026-06-04T00:00:00Z", "end": "2026-06-04T23:00:00Z", "approved": True}],
            "geopolitics",
            parse_iso_datetime("2026-06-04T03:00:00Z"),
        )
        is True
    )


def test_scheduler_decisions_are_stable_and_enforce_authority_locks() -> None:
    packet_a = decide_ingest_windows(
        adapter_config_set=_adapter_config(),
        window_policy=_policy(),
        scheduler_state=_scheduler_state(),
        anomaly_state=_anomaly_state(),
        now_iso="2026-06-04T03:00:00Z",
    )
    packet_b = decide_ingest_windows(
        adapter_config_set=_adapter_config(),
        window_policy=_policy(),
        scheduler_state=_scheduler_state(),
        anomaly_state=_anomaly_state(),
        now_iso="2026-06-04T03:00:00Z",
    )

    assert packet_a["decision_hash"] == packet_b["decision_hash"]
    assert packet_a["advisory_only"] is True
    assert packet_a["projection_only"] is True
    assert packet_a["non_authoritative"] is True
    assert packet_a["forecast_authority"] is False
    assert packet_a["canon_mutation"] is False
    assert packet_a["runtime_mutation"] is False
    assert packet_a["execution_authority"] is False
    decisions = {row["adapter_id"]: row for row in packet_a["decisions"]}
    assert decisions["abx_market_feed_v1"]["decision"] == "RUN"
    assert decisions["abx_geo_feed_v1"]["decision"] == "SKIP_OPERATOR_WINDOW_REQUIRED"


def test_scheduler_manifest_and_receipt_follow_decision_set() -> None:
    decision_set = decide_ingest_windows(
        adapter_config_set=_adapter_config(),
        window_policy=_policy(),
        scheduler_state=_scheduler_state(),
        anomaly_state=_anomaly_state(),
        now_iso="2026-06-04T03:00:00Z",
    )
    manifest = build_scheduled_manifest(
        decision_set,
        max_concurrent_adapters=1,
        oracle_signal_module_present=True,
    )
    receipt = build_scheduler_receipt(decision_set, manifest)
    assert manifest["eligible_adapters"] == ["abx_market_feed_v1"]
    assert "abx_geo_feed_v1" in manifest["blocked_adapters"]
    assert manifest["handoff"]["target_patch"] == TARGET_PATCH_ID
    assert manifest["projection_only"] is True
    assert manifest["non_authoritative"] is True
    assert receipt["status"] == "ADVISORY_ONLY"
    assert receipt["projection_only"] is True
    assert receipt["non_authoritative"] is True
    eligibility = manifest["handoff"]["controlled_handoff_eligibility"]
    assert eligibility["controlled_handoff_eligible"] is True
    assert eligibility["execution_authority"] is False


def test_scheduler_contracts_validate() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    contract_dir = Path("contracts/ingest")
    policy_schema = json.loads((contract_dir / "ingest_window_policy.v1.schema.json").read_text(encoding="utf-8"))
    state_schema = json.loads((contract_dir / "scheduler_state.v1.schema.json").read_text(encoding="utf-8"))
    anomaly_schema = json.loads((contract_dir / "shadow_anomaly_state.v1.schema.json").read_text(encoding="utf-8"))
    decision_schema = json.loads((contract_dir / "ingest_window_decision_set.v1.schema.json").read_text(encoding="utf-8"))
    manifest_schema = json.loads((contract_dir / "scheduled_ingest_run_manifest.v1.schema.json").read_text(encoding="utf-8"))
    receipt_schema = json.loads((contract_dir / "scheduler_receipt.v1.schema.json").read_text(encoding="utf-8"))

    decision_set = decide_ingest_windows(
        adapter_config_set=_adapter_config(),
        window_policy=_policy(),
        scheduler_state=_scheduler_state(),
        anomaly_state=_anomaly_state(),
        now_iso="2026-06-04T03:00:00Z",
    )
    manifest = build_scheduled_manifest(
        decision_set,
        max_concurrent_adapters=1,
        oracle_signal_module_present=True,
    )
    receipt = build_scheduler_receipt(decision_set, manifest)

    jsonschema.validate(_policy(), policy_schema)
    jsonschema.validate(_scheduler_state(), state_schema)
    jsonschema.validate(_anomaly_state(), anomaly_schema)
    jsonschema.validate(decision_set, decision_schema)
    jsonschema.validate(manifest, manifest_schema)
    jsonschema.validate(receipt, receipt_schema)
