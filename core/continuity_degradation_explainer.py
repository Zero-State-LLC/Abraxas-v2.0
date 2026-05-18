from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

PATCH_ID = "PATCH-P33-CONTINUITY-DEGRADATION-EXPLAINER-001"
SCHEMA_VERSION = "ContinuityDegradationExplainer.v1"
EXPLAINER_ID = "continuity_degradation_explainer_001"

NOT_COMPUTABLE = "NOT_COMPUTABLE"
BLOCKED = "BLOCKED"

_GOVERNANCE_FLAGS: dict[str, Any] = {
    "advisory_only": True,
    "projection_only": True,
    "explainer_only": True,
    "non_authoritative": True,
    "evidence_linked": True,
    "mutation_allowed": False,
    "authority_granted": False,
    "execution_authority": False,
    "forecast_authority": False,
    "routing_change_allowed": False,
    "queue_mutation_allowed": False,
    "canon_mutation_allowed": False,
    "runtime_mutation_allowed": False,
    "adaptive_behavior_allowed": False,
    "speculative_causation_allowed": False,
    "psychological_claims_allowed": False,
    "auto_execute": False,
    "auto_approve": False,
    "command_channel": False,
    "bidirectional_control": False,
}

_VECTOR_ORDER = {
    "SOURCE_NOT_COMPUTABLE_PROPAGATION": 0,
    "CORRIDOR_PRESSURE_PERSISTENCE": 1,
    "LEDGER_POSTURE_PERSISTENCE": 2,
    "WEATHER_URGENCY_ALIGNMENT": 3,
    "ROUTING_PRIORITY_ALIGNMENT": 4,
    "UPSTREAM_BLOCKER_RECURRENCE": 5,
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
    }


def _stable_blockers(values: list[Any]) -> list[str]:
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _dominant_vectors(*, missing_or_corrupt: bool, pressure: bool, ledger_degraded: bool, weather_urgent: bool, routing_urgent: bool, blockers: list[str]) -> list[str]:
    vectors: list[str] = []
    if missing_or_corrupt:
        vectors.append("SOURCE_NOT_COMPUTABLE_PROPAGATION")
    if pressure:
        vectors.append("CORRIDOR_PRESSURE_PERSISTENCE")
    if ledger_degraded:
        vectors.append("LEDGER_POSTURE_PERSISTENCE")
    if weather_urgent:
        vectors.append("WEATHER_URGENCY_ALIGNMENT")
    if routing_urgent:
        vectors.append("ROUTING_PRIORITY_ALIGNMENT")
    if blockers:
        vectors.append("UPSTREAM_BLOCKER_RECURRENCE")
    return sorted(set(vectors), key=lambda item: (_VECTOR_ORDER.get(item, 999), item))


