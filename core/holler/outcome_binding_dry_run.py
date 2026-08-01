"""Holler ticket → ForecastOutcomeBindingPacket dry-run (no ledger / odds write).

Projects HollerSportsTicketOperatorPacket.v0 outcome_binding onto
ForecastOutcomeBindingPacket.v1 shape without publishing bindings or
granting forecast weight / live odds execution.
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash
from core.holler.ticket_operator_packet import (
    build_ticket_operator_packet,
    build_ticket_operator_packet_from_ticket,
)

SCHEMA_VERSION = "HollerOutcomeBindingDryRun.v0"
PIPELINE_ID = "hollersports_ticket"
BINDING_TARGET = "out/forecast"
DETERMINISTIC_TIMESTAMP = "holler_outcome_binding_dry_run_v0_ts_0"

DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "promotion_authorized": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
    "binding_write_authorized": False,
    "live_odds_execution_authorized": False,
}


def project_outcome_binding_candidate(
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Map ticket packet → ForecastOutcomeBindingPacket.v1-shaped projection."""
    binding = (
        packet.get("outcome_binding")
        if isinstance(packet.get("outcome_binding"), dict)
        else {}
    )
    proof = (
        packet.get("forecast_proof")
        if isinstance(packet.get("forecast_proof"), dict)
        else {}
    )
    forecast_hash = str(proof.get("forecast_hash") or packet.get("canonical_hash") or "")
    expected_hash = str(binding.get("expected_outcome_hash") or "")
    observed_hash = binding.get("observed_outcome_hash")
    binding_status = str(binding.get("binding_status") or "not_seeded")
    binding_id = str(binding.get("binding_id") or "")
    proof_status = str(proof.get("proof_status") or "NOT_COMPUTABLE")

    if binding_status == "not_seeded" or not expected_hash:
        projection_status = "NOT_SEEDED"
        status = "dry_run_not_seeded"
    elif binding_status == "unresolved":
        projection_status = "UNRESOLVED"
        status = "dry_run_awaiting_outcome"
    elif binding_status == "matched":
        projection_status = "MATCHED"
        status = "dry_run_matched"
    elif binding_status == "mismatched":
        projection_status = "MISMATCHED"
        status = "dry_run_mismatched"
    else:
        projection_status = "BLOCKED"
        status = "dry_run_blocked"

    if proof_status in {"NOT_COMPUTABLE", "PROOF_BLOCKED"}:
        projection_status = "BLOCKED"
        status = "dry_run_blocked"

    # ForecastOutcomeBindingPacket.v1-shaped fields (projection only).
    projected = {
        "schema_version": "ForecastOutcomeBindingPacket.v1",
        "projection_status": projection_status,
        "binding_id": binding_id or None,
        "forecast_hash": forecast_hash or None,
        "expected_outcome_hash": expected_hash or None,
        "observed_outcome_hash": observed_hash,
        "binding_status": binding_status,
        "status": status,
        "proof_status": proof_status,
        "brier_ready": bool(proof.get("brier_ready")),
        "probability": proof.get("probability"),
        "ticket_id": packet.get("ticket_id"),
        "event_ref": packet.get("event_ref"),
        "sport": packet.get("sport"),
        "authority": {
            "execution_authority": False,
            "promotion_allowed": False,
            "forecast_weight_allowed": False,
            "runtime_mutation_allowed": False,
            "canon_mutation_allowed": False,
        },
    }
    return projected


def build_holler_outcome_binding_dry_run(
    packet: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Build HollerOutcomeBindingDryRun.v0 from ticket operator packet."""
    if packet is None:
        packet = build_ticket_operator_packet()

    projected = project_outcome_binding_candidate(packet)
    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "dry_run": True,
        "binding_write_performed": False,
        "binding_write_authorized": False,
        "target_binding_path": BINDING_TARGET,
        "pipeline_id": PIPELINE_ID,
        "packet_id": packet.get("packet_id"),
        "ticket_id": packet.get("ticket_id"),
        "source_packet_hash": packet.get("canonical_hash"),
        "source_readiness": packet.get("readiness"),
        "projected_binding": projected,
        "projection_status": projected.get("projection_status"),
        "authority": dict(DEFAULT_AUTHORITY),
        "advisory_only": True,
        "lane": "FORECAST_GATED",
        "producer": {
            "module": "core.holler.outcome_binding_dry_run",
            "upstream": "core.holler.ticket_operator_packet",
            "pipeline_id": PIPELINE_ID,
        },
        "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
        "forecast_routing_blocked": True,
        "live_odds_execution_blocked": True,
        "note": (
            "Dry-run only. Does not write ForecastOutcomeBindingPacket.v1, "
            "route live forecasts, or execute odds. Dual-control required before publish."
        ),
    }
    body["canonical_hash"] = canonical_hash(body)
    return body


def build_outcome_binding_dry_run_from_ticket(
    ticket: dict[str, Any],
) -> dict[str, Any]:
    """Ticket-like dict → operator packet → outcome binding dry-run (pure)."""
    packet = build_ticket_operator_packet_from_ticket(ticket)
    return build_holler_outcome_binding_dry_run(packet)
