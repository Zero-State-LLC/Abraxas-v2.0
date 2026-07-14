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

PATCH_ID = "PATCH-P39-OPERATOR-LOAD-SEASONALITY-SURFACE-001"
SCHEMA_VERSION = "OperatorLoadSeasonalitySurface.v1"
SEASONALITY_ID = "operator_load_seasonality_001"


_GOVERNANCE_FLAGS: dict[str, Any] = {
    "advisory_only": True,
    "projection_only": True,
    "seasonality_only": True,
    "observation_only": True,
    "non_authoritative": True,
    "prediction_allowed": False,
    "forecast_authority": False,
    "trend_prediction_allowed": False,
    "readiness_claims_allowed": False,
    "adaptive_thresholds_allowed": False,
    "psychological_claims_allowed": False,
    "speculative_causation_allowed": False,
    "mutation_allowed": False,
    "authority_granted": False,
    "execution_authority": False,
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
        "operator_attention_ledger": paths.operator_attention_ledger_latest.as_posix(),
        "operator_fatigue_corridor": paths.operator_fatigue_corridor_latest.as_posix(),
        "continuity_degradation_explainer": paths.continuity_degradation_explainer_latest.as_posix(),
        "operator_climatology_summary": paths.operator_climatology_summary_latest.as_posix(),
        "pressure_motif_registry": paths.pressure_motif_registry_latest.as_posix(),
        "motif_governance_audit": paths.motif_governance_audit_latest.as_posix(),
    }


