"""ForensicLevel99Seed.v0 — seed Level99 content packet from forensics route.

SHADOW only. OpsGate remains DENIED. Never auto-publishes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash
from core.forensics.ops_route import build_memetic_ops_route_intent
from core.forensics.pipeline import run_forensics_from_pack_path
from core.level99.content_operator_packet import build_content_operator_packet

SCHEMA_VERSION = "ForensicLevel99Seed.v0"

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


def _load_pack(path: str | Path) -> dict[str, Any]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError(
            f"EvidencePack root must be a JSON object, got {type(raw).__name__}"
        )
    return raw


def _seed_content_packet(pack: Mapping[str, Any]) -> dict[str, Any]:
    pack_id = str(pack.get("pack_id") or "pack_unspecified")
    topic = str(pack.get("topic") or "").strip() or "UNTITLED"
    intent = str(pack.get("intent") or "").strip().lower()
    # Tech packs → thread; default unknown format (no media metrics claimed)
    format_target = "thread" if intent in {"tech", "research", "docs"} else "unknown"
    return build_content_operator_packet(
        content_id=f"forensic_seed:{pack_id}",
        topic=topic,
        format_target=format_target,
        humor_gradient=0,
        metrics_present=False,
        blocked_by=[
            "AUTO_PUBLISH_BLOCKED",
            "PLATFORM_MUTATION_BLOCKED",
            "PROMOTION_BLOCKED",
            "FORENSIC_SEED_ONLY",
        ],
    )


def build_forensic_level99_seed(
    run: Mapping[str, Any] | None,
    pack: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Compose route intent + optional Level99 content packet seed."""
    intent = build_memetic_ops_route_intent(run)
    route_intent = str(intent.get("route_intent") or "NONE")
    disposition = str(intent.get("disposition") or "")

    content_packet: dict[str, Any] | None = None
    content_hash = ""
    seed_status = "BLOCKED"

    if route_intent == "LEVEL99_CONTENT_SEED" and isinstance(pack, Mapping):
        content_packet = _seed_content_packet(pack)
        content_hash = _hex64(content_packet.get("canonical_hash"))
        seed_status = "SEEDED"

    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "seed_status": seed_status,
        "route_intent": route_intent,
        "route_status": intent.get("route_status"),
        "ops_gate_status": "DENIED",
        "disposition": disposition,
        "pack_id": intent.get("pack_id"),
        "source_run_hash": _hex64(intent.get("source_run_hash")),
        "route_intent_hash": _hex64(intent.get("canonical_hash")),
        "content_packet": content_packet,
        "content_packet_hash": content_hash,
        "target_pipeline": intent.get("target_pipeline") or "",
        "execution_authorized": False,
        "publish_authorized": False,
        "advisory_only": True,
        "lane": "SHADOW",
        "authority": dict(DEFAULT_AUTHORITY),
    }
    body["canonical_hash"] = canonical_hash(body)
    return body


def build_forensic_level99_seed_from_pack_path(
    path: str | Path,
    *,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Pack path → forensics run → Level99 seed envelope."""
    p = Path(path)
    pack = _load_pack(p)
    run = run_forensics_from_pack_path(p, repo_root=repo_root)
    return build_forensic_level99_seed(run, pack)
