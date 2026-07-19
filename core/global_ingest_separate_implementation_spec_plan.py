from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "GlobalIngestSeparateImplementationSpecPlan.v1"
DECISION_RECORD_JSON_PATH = Path("out/operator_review/global_ingest_operator_decision_record_001.latest.json")
PLAN_JSON_PATH = Path("out/operator_review/global_ingest_separate_implementation_spec_plan_001.latest.json")
PLAN_MD_PATH = Path("out/operator_review/global_ingest_separate_implementation_spec_plan_001.latest.md")
IMPLEMENTATION_SPEC_JSON_PATH = Path("out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.json")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_optional_json(path: Path) -> dict[str, Any]:
    try:
        return _read_json(path)
    except (OSError, json.JSONDecodeError):
        return {}


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_global_ingest_separate_implementation_spec_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    decision = _read_json(root / DECISION_RECORD_JSON_PATH)
    approved = (
        decision.get("selected_decision") == "APPROVE_SEPARATE_IMPLEMENTATION_SPEC"
        and decision.get("implementation_spec_authoring_approved") is True
        and decision.get("implementation_authorized") is False
        and decision.get("execution_authority") is False
    )
    implementation_spec = _read_optional_json(root / IMPLEMENTATION_SPEC_JSON_PATH)
    implementation_spec_observed = (
        implementation_spec.get("schema_version") == "GlobalIngestAdapterSpineImplementationSpec.v1"
        and implementation_spec.get("status")
        == "GLOBAL_INGEST_ADAPTER_SPINE_IMPLEMENTATION_SPEC_CONSUMED_ADVISORY_ONLY"
        and implementation_spec.get("implementation_pr_consumed") is True
        and implementation_spec.get("safe_to_prepare_implementation_pr") is False
        and implementation_spec.get("implementation_authorized") is False
        and implementation_spec.get("execution_authority") is False
        and implementation_spec.get("valid_for_execution") is False
    )
    consumed_by_implementation_spec = approved and implementation_spec_observed

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "GLOBAL_INGEST_SEPARATE_IMPLEMENTATION_SPEC_PLAN_CONSUMED_BY_IMPLEMENTATION_SPEC"
            if consumed_by_implementation_spec
            else "GLOBAL_INGEST_SEPARATE_IMPLEMENTATION_SPEC_PLAN_READY"
            if approved
            else "GLOBAL_INGEST_SEPARATE_IMPLEMENTATION_SPEC_PLAN_BLOCKED"
        ),
        "spec_plan_id": "global_ingest_separate_implementation_spec_plan_001",
        "spec_plan_hash": "",
        "command": "BUILD_GLOBAL_INGEST_SEPARATE_IMPLEMENTATION_SPEC_PLAN_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "decision_record_observed": True,
        "decision_record_approved_spec_authoring": approved,
        "target_pipeline_id": "oracle_signal",
        "target_display_name": "Oracle Signal Layer Pipeline",
        "spec_scope": "GLOBAL_INGEST_ADAPTER_SPINE_SEPARATE_IMPLEMENTATION_SPEC",
        "spec_authoring_allowed": approved,
        "implementation_authorized": False,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "pipeline_or_route_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "forecast_weight_allowed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_planning_pr": approved and not consumed_by_implementation_spec,
        "implementation_spec_observed": consumed_by_implementation_spec,
        "implementation_spec": {
            "path": str(IMPLEMENTATION_SPEC_JSON_PATH),
            "hash": "DOWNSTREAM_IMPLEMENTATION_SPEC_HASH_NOT_BOUND_TO_AVOID_CIRCULAR_PROVENANCE",
            "status": str(implementation_spec.get("status", "NOT_COMPUTABLE")),
            "observed": consumed_by_implementation_spec,
        },
        "planned_spec_sections": [
            "operator_decision_evidence_binding",
            "oracle_signal_contract_boundary",
            "ingest_runner_non_mutation_boundary",
            "pipeline_route_non_mutation_boundary",
            "deterministic_serialization_contract",
            "shadow_only_validation_plan",
            "authority_lock_validation_matrix",
            "rollback_and_fail_closed_plan",
        ],
        "planned_delivery_surfaces": [
            "contracts/operator_review/global_ingest_adapter_spine_implementation_spec.v1.schema.json",
            "core/global_ingest_adapter_spine_implementation_spec.py",
            "scripts/run_global_ingest_adapter_spine_implementation_spec.py",
            "tests/test_global_ingest_adapter_spine_implementation_spec.py",
            "out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.json",
            "out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.md",
        ],
        "blocked_delivery_surfaces": [
            "core/oracle_signal.py",
            "scripts/ingest/run_ingest_once.py behavior changes",
            "scripts/ingest/run_oracle_intake.py behavior changes",
            "contracts/pipelines runtime binding mutations",
            "contracts/yggdrasil route mutations",
        ],
        "acceptance_criteria": [
            "consume the operator decision record hash",
            "preserve advisory_only/projection_only/non_authoritative posture",
            "keep implementation_authorized false",
            "keep execution_authority false",
            "deny runtime, scheduler, canon, route, queue, and forecast mutation",
            "produce deterministic JSON and markdown artifacts",
            "include targeted tests and fast-ci validation",
        ],
        "recommended_next_action": (
            "Global Ingest implementation spec has been observed; do not prepare another implementation-spec PR from this plan"
            if consumed_by_implementation_spec
            else "open a separate implementation-spec PR only; do not implement Oracle Signal or mutate ingest runtime behavior"
        ),
        "recommended_next_patch": (
            "NOT_COMPUTABLE"
            if consumed_by_implementation_spec
            else "PATCH-ABX-GLOBAL-INGEST-SEPARATE-IMPLEMENTATION-SPEC-001"
            if approved
            else "NOT_COMPUTABLE"
        ),
        "source_decision_record_path": str(DECISION_RECORD_JSON_PATH),
        "source_decision_record_hash": str(decision.get("decision_record_hash", "NOT_COMPUTABLE")),
        "source_decision_record_status": str(decision.get("status", "NOT_COMPUTABLE")),
        "source_selected_decision": str(decision.get("selected_decision", "NOT_COMPUTABLE")),
    }
    packet["spec_plan_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "spec_plan_hash"})
    return packet


def render_global_ingest_separate_implementation_spec_plan_markdown(packet: Mapping[str, Any]) -> list[str]:
    lines = [
        "# Global Ingest Separate Implementation Spec Plan",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `spec_authoring_allowed`: `{packet['spec_authoring_allowed']}`",
        f"- `implementation_authorized`: `{packet['implementation_authorized']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Planned Delivery Surfaces",
        "",
    ]
    for item in packet["planned_delivery_surfaces"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Blocked Delivery Surfaces", ""])
    for item in packet["blocked_delivery_surfaces"]:
        lines.append(f"- `{item}`")
    return lines


def write_global_ingest_separate_implementation_spec_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_global_ingest_separate_implementation_spec_plan(root)
    write_canonical_json(target_root / PLAN_JSON_PATH, packet)
    _write_markdown(target_root / PLAN_MD_PATH, render_global_ingest_separate_implementation_spec_plan_markdown(packet))
    return packet
