from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

PATCH_ID = "PATCH-P34-OPERATOR-CLIMATOLOGY-SUMMARY-001"
SCHEMA_VERSION = "OperatorClimatologySummary.v1"
SUMMARY_ID = "operator_climatology_summary_001"

NOT_COMPUTABLE = "NOT_COMPUTABLE"
BLOCKED = "BLOCKED"

_GOVERNANCE_FLAGS: dict[str, Any] = {
    "advisory_only": True,
    "projection_only": True,
    "climatology_only": True,
    "observation_only": True,
    "non_authoritative": True,
    "mutation_allowed": False,
    "authority_granted": False,
    "execution_authority": False,
    "forecast_authority": False,
    "trend_prediction_allowed": False,
    "readiness_claims_allowed": False,
    "adaptive_behavior_allowed": False,
    "psychological_claims_allowed": False,
    "routing_change_allowed": False,
    "queue_mutation_allowed": False,
    "canon_mutation_allowed": False,
    "runtime_mutation_allowed": False,
    "auto_execute": False,
    "auto_approve": False,
    "command_channel": False,
    "bidirectional_control": False,
}


def _load_json(path: str | Path) -> tuple[dict[str, Any] | None, str]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "MISSING"
    except (OSError, json.JSONDecodeError):
        return None, "CORRUPT"
    if not isinstance(payload, dict):
        return None, "CORRUPT"
    return payload, "PRESENT"


def _src_paths(paths: RuntimePaths) -> dict[str, str]:
    return {
        "operator_attention_weather": paths.operator_attention_weather_latest.as_posix(),
        "operator_review_routing_enhancer": paths.operator_review_routing_enhancer_latest.as_posix(),
        "operator_attention_ledger": paths.operator_attention_ledger_latest.as_posix(),
        "operator_fatigue_corridor": paths.operator_fatigue_corridor_latest.as_posix(),
        "continuity_degradation_explainer": paths.continuity_degradation_explainer_latest.as_posix(),
    }


