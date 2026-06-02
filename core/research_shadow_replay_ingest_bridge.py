from __future__ import annotations

import json
from typing import Any

from core.belief_graph.belief_graph_packet import BeliefGraphPacket
from core.canonical.json import canonical_hash, write_canonical_json
from core.ingest.ingest_packet import IngestPacket

ARTIFACT_TYPE = "ResearchShadowReplayIngestBridge.v1"
FINAL_STATUS = "RESEARCH_SHADOW_REPLAY_INGEST_BRIDGE_ADVISORY_ONLY"

AUTHORITY_LOCK_KEYS: tuple[str, ...] = (
    "FORECAST_ROUTING",
    "CANON_MUTATION",
    "RUNTIME_MUTATION",
    "EXECUTION_AUTHORITY",
    "TRUTH_ASSIGNMENT",
    "BELIEF_PROMOTION",
)

BOUNDARY_RULES: tuple[str, ...] = (
    "shadow_only_no_forecast_routing",
    "shadow_only_no_canon_mutation",
    "shadow_only_no_runtime_mutation",
    "shadow_only_no_execution_authority",
    "shadow_only_no_truth_assignment",
    "shadow_only_no_belief_promotion",
    "local_only_no_web_ingest",
    "source_provenance_preserved",
    "epistemic_status_preserved",
    "not_computable_on_missing_evidence_linkage",
)


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def _authority_locks_from_belief_graph_packet(
    bgp: BeliefGraphPacket,
) -> dict[str, bool]:
    locks_dump = bgp.authority_locks.model_dump()
    return {key: bool(locks_dump.get(key, False)) for key in AUTHORITY_LOCK_KEYS}


def _authority_locks_from_ingest_packet(ip: IngestPacket) -> dict[str, bool]:
    return {
        "FORECAST_ROUTING": bool(ip.FORECAST_ROUTING),
        "CANON_MUTATION": bool(ip.CANON_MUTATION),
        "RUNTIME_MUTATION": bool(ip.RUNTIME_MUTATION),
        "EXECUTION_AUTHORITY": bool(ip.EXECUTION_AUTHORITY),
        "TRUTH_ASSIGNMENT": bool(ip.TRUTH_ASSIGNMENT),
        "BELIEF_PROMOTION": False,
    }


def _authority_seal_valid(locks: dict[str, bool]) -> bool:
    return all(locks.get(key) is False for key in AUTHORITY_LOCK_KEYS)


def _build_candidates(
    bgp: BeliefGraphPacket,
) -> tuple[list[dict[str, Any]], list[str]]:
    evidence_hashes = {ev.hash for ev in bgp.evidence}
    candidates: list[dict[str, Any]] = []
    not_computable_reasons: list[str] = []

    for claim in bgp.claims:
        resolved_refs = [ref for ref in claim.evidence_refs if ref in evidence_hashes]
        unresolved_refs = [ref for ref in claim.evidence_refs if ref not in evidence_hashes]

        evidence_linkage_resolved = bool(resolved_refs) and not unresolved_refs
        has_any_evidence = bool(claim.evidence_refs)

        if not has_any_evidence:
            not_computable = True
            nc_reason: str | None = "no_evidence_refs"
            not_computable_reasons.append(f"claim:{claim.id}:no_evidence_refs")
        elif unresolved_refs:
            not_computable = True
            nc_reason = "unresolved_evidence_refs"
            not_computable_reasons.append(f"claim:{claim.id}:unresolved_evidence_refs")
        elif claim.status == "NOT_COMPUTABLE":
            not_computable = True
            nc_reason = "claim_status_not_computable"
            not_computable_reasons.append(f"claim:{claim.id}:claim_status_not_computable")
        else:
            not_computable = False
            nc_reason = None

        candidates.append(
            {
                "candidate_id": claim.id,
                "source_claim_id": claim.id,
                "epistemic_status": claim.status,
                "evidence_refs": list(claim.evidence_refs),
                "resolved_evidence_refs": resolved_refs,
                "unresolved_evidence_refs": unresolved_refs,
                "evidence_linkage_resolved": evidence_linkage_resolved,
                "not_computable": not_computable,
                "not_computable_reason": nc_reason,
                "source_provenance": dict(claim.provenance),
            }
        )

    return candidates, not_computable_reasons


