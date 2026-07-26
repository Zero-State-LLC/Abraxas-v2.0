from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash


def resolve_telemetry_hash(packet: dict[str, Any]) -> str:
    """Resolve a deterministic telemetry identity from observability/telemetry packets.

    Accepts:
    - top-level ``telemetry_hash``
    - ``ExecutionTelemetryPacket.telemetry_id`` (``out/telemetry/latest.json``)
    - nested ``projection_snapshot.telemetry_hash`` (``ObservabilityAggregation.v1``)
    - nested ``telemetry.telemetry_id`` / canonical hash of nested ``telemetry``

    Missing or placeholder ``\"unknown\"`` values fail closed so distinct inputs
    cannot collapse into one shared hash.
    """
    if not isinstance(packet, dict):
        raise TypeError("telemetry packet must be a dict")

    for key in ("telemetry_hash", "telemetry_id"):
        value = packet.get(key)
        if isinstance(value, str):
            normalized = value.strip()
            if normalized and normalized != "unknown":
                return normalized

    snapshot = packet.get("projection_snapshot")
    if isinstance(snapshot, dict):
        nested = snapshot.get("telemetry_hash")
        if isinstance(nested, str):
            normalized = nested.strip()
            if normalized and normalized != "unknown":
                return normalized

    telemetry = packet.get("telemetry")
    if isinstance(telemetry, dict) and telemetry:
        nested_id = telemetry.get("telemetry_id")
        if isinstance(nested_id, str):
            normalized = nested_id.strip()
            if normalized and normalized != "unknown":
                return normalized
        return canonical_hash(telemetry)

    raise ValueError("telemetry hash missing; refuse unknown fallback")
