"""Familiar ingestion receipt — EvidencePack.v0 → SHADOW ingest proof.

Closes abx-familiar / familiar_ingestion MISSING_CONTRACT gap at the receipt layer.
Does not network, promote canon, or grant execution authority.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import canonical_hash, write_classified_json
from core.signal.evidence_pack import (
    commercial_claims_blocked,
    evidence_density,
    load_evidence_pack_file,
    register_counts,
    validate_evidence_pack,
)

SCHEMA_VERSION = "FamiliarIngestionReceipt.v0"
PIPELINE_ID = "familiar_ingestion"
DETERMINISTIC_TIMESTAMP = "familiar_ingestion_receipt_v0_ts_0"
DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "promotion_authorized": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
}
PRODUCER = {
    "module": "core.ingest.familiar_ingestion_receipt",
    "skill_id": "abx-familiar-signal-forager",
}


def _source_summaries(pack: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    sources = pack.get("sources") or []
    if not isinstance(sources, list):
        return out
    for src in sources:
        if not isinstance(src, dict):
            continue
        sid = src.get("source_id")
        if not sid:
            continue
        out.append(
            {
                "source_id": str(sid),
                "source_class": str(src.get("source_class", "unknown")),
                "url_or_path": str(src.get("url_or_path", "")),
                "title": str(src.get("title", "")),
            }
        )
    out.sort(key=lambda s: s["source_id"])
    return out


def _finalize(body: dict[str, Any]) -> dict[str, Any]:
    sealed = dict(body)
    sealed.pop("receipt_hash", None)
    sealed["receipt_hash"] = canonical_hash(sealed)
    return sealed


def build_familiar_ingestion_receipt(
    pack: dict[str, Any] | None,
    *,
    pack_ref: str = "",
    repo_root: Path | None = None,
    load_error: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic SHADOW receipt from an EvidencePack (or None)."""
    if pack is None and load_error:
        return _finalize(
            {
                "schema_version": SCHEMA_VERSION,
                "receipt_id": "fir_load_failed",
                "pipeline_id": PIPELINE_ID,
                "pack_id": "",
                "pack_hash": canonical_hash({"load_error": load_error}),
                "pack_ref": pack_ref or "",
                "topic": "",
                "intent": "",
                "register_counts": {
                    "OBSERVED": 0,
                    "INFERRED": 0,
                    "SPECULATIVE": 0,
                    "NOT_COMPUTABLE": 0,
                },
                "source_count": 0,
                "claim_count": 0,
                "observed_claim_count": 0,
                "validation_status": "FAIL",
                "status": "REJECTED_INVALID_PACK",
                "blockers": ["pack_load_failed"],
                "validation_errors": [load_error],
                "commercial_claims_blocked": True,
                "evidence_density": 0.1,
                "authority": dict(DEFAULT_AUTHORITY),
                "advisory_only": True,
                "lane": "SHADOW",
                "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
                "source_summaries": [],
                "producer": dict(PRODUCER),
            }
        )

    if pack is None:
        return _finalize(
            {
                "schema_version": SCHEMA_VERSION,
                "receipt_id": "fir_no_input",
                "pipeline_id": PIPELINE_ID,
                "pack_id": "",
                "pack_hash": canonical_hash({"empty": True}),
                "pack_ref": pack_ref or "",
                "topic": "",
                "intent": "",
                "register_counts": {
                    "OBSERVED": 0,
                    "INFERRED": 0,
                    "SPECULATIVE": 0,
                    "NOT_COMPUTABLE": 0,
                },
                "source_count": 0,
                "claim_count": 0,
                "observed_claim_count": 0,
                "validation_status": "NOT_COMPUTABLE",
                "status": "NO_INPUT",
                "blockers": ["no_input"],
                "validation_errors": [],
                "commercial_claims_blocked": True,
                "evidence_density": 0.1,
                "authority": dict(DEFAULT_AUTHORITY),
                "advisory_only": True,
                "lane": "SHADOW",
                "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
                "source_summaries": [],
                "producer": dict(PRODUCER),
            }
        )

    errs = validate_evidence_pack(pack, repo_root=repo_root)
    counts = register_counts(pack)
    claims = pack.get("claims") if isinstance(pack.get("claims"), list) else []
    sources = pack.get("sources") if isinstance(pack.get("sources"), list) else []
    pack_hash = canonical_hash(pack)
    pack_id = str(pack.get("pack_id") or "")
    receipt_id = f"fir_{pack_hash[:16]}"

    if errs:
        status = "REJECTED_INVALID_PACK"
        validation_status = "FAIL"
        blockers = ["invalid_evidence_pack"]
        density = 0.1
        blocked = True
        summaries: list[dict[str, Any]] = []
    else:
        status = "INGESTED_SHADOW"
        validation_status = "PASS"
        blockers = []
        density = evidence_density({**pack, "status": "EVIDENCE_PACK"})
        blocked = commercial_claims_blocked(pack)
        summaries = _source_summaries(pack)

    return _finalize(
        {
            "schema_version": SCHEMA_VERSION,
            "receipt_id": receipt_id,
            "pipeline_id": PIPELINE_ID,
            "pack_id": pack_id,
            "pack_hash": pack_hash,
            "pack_ref": pack_ref,
            "topic": str(pack.get("topic") or ""),
            "intent": str(pack.get("intent") or ""),
            "register_counts": counts,
            "source_count": len(sources),
            "claim_count": len(claims),
            "observed_claim_count": counts["OBSERVED"],
            "validation_status": validation_status,
            "status": status,
            "blockers": blockers,
            "validation_errors": list(errs),
            "commercial_claims_blocked": blocked,
            "evidence_density": density,
            "authority": dict(DEFAULT_AUTHORITY),
            "advisory_only": True,
            "lane": "SHADOW",
            "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
            "source_summaries": summaries,
            "producer": dict(PRODUCER),
        }
    )


