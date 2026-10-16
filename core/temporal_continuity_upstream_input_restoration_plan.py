from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.runner_paths import resolve_runner_script

ARTIFACT_TYPE = "TemporalContinuityUpstreamInputRestorationPlan.v1"
SOURCE_GENERATOR_DISCOVERY_PATH = "out/temporal_continuity_generator_discovery_plan/latest.json"

_RESTORATION_STRATEGIES = (
    "UPSTREAM_GENERATOR_DISCOVERY_REQUIRED",
    "UPSTREAM_GENERATOR_IMPLEMENTATION_PLAN",
    "UPSTREAM_INPUT_REGENERATION_DRY_RUN_PLAN",
    "UPSTREAM_INPUT_REPAIR_PLAN",
    "UPSTREAM_INPUT_NOT_REQUIRED",
    "NOT_COMPUTABLE",
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
    "upstream_input_generation_authority",
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


def _unique_sorted(values: list[str]) -> list[str]:
    return sorted(set(values))


def _source_category(path: str) -> str:
    if path.startswith("out/audit/"):
        return "audit"
    if path.startswith("out/projections/"):
        return "projection"
    if path.startswith("out/archive/"):
        return "archive"
    if path.startswith("out/package/"):
        return "package"
    if path.startswith("scripts/"):
        return "script"
    if path.startswith("out/temporal_continuity"):
        return "temporal_continuity"
    return "unknown"


def _prerequisite_role(path: str, source_category: str) -> str:
    lowered = path.lower()
    if path.startswith("scripts/"):
        return "generator_prerequisite"
    if "temporal_state" in lowered and "diff" not in lowered:
        return "temporal_state_input"
    if "diff" in lowered:
        return "temporal_diff_input"
    if "lineage" in lowered:
        return "lineage_input"
    if source_category in {"audit", "projection", "archive", "package", "temporal_continuity"}:
        return "missing_evidence_prerequisite"
    return "unknown"


def _read_input_state(root: Path, path: str) -> tuple[bool, bool, bool, str]:
    target = root / path
    if not target.exists():
        return False, False, False, "NOT_COMPUTABLE"

    try:
        raw = target.read_bytes()
    except OSError:
        return True, False, False, "NOT_COMPUTABLE"

    malformed_json = False
    if path.endswith(".json"):
        try:
            json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            malformed_json = True

    readable = not malformed_json
    input_hash = hashlib.sha256(raw).hexdigest() if readable else "NOT_COMPUTABLE"
    return True, readable, malformed_json, input_hash


def _inspect_script(root: Path, script_path: str) -> tuple[bool, bool]:
    if script_path == "NOT_COMPUTABLE":
        return False, False

    target = root / script_path
    if not target.exists():
        return False, False

    try:
        target.read_bytes()
    except OSError:
        return True, False
    return True, True


def _infer_upstream_generator_script(root: Path, prerequisite_path: str) -> str:
    if prerequisite_path.startswith("scripts/") and prerequisite_path.endswith(".py"):
        return prerequisite_path

    if not prerequisite_path.startswith("out/") or not prerequisite_path.endswith(".json"):
        return "NOT_COMPUTABLE"

    file_name = prerequisite_path.rsplit("/", 1)[-1]
    stem = file_name
    for suffix in ("_001.latest.json", ".latest.json", ".json"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
            break

    if not stem:
        return "NOT_COMPUTABLE"

    return resolve_runner_script(root, stem)


def _derive_upstream_status(
    *,
    source_missing_prerequisite_paths: list[str],
    missing_upstream_input_paths: list[str],
    unreadable_upstream_input_paths: list[str],
    upstream_input_items: list[dict[str, Any]],
) -> str:
    if not source_missing_prerequisite_paths:
        return "UPSTREAM_RESTORATION_NOT_REQUIRED"

    if unreadable_upstream_input_paths:
        return "UPSTREAM_INPUTS_UNREADABLE"

    if missing_upstream_input_paths:
        missing_items = [item for item in upstream_input_items if not bool(item["input_observed"])]
        no_inferred_generator = any(
            str(item["likely_upstream_generator_script"]) == "NOT_COMPUTABLE" for item in missing_items
        )
        missing_or_unreadable_script = any(
            str(item["likely_upstream_generator_script"]) != "NOT_COMPUTABLE"
            and (
                (not bool(item["upstream_generator_observed"]))
                or (not bool(item["upstream_generator_readable"]))
            )
            for item in missing_items
        )
        if no_inferred_generator or missing_or_unreadable_script:
            return "UPSTREAM_GENERATORS_MISSING"
        return "UPSTREAM_INPUTS_MISSING"

    if upstream_input_items and all(
        bool(item["input_observed"]) and bool(item["input_readable"]) for item in upstream_input_items
    ):
        return "UPSTREAM_INPUTS_READY"

    return "NOT_COMPUTABLE"


def _build_recommended_lane(
    *, upstream_restoration_plan_status: str, degraded_evidence_inputs: list[str]
) -> tuple[str, str]:
    if upstream_restoration_plan_status == "NOT_COMPUTABLE":
        return (
            "P75_GENERATOR_DISCOVERY_PLAN_REGENERATION",
            "P75 generator discovery plan is missing, unreadable, or malformed; regenerate P75 before P76 planning.",
        )
    if upstream_restoration_plan_status == "UPSTREAM_GENERATORS_MISSING":
        return (
            "P77_TEMPORAL_CONTINUITY_UPSTREAM_GENERATOR_DISCOVERY_PLAN",
            "Missing upstream prerequisites have no usable upstream generator bindings; discovery planning is required.",
        )
    if upstream_restoration_plan_status == "UPSTREAM_INPUTS_UNREADABLE":
        return (
            "P77_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REPAIR_PLAN",
            "One or more upstream prerequisite inputs are unreadable or malformed and require repair planning.",
        )
    if upstream_restoration_plan_status == "UPSTREAM_INPUTS_MISSING":
        return (
            "P77_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_DRY_RUN_PLAN",
            "Upstream generators are observed but prerequisite inputs are missing; dry-run regeneration planning is required.",
        )
    if upstream_restoration_plan_status == "UPSTREAM_INPUTS_READY":
        return (
            "P77_TEMPORAL_CONTINUITY_ARTIFACT_REGENERATION_DRY_RUN_PLAN",
            "All upstream prerequisites are observed and readable; proceed to artifact regeneration dry-run planning.",
        )
    if upstream_restoration_plan_status == "UPSTREAM_RESTORATION_NOT_REQUIRED":
        if degraded_evidence_inputs:
            return (
                "P77_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN",
                "Upstream restoration is not required but degraded evidence remains and requires repair planning.",
            )
        return (
            "P77_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING_GATE",
            "Upstream restoration is not required and no degraded evidence remains.",
        )

    return (
        "P75_GENERATOR_DISCOVERY_PLAN_REGENERATION",
        "Signals are weak or inconsistent; fail closed to regenerate P75 before P76 planning.",
    )


def _build_not_computable_packet(
    *, source_path: str, source_observed: bool
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
        "upstream_input_generation_authority": False,
        "spine_implementation_authority": False,
        "source_generator_discovery_path": source_path,
        "source_generator_discovery_observed": source_observed,
        "source_generator_discovery_hash": "NOT_COMPUTABLE",
        "source_generator_discovery_status": "NOT_COMPUTABLE",
        "source_recommended_next_lane": "NOT_COMPUTABLE",
        "upstream_restoration_plan_status": "NOT_COMPUTABLE",
        "upstream_input_items": [],
        "missing_upstream_input_paths": [source_path],
        "observed_upstream_input_paths": [],
        "unreadable_upstream_input_paths": [],
        "outputs_blocked_by_upstream_inputs": [],
        "missing_upstream_generator_scripts": [],
        "observed_upstream_generator_scripts": [],
        "degraded_evidence_inputs": [],
        "inherited_blockers": [f"source_generator_discovery_not_computable:{source_path}"],
        "inherited_drift_flags": ["SOURCE_GENERATOR_DISCOVERY_NOT_COMPUTABLE"],
        "semantic_overlap_flags": [],
        "upstream_strategy_summary": {s: 0 for s in _RESTORATION_STRATEGIES},
        "recommended_next_lane": "P75_GENERATOR_DISCOVERY_PLAN_REGENERATION",
        "recommended_next_lane_reason": (
            "P75 generator discovery plan is missing, unreadable, or malformed; regenerate P75 before P76 planning."
        ),
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def build_temporal_continuity_upstream_input_restoration_plan(
    *,
    repo_root: str | Path = ".",
    source_generator_discovery_path: str = SOURCE_GENERATOR_DISCOVERY_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_generator_discovery_path
    source_observed = source_path.exists()

    source_payload = _load_json_dict(source_path)
    if source_payload is None:
        return _build_not_computable_packet(
            source_path=source_generator_discovery_path,
            source_observed=source_observed,
        )

    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    source_generator_discovery_status = str(
        source_payload.get("generator_discovery_status", "NOT_COMPUTABLE")
    )
    source_recommended_next_lane = str(source_payload.get("recommended_next_lane", "NOT_COMPUTABLE"))

    degraded_evidence_inputs = _as_str_list(source_payload.get("degraded_evidence_inputs"))
    inherited_blockers = _as_str_list(source_payload.get("inherited_blockers"))
    inherited_drift_flags = _as_str_list(source_payload.get("inherited_drift_flags"))
    semantic_overlap_flags = _as_str_list(source_payload.get("semantic_overlap_flags"))

    source_missing_prerequisite_paths = _unique_sorted(
        _as_str_list(source_payload.get("missing_prerequisite_paths"))
    )

    raw_generator_items = source_payload.get("generator_items")
    generator_items = (
        [item for item in raw_generator_items if isinstance(item, dict)]
        if isinstance(raw_generator_items, list)
        else []
    )

    upstream_input_items: list[dict[str, Any]] = []
    for generator_item in generator_items:
        output_path = str(generator_item.get("output_path", ""))
        group_id = str(generator_item.get("group_id", "UNKNOWN"))
        prerequisite_paths = _as_str_list(generator_item.get("prerequisite_paths"))

        for prerequisite_path in prerequisite_paths:
            source_category = _source_category(prerequisite_path)
            prerequisite_role = _prerequisite_role(prerequisite_path, source_category)
            input_observed, input_readable, malformed_json, input_hash = _read_input_state(
                root, prerequisite_path
            )
            likely_upstream_generator_script = _infer_upstream_generator_script(root, prerequisite_path)
            upstream_generator_observed, upstream_generator_readable = _inspect_script(
                root, likely_upstream_generator_script
            )

            if not input_observed:
                if likely_upstream_generator_script == "NOT_COMPUTABLE":
                    restoration_strategy = "UPSTREAM_GENERATOR_DISCOVERY_REQUIRED"
                    blocking_reason = "UPSTREAM_GENERATOR_NOT_INFERABLE_P76_PLANNING_ONLY"
                elif (not upstream_generator_observed) or (not upstream_generator_readable):
                    restoration_strategy = "UPSTREAM_GENERATOR_IMPLEMENTATION_PLAN"
                    blocking_reason = "UPSTREAM_GENERATOR_SCRIPT_MISSING_OR_UNREADABLE_P76_PLANNING_ONLY"
                else:
                    restoration_strategy = "UPSTREAM_INPUT_REGENERATION_DRY_RUN_PLAN"
                    blocking_reason = "UPSTREAM_INPUT_MISSING_GENERATOR_OBSERVED_P76_PLANNING_ONLY"
            elif (not input_readable) or malformed_json:
                restoration_strategy = "UPSTREAM_INPUT_REPAIR_PLAN"
                blocking_reason = "UPSTREAM_INPUT_UNREADABLE_OR_MALFORMED_P76_PLANNING_ONLY"
            elif input_observed and input_readable:
                restoration_strategy = "UPSTREAM_INPUT_NOT_REQUIRED"
                blocking_reason = "UPSTREAM_INPUT_PRESENT_AND_READABLE_P76_PLANNING_ONLY"
            else:
                restoration_strategy = "NOT_COMPUTABLE"
                blocking_reason = "WEAK_OR_INCONSISTENT_SIGNAL_P76_FAIL_CLOSED"

            upstream_input_items.append(
                {
                    "path": prerequisite_path,
                    "owning_output_path": output_path,
                    "group_id": group_id,
                    "source_category": source_category,
                    "prerequisite_role": prerequisite_role,
                    "input_observed": input_observed,
                    "input_readable": input_readable,
                    "malformed_json": malformed_json,
                    "input_hash": input_hash,
                    "likely_upstream_generator_script": likely_upstream_generator_script,
                    "upstream_generator_observed": upstream_generator_observed,
                    "upstream_generator_readable": upstream_generator_readable,
                    "restoration_strategy": restoration_strategy,
                    "blocking_reason": blocking_reason,
                    "safe_to_restore": False,
                }
            )

    upstream_input_items = sorted(
        upstream_input_items,
        key=lambda item: (
            str(item["path"]),
            str(item["owning_output_path"]),
            str(item["group_id"]),
        ),
    )

    missing_upstream_input_paths = _unique_sorted(
        [str(item["path"]) for item in upstream_input_items if not bool(item["input_observed"])]
    )
    observed_upstream_input_paths = _unique_sorted(
        [str(item["path"]) for item in upstream_input_items if bool(item["input_observed"])]
    )
    unreadable_upstream_input_paths = _unique_sorted(
        [
            str(item["path"])
            for item in upstream_input_items
            if bool(item["input_observed"])
            and ((not bool(item["input_readable"])) or bool(item["malformed_json"]))
        ]
    )

    blocked_by_input: dict[str, set[str]] = {}
    for item in upstream_input_items:
        if (not bool(item["input_observed"])) or (not bool(item["input_readable"])) or bool(
            item["malformed_json"]
        ):
            blocked_by_input.setdefault(str(item["path"]), set()).add(
                str(item["owning_output_path"])
            )
    outputs_blocked_by_upstream_inputs = [
        {
            "path": path,
            "blocked_output_paths": sorted(blocked_by_input[path]),
        }
        for path in sorted(blocked_by_input)
    ]

    missing_upstream_generator_scripts = _unique_sorted(
        [
            str(item["likely_upstream_generator_script"])
            for item in upstream_input_items
            if str(item["likely_upstream_generator_script"]) != "NOT_COMPUTABLE"
            and (not bool(item["upstream_generator_observed"]))
        ]
    )
    observed_upstream_generator_scripts = _unique_sorted(
        [
            str(item["likely_upstream_generator_script"])
            for item in upstream_input_items
            if str(item["likely_upstream_generator_script"]) != "NOT_COMPUTABLE"
            and bool(item["upstream_generator_observed"])
            and bool(item["upstream_generator_readable"])
        ]
    )

    upstream_strategy_summary = {
        strategy: sum(
            1
            for item in upstream_input_items
            if str(item.get("restoration_strategy", "NOT_COMPUTABLE")) == strategy
        )
        for strategy in _RESTORATION_STRATEGIES
    }

    upstream_restoration_plan_status = _derive_upstream_status(
        source_missing_prerequisite_paths=source_missing_prerequisite_paths,
        missing_upstream_input_paths=missing_upstream_input_paths,
        unreadable_upstream_input_paths=unreadable_upstream_input_paths,
        upstream_input_items=upstream_input_items,
    )
    recommended_next_lane, recommended_next_lane_reason = _build_recommended_lane(
        upstream_restoration_plan_status=upstream_restoration_plan_status,
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
        "upstream_input_generation_authority": False,
        "spine_implementation_authority": False,
        "source_generator_discovery_path": source_generator_discovery_path,
        "source_generator_discovery_observed": source_observed,
        "source_generator_discovery_hash": source_hash,
        "source_generator_discovery_status": source_generator_discovery_status,
        "source_recommended_next_lane": source_recommended_next_lane,
        "upstream_restoration_plan_status": upstream_restoration_plan_status,
        "upstream_input_items": upstream_input_items,
        "missing_upstream_input_paths": missing_upstream_input_paths,
        "observed_upstream_input_paths": observed_upstream_input_paths,
        "unreadable_upstream_input_paths": unreadable_upstream_input_paths,
        "outputs_blocked_by_upstream_inputs": outputs_blocked_by_upstream_inputs,
        "missing_upstream_generator_scripts": missing_upstream_generator_scripts,
        "observed_upstream_generator_scripts": observed_upstream_generator_scripts,
        "degraded_evidence_inputs": degraded_evidence_inputs,
        "inherited_blockers": inherited_blockers,
        "inherited_drift_flags": inherited_drift_flags,
        "semantic_overlap_flags": semantic_overlap_flags,
        "upstream_strategy_summary": upstream_strategy_summary,
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }
    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def write_temporal_continuity_upstream_input_restoration_plan(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
