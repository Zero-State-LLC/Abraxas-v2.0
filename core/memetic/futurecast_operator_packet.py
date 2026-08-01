"""Memetic futurecast operator packet — horizon policy + gates + Brier bridge.

Closes memetic_futurecast MISSING_CONTRACT at the operator-packet layer.
Does not route live forecasts, write Brier ledgers, promote canon, or execute.
"""

from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash

SCHEMA_VERSION = "MemeticFuturecastOperatorPacket.v0"
PIPELINE_ID = "memetic_futurecast"
DETERMINISTIC_TIMESTAMP = "memetic_futurecast_operator_packet_v0_ts_0"

DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "promotion_authorized": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
}

PRODUCER = {
    "module": "core.memetic.futurecast_operator_packet",
    "skill_id": "abx-familiar-signal-forager",
    "pipeline_id": PIPELINE_ID,
    "subsystem": "Oracle / ASE / Memetic Futurecast",
}

# Default ASE-style horizons (advisory policy set; operator may tighten)
DEFAULT_ALLOWED_HORIZONS = (
    "1d",
    "7d",
    "14d",
    "30d",
    "90d",
    "180d",
    "365d",
    "NOT_COMPUTABLE",
)

REGISTERS = frozenset({"OBSERVED", "INFERRED", "SPECULATIVE", "NOT_COMPUTABLE"})

_HORIZON_DAYS = {
    "1d": 1,
    "7d": 7,
    "14d": 14,
    "30d": 30,
    "90d": 90,
    "180d": 180,
    "365d": 365,
}


def _norm_register(raw: Any) -> str:
    s = str(raw or "NOT_COMPUTABLE").strip().upper()
    return s if s in REGISTERS else "NOT_COMPUTABLE"


def _norm_horizon(raw: Any) -> str:
    s = str(raw or "").strip().lower()
    if not s:
        return "UNSPECIFIED"
    # accept "30" or "30d"
    if s.isdigit():
        s = f"{s}d"
    if s in DEFAULT_ALLOWED_HORIZONS:
        return s
    if s.upper() == "NOT_COMPUTABLE":
        return "NOT_COMPUTABLE"
    return s


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


def _outcome_value(raw: Any) -> float | None:
    if raw is None or raw == "":
        return None
    try:
        v = float(raw)
    except (TypeError, ValueError):
        return None
    if v not in (0.0, 1.0):
        # allow only binary outcomes for provisional Brier
        return None
    return v


def _provisional_brier(probability: float, outcome: float) -> float:
    # Binary Brier: (p - o)^2 — advisory only, not ledger write
    return round((probability - outcome) ** 2, 10)


