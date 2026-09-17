"""SHADOW kernel run: forge envelope → familiar ingest → spine → oracle/belief bridge.

Does not write Oracle queues, mutate BeliefGraph, or grant forecast/canon.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import forge_ingest
from core.ingest.familiar_ingestion_receipt import build_familiar_ingestion_receipt
from core.signal.evidence_pack import validate_evidence_pack
from core.signal.familiar_oracle_belief_bridge import build_familiar_oracle_belief_bridge
from core.signal.spine_bridge import build_familiar_spine_touchpoint

SCHEMA_VERSION = "ForgeKernelRun.v1"
_DENIED = {
    "execution_authority": False,
    "promotion_authorized": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


PUBLIC_FEATURE_KEYS = (
    "specialist_id",
    "intent_digest",
    "construction",
    "engine",
    "primitives_len",
    "square_name",
    "sigil_root",
    "sigil_root_scope",
)


def public_feature_record(envelope: dict[str, Any]) -> dict[str, Any]:
    """v2 training features: public leaves only. Never plaintext or nonce."""
    feats = dict(envelope.get("specialist_features") or {})
    return {
        "schema_version": "SpecialistFeatureRecord.v1",
        "specialist_id": envelope.get("specialist_id") or "sigil-forge",
        "lane": "SHADOW",
        "intent_digest": feats.get("intent_digest") or envelope.get("intent_digest"),
        "construction": feats.get("construction") or envelope.get("construction"),
        "engine": feats.get("engine") or envelope.get("engine"),
        "primitives_len": feats.get("primitives_len"),
        "square_name": feats.get("square_name"),
        "sigil_root": feats.get("sigil_root") or envelope.get("sigil_root"),
        "sigil_root_scope": envelope.get("sigil_root_scope"),
        "plaintext_intent": False,
    }


def run_shadow_kernel(
    text: str,
    *,
    request_id: str = "sigil-forge-kernel",
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or _repo_root()
    envelope = forge_ingest.from_intent(text, request_id=request_id)
    pack = envelope["evidence_pack"]
    errors = validate_evidence_pack(pack, repo_root=root)
    receipt = build_familiar_ingestion_receipt(
        pack,
        pack_ref=f"forge:{envelope.get('envelope_id')}",
        repo_root=root,
    )
    touchpoint = build_familiar_spine_touchpoint(receipt)
    bridge = build_familiar_oracle_belief_bridge(touchpoint)
    inspect = forge_ingest.inspect_projection(envelope)
    return {
        "schema_version": SCHEMA_VERSION,
        "lane": "SHADOW",
        "specialist_id": "sigil-forge",
        "envelope": envelope,
        "pack_validation_errors": errors,
        "ingestion_receipt": receipt,
        "spine_touchpoint": touchpoint,
        "oracle_belief_bridge": bridge,
        "inspect_projection": inspect,
        "authority": dict(_DENIED),
        "advisory_only": True,
    }
