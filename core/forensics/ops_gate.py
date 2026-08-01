"""MemeticOpsGate.v0 — always DENIED in slice C. SHADOW advisory only."""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash

SCHEMA_VERSION = "MemeticOpsGate.v0"


def build_memetic_ops_gate(
    disposition: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Build MemeticOpsGate.v0.

    gate_status is always DENIED. simulation is WOULD_ALLOW only when the
    disposition packet reports READY; otherwise WOULD_DENY. Never authorizes
    publish or execution.
    """
    disp_value = ""
    source_hash = ""
    hint = ""
    if isinstance(disposition, Mapping):
        disp_value = str(disposition.get("disposition") or "")
        raw_hash = disposition.get("canonical_hash")
        if isinstance(raw_hash, str) and len(raw_hash) == 64:
            source_hash = raw_hash
        hint = str(disposition.get("ops_gate_hint") or "")

    simulation = "WOULD_ALLOW" if disp_value == "READY" else "WOULD_DENY"

    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "gate_status": "DENIED",
        "simulation": simulation,
        "execution_authorized": False,
        "publish_authorized": False,
        "disposition": disp_value,
        "ops_gate_hint": hint,
        "source_disposition_hash": source_hash,
        "advisory_only": True,
        "lane": "SHADOW",
    }
    body["canonical_hash"] = canonical_hash(body)
    return body
