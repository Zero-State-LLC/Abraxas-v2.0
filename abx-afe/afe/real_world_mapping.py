from __future__ import annotations

from typing import Any

from afe.provenance import stable_hash
from afe.trace import AUTHORITY

BATCH_ID = "AFE-BATCH-004"
SOURCE_DATE = "2026-04-22"

PATTERN_MAPPINGS: dict[str, dict[str, str]] = {
    "authority_deception_meme": {
        "real_world_equivalent": "institutional narrative capture + viral amplification",
        "observation_use": "flag capture topology",
    },
    "distributed_trust_meme": {
        "real_world_equivalent": "decentralized community meme stabilization",
        "observation_use": "identify durable viral fields",
    },
    "false_alliance_authority": {
        "real_world_equivalent": "fake coalition + authority legitimation",
        "observation_use": "detect brittle social contracts",
    },
    "scarcity_deception": {
        "real_world_equivalent": "extraction under resource pressure",
        "observation_use": "detect exploitative incentives",
    },
    "recovery_meme_repair": {
        "real_world_equivalent": "shared symbolic repair loop",
        "observation_use": "detect reconciliation pathways",
    },
    "reputation_noise": {
        "real_world_equivalent": "gameable reputation signals",
        "observation_use": "detect status-system distortion",
    },
    "distributed_trust_recovery": {
        "real_world_equivalent": "decentralized repair system",
        "observation_use": "detect resilience networks",
    },
    "reputation_market": {
        "real_world_equivalent": "status-coupled product adoption pressure",
        "observation_use": "detect trend-market reputation loops",
    },
}

SCENARIO_SEEDS: tuple[dict[str, str], ...] = (
    {
        "scenario": "Cooperative Meme Challenge",
        "source_family": "TikTok formats",
        "source_domain": "slang/meme propagation fields",
        "pattern": "distributed_trust_meme",
    },
    {
        "scenario": "Authority War Narrative",
        "source_family": "global stressors",
        "source_domain": "political/narrative ecosystems",
        "pattern": "authority_deception_meme",
    },
    {
        "scenario": "Wellness Optimization Loop",
        "source_family": "consumer trends",
        "source_domain": "market behavior",
        "pattern": "reputation_market",
    },
    {
        "scenario": "AI Creator Tool Adoption",
        "source_family": "tech trends",
        "source_domain": "creator communities",
        "pattern": "distributed_trust_meme",
    },
    {
        "scenario": "Election Pressure Narrative",
        "source_family": "global stressors",
        "source_domain": "political/narrative ecosystems",
        "pattern": "false_alliance_authority",
    },
    {
        "scenario": "Earth Day Ritual Hashtag Loop",
        "source_family": "daily hashtags",
        "source_domain": "social media systems",
        "pattern": "recovery_meme_repair",
    },
    {
        "scenario": "Scarcity Inflation Cascade",
        "source_family": "global stressors",
        "source_domain": "market behavior",
        "pattern": "scarcity_deception",
    },
)


def build_batch004_mapping_packet() -> dict[str, Any]:
    observations = [_build_observation(index=index + 1, seed=seed) for index, seed in enumerate(SCENARIO_SEEDS)]
    metric_frame = build_abx_metric_frame(observations)
    packet = {
        "artifact_type": "AFERealWorldMappingBatch.v1",
        "batch_id": BATCH_ID,
        "source_date": SOURCE_DATE,
        "authority": AUTHORITY,
        "output_effect": "ANNOTATION_ONLY",
        "annotation_only": True,
        "non_filtering_compliance": True,
        "original_output_preserved": True,
        "live_ingestion_performed": False,
        "observations": observations,
        "abx_metric_frame": metric_frame,
        "forbidden_effects": {
            "suppress_output": False,
            "filter_output": False,
            "rewrite_output": False,
            "demote_output": False,
            "hide_output": False,
            "sanitize_output": False,
            "block_output": False,
            "mutate_canon": False,
            "alter_forecast_weights": False,
        },
    }
    packet["provenance_hash"] = stable_hash(packet)
    return packet


def build_abx_metric_frame(observations: list[dict[str, Any]]) -> dict[str, Any]:
    metrics = {
        "SDR": _metric_for(observations, "distributed_trust_meme", "recovery_meme_repair"),
        "MSI": _metric_for(observations, "authority_deception_meme", "false_alliance_authority", "scarcity_deception"),
        "RFR": _metric_for(observations, "recovery_meme_repair", "distributed_trust_recovery"),
        "ARF": _metric_for(observations, "distributed_trust_meme", "reputation_market"),
        "NMC": _metric_for(observations, "recovery_meme_repair", "reputation_market"),
    }
    frame = {
        "packet_type": "ABXMetricFrame.v1",
        "authority": AUTHORITY,
        "annotation_only": True,
        "metrics": metrics,
        "source": [BATCH_ID],
    }
    frame["provenance_hash"] = stable_hash(frame)
    return frame


def attach_mapping_to_output(original_output: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    return {
        "original_output": dict(original_output),
        "batch004_mapping_label": observation["afe_pattern_match"],
        "confidence": observation["confidence_score"],
        "provenance_notes": observation["provenance_notes"],
        "output_effect": "ANNOTATION_ONLY",
        "non_filtering_compliance": True,
    }


def _build_observation(*, index: int, seed: dict[str, str]) -> dict[str, Any]:
    pattern = seed["pattern"]
    mapping = PATTERN_MAPPINGS[pattern]
    confidence = _confidence_for(pattern)
    return {
        "observation_id": f"{BATCH_ID}-OBS-{index:03d}",
        "source_domain": seed["source_domain"],
        "source_family": seed["source_family"],
        "observed_topology": seed["scenario"],
        "afe_pattern_match": pattern,
        "real_world_equivalent": mapping["real_world_equivalent"],
        "observation_use": mapping["observation_use"],
        "confidence_score": confidence,
        "drift_label": _drift_label(pattern),
        "non_filtering_compliance": True,
        "output_effect": "ANNOTATION_ONLY",
        "provenance_notes": f"Spec-seeded {BATCH_ID} mapping from {SOURCE_DATE}; no live ingestion performed.",
    }


def _confidence_for(pattern: str) -> float:
    confidence_by_pattern = {
        "distributed_trust_meme": 0.86,
        "authority_deception_meme": 0.82,
        "reputation_market": 0.74,
        "false_alliance_authority": 0.78,
        "recovery_meme_repair": 0.8,
        "scarcity_deception": 0.84,
    }
    return confidence_by_pattern.get(pattern, 0.65)


def _drift_label(pattern: str) -> str:
    if pattern in {"authority_deception_meme", "false_alliance_authority", "scarcity_deception"}:
        return "DRIFT_RISING"
    if pattern in {"recovery_meme_repair", "distributed_trust_recovery"}:
        return "REPAIR_PATHWAY_OBSERVED"
    return "STABLE_PROPAGATION_OBSERVED"


def _metric_for(observations: list[dict[str, Any]], *patterns: str) -> float:
    if not observations:
        return 0.0
    matched = [obs for obs in observations if obs["afe_pattern_match"] in patterns]
    if not matched:
        return 0.0
    weighted = sum(float(obs["confidence_score"]) for obs in matched) / len(observations)
    return round(min(1.0, weighted), 6)