def build_research_shadow_replay_ingest_bridge(
    *,
    ingest_packet: IngestPacket | None = None,
    belief_graph_packet: BeliefGraphPacket | None = None,
) -> dict[str, Any]:
    not_computable_reasons: list[str] = []

    if ingest_packet is None and belief_graph_packet is None:
        not_computable_reasons.append("source_missing:no_ingest_or_belief_graph_packet")
        packet_base: dict[str, Any] = {
            "artifact_type": ARTIFACT_TYPE,
            "canonical_status": "ADVISORY_ONLY",
            "advisory_only": True,
            "projection_only": True,
            "FORECAST_ROUTING": False,
            "CANON_MUTATION": False,
            "RUNTIME_MUTATION": False,
            "EXECUTION_AUTHORITY": False,
            "TRUTH_ASSIGNMENT": False,
            "BELIEF_PROMOTION": False,
            "FINAL_STATUS": FINAL_STATUS,
            "status": "NOT_COMPUTABLE",
            "source_type": None,
            "authority_seal_valid": True,
            "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
            "shadow_replay_candidates": [],
            "not_computable_reasons": not_computable_reasons,
            "provenance": {
                "source": None,
                "source_provenance": None,
                "boundary_rules": list(BOUNDARY_RULES),
            },
        }
        return _finalize(packet_base)

    if ingest_packet is not None and belief_graph_packet is not None:
        not_computable_reasons.append(
            "source_ambiguous:both_ingest_and_belief_graph_packet_provided"
        )
        packet_base = {
            "artifact_type": ARTIFACT_TYPE,
            "canonical_status": "ADVISORY_ONLY",
            "advisory_only": True,
            "projection_only": True,
            "FORECAST_ROUTING": False,
            "CANON_MUTATION": False,
            "RUNTIME_MUTATION": False,
            "EXECUTION_AUTHORITY": False,
            "TRUTH_ASSIGNMENT": False,
            "BELIEF_PROMOTION": False,
            "FINAL_STATUS": FINAL_STATUS,
            "status": "NOT_COMPUTABLE",
            "source_type": None,
            "authority_seal_valid": True,
            "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
            "shadow_replay_candidates": [],
            "not_computable_reasons": not_computable_reasons,
            "provenance": {
                "source": None,
                "source_provenance": None,
                "boundary_rules": list(BOUNDARY_RULES),
            },
        }
        return _finalize(packet_base)

    # Resolve source type and extract belief graph packet
    if ingest_packet is not None:
        source_type = "ingest_packet"
        source_authority_locks = _authority_locks_from_ingest_packet(ingest_packet)
        source_provenance = dict(ingest_packet.provenance)
        bgp = ingest_packet.to_belief_graph_packet()
    else:
        assert belief_graph_packet is not None
        source_type = "belief_graph_packet"
        source_authority_locks = _authority_locks_from_belief_graph_packet(
            belief_graph_packet
        )
        source_provenance = dict(belief_graph_packet.provenance)
        bgp = belief_graph_packet

    # Validate authority seal on source
    authority_seal_valid = _authority_seal_valid(source_authority_locks)
    if not authority_seal_valid:
        not_computable_reasons.append("source_authority_seal_violated")

    # Build candidates from claims
    candidates, candidate_nc_reasons = _build_candidates(bgp)
    not_computable_reasons.extend(candidate_nc_reasons)

    if not_computable_reasons:
        status = "NOT_COMPUTABLE"
    elif not candidates:
        not_computable_reasons.append("no_claims_in_source")
        status = "NOT_COMPUTABLE"
    else:
        status = "BRIDGE_EMITTED"

    packet_base = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "advisory_only": True,
        "projection_only": True,
        "FORECAST_ROUTING": False,
        "CANON_MUTATION": False,
        "RUNTIME_MUTATION": False,
        "EXECUTION_AUTHORITY": False,
        "TRUTH_ASSIGNMENT": False,
        "BELIEF_PROMOTION": False,
        "FINAL_STATUS": FINAL_STATUS,
        "status": status,
        "source_type": source_type,
        "authority_seal_valid": authority_seal_valid,
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "shadow_replay_candidates": candidates,
        "not_computable_reasons": sorted(set(not_computable_reasons)),
        "provenance": {
            "source": source_type,
            "source_provenance": source_provenance,
            "boundary_rules": list(BOUNDARY_RULES),
        },
    }
    return _finalize(packet_base)


def write_research_shadow_replay_ingest_bridge(
    path: Any,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
