"""MemeticOpsRouteIntent.v0 — SHADOW route intent; OpsGate remains DENIED.

Maps forensic disposition to Level 99 / Neon *seed* targets only.
Never grants execution or publish.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash
from core.forensics.pipeline import run_forensics_from_pack_path

SCHEMA_VERSION = "MemeticOpsRouteIntent.v0"

DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "forecast_weight_allowed": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
    "publish_authorized": False,
    "queue_write_authorized": False,
}


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _hex64(value: Any) -> str:
    if isinstance(value, str) and len(value) == 64:
        return value
    return ""


def build_memetic_ops_route_intent(
    run: Mapping[str, Any] | None,
    *,
    prefer_neon: bool = False,
) -> dict[str, Any]:
    """Build MemeticOpsRouteIntent.v0 from ForensicRunPacket (or None).

    READY → LEVEL99_CONTENT_SEED (or NEON if prefer_neon) with
    WOULD_ROUTE_IF_OPERATOR. Always ops_gate_status DENIED.
    execution_authorized and publish_authorized always false.
    """
    run_map = _as_mapping(run)
    disposition = _as_mapping(run_map.get("disposition"))
    disp_value = str(disposition.get("disposition") or "")
    if disp_value not in {"READY", "HOLD", "NOT_COMPUTABLE"}:
        disp_value = ""

    if disp_value == "READY":
        if prefer_neon:
            route_intent = "NEON_IDEATION_SEED"
            target = "neon_genie_ideation"
        else:
            route_intent = "LEVEL99_CONTENT_SEED"
            target = "level99_content"
        route_status = "WOULD_ROUTE_IF_OPERATOR"
    else:
        route_intent = "NONE"
        target = ""
        route_status = "BLOCKED"

    pack_id = run_map.get("pack_id")
    if pack_id is not None and not isinstance(pack_id, str):
        pack_id = str(pack_id)

    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "route_intent": route_intent,
        "route_status": route_status,
        "ops_gate_status": "DENIED",
        "disposition": disp_value,
        "source_run_hash": _hex64(run_map.get("canonical_hash")),
        "source_disposition_hash": _hex64(disposition.get("canonical_hash")),
        "pack_id": pack_id,
        "target_pipeline": target,
        "execution_authorized": False,
        "publish_authorized": False,
        "advisory_only": True,
        "lane": "SHADOW",
        "authority": dict(DEFAULT_AUTHORITY),
    }
    body["canonical_hash"] = canonical_hash(body)
    return body


def build_memetic_ops_route_intent_from_pack_path(
    path: str | Path,
    *,
    repo_root: str | Path | None = None,
    prefer_neon: bool = False,
) -> dict[str, Any]:
    """Pack path → forensics run → route intent."""
    run = run_forensics_from_pack_path(path, repo_root=repo_root)
    return build_memetic_ops_route_intent(run, prefer_neon=prefer_neon)