def build_continuity_degradation_explainer_packet(
    *,
    source_artifact_paths: dict[str, str] | None = None,
    source_packets: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
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

    blockers.extend(str(b) for b in weather.get("blocker_summary", []) if str(b))
    blockers.extend(str(b) for b in routing.get("blocker_summary", []) if str(b))
    blockers.extend(str(b) for b in ledger.get("blocker_summary", []) if str(b))
    blockers.extend(str(b) for b in corridor.get("blocker_summary", []) if str(b))
    blocker_summary = _stable_blockers(blockers)

    recurring_blockers = _stable_blockers([
        *(corridor.get("recurring_blocker_classes") or []),
        *(ledger.get("blocker_summary") or []),
    ])

    corridor_status = str(corridor.get("corridor_status", NOT_COMPUTABLE))
    corridor_final_status = str(corridor.get("final_status", NOT_COMPUTABLE))
    pressure_persistence_detected = bool(corridor.get("pressure_persistence_detected", False))

    ledger_final_status = str(ledger.get("final_status", NOT_COMPUTABLE))
    ledger_posture = str(ledger.get("ledger_posture", NOT_COMPUTABLE))

    weather_posture = str(weather.get("weather_posture", NOT_COMPUTABLE))
    attention_urgency = str(weather.get("attention_urgency", NOT_COMPUTABLE))

    routing_posture = str(routing.get("routing_posture", NOT_COMPUTABLE))
    review_priority_posture = str(routing.get("review_priority_posture", NOT_COMPUTABLE))

    missing_or_corrupt = any(v != "PRESENT" for v in source_status.values())
    ledger_degraded = ledger_final_status in {"ADVISORY_DEGRADED", BLOCKED} or ledger_posture in {"DEGRADED", BLOCKED}
    weather_urgent = weather_posture in {"DEGRADED", BLOCKED, "CRITICAL"} or attention_urgency in {"HIGH", "CRITICAL"}
    routing_urgent = routing_posture in {"ELEVATED", "CRITICAL", BLOCKED} or review_priority_posture in {"HIGH", "CRITICAL"}

    if missing_or_corrupt:
        final_status = NOT_COMPUTABLE
        explanation_posture = NOT_COMPUTABLE
    elif corridor_final_status == BLOCKED or corridor_status == "BLOCKED_PERSISTENCE":
        final_status = BLOCKED
        explanation_posture = BLOCKED
    elif pressure_persistence_detected:
        final_status = "ADVISORY_DEGRADED"
        explanation_posture = "PRESSURE_PERSISTENCE"
    elif ledger_degraded and weather_urgent and routing_urgent:
        final_status = "ADVISORY_DEGRADED"
        explanation_posture = "DEGRADED"
    elif weather_posture == "WATCH" or routing_posture == "WATCH" or ledger_posture == "WATCH":
        final_status = "ADVISORY_ONLY"
        explanation_posture = "WATCH"
    else:
        final_status = "ADVISORY_ONLY"
        explanation_posture = "CLEAR"

    dominant_vectors = _dominant_vectors(
        missing_or_corrupt=missing_or_corrupt,
        pressure=pressure_persistence_detected,
        ledger_degraded=ledger_degraded,
        weather_urgent=weather_urgent,
        routing_urgent=routing_urgent,
        blockers=blocker_summary,
    )

    reason_chain = [
        f"P32 corridor_status={corridor_status}",
        f"P32 pressure_persistence_detected={str(pressure_persistence_detected).lower()}",
        f"P31 ledger_posture={ledger_posture}",
        f"P29 weather_posture={weather_posture} attention_urgency={attention_urgency}",
        f"P30 routing_posture={routing_posture} review_priority_posture={review_priority_posture}",
        f"blocker_summary_count={len(blocker_summary)}",
    ]

    source_hashes = {
        key: (str(canonical_hash(payload)) if isinstance(payload, dict) else NOT_COMPUTABLE)
        for key, payload in sorted(loaded.items())
    }

    evidence_refs = _stable_blockers([
        f"weather_hash:{weather.get('weather_hash', NOT_COMPUTABLE)}",
        f"enhancer_hash:{routing.get('enhancer_hash', NOT_COMPUTABLE)}",
        f"ledger_hash:{ledger.get('ledger_hash', NOT_COMPUTABLE)}",
        f"corridor_hash:{corridor.get('corridor_hash', NOT_COMPUTABLE)}",
        *(f"entry_hash:{str(entry.get('entry_hash', NOT_COMPUTABLE))}" for entry in (ledger.get("entries") or []) if isinstance(entry, dict)),
        *(str(ref) for ref in (corridor.get("evidence_refs") or []) if str(ref)),
    ])

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "explainer_id": EXPLAINER_ID,
        "final_status": final_status,
        "explanation_posture": explanation_posture,
        "dominant_degradation_vectors": dominant_vectors,
        "reason_chain": reason_chain,
        "observed_signal_map": {
            "corridor_status": corridor_status,
            "corridor_final_status": corridor_final_status,
            "ledger_posture": ledger_posture,
            "ledger_final_status": ledger_final_status,
            "weather_posture": weather_posture,
            "attention_urgency": attention_urgency,
            "routing_posture": routing_posture,
            "review_priority_posture": review_priority_posture,
        },
        "recurring_blocker_classes": recurring_blockers,
        "source_artifacts": sources,
        "source_hashes": source_hashes,
        "blocker_summary": blocker_summary,
        "evidence_refs": evidence_refs,
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {
            "source_packet_presence": source_status,
            "deterministic": True,
            "advisory_only": True,
            "projection_only": True,
            "evidence_linked": True,
        },
    }
    packet["explainer_hash"] = canonical_hash(packet)
    return packet


def build_continuity_degradation_explainer_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P33 Continuity Degradation Explainer",
        "",
        f"- explainer_id: `{packet['explainer_id']}`",
        f"- final_status: `{packet['final_status']}`",
        f"- explanation_posture: `{packet['explanation_posture']}`",
        "",
        "## Dominant Degradation Vectors",
    ]
    vectors = packet.get("dominant_degradation_vectors", [])
    if vectors:
        lines.extend(f"- `{item}`" for item in vectors)
    else:
        lines.append("- none")

    lines.append("")
    lines.append("## Reason Chain")
    lines.extend(f"- {item}" for item in packet.get("reason_chain", []))

    lines.append("")
    lines.append("## Blockers")
    blockers = packet.get("blocker_summary", [])
    if blockers:
        lines.extend(f"- `{item}`" for item in blockers)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def write_continuity_degradation_explainer_packet(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_continuity_degradation_explainer_markdown(packet), encoding="utf-8")