def _count(values: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for v in values:
        key = str(v)
        counts[key] = counts.get(key, 0) + 1
    return {k: counts[k] for k in sorted(counts)}


def _normalize_blocker(value: Any) -> str:
    return str(value).strip().lower()


def build_operator_climatology_summary_packet(*, source_artifact_paths: dict[str, str] | None = None, source_packets: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    sources = source_artifact_paths or _src_paths(paths)

    loaded: dict[str, dict[str, Any] | None] = {}
    source_status: dict[str, str] = {}
    blockers: list[str] = []

    for key, path in sorted(sources.items()):
        payload, status = _load_json(path)
        loaded[key] = payload
        source_status[key] = status
        if status != "PRESENT":
            blockers.append(f"source_{status.lower()}:{key}")

    if source_packets:
        for key, payload in source_packets.items():
            loaded[key] = deepcopy(payload)
            source_status[key] = "PRESENT"

    weather = loaded.get("operator_attention_weather") or {}
    routing = loaded.get("operator_review_routing_enhancer") or {}
    ledger = loaded.get("operator_attention_ledger") or {}
    corridor = loaded.get("operator_fatigue_corridor") or {}
    explainer = loaded.get("continuity_degradation_explainer") or {}

    blockers.extend(str(b) for b in weather.get("blocker_summary", []) if str(b))
    blockers.extend(str(b) for b in routing.get("blocker_summary", []) if str(b))
    blockers.extend(str(b) for b in ledger.get("blocker_summary", []) if str(b))
    blockers.extend(str(b) for b in corridor.get("blocker_summary", []) if str(b))
    blockers.extend(str(b) for b in explainer.get("blocker_summary", []) if str(b))

    missing_or_corrupt = any(v != "PRESENT" for v in source_status.values())

    corridor_status = str(corridor.get("corridor_status", NOT_COMPUTABLE))
    corridor_final_status = str(corridor.get("final_status", NOT_COMPUTABLE))
    explainer_final_status = str(explainer.get("final_status", NOT_COMPUTABLE))
    explainer_posture = str(explainer.get("explanation_posture", NOT_COMPUTABLE))

    if missing_or_corrupt:
        final_status = NOT_COMPUTABLE
        climatology_posture = NOT_COMPUTABLE
    elif corridor_final_status == BLOCKED or explainer_final_status == BLOCKED or corridor_status == "BLOCKED_PERSISTENCE":
        final_status = BLOCKED
        climatology_posture = BLOCKED
    elif (
        bool(corridor.get("pressure_persistence_detected", False))
        or corridor_status == "PRESSURE_PERSISTENCE"
        or corridor_final_status == "ADVISORY_DEGRADED"
        or explainer_final_status == "ADVISORY_DEGRADED"
    ):
        final_status = "ADVISORY_DEGRADED"
        climatology_posture = "PRESSURE_PERSISTENCE" if corridor_status == "PRESSURE_PERSISTENCE" or bool(corridor.get("pressure_persistence_detected", False)) else "DEGRADED"
    elif "WATCH" in {str(weather.get("weather_posture", "")), str(routing.get("routing_posture", "")), str(ledger.get("ledger_posture", "")), explainer_posture}:
        final_status = "ADVISORY_ONLY"
        climatology_posture = "WATCH"
    else:
        final_status = "ADVISORY_ONLY"
        climatology_posture = "CLEAR"

    weather_posture_counts = _count([str(weather.get("weather_posture", NOT_COMPUTABLE))])
    attention_urgency_counts = _count([str(weather.get("attention_urgency", NOT_COMPUTABLE))])
    routing_posture_counts = _count([str(routing.get("routing_posture", NOT_COMPUTABLE))])
    review_priority_posture_counts = _count([str(routing.get("review_priority_posture", NOT_COMPUTABLE))])
    ledger_posture_counts = _count([str(ledger.get("ledger_posture", NOT_COMPUTABLE))])
    corridor_status_counts = _count([corridor_status])
    degradation_vector_counts = _count([str(v) for v in (explainer.get("dominant_degradation_vectors") or [])])
    blocker_class_counts = _count([_normalize_blocker(b) for b in blockers if _normalize_blocker(b)])

    blocker_summary = sorted(set(str(b).strip() for b in blockers if str(b).strip()))

    source_hashes = {
        key: (str(canonical_hash(payload)) if isinstance(payload, dict) else NOT_COMPUTABLE)
        for key, payload in sorted(loaded.items())
    }
    source_hash_lineage = {
        "weather_hash": str(weather.get("weather_hash", NOT_COMPUTABLE)),
        "enhancer_hash": str(routing.get("enhancer_hash", NOT_COMPUTABLE)),
        "ledger_hash": str(ledger.get("ledger_hash", NOT_COMPUTABLE)),
        "corridor_hash": str(corridor.get("corridor_hash", NOT_COMPUTABLE)),
        "explainer_hash": str(explainer.get("explainer_hash", NOT_COMPUTABLE)),
    }

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "summary_id": SUMMARY_ID,
        "final_status": final_status,
        "climatology_posture": climatology_posture,
        "observed_distribution_summary": {
            "signal_family_count": 8,
            "source_packet_count": len(sources),
            "blocker_count": len(blocker_summary),
        },
        "weather_posture_counts": weather_posture_counts,
        "attention_urgency_counts": attention_urgency_counts,
        "routing_posture_counts": routing_posture_counts,
        "review_priority_posture_counts": review_priority_posture_counts,
        "ledger_posture_counts": ledger_posture_counts,
        "corridor_status_counts": corridor_status_counts,
        "degradation_vector_counts": degradation_vector_counts,
        "blocker_class_counts": blocker_class_counts,
        "source_hash_lineage": source_hash_lineage,
        "source_artifacts": sources,
        "source_hashes": source_hashes,
        "blocker_summary": blocker_summary,
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {
            "source_packet_presence": source_status,
            "deterministic": True,
            "advisory_only": True,
            "projection_only": True,
            "observation_only": True,
        },
    }
    packet["summary_hash"] = canonical_hash(packet)
    return packet


def build_operator_climatology_summary_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P34 Operator Climatology Summary",
        "",
        f"- summary_id: `{packet['summary_id']}`",
        f"- final_status: `{packet['final_status']}`",
        f"- climatology_posture: `{packet['climatology_posture']}`",
        "",
        "## Observed Distribution Summary",
    ]
    for key, value in sorted((packet.get("observed_distribution_summary") or {}).items()):
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Blockers")
    blockers = packet.get("blocker_summary", [])
    if blockers:
        lines.extend(f"- `{item}`" for item in blockers)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def write_operator_climatology_summary_packet(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_climatology_summary_markdown(packet), encoding="utf-8")
