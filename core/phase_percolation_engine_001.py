from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from core.belief_graph.belief_graph_packet import BeliefGraphPacket
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "PhasePercolationPacket.v1"
PATCH_ID = "PHASE_PERCOLATION_ENGINE_001"
FINAL_STATUS = "PHASE_PERCOLATION_ENGINE_ADVISORY_ONLY"

AUTHORITY_LOCK_KEYS: tuple[str, ...] = (
    "FORECAST_ROUTING",
    "CANON_MUTATION",
    "RUNTIME_MUTATION",
    "EXECUTION_AUTHORITY",
    "TRUTH_ASSIGNMENT",
    "BELIEF_PROMOTION",
)

BOUNDARY_RULES: tuple[str, ...] = (
    "advisory_only_phase_projection",
    "no_forecast_routing",
    "no_truth_assignment",
    "no_canon_mutation",
    "no_runtime_mutation",
    "authority_locks_preserved_from_source",
    "deterministic_ordering",
    "stable_ids_only",
    "not_computable_propagates",
)

_STATUS_WEIGHT: dict[str, float] = {
    "OBSERVED": 1.0,
    "INFERRED": 0.7,
    "SPECULATIVE": 0.4,
    "NOT_COMPUTABLE": 0.0,
}

_STATUS_RANK: dict[str, int] = {
    "NOT_COMPUTABLE": -1,
    "SPECULATIVE": 0,
    "INFERRED": 1,
    "OBSERVED": 2,
}


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def _stable_id(prefix: str, *parts: object) -> str:
    token = json.dumps(parts, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}.{digest}"


def _normalize_belief_graph_packet(
    belief_graph_packet: BeliefGraphPacket | Mapping[str, Any] | None,
) -> BeliefGraphPacket | None:
    if belief_graph_packet is None:
        return None
    if isinstance(belief_graph_packet, BeliefGraphPacket):
        return belief_graph_packet
    return BeliefGraphPacket.model_validate(belief_graph_packet)


def _normalize_packet_sequence(
    packets: Mapping[str, Any] | list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] | None,
) -> list[dict[str, Any]]:
    if packets is None:
        return []
    if isinstance(packets, Mapping):
        return [dict(deepcopy(packets))]
    return [
        dict(deepcopy(packet))
        for packet in packets
        if isinstance(packet, Mapping)
    ]


def _extract_strings(value: Any) -> set[str]:
    if isinstance(value, str):
        stripped = value.strip()
        return {stripped} if stripped else set()
    if isinstance(value, Mapping):
        output: set[str] = set()
        for item in value.values():
            output |= _extract_strings(item)
        return output
    if isinstance(value, (list, tuple, set, frozenset)):
        output: set[str] = set()
        for item in value:
            output |= _extract_strings(item)
        return output
    return set()


def _authority_locks_from_belief_graph_packet(
    bgp: BeliefGraphPacket,
) -> dict[str, bool]:
    locks_dump = bgp.authority_locks.model_dump()
    return {key: bool(locks_dump.get(key, False)) for key in AUTHORITY_LOCK_KEYS}


def _authority_seal_valid(locks: Mapping[str, bool]) -> bool:
    return all(locks.get(key) is False for key in AUTHORITY_LOCK_KEYS)


