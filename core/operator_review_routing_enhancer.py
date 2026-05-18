from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

PATCH_ID = "PATCH-P30-OPERATOR-REVIEW-ROUTING-ENHANCER-001"
SCHEMA_VERSION = "OperatorReviewRoutingEnhancer.v1"
ENHANCER_ID = "operator_review_routing_enhancer_001"

NOT_COMPUTABLE = "NOT_COMPUTABLE"
BLOCKED = "BLOCKED"

_GOVERNANCE_FLAGS: dict[str, Any] = {
    "advisory_only": True,
    "projection_only": True,
    "operator_review_only": True,
    "non_authoritative": True,
    "routing_suggestion_only": True,
    "routing_change_allowed": False,
    "mutation_allowed": False,
    "authority_granted": False,
    "execution_authority": False,
    "forecast_authority": False,
    "command_channel": False,
    "bidirectional_control": False,
    "auto_execute": False,
    "auto_approve": False,
    "allow_autonomous_approval": False,
    "queue_mutation_allowed": False,
    "canon_mutation_allowed": False,
    "runtime_mutation_allowed": False,
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
        "coherence_field_operator_surface": paths.coherence_field_operator_surface_latest.as_posix(),
        "operator_review_queue": (paths.out_dir / "operator_review" / "latest.json").as_posix(),
    }


def _has_p0_p1_items(queue: dict[str, Any]) -> tuple[bool, int, int]:
    items = queue.get("items") if isinstance(queue.get("items"), list) else []
    p0 = sum(1 for i in items if isinstance(i, dict) and str(i.get("priority", "")).upper() == "P0")
    p1 = sum(1 for i in items if isinstance(i, dict) and str(i.get("priority", "")).upper() == "P1")
    return (p0 + p1 > 0), p0, p1


def _escalate(posture: str) -> str:
    ladder = ["NORMAL", "WATCH", "ELEVATED", "CRITICAL", "BLOCKED"]
    if posture not in ladder:
        return posture
    idx = ladder.index(posture)
    return ladder[min(idx + 1, len(ladder) - 1)]


def build_operator_review_routing_enhancer_packet(*, source_artifact_paths: dict[str, str] | None = None, source_packets: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
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
    p28 = loaded.get("coherence_field_operator_surface") or {}
    queue = loaded.get("operator_review_queue") or {}

    weather_posture = str(weather.get("weather_posture", NOT_COMPUTABLE))
    attention_urgency = str(weather.get("attention_urgency", NOT_COMPUTABLE))
    p28_blockers = p28.get("remaining_blockers") if isinstance(p28.get("remaining_blockers"), list) else []
    blockers.extend(str(b) for b in p28_blockers)

    missing_or_corrupt = any(v != "PRESENT" for v in source_status.values())

    if missing_or_corrupt:
        final_status, routing_posture, review_priority_posture = NOT_COMPUTABLE, BLOCKED, "CRITICAL"
    elif weather_posture == BLOCKED:
        final_status, routing_posture, review_priority_posture = BLOCKED, BLOCKED, "CRITICAL"
    elif attention_urgency == "CRITICAL":
        final_status, routing_posture, review_priority_posture = "ADVISORY_DEGRADED", "CRITICAL", "CRITICAL"
    elif weather_posture == "DEGRADED" or attention_urgency == "HIGH":
        final_status, routing_posture, review_priority_posture = "ADVISORY_DEGRADED", "ELEVATED", "HIGH"
    else:
        final_status, routing_posture, review_priority_posture = "ADVISORY_ONLY", ("WATCH" if weather_posture == "WATCH" else "NORMAL"), ("MEDIUM" if weather_posture == "WATCH" else "LOW")

    if p28_blockers and routing_posture not in {"CRITICAL", BLOCKED}:
        routing_posture = _escalate(routing_posture)
        if review_priority_posture == "LOW":
            review_priority_posture = "MEDIUM"
        elif review_priority_posture == "MEDIUM":
            review_priority_posture = "HIGH"

    queue_pressure, p0_count, p1_count = _has_p0_p1_items(queue)
    suggestions = [
        "Advisory only: no queue mutation, no routing authority, no execution authority.",
        f"Current routing posture: {routing_posture}",
        f"Current review priority posture: {review_priority_posture}",
    ]
    if queue_pressure:
        suggestions.append(f"Queue pressure detected: prioritize operator attention for P0/P1 items (P0={p0_count}, P1={p1_count}).")

    source_hashes = {k: (str(canonical_hash(v)) if isinstance(v, dict) else NOT_COMPUTABLE) for k, v in sorted(loaded.items())}

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "enhancer_id": ENHANCER_ID,
        "final_status": final_status,
        "routing_posture": routing_posture,
        "review_priority_posture": review_priority_posture,
        "advisory_routing_suggestions": suggestions,
        "rationale_chain": [
            f"P29 weather_posture={weather_posture}",
            f"P29 attention_urgency={attention_urgency}",
            f"P28 blocker_count={len(p28_blockers)}",
            f"Queue priority pressure P0={p0_count}, P1={p1_count}",
        ],
        "source_artifacts": sources,
        "source_hashes": source_hashes,
        "blocker_summary": sorted(set(str(b) for b in blockers if str(b))),
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {"source_packet_presence": source_status, "deterministic": True, "advisory_only": True},
    }
    packet["enhancer_hash"] = canonical_hash(packet)
    return packet


def build_operator_review_routing_enhancer_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P30 Operator Review Routing Enhancer",
        "",
        f"- enhancer_id: `{packet['enhancer_id']}`",
        f"- final_status: `{packet['final_status']}`",
        f"- routing_posture: `{packet['routing_posture']}`",
        f"- review_priority_posture: `{packet['review_priority_posture']}`",
        "",
        "## Advisory Routing Suggestions",
    ]
    for s in packet.get("advisory_routing_suggestions", []):
        lines.append(f"- {s}")
    lines.append("")
    lines.append("## Blockers")
    blockers = packet.get("blocker_summary", [])
    if blockers:
        for b in blockers:
            lines.append(f"- `{b}`")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def write_operator_review_routing_enhancer_packet(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_review_routing_enhancer_markdown(packet), encoding="utf-8")
