"""AALVizForensicProjection.v0 — SHADOW projection-only view of ForensicRunPacket.

Never opens OpsGate. Never grants authority. No network.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash
from core.forensics.pipeline import run_forensics_from_pack_path

SCHEMA_VERSION = "AALVizForensicProjection.v0"

DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "forecast_weight_allowed": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
    "publish_authorized": False,
    "queue_write_authorized": False,
}

_EMPTY_REGISTER_COUNTS = {
    "OBSERVED": 0,
    "INFERRED": 0,
    "SPECULATIVE": 0,
    "NOT_COMPUTABLE": 0,
}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _graph_summary(propagation: Mapping[str, Any]) -> dict[str, Any]:
    nodes = _as_list(propagation.get("nodes"))
    edges = _as_list(propagation.get("edges"))
    summary: dict[str, Any] = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "write_performed": False,
        "network_calls": False,
    }
    schema = propagation.get("schema_version")
    if isinstance(schema, str) and schema:
        summary["schema_version"] = schema
    return summary


def build_aal_viz_forensic_projection(
    run: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Build AALVizForensicProjection.v0 from a ForensicRunPacket (or None).

    Pure. Fail-closed: missing/invalid run → empty disposition, DENIED gate,
    zero graph. Always forces ops_gate_status DENIED.
    """
    run_map = _as_mapping(run)
    disposition = _as_mapping(run_map.get("disposition"))
    ops_gate = _as_mapping(run_map.get("ops_gate"))
    propagation = _as_mapping(run_map.get("propagation"))

    disp_value = str(disposition.get("disposition") or "")
    if disp_value not in {"READY", "HOLD", "NOT_COMPUTABLE"}:
        disp_value = ""

    simulation = str(ops_gate.get("simulation") or "")
    if simulation not in {"WOULD_ALLOW", "WOULD_DENY"}:
        simulation = "WOULD_ALLOW" if disp_value == "READY" else "WOULD_DENY"

    source_hash = ""
    raw_hash = run_map.get("canonical_hash")
    if isinstance(raw_hash, str) and len(raw_hash) == 64:
        source_hash = raw_hash

    blocked = disposition.get("blocked_by")
    blocked_by = [str(x) for x in blocked] if isinstance(blocked, list) else []

    register_counts = disposition.get("register_counts")
    if isinstance(register_counts, Mapping):
        counts = {str(k): int(v) for k, v in register_counts.items()}
    else:
        counts = dict(_EMPTY_REGISTER_COUNTS)

    pack_id = run_map.get("pack_id")
    if pack_id is not None and not isinstance(pack_id, str):
        pack_id = str(pack_id)

    projection_id = (
        f"aal_viz_forensic:{source_hash[:16]}"
        if source_hash
        else "aal_viz_forensic:empty"
    )

    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "projection_id": projection_id,
        "source_run_hash": source_hash,
        "pack_id": pack_id,
        "pack_path": str(run_map.get("pack_path") or ""),
        "disposition": disp_value,
        "ops_gate_status": "DENIED",
        "simulation": simulation,
        "ops_gate_hint": str(disposition.get("ops_gate_hint") or ""),
        "blocked_by": blocked_by,
        "register_counts": counts,
        "graph_summary": _graph_summary(propagation),
        "bridge_status": run_map.get("bridge_status"),
        "projection_only": True,
        "advisory_only": True,
        "render_consumer_only": True,
        "non_authoritative": True,
        "lane": "SHADOW",
        "authority": dict(DEFAULT_AUTHORITY),
    }
    body["canonical_hash"] = canonical_hash(body)
    return body


def build_aal_viz_forensic_projection_from_pack_path(
    path: str | Path,
    *,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Pack path → ForensicRunPacket → AALVizForensicProjection.v0."""
    run = run_forensics_from_pack_path(path, repo_root=repo_root)
    return build_aal_viz_forensic_projection(run)