def _normalize_replay_candidates(
    replay_packets: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    candidates: list[dict[str, Any]] = []
    replay_packet_hashes: list[str] = []
    reasons: list[str] = []

    for packet_index, packet in enumerate(replay_packets):
        replay_packet_hashes.append(canonical_hash(packet))
        raw_candidates = packet.get("shadow_replay_candidates")
        if raw_candidates is None:
            raw_candidates = packet.get("replay_candidates")
        if not isinstance(raw_candidates, list):
            reasons.append(f"replay_packet:{packet_index}:missing_candidate_list")
            continue
        for candidate_index, candidate in enumerate(raw_candidates):
            if not isinstance(candidate, Mapping):
                reasons.append(
                    f"replay_packet:{packet_index}:candidate:{candidate_index}:malformed"
                )
                continue
            normalized = dict(candidate)
            normalized["_packet_index"] = packet_index
            normalized["_packet_hash"] = replay_packet_hashes[-1]
            candidates.append(normalized)
    return candidates, sorted(set(replay_packet_hashes)), sorted(set(reasons))


def _normalize_audit_artifacts(
    audit_artifacts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for artifact_index, artifact in enumerate(audit_artifacts):
        tokens = _extract_strings(artifact)
        normalized.append(
            {
                "artifact_id": _stable_id(
                    "audit",
                    artifact_index,
                    sorted(tokens),
                    artifact.get("artifact_type"),
                    artifact.get("path"),
                ),
                "tokens": sorted(tokens),
                "artifact": artifact,
            }
        )
    return sorted(normalized, key=lambda item: str(item["artifact_id"]))


def _cluster_status(statuses: list[str], not_computable: bool) -> str:
    if not_computable:
        return "NOT_COMPUTABLE"
    if not statuses:
        return "SPECULATIVE"
    return max(statuses, key=lambda item: _STATUS_RANK.get(item, -1))


def _build_signal_clusters(
    bgp: BeliefGraphPacket,
    replay_candidates: list[dict[str, Any]],
    audit_artifacts: list[dict[str, Any]],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[str],
]:
    replay_by_claim: dict[str, list[dict[str, Any]]] = {}
    for candidate in replay_candidates:
        claim_id = str(
            candidate.get("source_claim_id")
            or candidate.get("candidate_id")
            or ""
        ).strip()
        if not claim_id:
            continue
        replay_by_claim.setdefault(claim_id, []).append(candidate)

    evidence_hashes = {ev.hash for ev in bgp.evidence}
    cluster_index: dict[tuple[str, ...], dict[str, Any]] = {}
    not_computable_reasons: list[str] = []

    for claim in bgp.claims:
        resolved_refs = tuple(ref for ref in claim.evidence_refs if ref in evidence_hashes)
        unresolved_refs = tuple(
            ref for ref in claim.evidence_refs if ref not in evidence_hashes
        )
        cluster_key = resolved_refs or tuple(claim.evidence_refs) or (f"claim:{claim.id}",)
        replay_matches = sorted(
            replay_by_claim.get(claim.id, []),
            key=lambda item: (
                str(item.get("candidate_id", "")),
                str(item.get("_packet_hash", "")),
            ),
        )

        replay_ids = [
            str(item.get("candidate_id") or item.get("source_claim_id") or claim.id)
            for item in replay_matches
        ]
        audit_matches = [
            artifact
            for artifact in audit_artifacts
            if claim.id in artifact["tokens"]
            or any(ref in artifact["tokens"] for ref in claim.evidence_refs)
            or any(candidate_id in artifact["tokens"] for candidate_id in replay_ids)
        ]

        claim_not_computable = (
            claim.status == "NOT_COMPUTABLE"
            or not claim.evidence_refs
            or bool(unresolved_refs)
            or any(bool(item.get("not_computable")) for item in replay_matches)
        )
        if claim.status == "NOT_COMPUTABLE":
            not_computable_reasons.append(f"claim:{claim.id}:claim_status_not_computable")
        if not claim.evidence_refs:
            not_computable_reasons.append(f"claim:{claim.id}:no_evidence_refs")
        if unresolved_refs:
            not_computable_reasons.append(f"claim:{claim.id}:unresolved_evidence_refs")
        if any(bool(item.get("not_computable")) for item in replay_matches):
            not_computable_reasons.append(f"claim:{claim.id}:replay_not_computable")

        cluster = cluster_index.setdefault(
            cluster_key,
            {
                "cluster_key": cluster_key,
                "claims": [],
                "evidence_refs": list(cluster_key),
                "replay_candidate_ids": set(),
                "audit_artifact_ids": set(),
                "source_provenance": [],
                "statuses": [],
                "not_computable": False,
            },
        )
        cluster["claims"].append(
            {
                "claim_id": claim.id,
                "status": claim.status,
                "resolved_evidence_refs": list(resolved_refs),
                "unresolved_evidence_refs": list(unresolved_refs),
            }
        )
        cluster["replay_candidate_ids"].update(replay_ids)
        cluster["audit_artifact_ids"].update(
            str(artifact["artifact_id"]) for artifact in audit_matches
        )
        cluster["source_provenance"].append(deepcopy(claim.provenance))
        cluster["statuses"].append(claim.status)
        cluster["not_computable"] = bool(cluster["not_computable"] or claim_not_computable)

    signal_clusters: list[dict[str, Any]] = []
    pressure_surfaces: list[dict[str, Any]] = []
    transition_candidates: list[dict[str, Any]] = []
    regime_candidates: list[dict[str, Any]] = []

    for cluster_key, cluster in sorted(cluster_index.items(), key=lambda item: item[0]):
        claim_ids = sorted(str(item["claim_id"]) for item in cluster["claims"])
        replay_ids = sorted(str(item) for item in cluster["replay_candidate_ids"])
        audit_ids = sorted(str(item) for item in cluster["audit_artifact_ids"])
        statuses = sorted(set(str(item) for item in cluster["statuses"]))
        pressure_score = round(
            sum(_STATUS_WEIGHT.get(str(item["status"]), 0.0) for item in cluster["claims"])
            + (0.35 * len(replay_ids))
            + (0.2 * len(audit_ids)),
            6,
        )
        cluster_status = _cluster_status(statuses, bool(cluster["not_computable"]))
        cluster_id = _stable_id("cluster", list(cluster_key), claim_ids)
        signal_cluster = {
            "cluster_id": cluster_id,
            "claim_ids": claim_ids,
            "evidence_refs": sorted(str(item) for item in cluster["evidence_refs"]),
            "claim_statuses": statuses,
            "replay_candidate_ids": replay_ids,
            "audit_artifact_ids": audit_ids,
            "source_provenance": sorted(
                cluster["source_provenance"],
                key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")),
            ),
            "signal_count": len(claim_ids) + len(replay_ids) + len(audit_ids),
            "pressure_score": pressure_score,
            "status": cluster_status,
            "not_computable": bool(cluster["not_computable"]),
        }
        signal_clusters.append(signal_cluster)

        threshold_labels: list[str] = []
        if pressure_score >= 1.0:
            threshold_labels.append("SIGNAL_CLUSTER")
        if pressure_score >= 1.75:
            threshold_labels.append("TRANSITION_CANDIDATE")
        if pressure_score >= 2.4:
            threshold_labels.append("REGIME_CANDIDATE")

        pressure_surfaces.append(
            {
                "pressure_surface_id": _stable_id("surface", cluster_id),
                "cluster_id": cluster_id,
                "claim_count": len(claim_ids),
                "replay_count": len(replay_ids),
                "audit_count": len(audit_ids),
                "pressure_score": pressure_score,
                "threshold_labels": threshold_labels,
                "status": cluster_status,
            }
        )

        if threshold_labels:
            transition_candidate = {
                "transition_candidate_id": _stable_id("transition", cluster_id),
                "cluster_id": cluster_id,
                "source_claim_ids": claim_ids,
                "pressure_score": pressure_score,
                "threshold_labels": threshold_labels,
                "status": cluster_status,
            }
            transition_candidates.append(transition_candidate)

            if "REGIME_CANDIDATE" in threshold_labels:
                regime_candidates.append(
                    {
                        "regime_candidate_id": _stable_id("regime", cluster_id),
                        "transition_candidate_id": transition_candidate[
                            "transition_candidate_id"
                        ],
                        "cluster_id": cluster_id,
                        "source_claim_ids": claim_ids,
                        "pressure_score": pressure_score,
                        "status": cluster_status,
                    }
                )

    return (
        sorted(signal_clusters, key=lambda item: str(item["cluster_id"])),
        sorted(pressure_surfaces, key=lambda item: str(item["pressure_surface_id"])),
        sorted(
            transition_candidates, key=lambda item: str(item["transition_candidate_id"])
        ),
        sorted(regime_candidates, key=lambda item: str(item["regime_candidate_id"])),
        sorted(set(not_computable_reasons)),
    )


def _build_threshold_crossings(
    transition_candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    thresholds = {
        "SIGNAL_CLUSTER": 1.0,
        "TRANSITION_CANDIDATE": 1.75,
        "REGIME_CANDIDATE": 2.4,
    }
    crossings: list[dict[str, Any]] = []
    for candidate in transition_candidates:
        for threshold_name in candidate["threshold_labels"]:
            threshold_value = thresholds[threshold_name]
            crossings.append(
                {
                    "threshold_crossing_id": _stable_id(
                        "threshold",
                        candidate["transition_candidate_id"],
                        threshold_name,
                    ),
                    "transition_candidate_id": candidate["transition_candidate_id"],
                    "cluster_id": candidate["cluster_id"],
                    "threshold_name": threshold_name,
                    "threshold_value": threshold_value,
                    "observed_value": candidate["pressure_score"],
                    "status": candidate["status"],
                }
            )
    return sorted(crossings, key=lambda item: str(item["threshold_crossing_id"]))


def _packet_status(
    *,
    signal_clusters: list[dict[str, Any]],
    transition_candidates: list[dict[str, Any]],
    regime_candidates: list[dict[str, Any]],
    not_computable_reasons: list[str],
) -> str:
    if not_computable_reasons:
        return "NOT_COMPUTABLE"
    candidate_statuses = [
        str(item["status"])
        for item in (*regime_candidates, *transition_candidates, *signal_clusters)
    ]
    if not candidate_statuses:
        return "NOT_COMPUTABLE"
    return max(candidate_statuses, key=lambda item: _STATUS_RANK.get(item, -1))


def build_phase_percolation_packet(
    *,
    belief_graph_packet: BeliefGraphPacket | Mapping[str, Any] | None = None,
    replay_packets: Mapping[str, Any]
    | list[Mapping[str, Any]]
    | tuple[Mapping[str, Any], ...]
    | None = None,
    audit_artifacts: Mapping[str, Any]
    | list[Mapping[str, Any]]
    | tuple[Mapping[str, Any], ...]
    | None = None,
) -> dict[str, Any]:
    bgp = _normalize_belief_graph_packet(belief_graph_packet)
    replay_packet_list = _normalize_packet_sequence(replay_packets)
    audit_artifact_list = _normalize_packet_sequence(audit_artifacts)
    not_computable_reasons: list[str] = []

    if bgp is None:
        not_computable_reasons.append("belief_graph_packet_missing")
        packet_base: dict[str, Any] = {
            "schema_version": ARTIFACT_TYPE,
            "artifact_type": ARTIFACT_TYPE,
            "patch_id": PATCH_ID,
            "status": "NOT_COMPUTABLE",
            "advisory_only": True,
            "projection_only": True,
            "deterministic_ordering": True,
            "stable_ids": True,
            "authority_seal_valid": True,
            "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
            "signal_clusters": [],
            "pressure_surfaces": [],
            "transition_candidates": [],
            "regime_candidates": [],
            "threshold_crossings": [],
            "not_computable_reasons": not_computable_reasons,
            "provenance": {
                "source": None,
                "source_provenance": None,
                "source_authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
                "replay_packet_hashes": [],
                "audit_artifact_ids": [],
                "boundary_rules": list(BOUNDARY_RULES),
            },
            "FORECAST_ROUTING": False,
            "CANON_MUTATION": False,
            "RUNTIME_MUTATION": False,
            "EXECUTION_AUTHORITY": False,
            "TRUTH_ASSIGNMENT": False,
            "BELIEF_PROMOTION": False,
            "FINAL_STATUS": FINAL_STATUS,
        }
        return _finalize(packet_base)

    source_authority_locks = _authority_locks_from_belief_graph_packet(bgp)
    authority_seal_valid = _authority_seal_valid(source_authority_locks)
    if not authority_seal_valid:
        not_computable_reasons.append("source_authority_seal_violated")

    replay_candidates, replay_packet_hashes, replay_reasons = _normalize_replay_candidates(
        replay_packet_list
    )
    not_computable_reasons.extend(replay_reasons)
    normalized_audit_artifacts = _normalize_audit_artifacts(audit_artifact_list)

    (
        signal_clusters,
        pressure_surfaces,
        transition_candidates,
        regime_candidates,
        cluster_reasons,
    ) = _build_signal_clusters(bgp, replay_candidates, normalized_audit_artifacts)
    not_computable_reasons.extend(cluster_reasons)
    threshold_crossings = _build_threshold_crossings(transition_candidates)

    status = _packet_status(
        signal_clusters=signal_clusters,
        transition_candidates=transition_candidates,
        regime_candidates=regime_candidates,
        not_computable_reasons=sorted(set(not_computable_reasons)),
    )

    packet_base = {
        "schema_version": ARTIFACT_TYPE,
        "artifact_type": ARTIFACT_TYPE,
        "patch_id": PATCH_ID,
        "status": status,
        "advisory_only": True,
        "projection_only": True,
        "deterministic_ordering": True,
        "stable_ids": True,
        "authority_seal_valid": authority_seal_valid,
        "authority_locks": {key: False for key in AUTHORITY_LOCK_KEYS},
        "signal_clusters": signal_clusters,
        "pressure_surfaces": pressure_surfaces,
        "transition_candidates": transition_candidates,
        "regime_candidates": regime_candidates,
        "threshold_crossings": threshold_crossings,
        "not_computable_reasons": sorted(set(not_computable_reasons)),
        "provenance": {
            "source": "belief_graph_packet",
            "source_provenance": deepcopy(bgp.provenance),
            "source_authority_locks": source_authority_locks,
            "replay_packet_hashes": replay_packet_hashes,
            "audit_artifact_ids": [
                str(item["artifact_id"]) for item in normalized_audit_artifacts
            ],
            "boundary_rules": list(BOUNDARY_RULES),
        },
        "FORECAST_ROUTING": False,
        "CANON_MUTATION": False,
        "RUNTIME_MUTATION": False,
        "EXECUTION_AUTHORITY": False,
        "TRUTH_ASSIGNMENT": False,
        "BELIEF_PROMOTION": False,
        "FINAL_STATUS": FINAL_STATUS,
    }
    return _finalize(packet_base)


def build_phase_percolation_markdown(packet: Mapping[str, Any]) -> str:
    lines = [
        "# PHASE_PERCOLATION_ENGINE_001",
        "",
        f"- status: `{packet['status']}`",
        f"- signal_clusters: `{len(packet.get('signal_clusters', []))}`",
        f"- transition_candidates: `{len(packet.get('transition_candidates', []))}`",
        f"- regime_candidates: `{len(packet.get('regime_candidates', []))}`",
        "",
        "## Threshold Crossings",
    ]
    threshold_crossings = packet.get("threshold_crossings", [])
    if isinstance(threshold_crossings, list) and threshold_crossings:
        for crossing in threshold_crossings:
            if not isinstance(crossing, Mapping):
                continue
            lines.append(
                "- "
                f"`{crossing.get('threshold_crossing_id')}` "
                f"{crossing.get('threshold_name')} "
                f"score={crossing.get('observed_value')}"
            )
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def write_phase_percolation_packet(path: str | Path, packet: dict[str, Any]) -> None:
    target = Path(path)
    write_canonical_json(target, packet)
    target.with_suffix(".md").write_text(
        build_phase_percolation_markdown(packet), encoding="utf-8"
    )
