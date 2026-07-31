"""Phonomicon artifact operator packet — provenance + Proof of Resonance.

Closes phonomicon_artifact MISSING_CONTRACT at the operator-packet layer.
Aligned to Notion PATCH-GLOBAL-SPINE-007 (PRODUCT_CANDIDATE / PROVENANCE_ONLY).

Does not mint, list on marketplaces, transfer wallets, or publish.
"""

from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash

SCHEMA_VERSION = "PhonomiconArtifactOperatorPacket.v0"
PIPELINE_ID = "phonomicon_artifact"
DETERMINISTIC_TIMESTAMP = "phonomicon_artifact_operator_packet_v0_ts_0"

DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "promotion_authorized": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
    "mint_execution_allowed": False,
    "marketplace_listing_allowed": False,
    "wallet_transfer_allowed": False,
    "publication_allowed": False,
    "operator_approval_required": True,
    "provenance_only": True,
}

PRODUCER = {
    "module": "core.phonomicon.artifact_operator_packet",
    "pipeline_id": PIPELINE_ID,
    "subsystem": "Phonomicon",
    "notion_patch": "PATCH-GLOBAL-SPINE-007",
}


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _round6(x: float) -> float:
    return round(x, 6)


def _f01(raw: Any) -> float | None:
    if raw is None or raw == "":
        return None
    try:
        return _clamp01(float(raw))
    except (TypeError, ValueError):
        return None


