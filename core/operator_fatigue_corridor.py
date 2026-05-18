from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

PATCH_ID = "PATCH-P32-OPERATOR-FATIGUE-CORRIDOR-001"
SCHEMA_VERSION = "OperatorFatigueCorridor.v1"
CORRIDOR_ID = "operator_fatigue_corridor_001"

NOT_COMPUTABLE = "NOT_COMPUTABLE"
BLOCKED = "BLOCKED"

MIN_WINDOW_SIZE = 1
PRESSURE_THRESHOLD = 2
SINGLE_ENTRY_BLOCKED_SIGNAL = True

_GOVERNANCE_FLAGS: dict[str, Any] = {
    "advisory_only": True,
    "projection_only": True,
    "detector_only": True,
    "non_authoritative": True,
    "pressure_persistence_only": True,
    "psychological_claims_allowed": False,
    "adaptive_behavior_allowed": False,
    "threshold_self_modification_allowed": False,
    "mutation_allowed": False,
    "authority_granted": False,
    "execution_authority": False,
    "forecast_authority": False,
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
    return {"operator_attention_ledger": paths.operator_attention_ledger_latest.as_posix()}


def _entry_blockers(entry: dict[str, Any]) -> list[str]:
    blockers = entry.get("blocker_summary") if isinstance(entry.get("blocker_summary"), list) else []
    return [str(b).strip().lower() for b in blockers if str(b).strip()]


def build_operator_fatigue_corridor_packet(*, source_artifact_paths: dict[str, str] | None = None, source_packets: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    sources = source_artifact_paths or _src_paths(paths)

    loaded: dict[str, dict[str, Any] | None] = {}
    source_status: dict[str, str] = {}
    blocker_summary: list[str] = []

    for key, path in sorted(sources.items()):
        payload, status = _load_json(path)
        loaded[key] = payload
        source_status[key] = status
        if status != "PRESENT":
            blocker_summary.append(f"source_{status.lower()}:{key}")

    if source_packets:
        for key, payload in source_packets.items():
            loaded[key] = deepcopy(payload)
            source_status[key] = "PRESENT"

    ledger = loaded.get("operator_attention_ledger") or {}
    missing_or_corrupt = any(v != "PRESENT" for v in source_status.values())

    entries_raw = ledger.get("entries") if isinstance(ledger.get("entries"), list) else []
    entries = [e for e in entries_raw if isinstance(e, dict)]
    evaluated_entry_count = len(entries)
    corridor_window_size = max(MIN_WINDOW_SIZE, evaluated_entry_count)

    repeated_blocked_count = sum(1 for e in entries if str(e.get("routing_posture", "")) == BLOCKED)
    repeated_critical_count = sum(1 for e in entries if str(e.get("attention_urgency", "")) == "CRITICAL")
    repeated_degraded_count = sum(1 for e in entries if str(e.get("weather_posture", "")) == "DEGRADED")

    recurring_blocker_classes = sorted({b for e in entries for b in _entry_blockers(e)})
    blocker_summary.extend(str(b) for b in ledger.get("blocker_summary", []) if str(b))
    blocker_summary = sorted(set(blocker_summary))

    pressure_hits = repeated_blocked_count + repeated_critical_count + repeated_degraded_count
    has_pressure_persistence = pressure_hits >= PRESSURE_THRESHOLD

    ledger_final_status = str(ledger.get("final_status", NOT_COMPUTABLE))

    if missing_or_corrupt:
        final_status = NOT_COMPUTABLE
        corridor_status = NOT_COMPUTABLE
        pressure_persistence_detected = False
    elif ledger_final_status == BLOCKED:
        final_status = BLOCKED
        corridor_status = "BLOCKED_PERSISTENCE"
        pressure_persistence_detected = True
    elif evaluated_entry_count <= 1 and SINGLE_ENTRY_BLOCKED_SIGNAL and (
        repeated_critical_count >= 1 or str(ledger.get("ledger_posture", "")) == BLOCKED
    ):
        final_status = "ADVISORY_DEGRADED"
        corridor_status = "PRESSURE_PERSISTENCE"
        pressure_persistence_detected = True
    elif has_pressure_persistence:
        final_status = "ADVISORY_DEGRADED"
        corridor_status = "PRESSURE_PERSISTENCE"
        pressure_persistence_detected = True
    elif repeated_critical_count == 1 or repeated_degraded_count == 1:
        final_status = "ADVISORY_ONLY"
        corridor_status = "WATCH"
        pressure_persistence_detected = False
    else:
        final_status = "ADVISORY_ONLY"
        corridor_status = "CLEAR"
        pressure_persistence_detected = False

    evidence_refs = sorted(
        set([
            f"ledger_hash:{str(ledger.get('ledger_hash', NOT_COMPUTABLE))}",
            *[f"entry_hash:{str(e.get('entry_hash', NOT_COMPUTABLE))}" for e in entries],
        ])
    )

    source_hashes = {
        key: (str(canonical_hash(payload)) if isinstance(payload, dict) else NOT_COMPUTABLE)
        for key, payload in sorted(loaded.items())
    }

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "corridor_id": CORRIDOR_ID,
        "final_status": final_status,
        "corridor_status": corridor_status,
        "pressure_persistence_detected": pressure_persistence_detected,
        "corridor_window_size": corridor_window_size,
        "evaluated_entry_count": evaluated_entry_count,
        "repeated_blocked_count": repeated_blocked_count,
        "repeated_critical_count": repeated_critical_count,
        "repeated_degraded_count": repeated_degraded_count,
        "recurring_blocker_classes": recurring_blocker_classes,
        "evidence_refs": evidence_refs,
        "blocker_summary": blocker_summary,
        "source_artifacts": sources,
        "source_hashes": source_hashes,
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {
            "source_packet_presence": source_status,
            "deterministic": True,
            "advisory_only": True,
            "projection_only": True,
            "pressure_persistence_only": True,
        },
    }
    packet["corridor_hash"] = canonical_hash(packet)
    return packet


def build_operator_fatigue_corridor_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P32 Operator Fatigue Corridor Detector",
        "",
        f"- corridor_id: `{packet['corridor_id']}`",
        f"- final_status: `{packet['final_status']}`",
        f"- corridor_status: `{packet['corridor_status']}`",
        f"- pressure_persistence_detected: `{str(packet['pressure_persistence_detected']).lower()}`",
        f"- evaluated_entry_count: `{packet['evaluated_entry_count']}`",
        "",
        "## Recurring Blocker Classes",
    ]
    rec = packet.get("recurring_blocker_classes", [])
    if rec:
        for item in rec:
            lines.append(f"- `{item}`")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def write_operator_fatigue_corridor_packet(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_fatigue_corridor_markdown(packet), encoding="utf-8")
