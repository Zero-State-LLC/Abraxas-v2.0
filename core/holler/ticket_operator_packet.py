"""HollerSports ticket operator packet — forecast proof + outcome binding chain.

Closes hollersports_ticket MISSING_CONTRACT at the operator-packet layer.
Does not route live forecasts, place bets, promote canon, or grant execution.
"""

from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash

SCHEMA_VERSION = "HollerSportsTicketOperatorPacket.v0"
PIPELINE_ID = "hollersports_ticket"
DETERMINISTIC_TIMESTAMP = "hollersports_ticket_operator_packet_v0_ts_0"

DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "promotion_authorized": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
}

PRODUCER = {
    "module": "core.holler.ticket_operator_packet",
    "skill_id": "holler-ingest",
    "pipeline_id": PIPELINE_ID,
}

REGISTERS = frozenset({"OBSERVED", "INFERRED", "SPECULATIVE", "NOT_COMPUTABLE"})


def _norm_register(raw: Any) -> str:
    s = str(raw or "NOT_COMPUTABLE").strip().upper()
    return s if s in REGISTERS else "NOT_COMPUTABLE"


def _prob(raw: Any) -> float | None:
    if raw is None or raw == "":
        return None
    try:
        p = float(raw)
    except (TypeError, ValueError):
        return None
    if p < 0.0 or p > 1.0:
        return None
    return p


