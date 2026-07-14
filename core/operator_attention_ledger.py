from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

from core.status_result import (
    STATUS_BLOCKED as BLOCKED,
    STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE,
)

PATCH_ID = "PATCH-P31-OPERATOR-ATTENTION-LEDGER-001"
SCHEMA_VERSION = "OperatorAttentionLedger.v1"
LEDGER_ID = "operator_attention_ledger_001"


_GOVERNANCE_FLAGS: dict[str, Any] = {
    "advisory_only": True,
    "projection_only": True,
    "ledger_only": True,
    "non_authoritative": True,
    "append_only_semantics": True,
    "deterministic_materialization": True,
    "mutation_allowed": False,
    "authority_granted": False,
    "execution_authority": False,
    "forecast_authority": False,
    "routing_change_allowed": False,
    "queue_mutation_allowed": False,
    "canon_mutation_allowed": False,
    "runtime_mutation_allowed": False,
    "adaptive_behavior_allowed": False,
    "auto_learning_allowed": False,
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
    }


def _entry_from_sources(weather: dict[str, Any], routing: dict[str, Any]) -> dict[str, Any]:
    weather_hash = str(weather.get("weather_hash", NOT_COMPUTABLE))
    routing_hash = str(routing.get("enhancer_hash", NOT_COMPUTABLE))
    blockers = sorted(
        set(
            [*(str(b) for b in (weather.get("blocker_summary") or []) if str(b)), *(str(b) for b in (routing.get("blocker_summary") or []) if str(b))]
        )
    )
    entry: dict[str, Any] = {
        "entry_id": str(canonical_hash({"weather_hash": weather_hash, "routing_hash": routing_hash})),
        "source_weather_hash": weather_hash,
        "source_routing_hash": routing_hash,
        "weather_final_status": str(weather.get("final_status", NOT_COMPUTABLE)),
        "weather_posture": str(weather.get("weather_posture", NOT_COMPUTABLE)),
        "attention_urgency": str(weather.get("attention_urgency", NOT_COMPUTABLE)),
        "routing_final_status": str(routing.get("final_status", NOT_COMPUTABLE)),
        "routing_posture": str(routing.get("routing_posture", NOT_COMPUTABLE)),
        "review_priority_posture": str(routing.get("review_priority_posture", NOT_COMPUTABLE)),
        "blocker_summary": blockers,
    }
    entry["entry_hash"] = canonical_hash(entry)
    return entry


def build_operator_attention_ledger_packet(*, source_artifact_paths: dict[str, str] | None = None, source_packets: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
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

    blockers.extend(str(b) for b in (weather.get("blocker_summary") or []) if str(b))
    blockers.extend(str(b) for b in (routing.get("blocker_summary") or []) if str(b))
    blockers = sorted(set(blockers))

    source_hashes = {
        key: (str(canonical_hash(payload)) if isinstance(payload, dict) else NOT_COMPUTABLE)
        for key, payload in sorted(loaded.items())
    }

    missing_or_corrupt = any(v != "PRESENT" for v in source_status.values())
    weather_status = str(weather.get("final_status", NOT_COMPUTABLE))
    routing_status = str(routing.get("final_status", NOT_COMPUTABLE))
    weather_posture = str(weather.get("weather_posture", NOT_COMPUTABLE))

    if missing_or_corrupt:
        final_status = NOT_COMPUTABLE
        ledger_posture = BLOCKED
        entries: list[dict[str, Any]] = []
    elif weather_status == BLOCKED or routing_status == BLOCKED:
        final_status = BLOCKED
        ledger_posture = BLOCKED
        entries = [_entry_from_sources(weather, routing)]
    elif weather_status == "ADVISORY_DEGRADED" or routing_status == "ADVISORY_DEGRADED":
        final_status = "ADVISORY_DEGRADED"
        ledger_posture = "DEGRADED"
        entries = [_entry_from_sources(weather, routing)]
    else:
        final_status = "ADVISORY_ONLY"
        ledger_posture = "WATCH" if weather_posture == "WATCH" else "STABLE"
        entries = [_entry_from_sources(weather, routing)]

    entries = sorted(entries, key=lambda e: str(e.get("entry_id", "")))
    latest_entry = entries[-1] if entries else None

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "ledger_id": LEDGER_ID,
        "final_status": final_status,
        "ledger_posture": ledger_posture,
        "ledger_mode": "DETERMINISTIC_MATERIALIZED",
        "entries": entries,
        "entry_count": len(entries),
        "latest_entry": latest_entry,
        "blocker_summary": blockers,
        "source_artifacts": sources,
        "source_hashes": source_hashes,
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {
            "source_packet_presence": source_status,
            "deterministic": True,
            "append_only_semantics": True,
            "advisory_only": True,
        },
    }
    packet["ledger_hash"] = canonical_hash(packet)
    return packet


def build_operator_attention_ledger_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P31 Operator Attention Ledger",
        "",
        f"- ledger_id: `{packet['ledger_id']}`",
        f"- final_status: `{packet['final_status']}`",
        f"- ledger_posture: `{packet['ledger_posture']}`",
        f"- ledger_mode: `{packet['ledger_mode']}`",
        f"- entry_count: `{packet['entry_count']}`",
        "",
        "## Blockers",
    ]
    blockers = packet.get("blocker_summary", [])
    if blockers:
        for blocker in blockers:
            lines.append(f"- `{blocker}`")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def write_operator_attention_ledger_packet(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_attention_ledger_markdown(packet), encoding="utf-8")
