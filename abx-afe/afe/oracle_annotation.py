from __future__ import annotations

from copy import deepcopy
from typing import Any

from afe.provenance import stable_hash
from afe.real_world_mapping import build_batch004_mapping_packet
from afe.trace import AUTHORITY

ALLOWED_LABELS = (
    "trust topology stable",
    "trust topology degraded",
    "manipulation drift detected",
    "authority capture indicated",
    "deception loop indicated",
    "meme propagation stabilized",
    "distributed trust resilience observed",
    "recovery loop partial",
    "symbolic attention cluster",
    "participatory meme loop",
    "authority narrative stress",
    "scarcity pressure signal",
    "distributed trust opportunity",
    "long-term adoption trend",
    "NOT_COMPUTABLE",
)


def build_oracle_annotation(
    *,
    trace_packets: list[dict[str, Any]] | None = None,
    batch004_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    traces = trace_packets or []
    mapping_packet = batch004_packet or build_batch004_mapping_packet()
    metrics = _aggregate_afe_metrics(traces)
    source_run_ids = _source_run_ids(traces, mapping_packet)
    labels = [] if not source_run_ids else _labels_from_metrics(metrics) + _labels_from_batch004(mapping_packet)
    drift_flags = _drift_flags_from_trace_packets(traces) + _drift_flags_from_batch004(mapping_packet)
    observation = {
        "authority": AUTHORITY,
        "non_filtering_compliance": True,
        "source_run_ids": source_run_ids,
        "metrics": metrics,
        "labels": _unique_ordered(labels) or ["NOT_COMPUTABLE"],
        "drift_flags": _unique_ordered(drift_flags),
        "provenance_hash": "PENDING",
        "output_effect": "ANNOTATION_ONLY",
    }
    observation["provenance_hash"] = stable_hash(
        {
            "trace_packets": traces,
            "batch004_provenance_hash": mapping_packet.get("provenance_hash", "NOT_COMPUTABLE"),
            "observation_without_hash": {key: value for key, value in observation.items() if key != "provenance_hash"},
        }
    )
    return {"afe_observation": observation}


def attach_annotation_to_oracle_output(
    oracle_output: dict[str, Any],
    annotation: dict[str, Any],
) -> dict[str, Any]:
    return {
        "oracle_output": deepcopy(oracle_output),
        "afe_shadow_observation_panel": deepcopy(annotation["afe_observation"]),
        "observation_authority": AUTHORITY,
        "output_effect": "ANNOTATION_ONLY",
        "non_filtering_compliance": True,
        "forbidden_effects": {
            "delete_oracle_text": False,
            "shorten_oracle_text": False,
            "rewrite_oracle_text": False,
            "soften_oracle_text": False,
            "hide_oracle_text": False,
            "sanitize_oracle_text": False,
            "rank_oracle_text_invisibly": False,
            "suppress_generated_interpretations": False,
            "mutate_oracle_mode_routing": False,
            "bypass_provenance_requirements": False,
        },
    }


def _aggregate_afe_metrics(trace_packets: list[dict[str, Any]]) -> dict[str, float]:
    metric_keys = ("ACS", "MDI", "SES", "SLI", "ECI")
    if not trace_packets:
        return {key: 0.0 for key in metric_keys}
    aggregate: dict[str, float] = {}
    for key in metric_keys:
        values = [float(packet.get("metrics", {}).get(key, 0.0)) for packet in trace_packets]
        aggregate[key] = round(sum(values) / len(values), 6)
    return aggregate


def _labels_from_metrics(metrics: dict[str, float]) -> list[str]:
    labels: list[str] = []
    if metrics["ACS"] >= 0.65 and metrics["SES"] >= 0.55:
        labels.append("trust topology stable")
    if metrics["SES"] < 0.35:
        labels.append("trust topology degraded")
    if metrics["MDI"] >= 0.65:
        labels.append("manipulation drift detected")
    if metrics["SLI"] >= 0.65:
        labels.append("distributed trust resilience observed")
    if metrics["ECI"] < 0.25:
        labels.append("recovery loop partial")
    return labels


def _labels_from_batch004(packet: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    for observation in packet.get("observations", []):
        pattern = str(observation.get("afe_pattern_match", ""))
        source_family = str(observation.get("source_family", ""))
        if pattern == "authority_deception_meme":
            labels.append("authority narrative stress")
            labels.append("authority capture indicated")
        if pattern == "false_alliance_authority":
            labels.append("deception loop indicated")
        if pattern == "scarcity_deception":
            labels.append("scarcity pressure signal")
        if pattern == "distributed_trust_meme":
            labels.append("distributed trust opportunity")
        if pattern == "recovery_meme_repair":
            labels.append("symbolic attention cluster")
        if "TikTok" in source_family:
            labels.append("participatory meme loop")
        if source_family in {"consumer trends", "tech trends"}:
            labels.append("long-term adoption trend")
    return labels


def _drift_flags_from_trace_packets(trace_packets: list[dict[str, Any]]) -> list[str]:
    flags: list[str] = []
    for packet in trace_packets:
        flags.extend(str(flag) for flag in packet.get("shadow_diagnostic_candidates", []))
        flags.extend(str(reason) for reason in packet.get("not_computable_reasons", []))
    return flags


def _drift_flags_from_batch004(packet: dict[str, Any]) -> list[str]:
    return [
        str(observation["drift_label"])
        for observation in packet.get("observations", [])
        if str(observation.get("drift_label", "")).startswith("DRIFT")
    ]


def _source_run_ids(trace_packets: list[dict[str, Any]], batch004_packet: dict[str, Any]) -> list[str]:
    ids = [str(packet.get("episode_id", "NOT_COMPUTABLE")) for packet in trace_packets]
    ids.extend(str(source) for source in batch004_packet.get("abx_metric_frame", {}).get("source", []))
    return _unique_ordered(ids)


def _unique_ordered(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            unique.append(value)
    return unique