def _count(values: list[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for value in values:
        key = str(value)
        out[key] = out.get(key, 0) + 1
    return {k: out[k] for k in sorted(out)}


def _add_recurrence(prefix: str, counts: dict[str, int], classes: set[str]) -> None:
    for key, value in counts.items():
        if int(value) >= 2:
            classes.add(f"{prefix}:{key}")


def build_operator_load_seasonality_surface_packet(*, source_artifact_paths: dict[str, str] | None = None, source_packets: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
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

    p31 = loaded.get("operator_attention_ledger") or {}
    p32 = loaded.get("operator_fatigue_corridor") or {}
    p33 = loaded.get("continuity_degradation_explainer") or {}
    p34 = loaded.get("operator_climatology_summary") or {}
    p36 = loaded.get("pressure_motif_registry") or {}
    p38 = loaded.get("motif_governance_audit") or {}

    for packet in (p31, p32, p33, p34, p36, p38):
        blockers.extend(str(b) for b in (packet.get("blocker_summary") or []) if str(b))
    blocker_summary = sorted(set(blockers))

    missing_or_corrupt = any(v != "PRESENT" for v in source_status.values())

    load_posture_counts = _count([
        str(p31.get("ledger_posture", NOT_COMPUTABLE)),
        str(p34.get("climatology_posture", NOT_COMPUTABLE)),
    ])
    pressure_motif_class_counts = {str(k): int(v) for k, v in sorted((p36.get("motif_class_counts") or {}).items())}
    degradation_vector_counts = _count([
        *(str(x) for x in (p33.get("dominant_degradation_vectors") or [])),
        *(str(k) for k in (p34.get("degradation_vector_counts") or {}).keys()),
        *(str(v.get("motif_label", "")) for v in (p36.get("motif_catalog") or []) if isinstance(v, dict) and str(v.get("motif_class", "")) == "DEGRADATION_VECTOR"),
    ])
    corridor_status_counts = _count([
        str(p32.get("corridor_status", NOT_COMPUTABLE)),
        *(str(k) for k in (p34.get("corridor_status_counts") or {}).keys()),
    ])
    audit_status_counts = _count([str(p38.get("final_status", NOT_COMPUTABLE)), str(p38.get("audit_posture", NOT_COMPUTABLE))])

    recurrence_classes: set[str] = set()
    _add_recurrence("load_posture", load_posture_counts, recurrence_classes)
    _add_recurrence("motif_class", pressure_motif_class_counts, recurrence_classes)
    _add_recurrence("degradation_vector", degradation_vector_counts, recurrence_classes)
    _add_recurrence("corridor_status", corridor_status_counts, recurrence_classes)
    _add_recurrence("audit_status", audit_status_counts, recurrence_classes)

    pressure_persistence = bool(p32.get("pressure_persistence_detected", False)) or str(p32.get("corridor_status", "")) == "PRESSURE_PERSISTENCE" or str(p36.get("registry_posture", "")) == "PRESSURE_PERSISTENCE"

    p38_status = str(p38.get("final_status", NOT_COMPUTABLE))
    upstream_blocked = any(str(packet.get("final_status", "")) == BLOCKED for packet in (p31, p32, p33, p34, p36))

    if missing_or_corrupt:
        final_status = NOT_COMPUTABLE
        seasonality_posture = NOT_COMPUTABLE
    elif p38_status in {"FAIL", BLOCKED} or upstream_blocked:
        final_status = BLOCKED
        seasonality_posture = BLOCKED
    elif p38_status == "WARN":
        final_status = "ADVISORY_DEGRADED"
        seasonality_posture = "DEGRADED"
    elif pressure_persistence:
        final_status = "ADVISORY_DEGRADED"
        seasonality_posture = "PRESSURE_PERSISTENCE"
    elif recurrence_classes:
        final_status = "ADVISORY_ONLY"
        seasonality_posture = "RECURRENCE_OBSERVED"
    elif "WATCH" in {str(p31.get("ledger_posture", "")), str(p34.get("climatology_posture", "")), str(p33.get("explanation_posture", ""))}:
        final_status = "ADVISORY_ONLY"
        seasonality_posture = "WATCH"
    else:
        final_status = "ADVISORY_ONLY"
        seasonality_posture = "CLEAR"

    source_hashes = {k: (str(canonical_hash(v)) if isinstance(v, dict) else NOT_COMPUTABLE) for k, v in sorted(loaded.items())}
    source_hash_lineage = {
        "ledger_hash": str(p31.get("ledger_hash", NOT_COMPUTABLE)),
        "corridor_hash": str(p32.get("corridor_hash", NOT_COMPUTABLE)),
        "explainer_hash": str(p33.get("explainer_hash", NOT_COMPUTABLE)),
        "summary_hash": str(p34.get("summary_hash", NOT_COMPUTABLE)),
        "registry_hash": str(p36.get("registry_hash", NOT_COMPUTABLE)),
        "audit_hash": str(p38.get("audit_hash", NOT_COMPUTABLE)),
    }

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "seasonality_id": SEASONALITY_ID,
        "final_status": final_status,
        "seasonality_posture": seasonality_posture,
        "recurrence_summary": {
            "repeated_class_count": len(recurrence_classes),
            "pressure_persistence_observed": pressure_persistence,
            "source_packet_count": len(sources),
        },
        "observed_recurrence_classes": sorted(recurrence_classes),
        "load_posture_counts": load_posture_counts,
        "pressure_motif_class_counts": pressure_motif_class_counts,
        "degradation_vector_counts": degradation_vector_counts,
        "corridor_status_counts": corridor_status_counts,
        "audit_status_counts": audit_status_counts,
        "source_artifacts": sources,
        "source_hashes": source_hashes,
        "source_hash_lineage": source_hash_lineage,
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
    packet["seasonality_hash"] = canonical_hash(packet)
    return packet


def build_operator_load_seasonality_surface_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P39 Operator Load Seasonality Surface",
        "",
        f"- seasonality_id: `{packet['seasonality_id']}`",
        f"- final_status: `{packet['final_status']}`",
        f"- seasonality_posture: `{packet['seasonality_posture']}`",
        f"- repeated_class_count: `{packet.get('recurrence_summary', {}).get('repeated_class_count', 0)}`",
        "",
        "## Observed Recurrence Classes",
    ]
    classes = packet.get("observed_recurrence_classes", [])
    if classes:
        lines.extend(f"- `{item}`" for item in classes)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def write_operator_load_seasonality_surface_packet(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_load_seasonality_surface_markdown(packet), encoding="utf-8")