def build_ticket_operator_packet(
    *,
    ticket_id: str = "",
    sport: str = "UNKNOWN",
    event_ref: str = "",
    market_class: str = "UNKNOWN",
    model_ref: str = "holler_forecast_shadow",
    probability: float | None = None,
    register: str = "NOT_COMPUTABLE",
    expected_outcome: str = "",
    observed_outcome: str | None = None,
    forecast_payload: dict[str, Any] | None = None,
    blocked_by: list[str] | None = None,
) -> dict[str, Any]:
    """Build deterministic HollerSportsTicketOperatorPacket.v0 (FORECAST_GATED)."""
    tid = str(ticket_id or "").strip() or "ticket_unspecified"
    sport_n = str(sport or "UNKNOWN").strip() or "UNKNOWN"
    event = str(event_ref or "").strip()
    market = str(market_class or "UNKNOWN").strip() or "UNKNOWN"
    model = str(model_ref or "holler_forecast_shadow").strip()
    reg = _norm_register(register)
    prob = _prob(probability)
    payload = forecast_payload if isinstance(forecast_payload, dict) else {}

    blocks = list(blocked_by or [])
    for b in ("FORECAST_ROUTING_BLOCKED", "LIVE_ODDS_EXECUTION_BLOCKED"):
        if b not in blocks:
            blocks.append(b)

    # Forecast proof seed
    forecast_material = {
        "ticket_id": tid,
        "sport": sport_n,
        "event_ref": event,
        "market_class": market,
        "model_ref": model,
        "probability": prob,
        "register": reg,
        "payload": payload,
    }
    forecast_hash = canonical_hash(forecast_material)

    if not event:
        proof_status = "NOT_COMPUTABLE"
        if "MISSING_EVENT_REF" not in blocks:
            blocks.append("MISSING_EVENT_REF")
    elif prob is None and reg == "NOT_COMPUTABLE" and not payload:
        proof_status = "PROOF_INCOMPLETE"
        if "FORECAST_PROOF_INCOMPLETE" not in blocks:
            blocks.append("FORECAST_PROOF_INCOMPLETE")
    elif reg == "NOT_COMPUTABLE" and prob is None:
        proof_status = "PROOF_BLOCKED"
        if "FORECAST_NOT_COMPUTABLE" not in blocks:
            blocks.append("FORECAST_NOT_COMPUTABLE")
    else:
        proof_status = "PROOF_SEEDED"

    brier_ready = proof_status == "PROOF_SEEDED" and prob is not None

    forecast_proof = {
        "schema_version": "HollerForecastProof.v0",
        "proof_status": proof_status,
        "forecast_hash": forecast_hash,
        "model_ref": model,
        "brier_ready": brier_ready,
        "probability": prob,
        "register": reg,
    }

    # Outcome binding seed (mirrors ForecastOutcomeBindingPacket.v1 shape; no write)
    expected = str(expected_outcome or "").strip()
    if not expected and event:
        expected = f"event:{event}|market:{market}|ticket:{tid}"
    # Same key material so equal outcomes compare equal (binding seed only).
    expected_hash = canonical_hash({"outcome": expected}) if expected else ""
    observed = observed_outcome if observed_outcome is not None else None
    observed_s = str(observed).strip() if observed is not None else ""
    observed_hash = (
        canonical_hash({"outcome": observed_s}) if observed_s else None
    )

    if not expected_hash:
        binding_status = "not_seeded"
        if "OUTCOME_BINDING_NOT_SEEDED" not in blocks:
            blocks.append("OUTCOME_BINDING_NOT_SEEDED")
    elif observed_hash is None:
        binding_status = "unresolved"
    elif observed_hash == expected_hash:
        binding_status = "matched"
    else:
        binding_status = "mismatched"

    binding_id = "hob_" + canonical_hash(
        {
            "ticket_id": tid,
            "forecast_hash": forecast_hash,
            "expected_outcome_hash": expected_hash,
        }
    )[:16]

    outcome_binding = {
        "schema_version": "HollerOutcomeBindingSeed.v0",
        "binding_status": binding_status,
        "binding_id": binding_id,
        "expected_outcome_hash": expected_hash,
        "observed_outcome_hash": observed_hash,
        "forecast_outcome_binding_hint": "ForecastOutcomeBindingPacket.v1",
    }

    if proof_status == "NOT_COMPUTABLE" or not event:
        readiness = "NOT_COMPUTABLE"
    elif proof_status in {"PROOF_BLOCKED"}:
        readiness = "BLOCKED"
    else:
        readiness = "SHADOW_OPERATOR_REVIEW"

    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "pipeline_id": PIPELINE_ID,
        "packet_id": "htop_"
        + canonical_hash(
            {
                "ticket_id": tid,
                "forecast_hash": forecast_hash,
                "binding_id": binding_id,
            }
        )[:16],
        "ticket_id": tid,
        "sport": sport_n,
        "event_ref": event,
        "market_class": market,
        "forecast_proof": forecast_proof,
        "outcome_binding": outcome_binding,
        "readiness": readiness,
        "blocked_by": blocks,
        "forecast_routing_blocked": True,
        "live_odds_execution_blocked": True,
        "authority": dict(DEFAULT_AUTHORITY),
        "advisory_only": True,
        "lane": "FORECAST_GATED",
        "producer": dict(PRODUCER),
        "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
    }
    body["canonical_hash"] = canonical_hash(body)
    return body


def build_ticket_operator_packet_from_ticket(
    ticket: dict[str, Any],
    *,
    forecast_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Lift a ticket-like dict into the operator packet."""
    t = ticket if isinstance(ticket, dict) else {}
    forecast = t.get("forecast") if isinstance(t.get("forecast"), dict) else {}
    payload = forecast_payload if forecast_payload is not None else forecast
    return build_ticket_operator_packet(
        ticket_id=str(t.get("ticket_id") or t.get("id") or ""),
        sport=str(t.get("sport") or "UNKNOWN"),
        event_ref=str(t.get("event_ref") or t.get("event_id") or ""),
        market_class=str(t.get("market_class") or t.get("market") or "UNKNOWN"),
        model_ref=str(
            t.get("model_ref")
            or forecast.get("model_ref")
            or "holler_forecast_shadow"
        ),
        probability=t.get("probability", forecast.get("probability")),
        register=str(t.get("register") or forecast.get("register") or "NOT_COMPUTABLE"),
        expected_outcome=str(t.get("expected_outcome") or t.get("outcome") or ""),
        observed_outcome=t.get("observed_outcome"),
        forecast_payload=payload if isinstance(payload, dict) else {},
        blocked_by=list(t.get("blocked_by") or [])
        if isinstance(t.get("blocked_by"), list)
        else None,
    )
