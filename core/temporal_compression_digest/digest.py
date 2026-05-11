from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping, Sequence

from .models import *
from .validator import validate_temporal_compression_digest_projection

SCHEMA_VERSION = "TemporalClimateCompressionDigestProjection.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_temporal_compression_digest_projection_json(digest: TemporalClimateCompressionDigestProjection | Mapping[str, Any]) -> str:
    payload = asdict(digest) if isinstance(digest, TemporalClimateCompressionDigestProjection) else dict(digest)
    payload.pop("digest_hash", None)
    return _canonical_json(payload)


def temporal_compression_digest_projection_hash(digest: TemporalClimateCompressionDigestProjection | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_temporal_compression_digest_projection_json(digest))


def _status_from_posture(posture: str) -> str:
    return {
        "STABLE": "DIGEST_STABLE",
        "PRESSURE": "DIGEST_PRESSURE",
        "REGIME_RISK": "DIGEST_REGIME_RISK",
        "FRACTURE_RISK": "DIGEST_FRACTURE_RISK",
        "NONDETERMINISM": "DIGEST_NONDETERMINISM",
        "BLOCKED": "DIGEST_BLOCKED_HISTORY",
        "OVERLOADED": "DIGEST_SIGNAL_OVERLOAD",
        "INSUFFICIENT_INPUTS": "INSUFFICIENT_COMPRESSION_INPUTS",
        "WATCH": "DIGEST_READY",
    }.get(posture, "NOT_COMPUTABLE")


def build_temporal_compression_digest_projection(digest_id: str, input_refs: tuple[TemporalDigestInputRef, ...], sections: tuple[TemporalDigestSection, ...], signal_cards: tuple[TemporalDigestSignalCard, ...], provenance_refs: tuple[TemporalDigestProvenanceRef, ...], warnings: tuple[TemporalDigestWarning, ...], recommendations: tuple[TemporalDigestRecommendation, ...], digest_status: str, digest_posture: str, digest_policy: str, created_by_lane: str, authority_ref: dict | None) -> TemporalClimateCompressionDigestProjection:
    draft = TemporalClimateCompressionDigestProjection(SCHEMA_VERSION, digest_id, input_refs, sections, signal_cards, provenance_refs, warnings, recommendations, digest_status, digest_posture, digest_policy, created_by_lane, authority_ref, True, False, False, False, False, False, False, False, False, False, False, False, False, False, "PENDING")
    return replace(draft, digest_hash=temporal_compression_digest_projection_hash(draft))


