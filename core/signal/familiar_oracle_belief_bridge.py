"""Familiar spine → Oracle/BeliefGraph SHADOW bridge (advisory only).

Closes abx-familiar residual: bridge FamiliarIngestionReceipt / spine touchpoint
to oracle intake seeds and belief candidate seeds without runtime mutation.

Does not:
- invoke Oracle runtime or queues
- mutate BeliefGraph / claim truth
- grant promotion, forecast routing, or execution authority
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash
from core.signal.spine_bridge import (
    build_familiar_spine_touchpoint,
    build_touchpoint_from_pack_path,
)

SCHEMA_VERSION = "FamiliarOracleBeliefBridge.v0"
PIPELINE_ID = "familiar_ingestion"
DETERMINISTIC_TIMESTAMP = "familiar_oracle_belief_bridge_v0_ts_0"
DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "promotion_authorized": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
}
PRODUCER = {
    "module": "core.signal.familiar_oracle_belief_bridge",
    "skill_id": "abx-familiar-signal-forager",
    "upstream": "core.signal.spine_bridge",
}


def _finalize(body: dict[str, Any]) -> dict[str, Any]:
    sealed = dict(body)
    sealed.pop("bridge_hash", None)
    sealed["bridge_hash"] = canonical_hash(sealed)
    return sealed


def _belief_seeds_from_touchpoint(touchpoint: dict[str, Any]) -> list[dict[str, Any]]:
    """Emit non-mutating belief candidate seeds from touchpoint payload."""
    if touchpoint.get("route") != "ORACLE_SHADOW_CANDIDATE":
        return []

    input_seed = touchpoint.get("input_payload_seed") or {}
    if not isinstance(input_seed, dict):
        input_seed = {}
    pack_id = str(touchpoint.get("pack_id") or input_seed.get("pack_id") or "")
    topic = str(input_seed.get("topic") or "")
    counts = input_seed.get("register_counts") or touchpoint.get("register_counts") or {}
    if not isinstance(counts, dict):
        counts = {}
    summaries = input_seed.get("source_summaries") or []
    if not isinstance(summaries, list):
        summaries = []

    seeds: list[dict[str, Any]] = []
    # One aggregate seed per non-zero register tier (deterministic order)
    for register in ("OBSERVED", "INFERRED", "SPECULATIVE", "NOT_COMPUTABLE"):
        n = int(counts.get(register) or 0)
        if n <= 0:
            continue
        seeds.append(
            {
                "seed_id": f"bseed_{pack_id or 'pack'}_{register.lower()}",
                "register": register,
                "claim_count_hint": n,
                "statement_hint": (
                    f"{topic}: {n} {register} claim(s) from EvidencePack.v0"
                    if topic
                    else f"{n} {register} claim(s) from EvidencePack.v0"
                ),
                "evidence_pack_ref": pack_id,
                "source_count_hint": int(input_seed.get("source_count") or len(summaries) or 0),
                "truth_assignment": False,
                "belief_promotion": False,
                "advisory_only": True,
            }
        )

    # Source-title seeds (bounded, sorted) for operator review legibility
    for src in sorted(
        [s for s in summaries if isinstance(s, dict)],
        key=lambda s: str(s.get("source_id") or ""),
    )[:8]:
        sid = str(src.get("source_id") or "")
        if not sid:
            continue
        title = str(src.get("title") or sid)
        seeds.append(
            {
                "seed_id": f"bseed_src_{sid}",
                "register": "OBSERVED",
                "claim_count_hint": 1,
                "statement_hint": f"source:{title}",
                "evidence_pack_ref": pack_id,
                "source_id": sid,
                "source_class": str(src.get("source_class") or "unknown"),
                "truth_assignment": False,
                "belief_promotion": False,
                "advisory_only": True,
            }
        )
    return seeds


def _oracle_shadow_intake(touchpoint: dict[str, Any]) -> dict[str, Any]:
    """Map oracle_candidate_seed → advisory intake seed (no queue write)."""
    if touchpoint.get("route") != "ORACLE_SHADOW_CANDIDATE":
        return {}

    oc = touchpoint.get("oracle_candidate_seed") or {}
    if not isinstance(oc, dict):
        oc = {}
    payload = str(oc.get("payload") or "")
    source_id = str(oc.get("source_id") or f"familiar:{touchpoint.get('pack_id') or 'unknown'}")
    payload_hash = canonical_hash(
        {
            "source_id": source_id,
            "payload": payload,
            "pack_id": touchpoint.get("pack_id"),
            "pack_hash": touchpoint.get("pack_hash"),
        }
    )
    return {
        "schema_hint": "OracleIntakeEnvelope.v1_shadow_seed",
        "intake_status": "pending",
        "source_id": source_id,
        # Map evidence_pack seed into OracleIntakeEnvelope-compatible source_type
        "source_type": "receipt",
        "source_hash": str(touchpoint.get("pack_hash") or payload_hash),
        "raw_payload_hash": payload_hash,
        "payload": payload,
        "topic": (touchpoint.get("input_payload_seed") or {}).get("topic")
        if isinstance(touchpoint.get("input_payload_seed"), dict)
        else None,
        "pack_id": touchpoint.get("pack_id"),
        "pack_hash": touchpoint.get("pack_hash"),
        "touchpoint_id": touchpoint.get("touchpoint_id"),
        "advisory_only": True,
        "forecast_authority": False,
        "queue_write_authorized": False,
        "runtime_invoke_authorized": False,
    }


def build_familiar_oracle_belief_bridge(
    touchpoint: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build bridge packet from a FamiliarSpineTouchpoint (or None)."""
    if touchpoint is None:
        return _finalize(
            {
                "schema_version": SCHEMA_VERSION,
                "bridge_id": "fobb_no_touchpoint",
                "pipeline_id": PIPELINE_ID,
                "touchpoint_id": "",
                "receipt_id": "",
                "pack_id": "",
                "pack_hash": "",
                "route": "ABSTAIN_NO_INPUT",
                "status": "BRIDGE_NO_INPUT",
                "reason": "no_touchpoint",
                "oracle_shadow_intake": {},
                "belief_candidate_seeds": [],
                "register_counts": {},
                "commercial_claims_blocked": True,
                "evidence_density": 0.1,
                "advisory_only": True,
                "lane": "SHADOW",
                "authority": dict(DEFAULT_AUTHORITY),
                "producer": dict(PRODUCER),
                "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
            }
        )

    route = str(touchpoint.get("route") or "ABSTAIN_NO_INPUT")
    if route == "ORACLE_SHADOW_CANDIDATE":
        status = "BRIDGED_SHADOW"
        reason = "spine_touchpoint_oracle_shadow_candidate"
    elif route == "ABSTAIN_NO_INPUT":
        status = "BRIDGE_NO_INPUT"
        reason = str(touchpoint.get("reason") or "abstain_no_input")
    else:
        status = "BRIDGE_ABSTAINED"
        reason = str(touchpoint.get("reason") or f"abstain:{route}")

    pack_hash = str(touchpoint.get("pack_hash") or "")
    bridge_id = f"fobb_{(pack_hash or touchpoint.get('touchpoint_id') or 'empty')[:16]}"

    return _finalize(
        {
            "schema_version": SCHEMA_VERSION,
            "bridge_id": bridge_id,
            "pipeline_id": PIPELINE_ID,
            "touchpoint_id": str(touchpoint.get("touchpoint_id") or ""),
            "receipt_id": str(touchpoint.get("receipt_id") or ""),
            "pack_id": str(touchpoint.get("pack_id") or ""),
            "pack_hash": pack_hash,
            "route": route
            if route
            in {
                "ORACLE_SHADOW_CANDIDATE",
                "ABSTAIN_INVALID",
                "ABSTAIN_NO_INPUT",
                "ABSTAIN_NOT_INGESTED",
            }
            else "ABSTAIN_NOT_INGESTED",
            "status": status,
            "reason": reason,
            "oracle_shadow_intake": _oracle_shadow_intake(touchpoint),
            "belief_candidate_seeds": _belief_seeds_from_touchpoint(touchpoint),
            "register_counts": dict(touchpoint.get("register_counts") or {})
            if isinstance(touchpoint.get("register_counts"), dict)
            else {},
            "commercial_claims_blocked": bool(
                touchpoint.get("commercial_claims_blocked", True)
            ),
            "evidence_density": float(touchpoint.get("evidence_density") or 0.1),
            "advisory_only": True,
            "lane": "SHADOW",
            "authority": dict(DEFAULT_AUTHORITY),
            "producer": dict(PRODUCER),
            "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
            "blockers": list(touchpoint.get("blockers") or [])
            if isinstance(touchpoint.get("blockers"), list)
            else [],
        }
    )


def build_bridge_from_receipt(receipt: dict[str, Any] | None) -> dict[str, Any]:
    """Receipt → touchpoint → bridge (pure)."""
    tp = build_familiar_spine_touchpoint(receipt)
    return build_familiar_oracle_belief_bridge(tp)


def build_bridge_from_pack_path(
    path: str | Path,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Pack path → receipt → touchpoint → bridge (pure)."""
    tp = build_touchpoint_from_pack_path(path, repo_root=repo_root)
    return build_familiar_oracle_belief_bridge(tp)
