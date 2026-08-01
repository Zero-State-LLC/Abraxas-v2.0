"""ForensicRunPacket.v0 orchestrator: EvidencePack path → disposition + denied ops gate.

SHADOW advisory only. No network. No queue/brier/social writes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash
from core.forensics.disposition import build_forensic_disposition
from core.forensics.ops_gate import build_memetic_ops_gate
from core.forensics.propagation_graph import build_propagation_graph_from_pack
from core.signal.familiar_oracle_belief_bridge import build_bridge_from_pack_path

SCHEMA_VERSION = "ForensicRunPacket.v0"

DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "forecast_weight_allowed": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
    "publish_authorized": False,
    "queue_write_authorized": False,
}

_OK_DISPOSITIONS = frozenset({"READY", "HOLD", "NOT_COMPUTABLE"})


def _resolve_pack_hash(pack: dict[str, Any], bridge: dict[str, Any]) -> str:
    """Prefer pack-native hash keys; else bridge pack_hash; else derive deterministically."""
    for key in ("pack_hash", "canonical_hash", "source_pack_hash"):
        value = pack.get(key)
        if isinstance(value, str) and value:
            return value
    bridge_hash = bridge.get("pack_hash")
    if isinstance(bridge_hash, str) and bridge_hash:
        return bridge_hash
    return canonical_hash(dict(pack))


def run_forensics_from_pack_path(
    path: str | Path,
    *,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Load EvidencePack from path and compose ForensicRunPacket.v0.

    Always returns ops_gate.gate_status == DENIED. Never grants authority.
    """
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    p = Path(path)
    pack = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(pack, dict):
        pack = {}

    bridge = build_bridge_from_pack_path(p, repo_root=root)
    if not isinstance(bridge, dict):
        bridge = {}

    prop = build_propagation_graph_from_pack(pack)
    disp = build_forensic_disposition(
        pack=pack,
        propagation=prop,
        bridge_status=str(bridge.get("status") or ""),
    )
    gate = build_memetic_ops_gate(disp)

    disposition_value = str(disp.get("disposition") or "")
    gate_status = str(gate.get("gate_status") or "")
    ok = disposition_value in _OK_DISPOSITIONS and gate_status == "DENIED"

    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "pack_path": str(p),
        "pack_id": pack.get("pack_id"),
        "pack_hash": _resolve_pack_hash(pack, bridge),
        "bridge_status": bridge.get("status"),
        "propagation": prop,
        "disposition": disp,
        "ops_gate": gate,
        "ok": ok,
        "advisory_only": True,
        "lane": "SHADOW",
        "authority": dict(DEFAULT_AUTHORITY),
    }
    body["canonical_hash"] = canonical_hash(body)
    return body
