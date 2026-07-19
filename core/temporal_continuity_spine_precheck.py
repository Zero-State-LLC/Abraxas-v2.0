from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuitySpinePrecheck.v1"
SOURCE_RESUME_STATE_PATH = "out/canon_resume_state/latest.json"
RECOMMENDED_BINDER_LANE = "P71_TEMPORAL_CONTINUITY_SPINE_BINDER_CONTRACT"
RECOMMENDED_REPAIR_INDEX_LANE = "P71_TEMPORAL_CONTINUITY_EVIDENCE_REPAIR_INDEX"
RECOMMENDED_P69_REPAIR_LANE = "P69_CANON_RESUME_STATE_REPAIR"
_DEGRADED_TOKENS = ("DEGRADED", "FAIL", "FAILED", "BLOCKED", "ERROR")


@dataclass(frozen=True)
class StatusProbe:
    path: str
    fields: tuple[str, ...]


@dataclass(frozen=True)
class ContinuitySurfaceGroupDefinition:
    group_id: str
    expected_lanes: tuple[str, ...]
    required_paths: tuple[str, ...]
    status_probes: tuple[StatusProbe, ...]


DEFAULT_CONTINUITY_SURFACE_GROUPS: tuple[ContinuitySurfaceGroupDefinition, ...] = (
    ContinuitySurfaceGroupDefinition(
        group_id="archive_chain",
        expected_lanes=("P52", "P53", "P54", "P55", "P56"),
        required_paths=(
            "out/archive/operator_narrative_export_preview_archive_index_001.latest.json",
            "out/audit/operator_narrative_export_preview_archive_index_governance_audit_001.latest.json",
            "out/audit/operator_narrative_archive_chain_closure_receipt_001.latest.json",
            "out/audit/operator_narrative_archive_chain_stability_receipt_001.latest.json",
        ),
        status_probes=(
            StatusProbe(
                "out/archive/operator_narrative_export_preview_archive_index_001.latest.json",
                ("final_status", "status"),
            ),
            StatusProbe(
                "out/audit/operator_narrative_export_preview_archive_index_governance_audit_001.latest.json",
                ("final_status", "status"),
            ),
            StatusProbe(
                "out/audit/operator_narrative_archive_chain_closure_receipt_001.latest.json",
                ("final_status", "closure_posture", "status"),
            ),
            StatusProbe(
                "out/audit/operator_narrative_archive_chain_stability_receipt_001.latest.json",
                ("final_status", "stability_posture", "status"),
            ),
        ),
    ),
    ContinuitySurfaceGroupDefinition(
        group_id="static_archive_package_chain",
        expected_lanes=("P64", "P65", "P66", "P67", "P68"),
        required_paths=(
            "out/package/operator_narrative_static_archive_package_001.latest.json",
            "out/audit/operator_narrative_static_archive_package_governance_audit_001.latest.json",
            "out/audit/operator_narrative_static_archive_package_language_boundary_audit_001.latest.json",
            "out/audit/operator_narrative_static_archive_package_stability_receipt_001.latest.json",
            "out/audit/operator_narrative_static_archive_package_chain_closure_receipt_001.latest.json",
        ),
        status_probes=(
            StatusProbe(
                "out/package/operator_narrative_static_archive_package_001.latest.json",
                ("final_status", "status"),
            ),
            StatusProbe(
                "out/audit/operator_narrative_static_archive_package_governance_audit_001.latest.json",
                ("final_status", "status"),
            ),
            StatusProbe(
                "out/audit/operator_narrative_static_archive_package_language_boundary_audit_001.latest.json",
                ("final_status", "status"),
            ),
            StatusProbe(
                "out/audit/operator_narrative_static_archive_package_stability_receipt_001.latest.json",
                ("final_status", "stability_posture", "status"),
            ),
            StatusProbe(
                "out/audit/operator_narrative_static_archive_package_chain_closure_receipt_001.latest.json",
                ("final_status", "closure_posture", "status"),
            ),
        ),
    ),
    ContinuitySurfaceGroupDefinition(
        group_id="temporal_coherence_chain",
        expected_lanes=("P27", "P28", "P28.1"),
        required_paths=(
            "scripts/temporal/run_temporal_coherence_chain.py",
            "out/audit/temporal_coherence_chain_001.latest.json",
            "out/projections/temporal_resonance_coherence_001.latest.json",
            "out/projections/coherence_field_operator_surface_001.latest.json",
            "out/projections/cross_run_topology_fusion_001.latest.json",
            "out/projections/temporal_topology_cartography_001.latest.json",
        ),
        status_probes=(
            StatusProbe(
                "out/audit/temporal_coherence_chain_001.latest.json",
                ("final_chain_status", "status"),
            ),
            StatusProbe(
                "out/projections/temporal_resonance_coherence_001.latest.json",
                ("final_status", "status"),
            ),
            StatusProbe(
                "out/projections/coherence_field_operator_surface_001.latest.json",
                ("coherence_field_operator_surface_status", "status"),
            ),
            StatusProbe(
                "out/projections/cross_run_topology_fusion_001.latest.json",
                ("final_status", "status"),
            ),
            StatusProbe(
                "out/projections/temporal_topology_cartography_001.latest.json",
                ("final_status", "status"),
            ),
        ),
    ),
    ContinuitySurfaceGroupDefinition(
        group_id="temporal_release_governance",
        expected_lanes=(),
        required_paths=(
            "out/audit/temporal_contract_reconciliation_manifest.latest.json",
            "out/audit/temporal_governance_release_bundle_contract.latest.json",
            "out/audit/temporal_governance_release_index_registry_contract.latest.json",
            "out/audit/temporal_governance_drift_observatory_contract.latest.json",
            "out/audit/temporal_governance_topology_index_contract.latest.json",
            "out/audit/temporal_continuity_index_contract.latest.json",
            "out/projections/aal_viz_runtime_projection_001.latest.json",
        ),
        status_probes=(
            StatusProbe(
                "out/audit/temporal_contract_reconciliation_manifest.latest.json",
                ("status", "final_status"),
            ),
            StatusProbe(
                "out/audit/temporal_governance_release_bundle_contract.latest.json",
                ("status", "final_status"),
            ),
            StatusProbe(
                "out/audit/temporal_governance_release_index_registry_contract.latest.json",
                ("status", "final_status"),
            ),
            StatusProbe(
                "out/audit/temporal_governance_drift_observatory_contract.latest.json",
                ("status", "final_status"),
            ),
            StatusProbe(
                "out/audit/temporal_governance_topology_index_contract.latest.json",
                ("status", "final_status"),
            ),
            StatusProbe(
                "out/audit/temporal_continuity_index_contract.latest.json",
                ("status", "final_status"),
            ),
            StatusProbe(
                "out/projections/aal_viz_runtime_projection_001.latest.json",
                ("final_status", "status"),
            ),
        ),
    ),
)


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _extract_status(payload: dict[str, Any], fields: Sequence[str]) -> str:
    for field in fields:
        value = payload.get(field)
        if value is not None:
            return str(value)
    return "NOT_COMPUTABLE"


