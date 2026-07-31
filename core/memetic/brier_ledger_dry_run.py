"""Memetic futurecast → Brier ledger dry-run (no ledger write).

Projects MemeticFuturecastOperatorPacket.v0 brier_bridge onto a
BrierLedgerEntry.v1-shaped candidate without writing out/brier or granting
forecast weight.
"""

from __future__ import annotations

import hashlib
from typing import Any, Mapping

from core.canonical.json import canonical_hash
from core.memetic.futurecast_operator_packet import (
    build_futurecast_operator_packet,
    build_futurecast_operator_packet_from_forecast,
)

SCHEMA_VERSION = "MemeticBrierLedgerDryRun.v0"
PIPELINE_ID = "memetic_futurecast"
LEDGER_TARGET = "out/brier"
DETERMINISTIC_TIMESTAMP = "memetic_brier_ledger_dry_run_v0_ts_0"

DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "promotion_authorized": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
    "ledger_write_authorized": False,
}


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _score_hash(
    forecast_hash: str,
    probability: float,
    outcome: float,
    brier_score: float,
) -> str:
    payload = (
        f"{forecast_hash}|{probability:.10f}|{outcome:.10f}|{brier_score:.10f}"
    )
    return _sha256_text(payload)


def _ledger_hash(
    forecast_hash: str,
    score_hash: str,
    calibration_hash: str,
    generation: int,
) -> str:
    return _sha256_text(
        f"{forecast_hash}|{score_hash}|{calibration_hash}|{generation}"
    )


def project_ledger_entry_candidate(
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Map operator packet → BrierLedgerEntry.v1-shaped projection (pure)."""
    bridge = packet.get("brier_bridge") if isinstance(packet.get("brier_bridge"), dict) else {}
    forecast_hash = str(bridge.get("forecast_hash") or packet.get("canonical_hash") or "")
    packet_hash = str(packet.get("canonical_hash") or "")
    calibration_hash = _sha256_text(f"memetic_cal|{packet_hash}|{forecast_hash}")
    generation = 1

    bridge_status = str(bridge.get("bridge_status") or "BRIDGE_INCOMPLETE")
    brier_ready = bool(bridge.get("brier_ready"))
    prob = bridge.get("probability")
    outcome = bridge.get("outcome_value")
    provisional = bridge.get("provisional_brier")

    if bridge_status == "BRIDGE_BLOCKED" or not brier_ready:
        return {
            "schema_version": "BrierLedgerEntry.v1",
            "projection_status": "BLOCKED",
            "ledger_entry_id": None,
            "forecast_hash": forecast_hash or None,
            "score_hash": None,
            "calibration_hash": calibration_hash,
            "replay_hash": None,
            "ledger_generation": generation,
            "deterministic_ledger_hash": None,
            "status": "dry_run_blocked",
            "brier_score": provisional,
            "probability": prob,
            "outcome_value": outcome,
            "bridge_status": bridge_status,
            "authority": {
                "execution_authority": False,
                "promotion_allowed": False,
                "forecast_weight_allowed": False,
                "runtime_mutation_allowed": False,
                "canon_mutation_allowed": False,
            },
        }

    if provisional is None or prob is None or outcome is None:
        return {
            "schema_version": "BrierLedgerEntry.v1",
            "projection_status": "SEEDED_AWAITING_OUTCOME",
            "ledger_entry_id": None,
            "forecast_hash": forecast_hash or None,
            "score_hash": None,
            "calibration_hash": calibration_hash,
            "replay_hash": None,
            "ledger_generation": generation,
            "deterministic_ledger_hash": None,
            "status": "dry_run_seeded",
            "brier_score": None,
            "probability": prob,
            "outcome_value": outcome,
            "bridge_status": bridge_status,
            "authority": {
                "execution_authority": False,
                "promotion_allowed": False,
                "forecast_weight_allowed": False,
                "runtime_mutation_allowed": False,
                "canon_mutation_allowed": False,
            },
        }

    score = float(provisional)
    p = float(prob)
    o = float(outcome)
    s_hash = _score_hash(forecast_hash, p, o, score)
    d_hash = _ledger_hash(forecast_hash, s_hash, calibration_hash, generation)
    entry_id = "ledger_dry_" + d_hash[:16]
    return {
        "schema_version": "BrierLedgerEntry.v1",
        "projection_status": "PROJECTED",
        "ledger_entry_id": entry_id,
        "forecast_hash": forecast_hash,
        "score_hash": s_hash,
        "calibration_hash": calibration_hash,
        "replay_hash": None,
        "ledger_generation": generation,
        "deterministic_ledger_hash": d_hash,
        "status": "dry_run_projected",
        "brier_score": score,
        "probability": p,
        "outcome_value": o,
        "bridge_status": bridge_status,
        "authority": {
            "execution_authority": False,
            "promotion_allowed": False,
            "forecast_weight_allowed": False,
            "runtime_mutation_allowed": False,
            "canon_mutation_allowed": False,
        },
    }


def build_memetic_brier_ledger_dry_run(
    packet: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Build MemeticBrierLedgerDryRun.v0 from futurecast operator packet."""
    if packet is None:
        packet = build_futurecast_operator_packet(
            forecast_id="",
            topic="",
            selected_horizon="",
        )

    projected = project_ledger_entry_candidate(packet)
    bridge = packet.get("brier_bridge") if isinstance(packet.get("brier_bridge"), dict) else {}

    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "dry_run": True,
        "ledger_write_performed": False,
        "ledger_write_authorized": False,
        "target_ledger_path": LEDGER_TARGET,
        "pipeline_id": PIPELINE_ID,
        "packet_id": packet.get("packet_id"),
        "forecast_id": packet.get("forecast_id"),
        "source_packet_hash": packet.get("canonical_hash"),
        "bridge_status": bridge.get("bridge_status"),
        "brier_ready": bridge.get("brier_ready"),
        "source_readiness": packet.get("readiness"),
        "projected_ledger_entry": projected,
        "projection_status": projected.get("projection_status"),
        "authority": dict(DEFAULT_AUTHORITY),
        "advisory_only": True,
        "lane": "SHADOW_FORECAST_GATED",
        "producer": {
            "module": "core.memetic.brier_ledger_dry_run",
            "upstream": "core.memetic.futurecast_operator_packet",
            "pipeline_id": PIPELINE_ID,
        },
        "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
        "forecast_routing_blocked": True,
        "note": (
            "Dry-run only. Does not write BrierLedgerEntry.v1 to out/brier or "
            "grant forecast weight. Operator dual-control required before ledger publish."
        ),
    }
    body["canonical_hash"] = canonical_hash(body)
    return body


def build_brier_ledger_dry_run_from_forecast(
    forecast: dict[str, Any],
) -> dict[str, Any]:
    """Forecast-like dict → futurecast packet → ledger dry-run (pure)."""
    packet = build_futurecast_operator_packet_from_forecast(forecast)
    return build_memetic_brier_ledger_dry_run(packet)
