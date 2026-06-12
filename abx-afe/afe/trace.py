from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from typing import Any

from afe.metrics import compute_metrics
from afe.models import AFESimulationEpisode
from afe.not_computable import not_computable_reasons
from afe.provenance import stable_hash

AUTHORITY = "SHADOW_ONLY_TRACE"


def build_trace_packet(episode: AFESimulationEpisode) -> dict[str, Any]:
    episode_payload = {
        "agent_id": episode.agent_id,
        "environment_id": episode.environment_id,
        "episode_id": episode.episode_id,
        "interaction_events": [asdict(event) for event in episode.interaction_events],
        "cooperation_markers": list(episode.cooperation_markers),
        "manipulation_markers": list(episode.manipulation_markers),
        "drift_markers": list(episode.drift_markers),
        "provenance": dict(episode.provenance),
    }
    reasons = not_computable_reasons(episode_payload)
    metrics = compute_metrics(episode.interaction_events)
    packet = {
        "packet_type": "AFETracePacket.v1",
        "status": "NOT_COMPUTABLE" if reasons else "OK",
        "agent_id": episode.agent_id,
        "environment_id": episode.environment_id,
        "episode_id": episode.episode_id,
        "metrics": asdict(metrics),
        "shadow_diagnostic_candidates": _diagnostics(metrics),
        "not_computable_reasons": reasons,
        "provenance_hash": stable_hash(episode_payload) if not reasons else "NOT_COMPUTABLE",
        "authority": AUTHORITY,
    }
    return packet


def attach_observation_to_abraxas_output(
    abraxas_output: dict[str, Any],
    trace_packet: dict[str, Any],
) -> dict[str, Any]:
    return {
        "abraxas_output": deepcopy(abraxas_output),
        "afe_observation": deepcopy(trace_packet),
        "authority": AUTHORITY,
        "non_filtering_observation_lock": True,
    }


def _diagnostics(metrics: Any) -> list[str]:
    candidates: list[str] = []
    if metrics.MDI >= 0.65:
        candidates.append("MANIPULATION_DRIFT_OBSERVED")
    if metrics.SES <= 0.35:
        candidates.append("LOW_SIMULATION_EQUILIBRIUM_STABILITY")
    if metrics.ACS >= 0.65:
        candidates.append("COOPERATION_STABILITY_OBSERVED")
    return candidates