def derive_temporal_compression_digest_projection(ledgers: Sequence[Mapping[str, Any]], input_refs: Sequence[Mapping[str, Any]] | None = None) -> TemporalClimateCompressionDigestProjection:
    refs = tuple(TemporalDigestInputRef(str(r.get("source_type", "NOT_COMPUTABLE")), str(r.get("source_id", "")), str(r.get("source_hash", ""))) for r in (input_refs or []))
    if not ledgers:
        return build_temporal_compression_digest_projection("digest-1", refs, tuple(), tuple(), tuple(), (TemporalDigestWarning("w-0", "SIGNAL_GAP", "WARN", "No compression ledger inputs."),), (TemporalDigestRecommendation("rec-0", "NOT_COMPUTABLE", False, False, False, False, False),), "NOT_COMPUTABLE", "NOT_COMPUTABLE", "PROJECTION_ONLY", "PROJECTION", None)

    l = ledgers[-1]
    posture = str(l.get("ledger_posture", "NOT_COMPUTABLE"))
    status = _status_from_posture(posture)

    sections = [
        TemporalDigestSection("sec-exec", "EXECUTIVE_SUMMARY", "Executive Summary", f"Ledger posture: {posture}", "PASS" if posture == "STABLE" else "WARN" if posture in {"PRESSURE", "REGIME_RISK", "FRACTURE_RISK"} else "BLOCKED" if posture in {"BLOCKED", "NONDETERMINISM", "OVERLOADED"} else "WATCH", tuple(), True, False)
    ]
    for i, c in enumerate(l.get("compression_clusters", ()), start=1):
        ctype = str(c.get("cluster_type", "NOT_COMPUTABLE"))
        stype = "PRESSURE_SUMMARY" if ctype == "PRESSURE_CLUSTER" else "REGIME_SUMMARY" if ctype == "REGIME_CLUSTER" else "FRACTURE_SUMMARY" if ctype == "FRACTURE_CLUSTER" else "NONDETERMINISM_SUMMARY" if ctype == "NONDETERMINISM_CLUSTER" else "BLOCKED_HISTORY_SUMMARY" if ctype == "BLOCKED_HISTORY_CLUSTER" else "CONTINUITY_SUMMARY"
        sections.append(TemporalDigestSection(f"sec-{i}", stype, ctype.replace("_", " ").title(), f"Cluster posture={c.get('cluster_posture','NA')} signals={c.get('signal_count',0)}", str(c.get("cluster_posture", "NOT_COMPUTABLE")), tuple(c.get("source_ref_ids", ())), True, False))

    cards=[]
    for i, m in enumerate(l.get("compression_motifs", ()), start=1):
        mtype = str(m.get("motif_type", "NOT_COMPUTABLE"))
        ctype = "PRESSURE_CARD" if "PRESSURE" in mtype else "REGIME_CARD" if "REGIME" in mtype else "FRACTURE_CARD" if "FRACTURE" in mtype else "NONDETERMINISM_CARD" if "NONDETERMINISM" in mtype else "BLOCKED_HISTORY_CARD" if "BLOCKED_HISTORY" in mtype else "CONTINUITY_CARD"
        cards.append(TemporalDigestSignalCard(f"card-{i}", ctype, mtype, f"Motif weight={m.get('motif_weight',0.0)}", float(m.get("motif_weight",0.0)), "BLOCKED" if m.get("motif_visibility") == "BLOCKED" else "WARN" if m.get("motif_visibility") in {"HIGH","CRITICAL"} else "WATCH", tuple(), True, False, False))

    prov=[]
    for i,r in enumerate(refs, start=1): prov.append(TemporalDigestProvenanceRef(f"prov-{i}", r.source_id, r.source_type, r.source_hash, f"trace-{i}", True, True))

    warnings=[]
    if posture == "OVERLOADED": warnings.append(TemporalDigestWarning("w-ovl","SIGNAL_OVERLOAD","BLOCKED","Compression indicates overloaded review surface."))
    if any(c.card_type == "BLOCKED_HISTORY_CARD" for c in cards): warnings.append(TemporalDigestWarning("w-blk","BLOCKED_HISTORY_VISIBLE","BLOCKED","Blocked-history signal preserved in digest."))
    if any(c.card_type == "NONDETERMINISM_CARD" for c in cards): warnings.append(TemporalDigestWarning("w-nd","NONDETERMINISM_VISIBLE","BLOCKED","Nondeterminism signal preserved in digest."))

    rec = (TemporalDigestRecommendation("rec-1", "REQUEST_OPERATOR_REVIEW" if status in {"DIGEST_BLOCKED_HISTORY","DIGEST_NONDETERMINISM","DIGEST_SIGNAL_OVERLOAD","DIGEST_FRACTURE_RISK","DIGEST_REGIME_RISK","DIGEST_PRESSURE"} else "REVIEW_ONLY", False, False, False, False, False),)
    return build_temporal_compression_digest_projection("digest-1", refs, tuple(sections), tuple(cards), tuple(prov), tuple(warnings), rec, status, posture, "PROJECTION_ONLY", "PROJECTION", None)


def write_temporal_compression_digest_projection_contract_audit(base_dir: Path | str = ".") -> str:
    d = derive_temporal_compression_digest_projection([
        {"ledger_posture": "PRESSURE", "compression_clusters": ({"cluster_type": "PRESSURE_CLUSTER", "cluster_posture": "WATCH", "signal_count": 2, "source_ref_ids": ()},), "compression_motifs": ({"motif_type": "RECURSIVE_PRESSURE", "motif_weight": 0.7, "motif_visibility": "HIGH"},)}
    ], [{"source_type": "TEMPORAL_SIGNAL_COMPRESSION_LEDGER", "source_id": "l1", "source_hash": "h1"}])
    report = validate_temporal_compression_digest_projection(d)
    payload = {"status": report.status, "digest_hash": d.digest_hash, "receipt_hash": report.receipt_hash, "findings": [asdict(f) for f in report.findings], "schema_version": d.schema_version}
    text = _canonical_json(payload) + "\n"
    out = Path(base_dir) / "out/audit/temporal_climate_compression_digest_projection_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)
