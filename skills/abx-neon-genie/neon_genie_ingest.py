"""Map a Neon Genie cycle into a SHADOW ingest envelope.

Invention router, not a specialist model. Public pack carries overlap class,
honest score features, and seed digest — not a ranker, not forecast.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

SCHEMA_VERSION = "NeonGenieIngestEnvelope.v1"


def _denied_authority() -> Dict[str, Any]:
    return {
        "execution_authority": False,
        "promotion_authorized": False,
        "forecast_routing_authorized": False,
        "canon_mutation_allowed": False,
        "forecast_authority": False,
        "canon_authority": False,
        "lane": "SHADOW",
    }


def _seed_digest(request: Dict[str, Any]) -> str:
    raw = json.dumps(request, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def from_cycle(
    receipt: Dict[str, Any],
    request: Dict[str, Any],
    *,
    request_id: str = "neon-genie-ingest",
) -> Dict[str, Any]:
    digest = _seed_digest(request)
    envelope_id = f"nge-{digest[:16]}"
    vp = receipt.get("venture_packet") if isinstance(receipt.get("venture_packet"), dict) else {}
    score = vp.get("score_vector") if isinstance(vp.get("score_vector"), dict) else {}
    overlap = str(receipt.get("overlap_classification") or vp.get("overlap_classification") or "NOT_COMPUTABLE")
    density = (score.get("evidence_density") or {}).get("value")
    pack = {
        "schema_version": "EvidencePack.v0",
        "pack_id": envelope_id,
        "topic": "neon genie ideation",
        "intent": "other",
        "must_answer": [
            "What is the overlap classification?",
            "Is overall score NOT_COMPUTABLE without neon.rank?",
        ],
        "hard_exclusions": [
            "forecast weight",
            "canon mutation",
            "execution authority",
            "trained ranker claim",
        ],
        "sources": [
            {
                "source_id": "src-neon-genie-router",
                "url_or_path": "skills/abx-neon-genie/neon_genie_router.py",
                "title": "Neon Genie umbrella router",
                "source_class": "code",
                "excerpt": "Invention cycle: intake → discover → recombine → score → package.",
            },
            {
                "source_id": "src-neon-genie-score",
                "url_or_path": "skills/abx-neon-genie/neon_genie_score.py",
                "title": "Neon Genie honest score vector",
                "source_class": "code",
                "excerpt": "Ranker is none. overall/novelty axes NOT_COMPUTABLE.",
            },
        ],
        "claims": [
            {
                "claim_id": "c-overlap",
                "text": f"overlap_classification={overlap}",
                "register": "INFERRED",
                "source_ids": ["src-neon-genie-router", "src-neon-genie-score"],
                "join_logic": "Cycle receipt overlap class plus honest score_vector on the same packet.",
                "confidence_note": "Overlap detector is a stub inventory, not OBSERVED uniqueness.",
            },
            {
                "claim_id": "c-score",
                "text": "overall score NOT_COMPUTABLE; ranker=none",
                "register": "NOT_COMPUTABLE",
                "source_ids": ["src-neon-genie-score"],
                "join_logic": None,
                "confidence_note": "No neon.rank model. Features only.",
            },
        ],
        "authority": _denied_authority(),
        "provenance": {
            "producer_system": "MIXED",
            "skill_id": "abx-neon-genie",
            "tool_trace_summary": "neon-genie cycle → NeonGenieIngestEnvelope.v1",
            "notes": "Invention router. Not a specialist model. SHADOW only.",
        },
        "observed_source_count": 2,
        "register_counts": {
            "OBSERVED": 0,
            "INFERRED": 1,
            "SPECULATIVE": 0,
            "NOT_COMPUTABLE": 1,
        },
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "envelope_id": envelope_id,
        "invention_router_id": "neon-genie",
        "not_a_specialist_model": True,
        "request_id": request_id,
        "lane": "SHADOW",
        "seed_digest": digest,
        "input_mode": receipt.get("input_mode"),
        "overlap_classification": overlap,
        "venture_name": vp.get("venture_name"),
        "ranker": score.get("ranker") or "none",
        "score_vector": score,
        "specialist_features": {
            "seed_digest": digest,
            "overlap_classification": overlap,
            "evidence_density": density,
            "commercial_claims_blocked": bool(receipt.get("commercial_claims_blocked", True)),
            "ranker": "none",
            "input_mode": receipt.get("input_mode"),
        },
        "evidence_pack": pack,
        "authority": {
            "forecast_authority": False,
            "canon_authority": False,
            "execution_authority": False,
            "truth_authority": False,
            "promotion_authorized": False,
        },
        "envelope_hash": hashlib.sha256(digest.encode("utf-8")).hexdigest(),
    }