def build_provenance_chain(
    sources: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    """Build deterministic hash-linked provenance chain from source refs."""
    chain: list[dict[str, Any]] = []
    prev = "genesis"
    for i, src in enumerate(sources or []):
        if not isinstance(src, dict):
            continue
        ref = str(src.get("source_id") or src.get("ref") or f"src_{i}")
        system = str(src.get("source_system") or src.get("system") or "unknown")
        payload = {
            "index": i,
            "source_id": ref,
            "source_system": system,
            "prev_hash": prev,
            "meta": {
                k: src[k]
                for k in sorted(src.keys())
                if k not in {"source_id", "ref", "source_system", "system"}
            },
        }
        link_hash = canonical_hash(payload)
        link = {
            "index": i,
            "source_id": ref,
            "source_system": system,
            "prev_hash": prev,
            "link_hash": link_hash,
        }
        chain.append(link)
        prev = link_hash

    root = prev if chain else canonical_hash({"empty_chain": True})
    return {
        "schema_version": "PhonomiconProvenanceChain.v0",
        "chain": chain,
        "chain_root_hash": root,
        "link_count": len(chain),
    }


def _rarity_tier(score: float) -> str:
    if score < 0.0:
        return "NOT_COMPUTABLE"
    if score < 0.25:
        return "COMMON"
    if score < 0.50:
        return "UNCOMMON"
    if score < 0.75:
        return "RARE"
    return "MYTHIC"


def build_artifact_operator_packet(
    *,
    artifact_id: str = "",
    title: str = "",
    source_system: str = "manual",
    sources: list[dict[str, Any]] | None = None,
    felt_alignment: float | None = None,
    symbolic_alignment: float | None = None,
    sonic_plan_ref: str | None = None,
    uniqueness: float | None = None,
    blocked_by: list[str] | None = None,
) -> dict[str, Any]:
    """Build PhonomiconArtifactOperatorPacket.v0 (ARTIFACT_GOVERNANCE)."""
    aid = str(artifact_id or "").strip() or "artifact_unspecified"
    title_n = str(title or "").strip() or "UNTITLED"
    src_sys = str(source_system or "manual").strip() or "manual"

    blocks = list(blocked_by or [])
    for b in (
        "MINT_EXECUTION_BLOCKED",
        "MARKETPLACE_LISTING_BLOCKED",
        "WALLET_TRANSFER_BLOCKED",
        "PUBLICATION_BLOCKED",
        "PROMOTION_BLOCKED",
    ):
        if b not in blocks:
            blocks.append(b)

    provenance = build_provenance_chain(sources)
    felt = _f01(felt_alignment)
    symbolic = _f01(symbolic_alignment)
    uniq = _f01(uniqueness)

    if provenance["link_count"] == 0:
        proof_status = "NOT_COMPUTABLE"
        if "EMPTY_PROVENANCE_CHAIN" not in blocks:
            blocks.append("EMPTY_PROVENANCE_CHAIN")
        resonance = 0.0
    elif felt is None and symbolic is None:
        proof_status = "PROOF_INCOMPLETE"
        if "RESONANCE_INPUTS_INCOMPLETE" not in blocks:
            blocks.append("RESONANCE_INPUTS_INCOMPLETE")
        # chain presence alone gives base seed
        resonance = 0.25
    else:
        proof_status = "PROOF_SEEDED"
        f = felt if felt is not None else 0.5
        s = symbolic if symbolic is not None else 0.5
        u = uniq if uniq is not None else 0.5
        # weighted advisory resonance
        resonance = _clamp01(f * 0.4 + s * 0.35 + u * 0.25)

    proof_material = {
        "artifact_id": aid,
        "chain_root_hash": provenance["chain_root_hash"],
        "felt_alignment": felt,
        "symbolic_alignment": symbolic,
        "uniqueness": uniq,
        "sonic_plan_ref": sonic_plan_ref,
        "resonance_score": resonance,
    }
    proof_hash = canonical_hash(proof_material)

    rarity_score = _round6(
        _clamp01(
            resonance * 0.55
            + (uniq if uniq is not None else 0.0) * 0.30
            + min(provenance["link_count"], 5) / 5.0 * 0.15
        )
    )
    if proof_status == "NOT_COMPUTABLE":
        tier = "NOT_COMPUTABLE"
        rarity_score = 0.0
    else:
        tier = _rarity_tier(rarity_score)

    if proof_status == "NOT_COMPUTABLE":
        readiness = "NOT_COMPUTABLE"
    else:
        readiness = "SHADOW_OPERATOR_REVIEW"

    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "pipeline_id": PIPELINE_ID,
        "packet_id": "phop_"
        + canonical_hash(
            {
                "artifact_id": aid,
                "chain_root_hash": provenance["chain_root_hash"],
                "proof_hash": proof_hash,
            }
        )[:16],
        "artifact_id": aid,
        "title": title_n,
        "source_system": src_sys,
        "provenance": provenance,
        "proof_of_resonance": {
            "schema_version": "PhonomiconProofOfResonance.v0",
            "proof_status": proof_status,
            "resonance_score": _round6(resonance),
            "proof_hash": proof_hash,
            "felt_alignment": felt,
            "symbolic_alignment": symbolic,
            "sonic_plan_ref": sonic_plan_ref,
        },
        "rarity": {
            "schema_version": "PhonomiconRaritySeed.v0",
            "rarity_score": rarity_score,
            "tier": tier,
        },
        "readiness": readiness,
        "blocked_by": blocks,
        "mint_execution_blocked": True,
        "marketplace_listing_blocked": True,
        "wallet_transfer_blocked": True,
        "publication_blocked": True,
        "authority": dict(DEFAULT_AUTHORITY),
        "advisory_only": True,
        "lane": "ARTIFACT_GOVERNANCE",
        "producer": dict(PRODUCER),
        "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
    }
    body["canonical_hash"] = canonical_hash(body)
    return body


def build_artifact_operator_packet_from_sources(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Lift artifact-like dict with sources into operator packet."""
    d = artifact if isinstance(artifact, dict) else {}
    sources = d.get("sources") or d.get("provenance_sources") or []
    if not isinstance(sources, list):
        sources = []
    return build_artifact_operator_packet(
        artifact_id=str(d.get("artifact_id") or d.get("id") or ""),
        title=str(d.get("title") or d.get("name") or ""),
        source_system=str(d.get("source_system") or "manual"),
        sources=sources,
        felt_alignment=d.get("felt_alignment"),
        symbolic_alignment=d.get("symbolic_alignment"),
        sonic_plan_ref=str(d.get("sonic_plan_ref") or "") or None,
        uniqueness=d.get("uniqueness"),
        blocked_by=list(d.get("blocked_by") or [])
        if isinstance(d.get("blocked_by"), list)
        else None,
    )
