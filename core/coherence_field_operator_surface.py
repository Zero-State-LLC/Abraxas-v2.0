"""Deterministic operator-facing coherence field surface over P27 analytics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

from core.status_result import (
    STATUS_BLOCKED as BLOCKED,
    STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE,
)

PATCH_ID = "PATCH-P28-COHERENCE-FIELD-AAL-VIZ-OPERATOR-SURFACE-001"
SURFACE_SCHEMA = "CoherenceFieldOperatorSurface.v1"
PRESENT = "PRESENT"

_INVARIANTS: dict[str, Any] = {
    "advisory_only": True,
    "analytics_only": True,
    "projection_only": True,
    "mutation_allowed": False,
    "authority_granted": False,
    "forecast_authority": False,
    "execution_authority": False,
    "command_channel": False,
    "bidirectional_control": False,
    "autonomous_adaptation": False,
}

_FORBIDDEN_TRUE_FLAGS = frozenset(
    {
        "mutation_allowed",
        "authority_granted",
        "forecast_authority",
        "execution_authority",
        "command_channel",
        "bidirectional_control",
        "autonomous_adaptation",
    }
)

_SEVERITY_RANK = {
    "BLOCKED": 0,
    "CRITICAL": 1,
    "DEGRADED": 2,
    "HIGH": 3,
    "WATCH": 4,
    "MEDIUM": 5,
    "STABLE": 6,
    "LOW": 7,
    "LOCKED": 8,
    NOT_COMPUTABLE: 9,
}


def _apply_invariants(payload: dict[str, Any]) -> dict[str, Any]:
    return {**payload, **_INVARIANTS}


def _as_str(value: Any, default: str = "") -> str:
    return value if isinstance(value, str) else default


def _as_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(float(value))
        except ValueError:
            return default
    return default


def _as_float(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return default
    return default


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted(str(item) for item in value if str(item))


def _bound(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 6)


def _load_artifact(path: str | Path | None) -> tuple[dict[str, Any] | None, str]:
    if path is None:
        return None, "MISSING"
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "MISSING"
    except (json.JSONDecodeError, OSError):
        return None, "CORRUPT"
    if not isinstance(payload, dict):
        return None, "CORRUPT"
    return payload, "PRESENT"


def _safe_hash(payload: dict[str, Any] | None) -> str:
    if payload is None:
        return NOT_COMPUTABLE
    try:
        return str(canonical_hash(payload))
    except Exception:
        return NOT_COMPUTABLE


def _scan_forbidden_true_flags(payload: Any, prefix: str = "") -> list[str]:
    matches: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            key_str = str(key)
            path = f"{prefix}.{key_str}" if prefix else key_str
            if key_str in _FORBIDDEN_TRUE_FLAGS and value is True:
                matches.append(path)
            matches.extend(_scan_forbidden_true_flags(value, path))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            path = f"{prefix}[{index}]" if prefix else f"[{index}]"
            matches.extend(_scan_forbidden_true_flags(value, path))
    return sorted(set(matches))


def _phase_alignment_value(bucket: str) -> float:
    return {
        "LOW": 0.25,
        "MODERATE": 0.5,
        "HIGH": 0.75,
        "LOCKED": 1.0,
    }.get(bucket, 0.0)


def _derive_operator_posture(status: str, aggregate: float, dissonance: float) -> str:
    if status == BLOCKED:
        return BLOCKED
    if status == NOT_COMPUTABLE:
        return NOT_COMPUTABLE
    if aggregate >= 0.85 and dissonance <= 0.15:
        return "LOCKED"
    if aggregate >= 0.70 and dissonance <= 0.30:
        return "STABLE"
    if aggregate >= 0.50:
        return "WATCH"
    return "DEGRADED"


def _derive_attention_level(status: str, aggregate: float, dissonance: float) -> str:
    if status == BLOCKED:
        return "CRITICAL"
    if status == NOT_COMPUTABLE:
        return NOT_COMPUTABLE
    if dissonance >= 0.60:
        return "HIGH"
    if dissonance >= 0.35 or aggregate < 0.50:
        return "MEDIUM"
    return "LOW"


def _badge_set(
    *,
    status: str,
    aggregate: float,
    dissonance: float,
    phase_bucket: str,
    dominant_component: str,
    replay_resonance_zone_count: int,
    topology_alignment_zone_count: int,
) -> list[str]:
    badges: set[str] = set()
    if status == BLOCKED:
        badges.add("AUTHORITY_BLOCKED")
    if status == NOT_COMPUTABLE:
        badges.add(NOT_COMPUTABLE)
    if status == PRESENT and aggregate >= 0.85 and dissonance <= 0.15:
        badges.add("LOCKED_COHERENCE")
    if replay_resonance_zone_count > 0 or dominant_component == "replay_resonance":
        badges.add("REPLAY_RESONANT")
    if topology_alignment_zone_count > 0 or dominant_component == "topology_alignment":
        badges.add("TOPOLOGY_ALIGNED")
    if phase_bucket in {"HIGH", "LOCKED"}:
        badges.add("PHASE_ALIGNED")
    if dissonance > 0.0:
        badges.add("DISSONANCE_PRESENT")
    return sorted(badges)


def _card_status_for_signal(status: str, score: float) -> str:
    if status in {BLOCKED, NOT_COMPUTABLE}:
        return status
    if score >= 0.85:
        return "LOCKED"
    if score >= 0.70:
        return "STABLE"
    if score >= 0.50:
        return "WATCH"
    return "DEGRADED"


def _cards(
    *,
    status: str,
    aggregate: float,
    resonance: float,
    dissonance: float,
    phase_bucket: str,
    topology_alignment_zone_count: int,
    replay_resonance_zone_count: int,
    posture: str,
) -> list[dict[str, Any]]:
    phase_score = _phase_alignment_value(phase_bucket)
    topology_score = 1.0 if topology_alignment_zone_count > 0 else 0.0
    replay_score = 1.0 if replay_resonance_zone_count > 0 else 0.0

    cards: list[dict[str, Any]] = [
        {
            "card_id": "aggregate_coherence",
            "title": "Aggregate Coherence",
            "status": posture if posture in {BLOCKED, NOT_COMPUTABLE} else _card_status_for_signal(status, aggregate),
            "score": _bound(aggregate),
            "source_field": "aggregate_coherence_score",
            "advisory_text": "Operator-level aggregate coherence posture from P27 analytics.",
        },
        {
            "card_id": "resonance",
            "title": "Resonance",
            "status": _card_status_for_signal(status, resonance),
            "score": _bound(resonance),
            "source_field": "resonance_score",
            "advisory_text": "Resonance intensity projection from P27 packet.",
        },
        {
            "card_id": "dissonance",
            "title": "Dissonance",
            "status": _card_status_for_signal(status, _bound(1.0 - dissonance)),
            "score": _bound(dissonance),
            "source_field": "dissonance_score",
            "advisory_text": "Dissonance pressure requiring operator attention.",
        },
        {
            "card_id": "phase_alignment",
            "title": "Phase Alignment",
            "status": _card_status_for_signal(status, phase_score),
            "score": _bound(phase_score),
            "source_field": "phase_alignment_bucket",
            "advisory_text": "Phase alignment bucket projected as stable rail value.",
        },
        {
            "card_id": "topology_alignment",
            "title": "Topology Alignment",
            "status": _card_status_for_signal(status, topology_score),
            "score": _bound(topology_score),
            "source_field": "topology_alignment_zone_count",
            "advisory_text": "Topology alignment evidence from P27 coherence zones.",
        },
        {
            "card_id": "replay_resonance",
            "title": "Replay Resonance",
            "status": _card_status_for_signal(status, replay_score),
            "score": _bound(replay_score),
            "source_field": "replay_resonance_zone_count",
            "advisory_text": "Replay resonance evidence for operator monitoring.",
        },
    ]
    return sorted(
        cards,
        key=lambda item: (
            _SEVERITY_RANK.get(_as_str(item.get("status")), 999),
            -_as_float(item.get("score")),
            _as_str(item.get("card_id")),
        ),
    )


def _rails(
    *,
    status: str,
    aggregate: float,
    resonance: float,
    dissonance: float,
    phase_bucket: str,
    topology_alignment_zone_count: int,
    replay_resonance_zone_count: int,
) -> list[dict[str, Any]]:
    phase_score = _phase_alignment_value(phase_bucket)
    topology_score = 1.0 if topology_alignment_zone_count > 0 else 0.0
    replay_score = 1.0 if replay_resonance_zone_count > 0 else 0.0
    return [
        {
            "rail_id": "aggregate_coherence",
            "title": "Aggregate Coherence",
            "status": status,
            "value": _bound(aggregate),
            "source_field": "aggregate_coherence_score",
            "projection_only": True,
        },
        {
            "rail_id": "resonance",
            "title": "Resonance",
            "status": status,
            "value": _bound(resonance),
            "source_field": "resonance_score",
            "projection_only": True,
        },
        {
            "rail_id": "dissonance",
            "title": "Dissonance",
            "status": status,
            "value": _bound(dissonance),
            "source_field": "dissonance_score",
            "projection_only": True,
        },
        {
            "rail_id": "phase_alignment",
            "title": "Phase Alignment",
            "status": status,
            "value": _bound(phase_score),
            "source_field": "phase_alignment_bucket",
            "projection_only": True,
        },
        {
            "rail_id": "topology_alignment",
            "title": "Topology Alignment",
            "status": status,
            "value": _bound(topology_score),
            "source_field": "topology_alignment_zone_count",
            "projection_only": True,
        },
        {
            "rail_id": "replay_resonance",
            "title": "Replay Resonance",
            "status": status,
            "value": _bound(replay_score),
            "source_field": "replay_resonance_zone_count",
            "projection_only": True,
        },
    ]


def _observations(
    *,
    status: str,
    posture: str,
    attention: str,
    aggregate: float,
    dissonance: float,
) -> list[str]:
    if status == BLOCKED:
        return [
            "Authority boundary violation detected; treat this surface as blocked.",
            "Resolve forbidden authority or mutation flags upstream before operator review.",
        ]
    if status == NOT_COMPUTABLE:
        return [
            "Primary temporal resonance/coherence packet is missing or unreadable.",
            "Regenerate required P27 projection inputs and rerun P28 surface projection.",
        ]
    observations = [
        f"Operator posture is {posture} with attention level {attention}.",
        f"Aggregate coherence is {_bound(aggregate)} and dissonance is {_bound(dissonance)}.",
        "Treat all cards and rails as advisory-only projection guidance.",
    ]
    return sorted(observations)


def _surface_hash_material(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "patch_id": packet["patch_id"],
        "surface_schema": packet["surface_schema"],
        "coherence_field_operator_surface_status": packet[
            "coherence_field_operator_surface_status"
        ],
        "source_packet_id": packet["source_packet_id"],
        "source_packet_hash": packet["source_packet_hash"],
        "aggregate_coherence_score": packet["aggregate_coherence_score"],
        "resonance_score": packet["resonance_score"],
        "dissonance_score": packet["dissonance_score"],
        "phase_alignment_bucket": packet["phase_alignment_bucket"],
        "dominant_coherence_component": packet["dominant_coherence_component"],
        "operator_coherence_posture": packet["operator_coherence_posture"],
        "operator_attention_level": packet["operator_attention_level"],
        "coherence_cards": packet["coherence_cards"],
        "coherence_rails": packet["coherence_rails"],
        "coherence_badges": packet["coherence_badges"],
        "recommended_operator_observations": packet[
            "recommended_operator_observations"
        ],
        "remaining_blockers": packet["remaining_blockers"],
        "advisory_flags": packet["advisory_flags"],
        "blocker_code": packet.get("blocker_code"),
    }


def build_coherence_field_operator_surface_packet(
    *,
    packet_id: str = "coherence_field_operator_surface_001",
    source_artifact_paths: dict[str, str | Path] | None = None,
) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    defaults: dict[str, str | Path] = {
        "temporal_resonance_coherence": paths.temporal_resonance_coherence_latest,
        "aal_viz_runtime_projection": paths.aal_viz_runtime_projection_latest,
        "aal_viz_graph_render_packet": paths.aal_viz_graph_render_packet_latest,
        "operator_action_queue": paths.operator_action_queue_latest,
    }
    source_paths = {**defaults, **(source_artifact_paths or {})}

    p27_payload, p27_state = _load_artifact(source_paths.get("temporal_resonance_coherence"))
    optional_payloads: dict[str, dict[str, Any] | None] = {}
    optional_states: dict[str, str] = {}
    for optional_key in sorted(
        key for key in source_paths if key != "temporal_resonance_coherence"
    ):
        payload, state = _load_artifact(source_paths.get(optional_key))
        optional_payloads[optional_key] = payload
        optional_states[optional_key] = state

    source_packet_id = _as_str(
        p27_payload.get("packet_id") if isinstance(p27_payload, dict) else None,
        NOT_COMPUTABLE,
    )
    source_packet_hash = _as_str(
        p27_payload.get("packet_hash") if isinstance(p27_payload, dict) else None,
        _safe_hash(p27_payload),
    )

    if p27_state in {"MISSING", "CORRUPT"}:
        blockers = [f"{p27_state.lower()}_artifact:temporal_resonance_coherence"]
        advisory_flags = sorted(
            [
                "advisory_only",
                "not_computable",
                *[
                    f"optional_context_{state.lower()}:{key}"
                    for key, state in sorted(optional_states.items())
                    if state in {"MISSING", "CORRUPT"}
                ],
            ]
        )
        packet = _apply_invariants(
            {
                "patch_id": PATCH_ID,
                "surface_schema": SURFACE_SCHEMA,
                "packet_id": packet_id,
                "coherence_field_operator_surface_status": NOT_COMPUTABLE,
                "source_packet_id": source_packet_id,
                "source_packet_hash": source_packet_hash,
                "aggregate_coherence_score": 0.0,
                "resonance_score": 0.0,
                "dissonance_score": 0.0,
                "phase_alignment_bucket": NOT_COMPUTABLE,
                "dominant_coherence_component": NOT_COMPUTABLE,
                "operator_coherence_posture": NOT_COMPUTABLE,
                "operator_attention_level": NOT_COMPUTABLE,
                "coherence_cards": [],
                "coherence_rails": [],
                "coherence_badges": ["NOT_COMPUTABLE"],
                "recommended_operator_observations": _observations(
                    status=NOT_COMPUTABLE,
                    posture=NOT_COMPUTABLE,
                    attention=NOT_COMPUTABLE,
                    aggregate=0.0,
                    dissonance=0.0,
                ),
                "remaining_blockers": sorted(blockers),
                "advisory_flags": advisory_flags,
            }
        )
        packet["surface_hash"] = str(canonical_hash(_surface_hash_material(packet)))
        return packet

    p27 = p27_payload or {}
    aggregate = _bound(_as_float(p27.get("aggregate_coherence_score"), 0.0))
    resonance = _bound(_as_float(p27.get("resonance_score"), 0.0))
    dissonance = _bound(_as_float(p27.get("dissonance_score"), 0.0))
    phase_bucket = _as_str(p27.get("phase_alignment_bucket"), NOT_COMPUTABLE)
    dominant_component = _as_str(
        p27.get("dominant_coherence_component"), NOT_COMPUTABLE
    )
    replay_resonance_zone_count = _as_int(p27.get("replay_resonance_zone_count"), 0)
    topology_alignment_zone_count = _as_int(p27.get("topology_alignment_zone_count"), 0)

    violations: list[str] = []
    for key, payload in sorted(
        {
            "temporal_resonance_coherence": p27_payload,
            **optional_payloads,
        }.items()
    ):
        if payload is None:
            continue
        flagged_paths = _scan_forbidden_true_flags(payload)
        if flagged_paths:
            violations.extend(f"{key}:{path}" for path in flagged_paths)
    violations = sorted(set(violations))

    if violations:
        blockers = sorted(
            [f"authority_boundary_violation:{item}" for item in violations]
            + [
                f"optional_context_{state.lower()}:{key}"
                for key, state in sorted(optional_states.items())
                if state in {"MISSING", "CORRUPT"}
            ]
        )
        advisory_flags = sorted(["advisory_only", "authority_boundary_violation"])
        status = BLOCKED
        posture = _derive_operator_posture(status, aggregate, dissonance)
        attention = _derive_attention_level(status, aggregate, dissonance)
        packet = _apply_invariants(
            {
                "patch_id": PATCH_ID,
                "surface_schema": SURFACE_SCHEMA,
                "packet_id": packet_id,
                "coherence_field_operator_surface_status": status,
                "blocker_code": "authority_boundary_violation",
                "source_packet_id": source_packet_id,
                "source_packet_hash": source_packet_hash,
                "aggregate_coherence_score": aggregate,
                "resonance_score": resonance,
                "dissonance_score": dissonance,
                "phase_alignment_bucket": phase_bucket,
                "dominant_coherence_component": dominant_component,
                "operator_coherence_posture": posture,
                "operator_attention_level": attention,
                "coherence_cards": _cards(
                    status=status,
                    aggregate=aggregate,
                    resonance=resonance,
                    dissonance=dissonance,
                    phase_bucket=phase_bucket,
                    topology_alignment_zone_count=topology_alignment_zone_count,
                    replay_resonance_zone_count=replay_resonance_zone_count,
                    posture=posture,
                ),
                "coherence_rails": _rails(
                    status=status,
                    aggregate=aggregate,
                    resonance=resonance,
                    dissonance=dissonance,
                    phase_bucket=phase_bucket,
                    topology_alignment_zone_count=topology_alignment_zone_count,
                    replay_resonance_zone_count=replay_resonance_zone_count,
                ),
                "coherence_badges": _badge_set(
                    status=status,
                    aggregate=aggregate,
                    dissonance=dissonance,
                    phase_bucket=phase_bucket,
                    dominant_component=dominant_component,
                    replay_resonance_zone_count=replay_resonance_zone_count,
                    topology_alignment_zone_count=topology_alignment_zone_count,
                ),
                "recommended_operator_observations": _observations(
                    status=status,
                    posture=posture,
                    attention=attention,
                    aggregate=aggregate,
                    dissonance=dissonance,
                ),
                "remaining_blockers": blockers,
                "advisory_flags": advisory_flags,
            }
        )
        packet["surface_hash"] = str(canonical_hash(_surface_hash_material(packet)))
        return packet

    status = PRESENT
    posture = _derive_operator_posture(status, aggregate, dissonance)
    attention = _derive_attention_level(status, aggregate, dissonance)
    remaining_blockers = sorted(
        f"optional_context_{state.lower()}:{key}"
        for key, state in sorted(optional_states.items())
        if state in {"MISSING", "CORRUPT"}
    )
    advisory_flags = sorted(
        {
            "advisory_only",
            "analytics_only",
            "projection_only",
            "deterministic_ordering",
            *remaining_blockers,
        }
    )
    packet = _apply_invariants(
        {
            "patch_id": PATCH_ID,
            "surface_schema": SURFACE_SCHEMA,
            "packet_id": packet_id,
            "coherence_field_operator_surface_status": status,
            "source_packet_id": source_packet_id,
            "source_packet_hash": source_packet_hash,
            "aggregate_coherence_score": aggregate,
            "resonance_score": resonance,
            "dissonance_score": dissonance,
            "phase_alignment_bucket": phase_bucket,
            "dominant_coherence_component": dominant_component,
            "operator_coherence_posture": posture,
            "operator_attention_level": attention,
            "coherence_cards": _cards(
                status=status,
                aggregate=aggregate,
                resonance=resonance,
                dissonance=dissonance,
                phase_bucket=phase_bucket,
                topology_alignment_zone_count=topology_alignment_zone_count,
                replay_resonance_zone_count=replay_resonance_zone_count,
                posture=posture,
            ),
            "coherence_rails": _rails(
                status=status,
                aggregate=aggregate,
                resonance=resonance,
                dissonance=dissonance,
                phase_bucket=phase_bucket,
                topology_alignment_zone_count=topology_alignment_zone_count,
                replay_resonance_zone_count=replay_resonance_zone_count,
            ),
            "coherence_badges": _badge_set(
                status=status,
                aggregate=aggregate,
                dissonance=dissonance,
                phase_bucket=phase_bucket,
                dominant_component=dominant_component,
                replay_resonance_zone_count=replay_resonance_zone_count,
                topology_alignment_zone_count=topology_alignment_zone_count,
            ),
            "recommended_operator_observations": _observations(
                status=status,
                posture=posture,
                attention=attention,
                aggregate=aggregate,
                dissonance=dissonance,
            ),
            "remaining_blockers": remaining_blockers,
            "advisory_flags": advisory_flags,
        }
    )
    packet["surface_hash"] = str(canonical_hash(_surface_hash_material(packet)))
    return packet


def write_coherence_field_operator_surface_packet(
    path: str | Path, packet: dict[str, Any]
) -> Path:
    target = Path(path)
    write_canonical_json(target, packet)
    return target


def build_coherence_field_operator_surface_markdown(packet: dict[str, Any]) -> str:
    lines: list[str] = [
        "# P28 Coherence Field Operator Surface",
        "",
        f"Status: {packet.get('coherence_field_operator_surface_status', NOT_COMPUTABLE)}",
        f"Aggregate Coherence: {packet.get('aggregate_coherence_score', 0.0)}",
        f"Resonance: {packet.get('resonance_score', 0.0)}",
        f"Dissonance: {packet.get('dissonance_score', 0.0)}",
        f"Phase Alignment: {packet.get('phase_alignment_bucket', NOT_COMPUTABLE)}",
        f"Dominant Component: {packet.get('dominant_coherence_component', NOT_COMPUTABLE)}",
        f"Operator Posture: {packet.get('operator_coherence_posture', NOT_COMPUTABLE)}",
        f"Attention Level: {packet.get('operator_attention_level', NOT_COMPUTABLE)}",
        "",
        "## Coherence Badges",
    ]
    badges = _as_str_list(packet.get("coherence_badges", []))
    lines.extend([f"- {badge}" for badge in badges] if badges else ["- none"])
    lines.extend(["", "## Coherence Cards"])
    cards = packet.get("coherence_cards", [])
    if isinstance(cards, list) and cards:
        for card in cards:
            if isinstance(card, dict):
                lines.append(
                    "- "
                    + f"{_as_str(card.get('card_id'))}: "
                    + f"{_as_str(card.get('status'))} "
                    + f"(score={_as_float(card.get('score'), 0.0)})"
                )
    else:
        lines.append("- none")

    lines.extend(["", "## Operator Observations"])
    observations = _as_str_list(packet.get("recommended_operator_observations", []))
    lines.extend(
        [f"- {item}" for item in observations]
        if observations
        else ["- Continue advisory-only coherence monitoring."]
    )

    lines.extend(["", "## Remaining Blockers"])
    blockers = _as_str_list(packet.get("remaining_blockers", []))
    lines.extend([f"- {item}" for item in blockers] if blockers else ["- none"])

    lines.extend(
        [
            "",
            "## Authority Boundary",
            "- advisory_only: true",
            "- analytics_only: true",
            "- projection_only: true",
            "- mutation_allowed: false",
            "- authority_granted: false",
            "- forecast_authority: false",
            "- execution_authority: false",
            "- command_channel: false",
            "- bidirectional_control: false",
            "- autonomous_adaptation: false",
            "",
        ]
    )
    return "\n".join(lines)


def summarize_coherence_field_operator_surface(
    payload: dict[str, Any] | None,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return _apply_invariants(
            {
                "coherence_field_operator_surface_status": NOT_COMPUTABLE,
                "source_packet_id": NOT_COMPUTABLE,
                "source_packet_hash": NOT_COMPUTABLE,
                "aggregate_coherence_score": 0.0,
                "resonance_score": 0.0,
                "dissonance_score": 0.0,
                "phase_alignment_bucket": NOT_COMPUTABLE,
                "dominant_coherence_component": NOT_COMPUTABLE,
                "operator_coherence_posture": NOT_COMPUTABLE,
                "operator_attention_level": NOT_COMPUTABLE,
                "coherence_badges": [],
                "coherence_card_count": 0,
                "coherence_rail_count": 0,
                "recommended_operator_observations": [],
                "remaining_blockers": [],
                "advisory_flags": [],
                "surface_hash": NOT_COMPUTABLE,
            }
        )

    return _apply_invariants(
        {
            "coherence_field_operator_surface_status": _as_str(
                payload.get("coherence_field_operator_surface_status"), NOT_COMPUTABLE
            ),
            "source_packet_id": _as_str(payload.get("source_packet_id"), NOT_COMPUTABLE),
            "source_packet_hash": _as_str(
                payload.get("source_packet_hash"), NOT_COMPUTABLE
            ),
            "aggregate_coherence_score": _bound(
                _as_float(payload.get("aggregate_coherence_score"), 0.0)
            ),
            "resonance_score": _bound(_as_float(payload.get("resonance_score"), 0.0)),
            "dissonance_score": _bound(_as_float(payload.get("dissonance_score"), 0.0)),
            "phase_alignment_bucket": _as_str(
                payload.get("phase_alignment_bucket"), NOT_COMPUTABLE
            ),
            "dominant_coherence_component": _as_str(
                payload.get("dominant_coherence_component"), NOT_COMPUTABLE
            ),
            "operator_coherence_posture": _as_str(
                payload.get("operator_coherence_posture"), NOT_COMPUTABLE
            ),
            "operator_attention_level": _as_str(
                payload.get("operator_attention_level"), NOT_COMPUTABLE
            ),
            "coherence_badges": _as_str_list(payload.get("coherence_badges", [])),
            "coherence_card_count": len(
                payload.get("coherence_cards", [])
                if isinstance(payload.get("coherence_cards"), list)
                else []
            ),
            "coherence_rail_count": len(
                payload.get("coherence_rails", [])
                if isinstance(payload.get("coherence_rails"), list)
                else []
            ),
            "recommended_operator_observations": _as_str_list(
                payload.get("recommended_operator_observations", [])
            ),
            "remaining_blockers": _as_str_list(payload.get("remaining_blockers", [])),
            "advisory_flags": _as_str_list(payload.get("advisory_flags", [])),
            "surface_hash": _as_str(payload.get("surface_hash"), NOT_COMPUTABLE),
        }
    )
