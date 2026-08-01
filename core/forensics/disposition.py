"""ForensicDispositionPacket.v0 from EvidencePack + PropagationGraph. SHADOW only."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from core.canonical.json import canonical_hash

SCHEMA_VERSION = "ForensicDispositionPacket.v0"

DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "forecast_weight_allowed": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
    "publish_authorized": False,
    "queue_write_authorized": False,
}

REGISTER_KEYS = ("OBSERVED", "INFERRED", "SPECULATIVE", "NOT_COMPUTABLE")


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _pack_content(pack: Mapping[str, Any]) -> tuple[str, list[Any], list[Any]]:
    pack_id = str(pack.get("pack_id") or "")
    sources = _as_list(pack.get("sources"))
    claims = _as_list(pack.get("claims"))
    return pack_id, sources, claims


def _register_counts(
    pack: Mapping[str, Any] | None,
    override: Mapping[str, int] | None,
) -> dict[str, int]:
    if override is not None:
        return {str(k): int(v) for k, v in override.items()}
    counts = {k: 0 for k in REGISTER_KEYS}
    if not isinstance(pack, Mapping):
        return counts
    existing = pack.get("register_counts")
    if isinstance(existing, Mapping) and existing:
        out = {k: 0 for k in REGISTER_KEYS}
        for k, v in existing.items():
            try:
                out[str(k)] = int(v)
            except (TypeError, ValueError):
                continue
        return out
    for claim in _as_list(pack.get("claims")):
        if not isinstance(claim, dict):
            continue
        reg = str(claim.get("register") or "NOT_COMPUTABLE")
        counts[reg] = counts.get(reg, 0) + 1
    return counts


def _source_pack_hash(pack: Mapping[str, Any] | None) -> str:
    if not isinstance(pack, Mapping):
        return ""
    return canonical_hash(dict(pack))


def build_forensic_disposition(
    *,
    pack: Mapping[str, Any] | None,
    propagation: Mapping[str, Any] | None,
    bridge_status: str = "",
    receipt_status: str = "",
    register_counts: Mapping[str, int] | None = None,
    extra_blocked_by: Sequence[str] | None = None,
    extra_authority_violations: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Build ForensicDispositionPacket.v0. Never grants publish or auto-opens ops."""
    blocked_by: list[str] = []
    failed_gates: list[str] = []
    authority_violations: list[str] = [
        str(v) for v in (extra_authority_violations or []) if str(v)
    ]
    if extra_blocked_by:
        blocked_by.extend(str(b) for b in extra_blocked_by if str(b))

    pack_id = ""
    sources: list[Any] = []
    claims: list[Any] = []
    has_content = False
    invalid_pack = not isinstance(pack, Mapping)

    if isinstance(pack, Mapping):
        pack_id, sources, claims = _pack_content(pack)
        has_content = bool(sources) or bool(claims)
        if not pack_id and not has_content:
            invalid_pack = True
    else:
        invalid_pack = True

    counts = _register_counts(pack if isinstance(pack, Mapping) else None, register_counts)
    source_hash = _source_pack_hash(pack if isinstance(pack, Mapping) else None)

    prop_map = propagation if isinstance(propagation, Mapping) else None
    node_count = int(prop_map.get("node_count", 0)) if prop_map is not None else 0
    prop_hash = str(prop_map.get("canonical_hash") or "") if prop_map is not None else ""
    prop_missing = prop_map is None or node_count == 0

    inputs: list[dict[str, str]] = [
        {"kind": "pack", "hash": source_hash},
        {"kind": "propagation", "hash": prop_hash},
        {"kind": "bridge", "status": str(bridge_status or "")},
        {"kind": "receipt", "status": str(receipt_status or "")},
    ]

    if invalid_pack or (isinstance(pack, Mapping) and not has_content and not pack_id):
        disposition = "NOT_COMPUTABLE"
        blocked_by = list(dict.fromkeys([*blocked_by, "NO_PACK"]))
        failed_gates.append("pack")
        ops_gate_hint = "DENIED"
    elif not has_content:
        # pack_id present but empty forensic content
        disposition = "NOT_COMPUTABLE"
        blocked_by = list(dict.fromkeys([*blocked_by, "NO_PACK"]))
        failed_gates.append("pack")
        ops_gate_hint = "DENIED"
    elif prop_missing:
        disposition = "HOLD"
        blocked_by = list(dict.fromkeys([*blocked_by, "PROPAGATION_REQUIRED"]))
        failed_gates.append("propagation")
        ops_gate_hint = "DENIED"
    elif authority_violations:
        disposition = "HOLD"
        blocked_by = list(dict.fromkeys([*blocked_by, "AUTHORITY_LEAK"]))
        failed_gates.append("authority")
        ops_gate_hint = "DENIED"
    elif blocked_by:
        disposition = "HOLD"
        failed_gates.append("blocked_by")
        ops_gate_hint = "DENIED"
    else:
        disposition = "READY"
        ops_gate_hint = "WOULD_ALLOW_IF_OPERATOR"

    # Identity before hash: deterministic from pack + disposition + prop hash
    id_material = {
        "schema_version": SCHEMA_VERSION,
        "pack_id": pack_id,
        "source_pack_hash": source_hash,
        "propagation_hash": prop_hash,
        "disposition": disposition,
        "bridge_status": str(bridge_status or ""),
        "receipt_status": str(receipt_status or ""),
    }
    id_hash = canonical_hash(id_material)
    disposition_id = f"fd:{pack_id or 'none'}:{id_hash[:16]}"

    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "disposition_id": disposition_id,
        "pack_id": pack_id,
        "source_pack_hash": source_hash,
        "register_counts": counts,
        "disposition": disposition,
        "blocked_by": blocked_by,
        "failed_gates": failed_gates,
        "inputs": inputs,
        "authority": dict(DEFAULT_AUTHORITY),
        "authority_violations": authority_violations,
        "ops_gate_hint": ops_gate_hint,
        "bridge_status": str(bridge_status or ""),
        "receipt_status": str(receipt_status or ""),
        "advisory_only": True,
        "lane": "SHADOW",
    }
    body["canonical_hash"] = canonical_hash(body)
    return body