def build_futurecast_operator_packet(
    *,
    forecast_id: str = "",
    topic: str = "",
    selected_horizon: str = "",
    allowed_horizons: list[str] | tuple[str, ...] | None = None,
    probability: float | None = None,
    register: str = "NOT_COMPUTABLE",
    evidence_density: float | None = None,
    outcome_value: float | None = None,
    claim_text: str = "",
    blocked_by: list[str] | None = None,
) -> dict[str, Any]:
    """Build deterministic MemeticFuturecastOperatorPacket.v0 (SHADOW_FORECAST_GATED)."""
    fid = str(forecast_id or "").strip() or "fc_unspecified"
    topic_n = str(topic or "").strip() or "UNTITLED"
    allowed = list(allowed_horizons) if allowed_horizons else list(DEFAULT_ALLOWED_HORIZONS)
    allowed_norm = []
    for h in allowed:
        hn = _norm_horizon(h)
        if hn not in allowed_norm:
            allowed_norm.append(hn)
    if "NOT_COMPUTABLE" not in allowed_norm:
        allowed_norm.append("NOT_COMPUTABLE")

    horizon = _norm_horizon(selected_horizon)
    if horizon == "UNSPECIFIED" or not str(selected_horizon or "").strip():
        policy_status = "UNSPECIFIED"
        horizon_days = None
    elif horizon == "NOT_COMPUTABLE":
        policy_status = "NOT_COMPUTABLE"
        horizon_days = None
    elif horizon in allowed_norm:
        policy_status = "ALLOWED"
        horizon_days = _HORIZON_DAYS.get(horizon)
    else:
        policy_status = "DISALLOWED"
        horizon_days = _HORIZON_DAYS.get(horizon)

    reg = _norm_register(register)
    prob = _prob(probability)
    dens = None
    if evidence_density is not None and evidence_density != "":
        try:
            dens = float(evidence_density)
            if dens < 0.0 or dens > 1.0:
                dens = None
        except (TypeError, ValueError):
            dens = None
    outcome = _outcome_value(outcome_value)

    blocks = list(blocked_by or [])
    for b in ("FORECAST_ROUTING_BLOCKED", "CANON_MUTATION_BLOCKED", "BRIER_LEDGER_WRITE_BLOCKED"):
        if b not in blocks:
            blocks.append(b)

    # --- Horizon policy ---
    if policy_status == "DISALLOWED":
        if "HORIZON_POLICY_DISALLOWED" not in blocks:
            blocks.append("HORIZON_POLICY_DISALLOWED")
    elif policy_status == "UNSPECIFIED":
        if "HORIZON_UNSPECIFIED" not in blocks:
            blocks.append("HORIZON_UNSPECIFIED")

    horizon_policy = {
        "schema_version": "MemeticHorizonPolicy.v0",
        "selected_horizon": horizon if horizon != "UNSPECIFIED" else "",
        "allowed_horizons": allowed_norm,
        "policy_status": policy_status,
        "horizon_days": horizon_days,
    }

    # --- Validation gates ---
    if reg == "NOT_COMPUTABLE":
        register_gate = "FAIL"
        if "REGISTER_NOT_COMPUTABLE" not in blocks:
            blocks.append("REGISTER_NOT_COMPUTABLE")
    elif reg == "SPECULATIVE":
        register_gate = "PARTIAL"
    else:
        register_gate = "PASS"

    if policy_status == "ALLOWED":
        horizon_gate = "PASS"
    elif policy_status == "UNSPECIFIED":
        horizon_gate = "PARTIAL"
    elif policy_status == "NOT_COMPUTABLE":
        horizon_gate = "NOT_COMPUTABLE"
    else:
        horizon_gate = "FAIL"

    if dens is None:
        evidence_gate = "PARTIAL"
        if "EVIDENCE_DENSITY_UNKNOWN" not in blocks:
            blocks.append("EVIDENCE_DENSITY_UNKNOWN")
    elif dens < 0.2:
        evidence_gate = "FAIL"
        if "EVIDENCE_DENSITY_LOW" not in blocks:
            blocks.append("EVIDENCE_DENSITY_LOW")
    else:
        evidence_gate = "PASS"

    gate_rank = {"PASS": 3, "PARTIAL": 2, "FAIL": 1, "NOT_COMPUTABLE": 0}
    overall_score = min(
        gate_rank.get(register_gate, 0),
        gate_rank.get(horizon_gate, 0),
        gate_rank.get(evidence_gate, 0),
    )
    overall = {3: "PASS", 2: "PARTIAL", 1: "FAIL", 0: "NOT_COMPUTABLE"}[overall_score]

    validation_gates = {
        "schema_version": "MemeticValidationGates.v0",
        "register_gate": register_gate,
        "horizon_gate": horizon_gate,
        "evidence_gate": evidence_gate,
        "overall": overall,
        "register": reg,
        "evidence_density": dens,
    }

    # --- Brier bridge seed ---
    forecast_material = {
        "forecast_id": fid,
        "topic": topic_n,
        "horizon": horizon,
        "probability": prob,
        "register": reg,
        "claim_text": str(claim_text or "")[:500],
    }
    forecast_hash = canonical_hash(forecast_material)

    provisional = None
    if prob is None and outcome is None:
        bridge_status = "BRIDGE_INCOMPLETE"
        brier_ready = False
        if "BRIER_INPUTS_INCOMPLETE" not in blocks:
            blocks.append("BRIER_INPUTS_INCOMPLETE")
    elif prob is None:
        bridge_status = "BRIDGE_BLOCKED"
        brier_ready = False
        if "BRIER_PROBABILITY_MISSING" not in blocks:
            blocks.append("BRIER_PROBABILITY_MISSING")
    elif outcome is None:
        bridge_status = "BRIDGE_SEEDED"
        brier_ready = True  # ready to score once outcome lands
    else:
        bridge_status = "BRIDGE_SEEDED"
        brier_ready = True
        provisional = _provisional_brier(prob, outcome)

    if policy_status == "DISALLOWED":
        bridge_status = "BRIDGE_BLOCKED"
        brier_ready = False
    if not topic_n or topic_n == "UNTITLED":
        # still allow but mark incomplete topic
        if "TOPIC_WEAK" not in blocks:
            blocks.append("TOPIC_WEAK")

    brier_bridge = {
        "schema_version": "MemeticBrierBridge.v0",
        "bridge_status": bridge_status,
        "brier_ready": brier_ready,
        "ledger_hint": "BrierLedgerEntry.v1",
        "probability": prob,
        "outcome_value": outcome,
        "provisional_brier": provisional,
        "forecast_hash": forecast_hash,
    }

    # --- Readiness ---
    if policy_status == "NOT_COMPUTABLE" or (not fid and not topic):
        readiness = "NOT_COMPUTABLE"
    elif policy_status == "DISALLOWED" or overall == "FAIL":
        readiness = "BLOCKED"
    else:
        readiness = "SHADOW_OPERATOR_REVIEW"

    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "pipeline_id": PIPELINE_ID,
        "packet_id": "mfop_"
        + canonical_hash(
            {
                "forecast_id": fid,
                "forecast_hash": forecast_hash,
                "horizon": horizon,
            }
        )[:16],
        "forecast_id": fid,
        "topic": topic_n,
        "horizon_policy": horizon_policy,
        "validation_gates": validation_gates,
        "brier_bridge": brier_bridge,
        "readiness": readiness,
        "blocked_by": blocks,
        "forecast_routing_blocked": True,
        "canon_mutation_blocked": True,
        "authority": dict(DEFAULT_AUTHORITY),
        "advisory_only": True,
        "lane": "SHADOW_FORECAST_GATED",
        "producer": dict(PRODUCER),
        "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
    }
    body["canonical_hash"] = canonical_hash(body)
    return body


def build_futurecast_operator_packet_from_forecast(
    forecast: dict[str, Any],
) -> dict[str, Any]:
    """Lift a futurecast-like dict into the operator packet."""
    f = forecast if isinstance(forecast, dict) else {}
    return build_futurecast_operator_packet(
        forecast_id=str(f.get("forecast_id") or f.get("id") or ""),
        topic=str(f.get("topic") or f.get("claim") or ""),
        selected_horizon=str(f.get("horizon") or f.get("selected_horizon") or ""),
        allowed_horizons=f.get("allowed_horizons")
        if isinstance(f.get("allowed_horizons"), list)
        else None,
        probability=f.get("probability"),
        register=str(f.get("register") or "NOT_COMPUTABLE"),
        evidence_density=f.get("evidence_density"),
        outcome_value=f.get("outcome_value"),
        claim_text=str(f.get("claim_text") or f.get("claim") or ""),
        blocked_by=list(f.get("blocked_by") or [])
        if isinstance(f.get("blocked_by"), list)
        else None,
    )
