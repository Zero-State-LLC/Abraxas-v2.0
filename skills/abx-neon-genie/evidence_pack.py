"""EvidencePack.v0 load + normalize helpers for Neon Genie.

Accepts either:
- an already-normalized evidence dict on the request
- evidence_pack_path pointing at EvidencePack.v0 JSON (forager output)

Never grants authority. SHADOW / advisory density only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping, MutableMapping, Optional

EVIDENCE_PACK_SCHEMA = "EvidencePack.v0"
COMMERCIAL_CLAIM_KEYS = (
    "market",
    "revenue",
    "competitor",
    "competitors",
    "adoption",
    "tam",
    "pricing",
    "monetization",
)


def _as_dict(obj: Any) -> Dict[str, Any]:
    return dict(obj) if isinstance(obj, Mapping) else {}


def load_evidence_pack_file(path: str | Path) -> Dict[str, Any]:
    """Load JSON from disk. Raises FileNotFoundError / json.JSONDecodeError / ValueError."""
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        raise FileNotFoundError(f"evidence pack not found: {p}")
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("evidence pack root must be a JSON object")
    return data


def register_counts(pack: Mapping[str, Any]) -> Dict[str, int]:
    raw = pack.get("register_counts")
    if isinstance(raw, Mapping) and raw:
        out = {
            "OBSERVED": int(raw.get("OBSERVED", 0) or 0),
            "INFERRED": int(raw.get("INFERRED", 0) or 0),
            "SPECULATIVE": int(raw.get("SPECULATIVE", 0) or 0),
            "NOT_COMPUTABLE": int(raw.get("NOT_COMPUTABLE", 0) or 0),
        }
        return out
    counts = {"OBSERVED": 0, "INFERRED": 0, "SPECULATIVE": 0, "NOT_COMPUTABLE": 0}
    claims = pack.get("claims") or []
    if isinstance(claims, list):
        for claim in claims:
            if not isinstance(claim, Mapping):
                continue
            reg = str(claim.get("register", "")).upper()
            if reg in counts:
                counts[reg] += 1
    return counts


def commercial_claims_blocked(pack: Mapping[str, Any]) -> bool:
    """True when pack lacks enough OBSERVED density for commercial language."""
    counts = register_counts(pack)
    # Density heuristic from forager playbook: <3 OBSERVED sources → block hard commercial
    observed_sources = int(pack.get("observed_source_count") or 0)
    if observed_sources <= 0:
        sources = pack.get("sources") or []
        observed_sources = len(sources) if isinstance(sources, list) else 0
    # Prefer OBSERVED claim count when present
    observed_claims = counts["OBSERVED"]
    if pack.get("status") == "NOT_COMPUTABLE":
        return True
    if observed_claims == 0 and observed_sources == 0:
        return True
    # Explicit NOT_COMPUTABLE answer on market questions counts as block signal
    answers = pack.get("answers") or []
    if isinstance(answers, list):
        for ans in answers:
            if not isinstance(ans, Mapping):
                continue
            if str(ans.get("status", "")).upper() == "NOT_COMPUTABLE":
                summary = str(ans.get("summary", "")).lower()
                if any(k in summary for k in ("market", "tam", "revenue", "pricing")):
                    return True
    return observed_claims < 1


def evidence_density(pack: Mapping[str, Any]) -> float:
    """Deterministic density in [0, 1] for scoring stubs."""
    status = str(pack.get("status", "")).upper()
    if status == "PROMPT_ONLY":
        return 0.35
    if status == "NOT_COMPUTABLE":
        return 0.1
    counts = register_counts(pack)
    observed = counts["OBSERVED"]
    inferred = counts["INFERRED"]
    # Cap contribution; OBSERVED weighs more than INFERRED
    score = min(1.0, (observed * 0.18) + (inferred * 0.06))
    if pack.get("schema_version") == EVIDENCE_PACK_SCHEMA and observed >= 3:
        score = max(score, 0.55)
    if pack.get("schema_version") == EVIDENCE_PACK_SCHEMA and observed >= 6:
        score = max(score, 0.75)
    if commercial_claims_blocked(pack) and status not in {"PROMPT_ONLY"}:
        # Still allow some density for tech OBSERVED packs that block only market TAM
        if observed >= 3:
            return round(min(score, 0.8), 2)
        return round(min(score, 0.25), 2)
    return round(min(max(score, 0.0), 1.0), 2)


def normalize_evidence_pack(
    pack: Mapping[str, Any],
    *,
    source_path: str | None = None,
) -> Dict[str, Any]:
    """Return Neon-Genie-facing evidence dict with status + density."""
    data = _as_dict(pack)
    schema = data.get("schema_version")
    if schema == EVIDENCE_PACK_SCHEMA:
        counts = register_counts(data)
        blocked = commercial_claims_blocked(data)
        status = "EVIDENCE_PACK"
        if counts["OBSERVED"] == 0 and counts["INFERRED"] == 0:
            status = "NOT_COMPUTABLE"
        out: Dict[str, Any] = {
            "status": status,
            "schema_version": EVIDENCE_PACK_SCHEMA,
            "pack_id": data.get("pack_id"),
            "topic": data.get("topic"),
            "intent": data.get("intent"),
            "register_counts": counts,
            "observed_source_count": int(
                data.get("observed_source_count")
                or (len(data.get("sources") or []) if isinstance(data.get("sources"), list) else 0)
            ),
            "commercial_claims_blocked": blocked,
            "evidence_density": evidence_density({**data, "status": status}),
            "authority": data.get("authority")
            or {
                "execution_authority": False,
                "promotion_authorized": False,
                "forecast_routing_authorized": False,
                "canon_mutation_allowed": False,
                "lane": "SHADOW",
            },
            "pack_ref": source_path,
            "claims": data.get("claims") or [],
            "sources": data.get("sources") or [],
            "answers": data.get("answers") or [],
            "raw_pack": data,
        }
        return out

    # Legacy / stub shapes
    status = str(data.get("status", "UNKNOWN")).upper() or "UNKNOWN"
    if "status" not in data and data:
        # bare dict without status — treat as unknown lightweight pack
        status = "UNKNOWN"
    out = dict(data)
    out["status"] = status
    out.setdefault("commercial_claims_blocked", status == "NOT_COMPUTABLE")
    out["evidence_density"] = evidence_density(out)
    if source_path:
        out["pack_ref"] = source_path
    return out


def resolve_evidence_for_request(request: Mapping[str, Any], *, needs_evidence: bool) -> Dict[str, Any]:
    """Resolve evidence_pack from request body or evidence_pack_path."""
    req = _as_dict(request)

    # Explicit path wins if provided (operator forage hand-off)
    path = req.get("evidence_pack_path") or req.get("evidence_pack_file")
    if path:
        try:
            loaded = load_evidence_pack_file(str(path))
            return normalize_evidence_pack(loaded, source_path=str(Path(str(path)).expanduser()))
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            return {
                "status": "NOT_COMPUTABLE",
                "reason": f"evidence_pack_path load failed: {exc}",
                "pack_ref": str(path),
                "commercial_claims_blocked": True,
                "evidence_density": 0.1,
            }

    if "evidence_pack" in req and req["evidence_pack"] is not None:
        ep = req["evidence_pack"]
        if isinstance(ep, (str, Path)):
            # allow passing path as evidence_pack string
            try:
                loaded = load_evidence_pack_file(str(ep))
                return normalize_evidence_pack(loaded, source_path=str(ep))
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                return {
                    "status": "NOT_COMPUTABLE",
                    "reason": f"evidence_pack path load failed: {exc}",
                    "pack_ref": str(ep),
                    "commercial_claims_blocked": True,
                    "evidence_density": 0.1,
                }
        return normalize_evidence_pack(_as_dict(ep))

    if needs_evidence:
        return {
            "status": "NOT_COMPUTABLE",
            "reason": "no evidence acquired",
            "commercial_claims_blocked": True,
            "evidence_density": 0.1,
            "hint": "Pass evidence_pack_path from abx-familiar-signal-forager EvidencePack.v0",
        }
    return {
        "status": "PROMPT_ONLY",
        "commercial_claims_blocked": True,
        "evidence_density": 0.35,
    }


def redact_commercial_fields(venture_packet: MutableMapping[str, Any], evidence_pack: Mapping[str, Any]) -> None:
    """In-place: force market/commercial fields to NOT_COMPUTABLE when blocked."""
    if not evidence_pack.get("commercial_claims_blocked", True):
        # Still never invent market_model numbers without sources
        return
    for key in COMMERCIAL_CLAIM_KEYS:
        if key in venture_packet:
            venture_packet[key] = "NOT_COMPUTABLE"
    mm = venture_packet.get("market_model")
    if isinstance(mm, dict):
        for k in list(mm.keys()):
            mm[k] = "NOT_COMPUTABLE"
        mm["status"] = "NOT_COMPUTABLE"
        mm["reason"] = "commercial claims blocked without sufficient OBSERVED EvidencePack density"
    venture_packet["commercial_claims_status"] = "NOT_COMPUTABLE"
    venture_packet["commercial_claims_reason"] = evidence_pack.get(
        "reason", "EvidencePack commercial density gate"
    )
