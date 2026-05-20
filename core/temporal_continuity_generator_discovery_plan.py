from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityGeneratorDiscoveryPlan.v1"
SOURCE_RESTORATION_PLAN_PATH = (
    "out/temporal_continuity_missing_evidence_restoration_plan/latest.json"
)

_CALLABLE_PATTERNS = (
    'if __name__ == "__main__"',
    "if __name__ == '__main__'",
    "def main(",
    "def run(",
)

_GENERATOR_BINDING_STATUSES = (
    "GENERATOR_OBSERVED",
    "GENERATOR_MISSING",
    "GENERATOR_UNREADABLE",
    "GENERATOR_NOT_COMPUTABLE",
    "GENERATOR_AMBIGUOUS",
)

_DENIED_AUTHORITY = (
    "production_activation",
    "canon_promotion",
    "forecast_influence",
    "scheduler_mutation",
    "runtime_authority",
    "repair_authority",
    "evidence_generation_authority",
    "restoration_execution_authority",
    "generator_execution_authority",
    "spine_implementation_authority",
)


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _unique_sorted(items: list[str]) -> list[str]:
    return sorted(set(items))


def _inspect_script(root: Path, script_path: str) -> tuple[bool, bool, bool]:
    """Return (observed, readable, callable_hint).

    Performs static inspection only — the script is never executed.
    callable_hint is True only when the script is readable and contains
    a recognised Python entrypoint pattern.
    """
    if script_path == "NOT_COMPUTABLE":
        return False, False, False

    target = root / script_path
    if not target.exists():
        return False, False, False

    try:
        text = target.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return True, False, False

    callable_hint = any(pattern in text for pattern in _CALLABLE_PATTERNS)
    return True, True, callable_hint


def _check_path_exists(root: Path, path: str) -> bool:
    return (root / path).exists()


