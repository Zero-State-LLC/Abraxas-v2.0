"""EvidencePack.v0 — canonical load, schema validate, normalize (AI OS syscall).

SHADOW / advisory only. Never grants execution, promotion, forecast routing, or canon mutation.

Canonical schema: ``contracts/signal/evidence_pack.v0.schema.json``
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Mapping, MutableMapping, Sequence

EVIDENCE_PACK_SCHEMA_VERSION = "EvidencePack.v0"
SCHEMA_REL = Path("contracts/signal/evidence_pack.v0.schema.json")

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

# Back-compat alias used by Neon Genie
EVIDENCE_PACK_SCHEMA = EVIDENCE_PACK_SCHEMA_VERSION


def repo_root_from_here() -> Path:
    """core/signal/evidence_pack.py → repo root."""
    return Path(__file__).resolve().parents[2]


def schema_path(*, repo_root: Path | None = None) -> Path:
    root = repo_root or repo_root_from_here()
    return (root / SCHEMA_REL).resolve()


@lru_cache(maxsize=4)
def _load_schema_bytes(path_str: str) -> dict[str, Any]:
    data = json.loads(Path(path_str).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("EvidencePack schema root must be object")
    return data


def load_schema(*, repo_root: Path | None = None) -> dict[str, Any]:
    path = schema_path(repo_root=repo_root)
    if not path.is_file():
        raise FileNotFoundError(f"EvidencePack schema missing: {path}")
    return _load_schema_bytes(str(path))


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
        return {
            "OBSERVED": int(raw.get("OBSERVED", 0) or 0),
            "INFERRED": int(raw.get("INFERRED", 0) or 0),
            "SPECULATIVE": int(raw.get("SPECULATIVE", 0) or 0),
            "NOT_COMPUTABLE": int(raw.get("NOT_COMPUTABLE", 0) or 0),
        }
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


def semantic_errors(pack: Mapping[str, Any]) -> List[str]:
    """Register / authority rules beyond JSON Schema."""
    errors: List[str] = []
    if pack.get("schema_version") != EVIDENCE_PACK_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {EVIDENCE_PACK_SCHEMA_VERSION!r}, got {pack.get('schema_version')!r}"
        )

    auth = pack.get("authority")
    if not isinstance(auth, Mapping):
        errors.append("authority must be an object")
    else:
        for key in (
            "execution_authority",
            "promotion_authorized",
            "forecast_routing_authorized",
            "canon_mutation_allowed",
        ):
            if auth.get(key) is not False:
                errors.append(f"authority.{key} must be false")

    source_ids: set[str] = set()
    sources = pack.get("sources") or []
    if isinstance(sources, list):
        for src in sources:
            if isinstance(src, Mapping) and src.get("source_id"):
                source_ids.add(str(src["source_id"]))

    claims = pack.get("claims") or []
    if isinstance(claims, list):
        for claim in claims:
            if not isinstance(claim, Mapping):
                errors.append("claim entries must be objects")
                continue
            cid = claim.get("claim_id", "<missing>")
            reg = str(claim.get("register", "")).upper()
            c_sources = claim.get("source_ids") or []
            if not isinstance(c_sources, list):
                errors.append(f"claim {cid}: source_ids must be array")
                c_sources = []
            if reg == "OBSERVED":
                if not c_sources:
                    errors.append(f"claim {cid}: OBSERVED requires non-empty source_ids")
                for sid in c_sources:
                    if str(sid) not in source_ids:
                        errors.append(f"claim {cid}: unknown source_id {sid!r}")
            elif reg == "INFERRED":
                if len(c_sources) < 2:
                    errors.append(f"claim {cid}: INFERRED requires >=2 source_ids")
                if not claim.get("join_logic"):
                    errors.append(f"claim {cid}: INFERRED requires join_logic")
                for sid in c_sources:
                    if str(sid) not in source_ids:
                        errors.append(f"claim {cid}: unknown source_id {sid!r}")
            elif reg == "NOT_COMPUTABLE":
                pass
            elif reg == "SPECULATIVE":
                pass
            else:
                errors.append(f"claim {cid}: invalid register {reg!r}")

    return errors


def validate_evidence_pack(
    pack: Mapping[str, Any],
    *,
    repo_root: Path | None = None,
    strict_schema: bool = True,
) -> List[str]:
    """Return list of validation errors (empty == valid)."""
    errors: List[str] = []
    if not isinstance(pack, Mapping):
        return ["pack must be a mapping"]

    if strict_schema:
        try:
            schema = load_schema(repo_root=repo_root)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            return [f"schema load failed: {exc}"]
        try:
            from jsonschema import Draft7Validator

            validator = Draft7Validator(schema)
            for err in sorted(validator.iter_errors(dict(pack)), key=lambda e: list(e.path)):
                path = ".".join(str(p) for p in err.path) or "<root>"
                errors.append(f"schema:{path}: {err.message}")
        except ImportError:
            # Fail closed on missing dependency in environments that should have it
            errors.append("jsonschema package required for EvidencePack validation")
        except Exception as exc:  # noqa: BLE001 — surface validator failures
            errors.append(f"schema validation error: {exc}")

    errors.extend(semantic_errors(pack))
    return errors


def assert_valid_evidence_pack(
    pack: Mapping[str, Any],
    *,
    repo_root: Path | None = None,
) -> Dict[str, Any]:
    """Raise ValueError if invalid; return pack as dict."""
    errs = validate_evidence_pack(pack, repo_root=repo_root)
    if errs:
        raise ValueError("EvidencePack invalid:\n- " + "\n- ".join(errs))
    return dict(pack)


def commercial_claims_blocked(pack: Mapping[str, Any]) -> bool:
    """True when pack lacks enough OBSERVED density for commercial language."""
    counts = register_counts(pack)
    observed_sources = int(pack.get("observed_source_count") or 0)
    if observed_sources <= 0:
        sources = pack.get("sources") or []
        observed_sources = len(sources) if isinstance(sources, list) else 0
    observed_claims = counts["OBSERVED"]
    if pack.get("status") == "NOT_COMPUTABLE":
        return True
    if observed_claims == 0 and observed_sources == 0:
        return True
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
    score = min(1.0, (observed * 0.18) + (inferred * 0.06))
    if pack.get("schema_version") == EVIDENCE_PACK_SCHEMA_VERSION and observed >= 3:
        score = max(score, 0.55)
    if pack.get("schema_version") == EVIDENCE_PACK_SCHEMA_VERSION and observed >= 6:
        score = max(score, 0.75)
    if commercial_claims_blocked(pack) and status not in {"PROMPT_ONLY"}:
        if observed >= 3:
            return round(min(score, 0.8), 2)
        return round(min(score, 0.25), 2)
    return round(min(max(score, 0.0), 1.0), 2)


def normalize_evidence_pack(
    pack: Mapping[str, Any],
    *,
    source_path: str | None = None,
    validate: bool = False,
    repo_root: Path | None = None,
) -> Dict[str, Any]:
    """Return Neon/OS-facing evidence dict with status + density.

    When ``validate=True`` and pack claims EvidencePack.v0, schema+semantic
    validation runs; failures become status NOT_COMPUTABLE with reasons.
    """
    data = _as_dict(pack)
    schema = data.get("schema_version")
    if schema == EVIDENCE_PACK_SCHEMA_VERSION:
        if validate:
            errs = validate_evidence_pack(data, repo_root=repo_root)
            if errs:
                return {
                    "status": "NOT_COMPUTABLE",
                    "reason": "EvidencePack validation failed",
                    "validation_errors": errs,
                    "commercial_claims_blocked": True,
                    "evidence_density": 0.1,
                    "pack_ref": source_path,
                    "schema_version": EVIDENCE_PACK_SCHEMA_VERSION,
                    "pack_id": data.get("pack_id"),
                }
        counts = register_counts(data)
        blocked = commercial_claims_blocked(data)
        status = "EVIDENCE_PACK"
        if counts["OBSERVED"] == 0 and counts["INFERRED"] == 0:
            status = "NOT_COMPUTABLE"
        return {
            "status": status,
            "schema_version": EVIDENCE_PACK_SCHEMA_VERSION,
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

    status = str(data.get("status", "UNKNOWN")).upper() or "UNKNOWN"
    if "status" not in data and data:
        status = "UNKNOWN"
    out = dict(data)
    out["status"] = status
    out.setdefault("commercial_claims_blocked", status == "NOT_COMPUTABLE")
    out["evidence_density"] = evidence_density(out)
    if source_path:
        out["pack_ref"] = source_path
    return out


def resolve_evidence_for_request(
    request: Mapping[str, Any],
    *,
    needs_evidence: bool,
    validate: bool = True,
    repo_root: Path | None = None,
) -> Dict[str, Any]:
    """Resolve evidence_pack from request body or evidence_pack_path."""
    req = _as_dict(request)

    path = req.get("evidence_pack_path") or req.get("evidence_pack_file")
    if path:
        try:
            loaded = load_evidence_pack_file(str(path))
            return normalize_evidence_pack(
                loaded,
                source_path=str(Path(str(path)).expanduser()),
                validate=validate,
                repo_root=repo_root,
            )
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
            try:
                loaded = load_evidence_pack_file(str(ep))
                return normalize_evidence_pack(
                    loaded,
                    source_path=str(ep),
                    validate=validate,
                    repo_root=repo_root,
                )
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                return {
                    "status": "NOT_COMPUTABLE",
                    "reason": f"evidence_pack path load failed: {exc}",
                    "pack_ref": str(ep),
                    "commercial_claims_blocked": True,
                    "evidence_density": 0.1,
                }
        return normalize_evidence_pack(
            _as_dict(ep), validate=validate, repo_root=repo_root
        )

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


def redact_commercial_fields(
    venture_packet: MutableMapping[str, Any], evidence_pack: Mapping[str, Any]
) -> None:
    """In-place: force market/commercial fields to NOT_COMPUTABLE when blocked."""
    if not evidence_pack.get("commercial_claims_blocked", True):
        return
    for key in COMMERCIAL_CLAIM_KEYS:
        if key in venture_packet:
            venture_packet[key] = "NOT_COMPUTABLE"
    mm = venture_packet.get("market_model")
    if isinstance(mm, dict):
        for k in list(mm.keys()):
            mm[k] = "NOT_COMPUTABLE"
        mm["status"] = "NOT_COMPUTABLE"
        mm["reason"] = (
            "commercial claims blocked without sufficient OBSERVED EvidencePack density"
        )
    venture_packet["commercial_claims_status"] = "NOT_COMPUTABLE"
    venture_packet["commercial_claims_reason"] = evidence_pack.get(
        "reason", "EvidencePack commercial density gate"
    )


def validate_path(
    path: str | Path,
    *,
    repo_root: Path | None = None,
) -> Dict[str, Any]:
    """CLI/helper: load + validate a pack file; return report dict."""
    p = Path(path).expanduser()
    try:
        pack = load_evidence_pack_file(p)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return {
            "ok": False,
            "path": str(p),
            "errors": [str(exc)],
            "authority": {
                "execution_authority": False,
                "promotion_authorized": False,
            },
        }
    errs = validate_evidence_pack(pack, repo_root=repo_root)
    report: Dict[str, Any] = {
        "ok": not errs,
        "path": str(p.resolve()) if p.exists() else str(p),
        "pack_id": pack.get("pack_id"),
        "topic": pack.get("topic"),
        "schema_version": pack.get("schema_version"),
        "register_counts": register_counts(pack),
        "source_count": len(pack.get("sources") or [])
        if isinstance(pack.get("sources"), list)
        else 0,
        "commercial_claims_blocked": commercial_claims_blocked(pack),
        "evidence_density": evidence_density(
            {**pack, "status": "EVIDENCE_PACK" if not errs else "NOT_COMPUTABLE"}
        ),
        "errors": errs,
        "authority": {
            "execution_authority": False,
            "promotion_authorized": False,
            "forecast_routing_authorized": False,
            "canon_mutation_allowed": False,
            "lane": "SHADOW",
        },
    }
    return report
