from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from afe.models import AFEAgentProfile, AFESimulationEnvironment
from afe.notion_logger import build_notion_payload_row
from afe.provenance import stable_hash
from afe.simulation import run_episode
from afe.trace import AUTHORITY, build_trace_packet

ENVIRONMENT_PRESETS: dict[str, AFESimulationEnvironment] = {
    "baseline": AFESimulationEnvironment(
        environment_id="cooperative_baseline",
        max_episode_length=12,
        rules=("stable_prosocial_control_field",),
    ),
    "cooperative_baseline": AFESimulationEnvironment(
        environment_id="cooperative_baseline",
        max_episode_length=12,
        rules=("stable_prosocial_control_field",),
    ),
    "scarcity": AFESimulationEnvironment(
        environment_id="scarcity_pressure",
        max_episode_length=12,
        rules=("resource_pressure", "extraction_drift_observation"),
    ),
    "scarcity_pressure": AFESimulationEnvironment(
        environment_id="scarcity_pressure",
        max_episode_length=12,
        rules=("resource_pressure", "extraction_drift_observation"),
    ),
    "high-noise": AFESimulationEnvironment(
        environment_id="high_noise_social",
        max_episode_length=12,
        rules=("ambiguity_pressure", "misread_loop_observation"),
    ),
    "high_noise_social": AFESimulationEnvironment(
        environment_id="high_noise_social",
        max_episode_length=12,
        rules=("ambiguity_pressure", "misread_loop_observation"),
    ),
    "authority": AFESimulationEnvironment(
        environment_id="authority_injection",
        max_episode_length=12,
        rules=("authority_inflation_probe",),
    ),
    "authority_injection": AFESimulationEnvironment(
        environment_id="authority_injection",
        max_episode_length=12,
        rules=("authority_inflation_probe",),
    ),
    "meme": AFESimulationEnvironment(
        environment_id="meme_contagion",
        max_episode_length=12,
        rules=("social_propagation_probe", "loop_capture_observation"),
    ),
    "meme_contagion": AFESimulationEnvironment(
        environment_id="meme_contagion",
        max_episode_length=12,
        rules=("social_propagation_probe", "loop_capture_observation"),
    ),
}


def build_hybrid_batch(
    *,
    batch_id: str,
    runs: int,
    seed_start: int,
    environment_set: Iterable[str],
    agent: AFEAgentProfile | None = None,
    export_target: str = "json",
) -> dict[str, Any]:
    if runs < 1:
        return _not_computable_batch(batch_id=batch_id, reason="RUN_COUNT_MUST_BE_POSITIVE")

    environments = _resolve_environments(environment_set)
    if not environments:
        return _not_computable_batch(batch_id=batch_id, reason="ENVIRONMENT_SET_EMPTY_OR_UNKNOWN")

    active_agent = agent or AFEAgentProfile(agent_id="afe-agent-001", cooperation_bias=0.7, manipulation_bias=0.1)
    run_records: list[dict[str, Any]] = []
    notion_rows: list[dict[str, Any]] = []

    for index in range(runs):
        run_index = index + 1
        seed = seed_start + index
        environment = environments[index % len(environments)]
        episode = run_episode(seed=seed, agent=active_agent, environment=environment)
        trace_packet = build_trace_packet(episode)
        run_record = {
            "run_id": f"{batch_id}-RUN-{run_index:03d}",
            "run_index": run_index,
            "seed": seed,
            "environment_id": environment.environment_id,
            "episode_length": len(episode.interaction_events),
            "trace_packet": trace_packet,
        }
        run_records.append(run_record)
        notion_rows.append(
            build_notion_payload_row(
                batch_id=batch_id,
                run_index=run_index,
                seed=seed,
                trace_packet=trace_packet,
                episode_length=len(episode.interaction_events),
            )
        )

    summary = _build_shadow_summary(run_records)
    packet = {
        "artifact_type": "AFEHybridBatch.v1",
        "batch_id": batch_id,
        "status": "OK" if summary["not_computable_count"] == 0 else "NOT_COMPUTABLE",
        "authority": AUTHORITY,
        "agent_trace_intake_export": {
            "export_type": "AgentTraceIntakeExport.v1",
            "target": "AGENT_TRACE_INTAKE_LAYER",
            "writeback_performed": False,
            "trace_packets": [record["trace_packet"] for record in run_records],
        },
        "export_target": export_target,
        "live_notion_writeback": False,
        "notion_payload_rows": notion_rows if export_target == "notion" else [],
        "shadow_batch_summary": summary,
        "runs": run_records,
        "non_limitation_locks": {
            "suppress_abraxas_output": False,
            "rewrite_abraxas_output": False,
            "filter_abraxas_output": False,
            "mutate_canon": False,
            "alter_forecast_weights": False,
            "live_notion_writeback": False,
        },
    }
    packet["batch_hash"] = stable_hash(packet)
    return packet