def _build_not_computable_packet(
    *,
    source_path: str,
    source_observed: bool,
) -> dict[str, Any]:
    packet_base: dict[str, Any] = {
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
        "evidence_generation_authority": False,
        "restoration_execution_authority": False,
        "generator_execution_authority": False,
        "spine_implementation_authority": False,
        "source_restoration_plan_path": source_path,
        "source_restoration_plan_observed": source_observed,
        "source_restoration_plan_hash": "NOT_COMPUTABLE",
        "source_restoration_plan_status": "NOT_COMPUTABLE",
        "source_recommended_next_lane": "NOT_COMPUTABLE",
        "generator_discovery_status": "NOT_COMPUTABLE",
        "generator_items": [],
        "missing_generator_scripts": [],
        "observed_generator_scripts": [],
        "unreadable_generator_scripts": [],
        "ambiguous_generator_bindings": [],
        "missing_prerequisite_paths": [source_path],
        "degraded_evidence_inputs": [],
        "inherited_blockers": [f"source_restoration_plan_not_computable:{source_path}"],
        "inherited_drift_flags": ["SOURCE_RESTORATION_PLAN_NOT_COMPUTABLE"],
        "semantic_overlap_flags": [],
        "generator_strategy_summary": {s: 0 for s in _GENERATOR_BINDING_STATUSES},
        "recommended_next_lane": "P74_RESTORATION_PLAN_REGENERATION",
        "recommended_next_lane_reason": (
            "P74 restoration plan is missing, unreadable, or malformed; "
            "regenerate P74 before P75 generator discovery planning."
        ),
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def _derive_generator_binding_status(
    *,
    likely_generator_script: str,
    observed: bool,
    readable: bool,
    is_ambiguous: bool,
) -> str:
    if likely_generator_script == "NOT_COMPUTABLE":
        return "GENERATOR_NOT_COMPUTABLE"
    if is_ambiguous:
        return "GENERATOR_AMBIGUOUS"
    if not observed:
        return "GENERATOR_MISSING"
    if not readable:
        return "GENERATOR_UNREADABLE"
    return "GENERATOR_OBSERVED"


def _derive_blocking_reason(
    *,
    binding_status: str,
    missing_prerequisite_paths: list[str],
    restoration_strategy: str,
) -> str:
    if restoration_strategy == "RESTORATION_NOT_REQUIRED":
        return "EVIDENCE_PRESENT_AND_READABLE_GENERATOR_DISCOVERY_NOT_REQUIRED"
    if binding_status == "GENERATOR_NOT_COMPUTABLE":
        return "GENERATOR_NOT_COMPUTABLE_P75_DISCOVERY_ONLY"
    if binding_status == "GENERATOR_MISSING":
        return "GENERATOR_MISSING_SCRIPT_NOT_FOUND_P75_DISCOVERY_ONLY"
    if binding_status == "GENERATOR_UNREADABLE":
        return "GENERATOR_UNREADABLE_P75_DISCOVERY_ONLY"
    if binding_status == "GENERATOR_AMBIGUOUS":
        return "GENERATOR_AMBIGUOUS_BINDING_P75_DISCOVERY_ONLY"
    if missing_prerequisite_paths:
        return "GENERATOR_OBSERVED_PREREQUISITES_MISSING_P75_DISCOVERY_ONLY"
    return "GENERATOR_OBSERVED_EXECUTION_DENIED_IN_P75"


def _derive_generator_discovery_status(
    *,
    source_usable: bool,
    restoration_plan_status: str,
    generator_items: list[dict[str, Any]],
    all_missing_prerequisite_paths: list[str],
) -> str:
    if not source_usable:
        return "NOT_COMPUTABLE"

    if restoration_plan_status == "RESTORATION_NOT_REQUIRED":
        return "GENERATOR_DISCOVERY_NOT_REQUIRED"

    # Items that require generator discovery (not already resolved)
    active_items = [
        item
        for item in generator_items
        if item.get("restoration_strategy") != "RESTORATION_NOT_REQUIRED"
    ]

    if not active_items:
        return "GENERATOR_DISCOVERY_NOT_REQUIRED"

    statuses = {str(item["generator_binding_status"]) for item in active_items}

    # "problem" statuses — script missing, unreadable, or not computable
    problem_statuses = {"GENERATOR_MISSING", "GENERATOR_NOT_COMPUTABLE", "GENERATOR_UNREADABLE"}
    has_problem = bool(statuses & problem_statuses)
    has_observed = bool({"GENERATOR_OBSERVED", "GENERATOR_AMBIGUOUS"} & statuses)

    if has_problem and has_observed:
        return "GENERATORS_PARTIAL"
    if has_problem and not has_observed:
        return "GENERATORS_MISSING"
    # All are GENERATOR_OBSERVED or GENERATOR_AMBIGUOUS
    if all_missing_prerequisite_paths:
        return "GENERATORS_OBSERVED_WITH_MISSING_PREREQUISITES"
    return "GENERATORS_OBSERVED"


def _build_recommended_lane(
    *,
    source_usable: bool,
    generator_discovery_status: str,
    generator_items: list[dict[str, Any]],
    all_missing_prerequisite_paths: list[str],
    degraded_evidence_inputs: list[str],
) -> tuple[str, str]:
    if not source_usable or generator_discovery_status == "NOT_COMPUTABLE":
        return (
            "P74_RESTORATION_PLAN_REGENERATION",
            "P74 restoration plan is missing, unreadable, or malformed; "
            "regenerate P74 before P75 generator discovery planning.",
        )

    # Collect binding statuses for active (non-RESTORATION_NOT_REQUIRED) items
    active_items = [
        item
        for item in generator_items
        if item.get("restoration_strategy") != "RESTORATION_NOT_REQUIRED"
    ]
    binding_statuses = {str(item["generator_binding_status"]) for item in active_items}

    if "GENERATOR_MISSING" in binding_statuses or "GENERATOR_NOT_COMPUTABLE" in binding_statuses:
        return (
            "P76_TEMPORAL_CONTINUITY_GENERATOR_IMPLEMENTATION_PLAN",
            "One or more missing/not-computable generator scripts require implementation "
            "before evidence can be regenerated.",
        )
    if "GENERATOR_UNREADABLE" in binding_statuses:
        return (
            "P76_TEMPORAL_CONTINUITY_GENERATOR_REPAIR_PLAN",
            "One or more generator scripts are present but unreadable; "
            "repair is required before execution.",
        )
    if "GENERATOR_AMBIGUOUS" in binding_statuses:
        return (
            "P76_TEMPORAL_CONTINUITY_GENERATOR_BINDING_DISAMBIGUATION_PLAN",
            "One or more generator scripts have ambiguous output ownership; "
            "disambiguation is required before execution.",
        )

    # All generators observed (or not needed)
    if generator_discovery_status == "GENERATORS_OBSERVED_WITH_MISSING_PREREQUISITES":
        return (
            "P76_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_RESTORATION_PLAN",
            "All required generators are observed but one or more upstream prerequisite "
            "inputs are missing; upstream restoration planning is required.",
        )
    if generator_discovery_status == "GENERATORS_OBSERVED":
        return (
            "P76_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN",
            "All required generators are observed and prerequisites are present; "
            "proceed with advisory-only artifact regeneration dry-run planning.",
        )

    # Generator discovery not required
    if degraded_evidence_inputs:
        return (
            "P76_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN",
            "Generator discovery is not required but degraded evidence remains; "
            "degraded evidence repair planning is required.",
        )
    return (
        "P76_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE",
        "Generator discovery is not required and no degraded evidence remains; "
        "proceed to the temporal continuity spine implementation planning gate.",
    )


def build_temporal_continuity_generator_discovery_plan(
    *,
    repo_root: str | Path = ".",
    source_restoration_plan_path: str = SOURCE_RESTORATION_PLAN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_restoration_plan_path
    source_observed = source_path.exists()

    source_payload = _load_json_dict(source_path)
    source_usable = source_payload is not None

    if not source_usable:
        return _build_not_computable_packet(
            source_path=source_restoration_plan_path,
            source_observed=source_observed,
        )

    import hashlib

    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    restoration_plan_status = str(source_payload.get("restoration_plan_status", "NOT_COMPUTABLE"))
    source_recommended_next_lane = str(source_payload.get("recommended_next_lane", "NOT_COMPUTABLE"))

    # Preserve inherited fields exactly
    degraded_evidence_inputs = _as_str_list(source_payload.get("degraded_evidence_inputs"))
    inherited_blockers = _as_str_list(source_payload.get("inherited_blockers"))
    inherited_drift_flags = _as_str_list(source_payload.get("inherited_drift_flags"))
    semantic_overlap_flags = _as_str_list(source_payload.get("semantic_overlap_flags"))

    raw_items = source_payload.get("restoration_items")
    restoration_items = (
        [item for item in raw_items if isinstance(item, dict)]
        if isinstance(raw_items, list)
        else []
    )

    # --- Detect ambiguous generator bindings (same script → multiple output paths) ---
    script_to_output_paths: dict[str, list[str]] = {}
    for item in restoration_items:
        script = str(item.get("likely_generator_script", "NOT_COMPUTABLE"))
        if script == "NOT_COMPUTABLE":
            continue
        output_path = str(item.get("path", ""))
        script_to_output_paths.setdefault(script, []).append(output_path)

    ambiguous_scripts: set[str] = {
        script
        for script, paths in script_to_output_paths.items()
        if len(paths) > 1
    }

    # --- Build generator_items ---
    generator_items: list[dict[str, Any]] = []
    for item in restoration_items:
        output_path = str(item.get("path", ""))
        group_id = str(item.get("group_id", "UNKNOWN"))
        source_category = str(item.get("source_category", "unknown"))
        evidence_role = str(item.get("evidence_role", "unknown"))
        restoration_strategy = str(item.get("restoration_strategy", "NOT_COMPUTABLE"))
        likely_generator_script = str(item.get("likely_generator_script", "NOT_COMPUTABLE"))
        prerequisite_paths = _as_str_list(item.get("prerequisite_paths"))

        is_ambiguous = likely_generator_script in ambiguous_scripts

        gen_observed, gen_readable, callable_hint = _inspect_script(root, likely_generator_script)

        binding_status = _derive_generator_binding_status(
            likely_generator_script=likely_generator_script,
            observed=gen_observed,
            readable=gen_readable,
            is_ambiguous=is_ambiguous,
        )

        missing_prereqs = [
            p
            for p in prerequisite_paths
            if not _check_path_exists(root, p)
        ]

        blocking_reason = _derive_blocking_reason(
            binding_status=binding_status,
            missing_prerequisite_paths=missing_prereqs,
            restoration_strategy=restoration_strategy,
        )

        generator_items.append(
            {
                "output_path": output_path,
                "group_id": group_id,
                "source_category": source_category,
                "evidence_role": evidence_role,
                "restoration_strategy": restoration_strategy,
                "likely_generator_script": likely_generator_script,
                "generator_observed": gen_observed,
                "generator_readable": gen_readable,
                "generator_callable_hint": callable_hint,
                "generator_binding_status": binding_status,
                "prerequisite_paths": prerequisite_paths,
                "missing_prerequisite_paths": missing_prereqs,
                "blocking_reason": blocking_reason,
                "safe_to_execute": False,
            }
        )

    # Sort deterministically
    generator_items = sorted(
        generator_items,
        key=lambda it: (
            str(it["output_path"]),
            str(it["group_id"]),
            str(it["likely_generator_script"]),
        ),
    )

    # --- Aggregate fields ---
    missing_generator_scripts = _unique_sorted(
        [
            str(it["likely_generator_script"])
            for it in generator_items
            if it["generator_binding_status"] == "GENERATOR_MISSING"
        ]
    )
    observed_generator_scripts = _unique_sorted(
        [
            str(it["likely_generator_script"])
            for it in generator_items
            if it["generator_binding_status"] == "GENERATOR_OBSERVED"
        ]
    )
    unreadable_generator_scripts = _unique_sorted(
        [
            str(it["likely_generator_script"])
            for it in generator_items
            if it["generator_binding_status"] == "GENERATOR_UNREADABLE"
        ]
    )
    ambiguous_generator_bindings = _unique_sorted(
        [
            str(it["likely_generator_script"])
            for it in generator_items
            if it["generator_binding_status"] == "GENERATOR_AMBIGUOUS"
        ]
    )
    all_missing_prerequisite_paths = _unique_sorted(
        [p for it in generator_items for p in it["missing_prerequisite_paths"]]
    )

    generator_strategy_summary = {
        status: sum(
            1
            for it in generator_items
            if str(it.get("generator_binding_status", "GENERATOR_NOT_COMPUTABLE")) == status
        )
        for status in _GENERATOR_BINDING_STATUSES
    }

    generator_discovery_status = _derive_generator_discovery_status(
        source_usable=source_usable,
        restoration_plan_status=restoration_plan_status,
        generator_items=generator_items,
        all_missing_prerequisite_paths=all_missing_prerequisite_paths,
    )

    recommended_next_lane, recommended_next_lane_reason = _build_recommended_lane(
        source_usable=source_usable,
        generator_discovery_status=generator_discovery_status,
        generator_items=generator_items,
        all_missing_prerequisite_paths=all_missing_prerequisite_paths,
        degraded_evidence_inputs=degraded_evidence_inputs,
    )

    packet_base: dict[str, Any] = {
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
        "evidence_generation_authority": False,
        "restoration_execution_authority": False,
        "generator_execution_authority": False,
        "spine_implementation_authority": False,
        "source_restoration_plan_path": source_restoration_plan_path,
        "source_restoration_plan_observed": source_observed,
        "source_restoration_plan_hash": source_hash,
        "source_restoration_plan_status": restoration_plan_status,
        "source_recommended_next_lane": source_recommended_next_lane,
        "generator_discovery_status": generator_discovery_status,
        "generator_items": generator_items,
        "missing_generator_scripts": missing_generator_scripts,
        "observed_generator_scripts": observed_generator_scripts,
        "unreadable_generator_scripts": unreadable_generator_scripts,
        "ambiguous_generator_bindings": ambiguous_generator_bindings,
        "missing_prerequisite_paths": all_missing_prerequisite_paths,
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        "generator_strategy_summary": generator_strategy_summary,
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def write_temporal_continuity_generator_discovery_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
