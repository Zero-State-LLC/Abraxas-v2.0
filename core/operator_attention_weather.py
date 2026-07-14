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

PATCH_ID = "PATCH-P29-OPERATOR-ATTENTION-WEATHER-001"
SCHEMA_VERSION = "OperatorAttentionWeather.v1"
WEATHER_ID = "operator_attention_weather_001"


_GOVERNANCE_FLAGS: dict[str, Any] = {
    "advisory_only": True,
    "projection_only": True,
    "operator_review_only": True,
    "non_authoritative": True,
    "mutation_allowed": False,
    "authority_granted": False,
    "forecast_authority": False,
    "execution_authority": False,
    "command_channel": False,
    "bidirectional_control": False,
    "auto_execute": False,
    "auto_approve": False,
    "queue_mutation_allowed": False,
    "canon_mutation_allowed": False,
    "runtime_mutation_allowed": False,
}


def _load_json(path: str | Path) -> tuple[dict[str, Any] | None, str]:
    p = Path(path)
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "MISSING"
    except (OSError, json.JSONDecodeError):
        return None, "CORRUPT"
    if not isinstance(payload, dict):
        return None, "CORRUPT"
    return payload, "PRESENT"


def _src_paths(paths: RuntimePaths) -> dict[str, str]:
    return {
        "coherence_field_operator_surface": paths.coherence_field_operator_surface_latest.as_posix(),
        "temporal_coherence_chain": (paths.audit_dir / "temporal_coherence_chain_001.latest.json").as_posix(),
        "temporal_upstream_evidence": (paths.audit_dir / "temporal_upstream_evidence_001.latest.json").as_posix(),
    }


def build_operator_attention_weather_packet(
    *,
    source_artifact_paths: dict[str, str] | None = None,
    source_packets: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    paths = RuntimePaths.from_env()
    sources = source_artifact_paths or _src_paths(paths)
    loaded: dict[str, dict[str, Any] | None] = {}
    source_status: dict[str, str] = {}

    for key, path in sources.items():
        payload, status = _load_json(path)
        loaded[key] = payload
        source_status[key] = status

    if source_packets:
        for key, payload in source_packets.items():
            loaded[key] = deepcopy(payload)
            source_status[key] = "PRESENT"

    missing_or_corrupt = any(v != "PRESENT" for v in source_status.values())
    blockers: list[str] = []
    for key, status in sorted(source_status.items()):
        if status != "PRESENT":
            blockers.append(f"source_{status.lower()}:{key}")

    p28 = loaded.get("coherence_field_operator_surface") or {}
    chain = loaded.get("temporal_coherence_chain") or {}
    evidence = loaded.get("temporal_upstream_evidence") or {}

    chain_status = str(chain.get("final_chain_status", NOT_COMPUTABLE))
    evidence_status = str(evidence.get("final_evidence_status", NOT_COMPUTABLE))
    p28_status = str(p28.get("coherence_field_operator_surface_status", NOT_COMPUTABLE))
    p28_attention = str(p28.get("operator_attention_level", "LOW"))

    chain_blockers = chain.get("blockers") if isinstance(chain.get("blockers"), list) else []
    p28_blockers = p28.get("remaining_blockers") if isinstance(p28.get("remaining_blockers"), list) else []
    evidence_blockers: list[str] = []
    checked = evidence.get("checked_artifacts") if isinstance(evidence.get("checked_artifacts"), list) else []
    for item in checked:
        if isinstance(item, dict):
            for b in item.get("blockers", []):
                evidence_blockers.append(str(b))

    blockers.extend(str(b) for b in chain_blockers)
    blockers.extend(str(b) for b in p28_blockers)
    blockers.extend(sorted(set(evidence_blockers)))

    if missing_or_corrupt:
        final_status = NOT_COMPUTABLE
        weather_posture = BLOCKED
        urgency = "CRITICAL"
    elif chain_status == BLOCKED:
        final_status = BLOCKED
        weather_posture = BLOCKED
        urgency = "CRITICAL"
    elif evidence_status == "NOT_READY":
        final_status = "ADVISORY_DEGRADED"
        weather_posture = "BLOCKED" if blockers else "DEGRADED"
        urgency = "HIGH" if not blockers else "CRITICAL"
    elif p28_status in {BLOCKED, NOT_COMPUTABLE}:
        final_status = "ADVISORY_DEGRADED"
        weather_posture = "CRITICAL" if p28_status == BLOCKED else "DEGRADED"
        urgency = "HIGH"
    elif chain_status == "ADVISORY_ONLY" and evidence_status == "READY" and p28_status == "PRESENT":
        final_status = "ADVISORY_ONLY"
        weather_posture = "WATCH" if p28_attention in {"MEDIUM", "HIGH"} else "CLEAR"
        urgency = "MEDIUM" if weather_posture == "WATCH" else "LOW"
    else:
        final_status = "ADVISORY_DEGRADED"
        weather_posture = "DEGRADED"
        urgency = "HIGH" if blockers else "MEDIUM"

    source_hashes = {
        key: (str(canonical_hash(payload)) if isinstance(payload, dict) else NOT_COMPUTABLE)
        for key, payload in sorted(loaded.items())
    }

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "weather_id": WEATHER_ID,
        "final_status": final_status,
        "weather_posture": weather_posture,
        "attention_urgency": urgency,
        "operator_summary": f"{weather_posture} posture from P28/chain/evidence synthesis.",
        "review_urgency_posture": f"{urgency}:{weather_posture}",
        "source_artifacts": sources,
        "source_hashes": source_hashes,
        "blocker_summary": sorted(set(str(b) for b in blockers if str(b))),
        "signal_summary": {
            "coherence_surface_status": p28_status,
            "chain_status": chain_status,
            "evidence_status": evidence_status,
            "coherence_attention_level": p28_attention,
        },
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {
            "source_packet_presence": source_status,
            "deterministic": True,
            "advisory_only": True,
        },
    }
    packet["weather_hash"] = canonical_hash(packet)
    return packet


def build_operator_attention_weather_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P29 Operator Attention Weather",
        "",
        f"- weather_id: `{packet['weather_id']}`",
        f"- final_status: `{packet['final_status']}`",
        f"- weather_posture: `{packet['weather_posture']}`",
        f"- attention_urgency: `{packet['attention_urgency']}`",
        "",
        "## Blockers",
    ]
    blockers = packet.get("blocker_summary", [])
    if blockers:
        for b in blockers:
            lines.append(f"- `{b}`")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def write_operator_attention_weather_packet(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_attention_weather_markdown(packet), encoding="utf-8")