def _group_sort_key(group: ContinuitySurfaceGroupDefinition) -> str:
    return group.group_id


def _is_degraded_status(status: str) -> bool:
    upper = status.upper()
    return any(token in upper for token in _DEGRADED_TOKENS)


def _semantic_overlap_flags(paths: Sequence[str]) -> tuple[str, ...]:
    checks = (
        ("SEMANTIC_OVERLAP_CLOSURE_RECEIPT", "closure_receipt"),
        ("SEMANTIC_OVERLAP_CONTINUITY", "continuity"),
        ("SEMANTIC_OVERLAP_LATEST_JSON", "latest.json"),
        ("SEMANTIC_OVERLAP_STABILITY_RECEIPT", "stability_receipt"),
        ("SEMANTIC_OVERLAP_TEMPORAL_RELEASE", "temporal_release"),
    )
    flags: list[str] = []
    for flag_name, token in checks:
        matches = sorted(path for path in paths if token in path)
        if len(matches) > 1:
            flags.append(f"{flag_name}:{'|'.join(matches)}")
    return tuple(sorted(flags))


def build_temporal_continuity_spine_precheck(
    *,
    repo_root: str | Path = ".",
    source_resume_state_path: str = SOURCE_RESUME_STATE_PATH,
    surface_groups: Sequence[ContinuitySurfaceGroupDefinition] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    resume_path = root / source_resume_state_path
    resume_payload = _load_json_dict(resume_path)
    resume_observed = resume_path.exists()
    resume_usable = resume_payload is not None
    resume_hash = _sha256_file(resume_path) if resume_usable else "NOT_COMPUTABLE"

    groups = tuple(sorted(surface_groups or DEFAULT_CONTINUITY_SURFACE_GROUPS, key=_group_sort_key))
    blockers: set[str] = set()
    drift_flags: set[str] = set()
    binder_candidate_inputs: set[str] = set()
    missing_or_not_computable_inputs: set[str] = set()
    observed_surface_paths: set[str] = set()
    group_packets: list[dict[str, Any]] = []

    if not resume_usable:
        blockers.add(f"source_resume_state_not_computable:{source_resume_state_path}")
        drift_flags.add("SOURCE_RESUME_STATE_NOT_COMPUTABLE")
        missing_or_not_computable_inputs.add(source_resume_state_path)
    else:
        binder_candidate_inputs.add(source_resume_state_path)

    for group in groups:
        observed_paths = sorted(
            path for path in group.required_paths if (root / path).exists()
        )
        missing_paths = sorted(
            path for path in group.required_paths if not (root / path).exists()
        )
        observed_surface_paths.update(observed_paths)
        missing_or_not_computable_inputs.update(missing_paths)

        degraded_statuses: list[str] = []
        not_computable_probe_paths: list[str] = []
        for probe in group.status_probes:
            probe_path = root / probe.path
            if not probe_path.exists():
                continue
            payload = _load_json_dict(probe_path)
            if payload is None:
                not_computable_probe_paths.append(probe.path)
                continue
            status = _extract_status(payload, probe.fields)
            if status == "NOT_COMPUTABLE":
                not_computable_probe_paths.append(probe.path)
                continue
            if _is_degraded_status(status):
                degraded_statuses.append(f"{probe.path}:{status}")

        if not resume_usable:
            status = "NOT_COMPUTABLE"
        elif not observed_paths:
            status = "NOT_COMPUTABLE"
        elif not_computable_probe_paths:
            status = "NOT_COMPUTABLE"
        elif missing_paths:
            status = "PARTIAL"
        elif degraded_statuses:
            status = "DEGRADED"
        else:
            status = "READY"

        spine_input_ready = resume_usable and status in {"READY", "DEGRADED"}
        if spine_input_ready:
            binder_candidate_inputs.update(observed_paths)
        if status != "READY":
            drift_flags.add(f"GROUP_{group.group_id.upper()}_{status}")
        for path in missing_paths:
            blockers.add(f"{group.group_id}:missing:{path}")
        for path in sorted(not_computable_probe_paths):
            blockers.add(f"{group.group_id}:not_computable:{path}")
            missing_or_not_computable_inputs.add(path)
        for degraded in sorted(degraded_statuses):
            blockers.add(f"{group.group_id}:degraded:{degraded}")

        group_packets.append(
            {
                "group_id": group.group_id,
                "expected_lanes": group.expected_lanes,
                "observed_paths": observed_paths,
                "missing_paths": missing_paths,
                "status": status,
                "spine_input_ready": spine_input_ready,
            }
        )

    semantic_overlap_flags = _semantic_overlap_flags(sorted(observed_surface_paths))
    if not resume_usable:
        recommended_next_lane = RECOMMENDED_P69_REPAIR_LANE
        recommended_next_lane_reason = (
            "Canon resume state is missing or not computable; repair the advisory continuity pointer before binder planning."
        )
    elif all(group["status"] in {"READY", "DEGRADED", "PARTIAL"} for group in group_packets):
        recommended_next_lane = RECOMMENDED_BINDER_LANE
        recommended_next_lane_reason = (
            "Canon resume state is usable and every major continuity group has at least partial evidence, so binder-contract planning can proceed advisory-only."
        )
    else:
        recommended_next_lane = RECOMMENDED_REPAIR_INDEX_LANE
        recommended_next_lane_reason = (
            "One or more major continuity groups remain not computable, so a deterministic evidence repair/index pass is required before binder work."
        )

    packet_base = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "production_activation": False,
        "canon_promotion": False,
        "forecast_influence": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "repair_authority": False,
        "spine_implementation_authority": False,
        "source_resume_state_path": source_resume_state_path,
        "source_resume_state_observed": resume_observed,
        "source_resume_state_hash": resume_hash,
        "continuity_surface_groups": group_packets,
        "semantic_overlap_flags": list(semantic_overlap_flags),
        "binder_candidate_inputs": sorted(binder_candidate_inputs),
        "missing_or_not_computable_inputs": sorted(missing_or_not_computable_inputs),
        "blockers": sorted(blockers),
        "drift_flags": sorted(drift_flags),
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
    }
    packet = {
        **packet_base,
        "packet_hash": canonical_hash(packet_base),
    }
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def write_temporal_continuity_spine_precheck(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
