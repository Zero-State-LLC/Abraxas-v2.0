from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.config import RuntimePaths

PATCH_ID = "PATCH-P36-PRESSURE-MOTIF-REGISTRY-001"
SCHEMA_VERSION = "PressureMotifRegistry.v1"
REGISTRY_ID = "pressure_motif_registry_001"

NOT_COMPUTABLE = "NOT_COMPUTABLE"
BLOCKED = "BLOCKED"

_GOVERNANCE_FLAGS: dict[str, Any] = {
    "advisory_only": True,
    "projection_only": True,
    "registry_only": True,
    "observed_only": True,
    "non_authoritative": True,
    "prediction_allowed": False,
    "forecast_authority": False,
    "readiness_claims_allowed": False,
    "motif_learning_authority": False,
    "adaptive_ontology_mutation_allowed": False,
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
        "operator_fatigue_corridor": paths.operator_fatigue_corridor_latest.as_posix(),
        "continuity_degradation_explainer": paths.continuity_degradation_explainer_latest.as_posix(),
        "operator_climatology_summary": paths.operator_climatology_summary_latest.as_posix(),
        "aal_viz_operator_climate_overlay": paths.aal_viz_operator_climate_overlay_latest.as_posix(),
    }


def _stable(values: list[str]) -> list[str]:
    return sorted(set(v for v in values if v))


def _normalize_token(motif_class: str, label: str) -> str:
    raw = str(label).strip()
    if motif_class == "DEGRADATION_VECTOR":
        return raw.upper()
    return raw.lower()


def _make_motif(*, motif_class: str, motif_label: str, observed_count: int, source_surfaces: list[str], evidence_refs: list[str]) -> dict[str, Any]:
    normalized_token = _normalize_token(motif_class, motif_label)
    digest = hashlib.sha256(normalized_token.encode("utf-8")).hexdigest()[:12]
    motif_id = f"motif.{motif_class.lower()}.{digest}"
    motif: dict[str, Any] = {
        "motif_id": motif_id,
        "motif_class": motif_class,
        "motif_label": str(motif_label).strip(),
        "normalized_token": normalized_token,
        "observed_count": max(0, int(observed_count)),
        "source_surfaces": sorted(set(source_surfaces)),
        "evidence_refs": _stable([str(ref).strip() for ref in evidence_refs if str(ref).strip()]),
    }
    motif["motif_hash"] = canonical_hash(motif)
    return motif


