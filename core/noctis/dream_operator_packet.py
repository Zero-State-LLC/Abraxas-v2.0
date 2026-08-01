"""Noctis dream operator packet — IR + SHADOW operator review receipt.

Closes noctis_dream MISSING_CONTRACT at the operator-packet / IR layer.
Does not diagnose, forecast, write durable memory, or mutate canon.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

from core.canonical.json import canonical_hash

SCHEMA_VERSION = "NoctisDreamOperatorPacket.v0"
IR_SCHEMA_VERSION = "NoctisDreamIR.v0"
PIPELINE_ID = "noctis_dream"
DETERMINISTIC_TIMESTAMP = "noctis_dream_operator_packet_v0_ts_0"

MODES = frozenset(
    {
        "HUMAN_DREAM",
        "SYSTEM_DREAM",
        "DREAM_HISTORY_REVIEW",
        "ARTIFACT_INTENT",
        "PROBE_CANDIDATE",
        "PROJECTION_ONLY",
        "UNKNOWN",
    }
)
PRIVACY_TIERS = frozenset({"PRIVATE", "RESEARCH", "PUBLIC_SYNTHETIC", "UNKNOWN"})
SOURCES = frozenset({"USER", "EXTERNAL", "SYSTEM", "UNKNOWN"})

DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "promotion_authorized": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
    "medical_claims_allowed": False,
    "memory_direct_write_allowed": False,
}

PRODUCER = {
    "module": "core.noctis.dream_operator_packet",
    "skill_id": "abx-noctis-dream-functions",
    "pipeline_id": PIPELINE_ID,
}

# Lightweight medical/therapy claim gate (symbolic lane only)
_MEDICAL_MARKERS = re.compile(
    r"\b(diagnos(?:e|is|tic)|prescri(?:be|ption)|therap(?:y|eutic)|"
    r"psychiatr(?:y|ic)|clinical\s+depression|bipolar|schizophren|"
    r"suicid(?:e|al)|medication|dosage)\b",
    re.I,
)


def normalize_dream(narrative_raw: str) -> str:
    """Deterministic whitespace normalization; preserves content tokens."""
    if not narrative_raw or not str(narrative_raw).strip():
        return ""
    return " ".join(str(narrative_raw).split())


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_motifs(narrative: str, dream_id: str, *, limit: int = 10) -> list[dict[str, Any]]:
    """Bounded evidence-bound motif extraction (deterministic stub IR)."""
    motifs: list[dict[str, Any]] = []
    if not narrative:
        return motifs
    words = narrative.lower().split()
    seen: set[str] = set()
    for i, w in enumerate(words):
        if len(motifs) >= limit:
            break
        token = re.sub(r"[^a-z0-9_\-]", "", w)
        if len(token) <= 3 or token in seen:
            continue
        seen.add(token)
        mid = hashlib.sha256(f"{dream_id}:motif:{token}:{i}".encode()).hexdigest()[:12]
        motifs.append(
            {
                "motif_id": mid,
                "label": token,
                "motif_type": "term",
                "evidence_text": token,
                "frequency": 1,
                "confidence": 0.6,
                "source_span": i,
                "register": "INFERRED",
            }
        )
    return motifs


def _norm_mode(raw: Any) -> str:
    s = str(raw or "UNKNOWN").strip().upper()
    return s if s in MODES else "UNKNOWN"


def _norm_privacy(raw: Any) -> str:
    s = str(raw or "UNKNOWN").strip().upper()
    return s if s in PRIVACY_TIERS else "UNKNOWN"


def _norm_source(raw: Any) -> str:
    s = str(raw or "UNKNOWN").strip().upper()
    return s if s in SOURCES else "UNKNOWN"


def _stable_dream_id(dream_id: str | None, narrative: str, seed: str) -> str:
    if dream_id and str(dream_id).strip():
        return str(dream_id).strip()
    base = f"{narrative}|{seed}"
    return "dream_" + hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]


def build_dream_operator_packet(
    *,
    mode: str = "UNKNOWN",
    dream_id: str | None = None,
    source: str = "UNKNOWN",
    privacy_tier: str = "PRIVATE",
    narrative_raw: str = "",
    narrative_normalized: str | None = None,
    seed: str = "0",
    motifs: list[dict[str, Any]] | None = None,
    blocked_by: list[str] | None = None,
) -> dict[str, Any]:
    """Build deterministic NoctisDreamOperatorPacket.v0 (SHADOW_SYMBOLIC)."""
    mode_n = _norm_mode(mode)
    privacy = _norm_privacy(privacy_tier)
    source_n = _norm_source(source)
    raw = str(narrative_raw or "")
    normalized = (
        narrative_normalized
        if narrative_normalized is not None
        else normalize_dream(raw)
    )
    did = _stable_dream_id(dream_id, normalized or raw, str(seed or "0"))
    narrative_present = bool((normalized or raw).strip())
    narrative_hash = _sha256_text(normalized or raw) if narrative_present else ""

    motif_list = list(motifs) if isinstance(motifs, list) else None
    if motif_list is None:
        motif_list = extract_motifs(normalized or raw, did)

    blocks = list(blocked_by or [])
    # Always-on domain blocks
    for b in (
        "MEDICAL_CLAIMS_BLOCKED",
        "FORECAST_ROUTING_BLOCKED",
        "MEMORY_DIRECT_WRITE_BLOCKED",
    ):
        if b not in blocks:
            blocks.append(b)

    if narrative_present and _MEDICAL_MARKERS.search(normalized or raw):
        if "MEDICAL_LANGUAGE_DETECTED" not in blocks:
            blocks.append("MEDICAL_LANGUAGE_DETECTED")

    if not narrative_present:
        readiness = "NOT_COMPUTABLE"
        analysis_status = "NOT_COMPUTABLE"
        if "EMPTY_NARRATIVE" not in blocks:
            blocks.append("EMPTY_NARRATIVE")
    elif "MEDICAL_LANGUAGE_DETECTED" in blocks and privacy == "PRIVATE":
        readiness = "BLOCKED"
        analysis_status = "BLOCKED_PRIVACY_MEDICAL_GATE"
    else:
        readiness = "SHADOW_OPERATOR_REVIEW"
        analysis_status = "IR_EMITTED"

    # Privacy: never attach raw private narrative to operator packet
    excerpt_allowed = privacy == "PUBLIC_SYNTHETIC"

    ir: dict[str, Any] = {
        "schema_version": IR_SCHEMA_VERSION,
        "motif_count": len(motif_list),
        "motifs": motif_list,
        "registers": {
            "OBSERVED": 0,
            "INFERRED": len(motif_list),
            "SPECULATIVE": 0,
            "NOT_COMPUTABLE": 0 if narrative_present else 1,
        },
    }

    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "pipeline_id": PIPELINE_ID,
        "packet_id": "ndop_"
        + canonical_hash(
            {
                "dream_id": did,
                "mode": mode_n,
                "narrative_sha256": narrative_hash,
                "motif_count": len(motif_list),
            }
        )[:16],
        "dream_id": did,
        "mode": mode_n,
        "privacy_tier": privacy,
        "source": source_n,
        "narrative_sha256": narrative_hash,
        "narrative_present": narrative_present,
        "narrative_excerpt_allowed": excerpt_allowed,
        "ir": ir,
        "readiness": readiness,
        "blocked_by": blocks,
        "medical_claims_blocked": True,
        "forecast_routing_blocked": True,
        "memory_direct_write_blocked": True,
        "analysis_status": analysis_status,
        "authority": dict(DEFAULT_AUTHORITY),
        "advisory_only": True,
        "lane": "SHADOW_SYMBOLIC",
        "producer": dict(PRODUCER),
        "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
    }
    if excerpt_allowed and narrative_present:
        # Safe synthetic-only excerpt for fixtures/tests
        body["narrative_excerpt"] = (normalized or raw)[:240]
    body["canonical_hash"] = canonical_hash(body)
    return body


def build_dream_operator_packet_from_input(
    dream_input: dict[str, Any],
    *,
    mode: str | None = None,
    motifs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Lift DreamInput-like dict into operator packet."""
    di = dream_input if isinstance(dream_input, dict) else {}
    return build_dream_operator_packet(
        mode=mode or str(di.get("mode") or "HUMAN_DREAM"),
        dream_id=str(di.get("dream_id") or "") or None,
        source=str(di.get("source") or "UNKNOWN"),
        privacy_tier=str(di.get("privacy_tier") or "PRIVATE"),
        narrative_raw=str(di.get("narrative_raw") or ""),
        narrative_normalized=di.get("narrative_normalized")
        if isinstance(di.get("narrative_normalized"), str)
        else None,
        seed=str(di.get("seed") or "0"),
        motifs=motifs,
    )


def build_dream_operator_packet_from_delivery(
    delivery: dict[str, Any],
    *,
    narrative_raw: str = "",
    narrative_normalized: str | None = None,
    motifs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Lift NoctisDreamDelivery-like dict into operator packet."""
    d = delivery if isinstance(delivery, dict) else {}
    return build_dream_operator_packet(
        mode=str(d.get("mode") or "UNKNOWN"),
        dream_id=str(d.get("dream_id") or "") or None,
        source=str(d.get("source") or "UNKNOWN"),
        privacy_tier=str(d.get("privacy_tier") or "PRIVATE"),
        narrative_raw=narrative_raw,
        narrative_normalized=narrative_normalized,
        motifs=motifs,
    )