def _resolve_environments(environment_set: Iterable[str]) -> tuple[AFESimulationEnvironment, ...]:
    environments: list[AFESimulationEnvironment] = []
    for raw_name in environment_set:
        key = raw_name.strip()
        if not key:
            continue
        preset = ENVIRONMENT_PRESETS.get(key)
        if preset is not None:
            environments.append(preset)
    return tuple(environments)


def _build_shadow_summary(run_records: list[dict[str, Any]]) -> dict[str, Any]:
    if not run_records:
        return {
            "average_ACS": 0.0,
            "average_MDI": 0.0,
            "average_SES": 0.0,
            "drift_flags": 0,
            "strongest_environment_instability": "NOT_COMPUTABLE",
            "most_stable_environment": "NOT_COMPUTABLE",
            "not_computable_count": 1,
        }
    metrics_by_environment: dict[str, list[dict[str, float]]] = {}
    not_computable_count = 0
    drift_flags = 0
    for record in run_records:
        packet = record["trace_packet"]
        metrics = {key: float(value) for key, value in packet["metrics"].items()}
        metrics_by_environment.setdefault(str(record["environment_id"]), []).append(metrics)
        if packet["status"] == "NOT_COMPUTABLE":
            not_computable_count += 1
        if "MANIPULATION_DRIFT_OBSERVED" in packet["shadow_diagnostic_candidates"]:
            drift_flags += 1

    all_metrics = [metrics for values in metrics_by_environment.values() for metrics in values]
    instability_scores = {
        environment_id: _average([metrics["MDI"] + (1.0 - metrics["SES"]) for metrics in values])
        for environment_id, values in metrics_by_environment.items()
    }
    stability_scores = {
        environment_id: _average([metrics["SES"] for metrics in values])
        for environment_id, values in metrics_by_environment.items()
    }
    return {
        "average_ACS": _average([metrics["ACS"] for metrics in all_metrics]),
        "average_MDI": _average([metrics["MDI"] for metrics in all_metrics]),
        "average_SES": _average([metrics["SES"] for metrics in all_metrics]),
        "drift_flags": drift_flags,
        "strongest_environment_instability": max(instability_scores.items(), key=lambda item: (item[1], item[0]))[0],
        "most_stable_environment": max(stability_scores.items(), key=lambda item: (item[1], item[0]))[0],
        "not_computable_count": not_computable_count,
    }


def _average(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 6)


def _not_computable_batch(*, batch_id: str, reason: str) -> dict[str, Any]:
    packet = {
        "artifact_type": "AFEHybridBatch.v1",
        "batch_id": batch_id,
        "status": "NOT_COMPUTABLE",
        "authority": AUTHORITY,
        "agent_trace_intake_export": {
            "export_type": "AgentTraceIntakeExport.v1",
            "target": "AGENT_TRACE_INTAKE_LAYER",
            "writeback_performed": False,
            "trace_packets": [],
        },
        "export_target": "NOT_COMPUTABLE",
        "live_notion_writeback": False,
        "notion_payload_rows": [],
        "shadow_batch_summary": {
            "average_ACS": 0.0,
            "average_MDI": 0.0,
            "average_SES": 0.0,
            "drift_flags": 0,
            "strongest_environment_instability": "NOT_COMPUTABLE",
            "most_stable_environment": "NOT_COMPUTABLE",
            "not_computable_count": 1,
        },
        "runs": [],
        "not_computable_reasons": [reason],
        "non_limitation_locks": {
            "suppress_abraxas_output": False,
            "rewrite_abraxas_output": False,
            "filter_abraxas_output": False,
            "mutate_canon": False,
            "alter_forecast_weights": False,
            "live_notion_writeback": False,
        },
    }
    packet["batch_hash"] = stable_hash(packet)
    return packet