def build_familiar_ingestion_receipt_from_path(
    path: str | Path,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    p = Path(path).expanduser()
    try:
        pack = load_evidence_pack_file(p)
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        return build_familiar_ingestion_receipt(
            None,
            pack_ref=str(p),
            repo_root=repo_root,
            load_error=str(exc),
        )
    return build_familiar_ingestion_receipt(
        pack, pack_ref=str(p.resolve()), repo_root=repo_root
    )


def build_familiar_ingestion_receipt_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Familiar Ingestion Receipt",
        "",
        f"- receipt_id: `{packet.get('receipt_id')}`",
        f"- status: `{packet.get('status')}`",
        f"- validation_status: `{packet.get('validation_status')}`",
        f"- pack_id: `{packet.get('pack_id')}`",
        f"- pack_hash: `{packet.get('pack_hash')}`",
        f"- topic: {packet.get('topic')}",
        f"- source_count: `{packet.get('source_count')}`",
        f"- observed_claim_count: `{packet.get('observed_claim_count')}`",
        f"- commercial_claims_blocked: `{packet.get('commercial_claims_blocked')}`",
        f"- evidence_density: `{packet.get('evidence_density')}`",
        f"- lane: `{packet.get('lane')}`",
        f"- receipt_hash: `{packet.get('receipt_hash')}`",
        "",
        "Authority: execution/promotion/forecast/canon all **false** (SHADOW).",
        "",
    ]
    blockers = packet.get("blockers") or []
    if blockers:
        lines.append("## Blockers")
        for b in blockers:
            lines.append(f"- {b}")
        lines.append("")
    return "\n".join(lines)


def write_familiar_ingestion_receipt(
    path: Path,
    packet: dict[str, Any],
    *,
    out_root: Path | None = None,
) -> None:
    """Write classified JSON + companion markdown."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    root = out_root or path.parent
    write_classified_json(
        path,
        packet,
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=root,
    )
    path.with_suffix(".md").write_text(
        build_familiar_ingestion_receipt_markdown(packet),
        encoding="utf-8",
    )