def build_pressure_motif_registry_packet(*, source_artifact_paths: dict[str, str] | None = None, source_packets: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
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

    p32 = loaded.get("operator_fatigue_corridor") or {}
    p33 = loaded.get("continuity_degradation_explainer") or {}
    p34 = loaded.get("operator_climatology_summary") or {}
    p35 = loaded.get("aal_viz_operator_climate_overlay") or {}

    for packet in (p32, p33, p34, p35):
        blockers.extend(str(b) for b in packet.get("blocker_summary", []) if str(b).strip())
    blocker_summary = _stable([str(b).strip() for b in blockers])

    missing_or_corrupt = any(v != "PRESENT" for v in source_status.values())
    blocked = any(str(packet.get("final_status", "")) == BLOCKED for packet in (p32, p33, p34, p35))

    motifs: list[dict[str, Any]] = []

    for token in sorted(str(x).strip().lower() for x in (p32.get("recurring_blocker_classes") or []) if str(x).strip()):
        motifs.append(_make_motif(motif_class="BLOCKER_CLASS", motif_label=token, observed_count=1, source_surfaces=["operator_fatigue_corridor"], evidence_refs=p32.get("evidence_refs", [])))
    for token in sorted(str(x).strip().lower() for x in (p33.get("recurring_blocker_classes") or []) if str(x).strip()):
        motifs.append(_make_motif(motif_class="BLOCKER_CLASS", motif_label=token, observed_count=1, source_surfaces=["continuity_degradation_explainer"], evidence_refs=p33.get("evidence_refs", [])))
    for token, count in sorted((p34.get("blocker_class_counts") or {}).items()):
        motifs.append(_make_motif(motif_class="BLOCKER_CLASS", motif_label=str(token), observed_count=int(count), source_surfaces=["operator_climatology_summary"], evidence_refs=[f"climatology:blocker_class_counts:{token}"]))

    for token in sorted(str(x).strip().upper() for x in (p33.get("dominant_degradation_vectors") or []) if str(x).strip()):
        motifs.append(_make_motif(motif_class="DEGRADATION_VECTOR", motif_label=token, observed_count=1, source_surfaces=["continuity_degradation_explainer"], evidence_refs=p33.get("evidence_refs", [])))
    for token, count in sorted((p34.get("degradation_vector_counts") or {}).items()):
        motifs.append(_make_motif(motif_class="DEGRADATION_VECTOR", motif_label=str(token).upper(), observed_count=int(count), source_surfaces=["operator_climatology_summary"], evidence_refs=[f"climatology:degradation_vector_counts:{token}"]))

    motifs.append(_make_motif(
        motif_class="CORRIDOR_PRESSURE",
        motif_label=str(p32.get("corridor_status", NOT_COMPUTABLE)),
        observed_count=1,
        source_surfaces=["operator_fatigue_corridor"],
        evidence_refs=p32.get("evidence_refs", []),
    ))

    for group in ("weather_posture_counts", "attention_urgency_counts", "routing_posture_counts", "review_priority_posture_counts", "ledger_posture_counts", "corridor_status_counts"):
        for token, count in sorted((p34.get(group) or {}).items()):
            motifs.append(_make_motif(motif_class="CLIMATOLOGY_COUNT", motif_label=f"{group}:{token}", observed_count=int(count), source_surfaces=["operator_climatology_summary"], evidence_refs=[f"climatology:{group}:{token}"]))

    lineage = p35.get("climate_summary", {}).get("source_hash_lineage", {}) if isinstance(p35.get("climate_summary"), dict) else {}
    for source_key, source_hash in sorted(lineage.items()):
        motifs.append(_make_motif(motif_class="OVERLAY_LINEAGE", motif_label=f"{source_key}:{source_hash}", observed_count=1, source_surfaces=["aal_viz_operator_climate_overlay"], evidence_refs=[f"overlay_lineage:{source_key}"]))

    motifs = sorted(motifs, key=lambda item: str(item["motif_id"]))

    if missing_or_corrupt:
        final_status = NOT_COMPUTABLE
        registry_posture = NOT_COMPUTABLE
    elif blocked:
        final_status = BLOCKED
        registry_posture = BLOCKED
    elif str(p32.get("corridor_status", "")) == "PRESSURE_PERSISTENCE" or str(p32.get("final_status", "")) == "ADVISORY_DEGRADED":
        final_status = "ADVISORY_DEGRADED"
        registry_posture = "PRESSURE_PERSISTENCE"
    elif any(str(packet.get("final_status", "")) == "ADVISORY_DEGRADED" for packet in (p33, p34, p35)):
        final_status = "ADVISORY_DEGRADED"
        registry_posture = "DEGRADED"
    elif not motifs:
        final_status = "ADVISORY_ONLY"
        registry_posture = "WATCH"
    else:
        final_status = "ADVISORY_ONLY"
        registry_posture = "CLEAR"

    class_counts: dict[str, int] = {}
    for motif in motifs:
        klass = str(motif["motif_class"])
        class_counts[klass] = class_counts.get(klass, 0) + 1

    source_hashes = {key: (str(canonical_hash(value)) if isinstance(value, dict) else NOT_COMPUTABLE) for key, value in sorted(loaded.items())}

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "registry_id": REGISTRY_ID,
        "final_status": final_status,
        "registry_posture": registry_posture,
        "motif_catalog": motifs,
        "motif_count": len(motifs),
        "motif_class_counts": {k: class_counts[k] for k in sorted(class_counts)},
        "source_artifacts": sources,
        "source_hashes": source_hashes,
        "source_hash_lineage": deepcopy(lineage) if isinstance(lineage, dict) else {},
        "motif_evidence_refs": _stable([ref for motif in motifs for ref in motif.get("evidence_refs", [])]),
        "blocker_summary": blocker_summary,
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {
            "source_packet_presence": source_status,
            "deterministic": True,
            "advisory_only": True,
            "projection_only": True,
            "observed_only": True,
        },
    }
    packet["registry_hash"] = canonical_hash(packet)
    return packet


def build_pressure_motif_registry_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P36 Pressure Motif Registry",
        "",
        f"- registry_id: `{packet['registry_id']}`",
        f"- final_status: `{packet['final_status']}`",
        f"- registry_posture: `{packet['registry_posture']}`",
        f"- motif_count: `{packet['motif_count']}`",
        "",
        "## Motif Catalog",
    ]
    motifs = packet.get("motif_catalog", [])
    if motifs:
        lines.extend(f"- `{m['motif_id']}` | `{m['motif_class']}` | `{m['motif_label']}` | count={m['observed_count']}" for m in motifs)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def write_pressure_motif_registry_packet(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_pressure_motif_registry_markdown(packet), encoding="utf-8")
