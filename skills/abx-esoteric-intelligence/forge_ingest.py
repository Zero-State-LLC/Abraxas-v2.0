"""Map a Sigil-Forge genotype into a SHADOW ingest envelope.

Public envelope carries digests and method labels only — never plaintext
intent. EvidencePack.v0 is attached as a kernel-path seed; producer is the
esoteric adapter, not the familiar forager.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict

import alife_adapter as alife
import proof_of_intent
import sigil_forge_bridge as bridge


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


def from_intent(text: str, request_id: str = "sigil-forge-ingest") -> Dict[str, Any]:
    genotype = alife.build_sigil_genotype(text, {"request_id": request_id})
    core = genotype["genotype"]
    digest = core["intent_digest"]
    envelope_id = f"sfe-{digest[:16]}"
    claim_class = genotype.get("claim_class", "COMPUTED")
    register = "NOT_COMPUTABLE" if claim_class == "NOT_COMPUTABLE" else "INFERRED"
    primitives = core.get("primitives") or []
    claim_text = (
        f"Spare letter_monogram bound {len(primitives)} primitives to intent_digest; "
        f"engine={core.get('engine')}; construction={core.get('construction')}."
    )
    if claim_class == "NOT_COMPUTABLE":
        claim_text = core.get("reason") or "NOT_COMPUTABLE: no surviving Spare consonants"
    normalized = bridge.normalize_intent(text)
    poi = proof_of_intent.public_surface(
        normalized=normalized,
        digest=digest,
        construction=str(core.get("construction") or ""),
        engine=str(core.get("engine") or ""),
    )
    pack = {
        "schema_version": "EvidencePack.v0",
        "pack_id": envelope_id,
        "topic": "sigil-forge intent compression",
        "intent": "other",
        "must_answer": [
            "What is the intent_digest?",
            "Which construction family produced the genotype?",
        ],
        "hard_exclusions": [
            "plaintext intent",
            "efficacy claims",
            "forecast weight",
            "canon mutation",
        ],
        "sources": [
            {
                "source_id": "src-sigil-forge-adapter",
                "url_or_path": "skills/abx-esoteric-intelligence/sigil_forge_bridge.py",
                "title": "Sigil-Forge Abraxas bridge",
                "source_class": "code",
                "excerpt": "Deterministic Spare letter_monogram + optional forge_core.",
            },
            {
                "source_id": "src-sigil-forge-engine",
                "url_or_path": "scripts/forge_core.py",
                "title": "Sigil-Forge forge_core",
                "source_class": "code",
                "excerpt": "Pure intent → digest/geometry; no filesystem; public leaves only.",
            },
        ],
        "claims": [
            {
                "claim_id": "c-digest",
                "text": f"intent_digest={digest}",
                "register": register,
                "source_ids": ["src-sigil-forge-adapter", "src-sigil-forge-engine"],
                "join_logic": (
                    "SHA-256 of normalized intent; adapter and forge_core share the digest."
                    if register == "INFERRED"
                    else None
                ),
                "confidence_note": "SHA-256 of normalized intent; plaintext omitted",
            },
            {
                "claim_id": "c-genotype",
                "text": claim_text,
                "register": register,
                "source_ids": ["src-sigil-forge-adapter", "src-sigil-forge-engine"],
                "join_logic": (
                    "Same construction run: primitives from Spare letter_monogram bound to digest."
                    if register == "INFERRED"
                    else None
                ),
            },
        ],
        "authority": _denied_authority(),
        "provenance": {
            "producer_system": "MIXED",
            "skill_id": "abx-esoteric-intelligence",
            "tool_trace_summary": "sigil-forge genotype → ForgeIngestEnvelope.v1",
            "notes": "Agent-agnostic adapter. Not a familiar-forager pack. SHADOW only.",
        },
        "observed_source_count": 2,
        "register_counts": {
            "OBSERVED": 0,
            "INFERRED": 2 if register == "INFERRED" else 0,
            "SPECULATIVE": 0,
            "NOT_COMPUTABLE": 2 if register == "NOT_COMPUTABLE" else 0,
        },
    }
    return {
        "schema_version": "ForgeIngestEnvelope.v1",
        "envelope_id": envelope_id,
        "specialist_id": "sigil-forge",
        "request_id": request_id,
        "lane": "SHADOW",
        "claim_class": claim_class,
        "intent_digest": digest,
        "sigil_root": poi["sigil_root"],
        "sigil_root_scope": poi["sigil_root_scope"],
        "intent_commitment": poi["intent_commitment"],
        "zk_provenance": poi["zk_provenance"],
        "construction": core.get("construction"),
        "engine": core.get("engine"),
        "compatible_runes": core.get("compatible_runes", []),
        "plaintext_intent_in_public": False,
        "genotype": {
            "construction": core.get("construction"),
            "primitives_len": len(primitives),
            "intent_digest": digest,
            "engine": core.get("engine"),
            "variant_classification": genotype.get("variant_classification"),
        },
        "specialist_features": {
            "intent_digest": digest,
            "sigil_root": poi["sigil_root"],
            "construction": core.get("construction"),
            "engine": core.get("engine"),
            "primitives_len": len(primitives),
            "square_name": core.get("square_name"),
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


def inspect_projection(envelope: Dict[str, Any]) -> Dict[str, Any]:
    """AAL-Viz inspect chips. Projection only — no geometry restyle."""
    poi = envelope.get("zk_provenance") or {}
    root = envelope.get("sigil_root")
    return {
        "schema_version": "ForgeInspectProjection.v1",
        "lane": envelope.get("lane", "SHADOW"),
        "specialist_id": envelope.get("specialist_id", "sigil-forge"),
        "chips": {
            "engine": envelope.get("engine") or "unknown",
            "construction": envelope.get("construction") or "unknown",
            "proof": poi.get("status") or "skipped",
            "authority": "SHADOW",
        },
        "intent_digest_prefix": (envelope.get("intent_digest") or "")[:16] or None,
        "sigil_root_prefix": (root or "")[:16] or None,
        "authority_visible": True,
        "geometry_redrawn": False,
    }
