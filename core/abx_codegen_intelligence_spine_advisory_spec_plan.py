from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineAdvisorySpecPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_ADVISORY_SPEC_PLAN_001"
OUT_JSON = "out/audit/abx_codegen_intelligence_spine_advisory_spec_plan_001.latest.json"
OUT_MD = "out/audit/abx_codegen_intelligence_spine_advisory_spec_plan_001.latest.md"

GAP_ANALYSIS_PLAN_JSON = "out/audit/abx_codegen_intelligence_spine_gap_analysis_plan_001.latest.json"
CANON_RESUME_STATE_JSON = "out/canon_resume_state/latest.json"
TEMPORAL_SPINE_PRECHECK_JSON = "out/temporal_continuity_spine_precheck/latest.json"

SCHEMA_CONTRACT_PATHS: tuple[str, ...] = (
    "contracts/canon/gap_diagnosis_packet.v1.schema.json",
    "contracts/canon/improvement_proposal.v1.schema.json",
    "contracts/canon/shadow_improvement_receipt.v1.schema.json",
)

NOTION_SPEC_STACK: tuple[dict[str, str], ...] = (
    {
        "surface_id": "37d3e8ba-2f5c-816d-8ccc-c0b46b9a2760",
        "title": "ABX_CODEGEN_INTELLIGENCE_SPINE_001 — Governed Recursive Self-Improvement Spec",
        "status": "ADVISORY_DRAFT_PLANNING_ONLY",
        "source_observed_at": "2026-06-12T19:57:22Z",
    },
    {
        "surface_id": "37d3e8ba-2f5c-81bc-8cc8-e5399d20e21a",
        "title": "ABX_CODEGEN_INTELLIGENCE_SPINE_ADVISORY_SPEC_PLAN_001",
        "status": "ADVISORY_PLANNING_READY",
        "source_observed_at": "2026-06-12T19:57:18Z",
    },
    {
        "surface_id": "37d3e8ba-2f5c-81d5-b6e7-e310caf15f13",
        "title": "GapDiagnosisPacket.v1 — Packet Schema",
        "status": "ADVISORY_PLANNING_DRAFT",
        "source_observed_at": "2026-06-12T19:48:15Z",
    },
    {
        "surface_id": "37d3e8ba-2f5c-818b-a014-f8e8869d08d3",
        "title": "ImprovementProposal.v1 — Packet Schema",
        "status": "ADVISORY_PLANNING_DRAFT",
        "source_observed_at": "2026-06-12T19:48:00Z",
    },
    {
        "surface_id": "37d3e8ba-2f5c-8187-8882-f0c760ddf729",
        "title": "ShadowImprovementReceipt.v1 — Packet Schema",
        "status": "ADVISORY_PLANNING_DRAFT_V1_1",
        "source_observed_at": "2026-06-12T19:56:48Z",
    },
    {
        "surface_id": "37d3e8ba-2f5c-81d8-bfea-c295f875e36d",
        "title": "Codegen Intelligence Spine — Sample Fixtures & Test Vectors v1",
        "status": "ADVISORY_PLANNING_SAMPLES",
        "source_observed_at": "2026-06-12T19:58:18Z",
    },
    {
        "surface_id": "37d3e8ba-2f5c-81a3-b6a7-c53020554e81",
        "title": "ImprovementProposal.v1 → Shadow Replay Harness Wiring Spec",
        "status": "ADVISORY_PLANNING_DRAFT",
        "source_observed_at": "2026-06-12T19:56:57Z",
    },
    {
        "surface_id": "37d3e8ba-2f5c-811c-b80a-dd31b2d8f4ce",
        "title": "Self-Improvement Meta-Gate Spec — Codegen Intelligence Spine",
        "status": "ADVISORY_PLANNING_DRAFT",
        "source_observed_at": "2026-06-12T20:00:59Z",
    },
)

AUTHORITY_LOCKS: dict[str, bool] = {
    "activation": False,
    "auto_approval": False,
    "auto_continuation": False,
    "canon_mutation": False,
    "code_generation": False,
    "code_mutation": False,
    "execution_authority": False,
    "file_writeback": False,
    "forecast_routing": False,
    "github_writeback": False,
    "notion_writeback": False,
    "queue_mutation": False,
    "runtime_mutation": False,
    "scheduler_mutation": False,
    "self_authorization": False,
    "shadow_replay_execution": False,
}

BLOCKED_ACTIONS: tuple[str, ...] = (
    "codegen_engine_implementation",
    "code_generation",
    "code_mutation",
    "file_writeback",
    "shadow_replay_execution",
    "runtime_dispatch_mutation",
    "canon_mutation",
    "queue_mutation",
    "scheduler_mutation",
    "forecast_routing",
    "notion_writeback",
    "github_writeback",
    "auto_approval",
    "self_authorization",
    "activation_or_execution",
)

_SEVERITY_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
_HOLD_OR_BLOCK_RECOMMENDATIONS = {
    "HOLD_FOR_OPERATOR",
    "HOLD_FOR_META_GATE",
    "BLOCK_POLICY_VIOLATION",
    "BLOCK_REPLAY_FAILURE",
}


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _read_json(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _status_for(path: Path) -> str:
    return "OBSERVED" if path.exists() else "MISSING"


def _notion_spec_stack() -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for item in NOTION_SPEC_STACK:
        record = dict(item)
        record["source_hash"] = canonical_hash(item)
        records.append(record)
    return records


def _schema_contract_records(repo_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in SCHEMA_CONTRACT_PATHS:
        target = repo_root / path
        records.append(
            {
                "path": path,
                "status": _status_for(target),
                "source_hash": _sha256(target) if target.exists() else "NOT_COMPUTABLE",
                "validation_mode": "SCHEMA_AND_GOVERNANCE_RULES",
                "advisory_only": True,
                "grants_execution_authority": False,
            }
        )
    return records


def _fixture_records(repo_root: Path) -> list[dict[str, Any]]:
    fixture_root = repo_root / "tests/fixtures/codegen"
    records: list[dict[str, Any]] = []
    for target in sorted(fixture_root.glob("*.json")):
        rel = target.relative_to(repo_root).as_posix()
        records.append(
            {
                "path": rel,
                "fixture_class": "NEGATIVE" if target.name.startswith("invalid_") else "VALID",
                "source_hash": _sha256(target),
            }
        )
    return records


def validate_codegen_packet_semantics(packet: Mapping[str, Any]) -> list[str]:
    """Return fail-closed governance rule violations for codegen planning packets."""
    schema_version = packet.get("schema_version")
    errors: list[str] = []

    if schema_version == "GapDiagnosisPacket.v1":
        if packet.get("self_diagnosis_flag") is True:
            severity = str(packet.get("severity", "LOW"))
            if _SEVERITY_ORDER.get(severity, -1) < _SEVERITY_ORDER["MEDIUM"]:
                errors.append("self_diagnosis_requires_medium_severity")
        for source in packet.get("evidence_sources", []):
            if isinstance(source, dict) and not source.get("hash"):
                errors.append("evidence_source_hash_required")
        return sorted(set(errors))

    if schema_version == "ImprovementProposal.v1":
        risk = packet.get("risk_assessment", {})
        self_modification = isinstance(risk, dict) and risk.get("self_modification_risk") is True
        if self_modification and packet.get("operator_decision_required") is not True:
            errors.append("self_modification_requires_operator_decision")
        if packet.get("promotion_path") == "CANON":
            errors.append("canon_promotion_requires_prior_canary_success")
        provenance = packet.get("provenance", {})
        if isinstance(provenance, dict) and not provenance.get("source_gap_analysis"):
            errors.append("provenance_source_gap_analysis_required")
        for delta in packet.get("contract_deltas", []):
            if not isinstance(delta, dict):
                continue
            proposed_content = delta.get("proposed_content", {})
            if (
                isinstance(proposed_content, dict)
                and proposed_content.get("allow_auto_mutation") is True
            ):
                errors.append("core_policy_auto_mutation_denied")
        return sorted(set(errors))

    if schema_version == "ShadowImprovementReceipt.v1":
        validation = packet.get("validation_results", {})
        metrics = packet.get("metrics", {})
        flags = packet.get("governance_flags", {})
        recommendation = packet.get("recommendation")
        governance_compliance = (
            isinstance(validation, dict) and validation.get("governance_compliance") is True
        )
        invariance_passed = (
            isinstance(metrics, dict) and metrics.get("12_run_invariance_passed") is True
        )
        self_modification = (
            isinstance(flags, dict) and flags.get("self_modification_detected") is True
        )
        requires_operator_review = (
            isinstance(flags, dict) and flags.get("requires_operator_review") is True
        )
        if recommendation == "PROMOTE_TO_CANARY" and not governance_compliance:
            errors.append("promotion_requires_governance_compliance")
        if recommendation == "PROMOTE_TO_CANARY" and not invariance_passed:
            errors.append("promotion_requires_12_run_invariance")
        if self_modification and not requires_operator_review:
            errors.append("self_modification_requires_operator_review")
        if self_modification and recommendation not in {"HOLD_FOR_META_GATE", "HOLD_FOR_OPERATOR"}:
            errors.append("self_modification_requires_hold_recommendation")
        if recommendation in _HOLD_OR_BLOCK_RECOMMENDATIONS and not packet.get(
            "promotion_blockers"
        ):
            errors.append("hold_or_block_requires_promotion_blockers")
        return sorted(set(errors))

    return ["unsupported_codegen_packet_schema_version"]


def build_abx_codegen_intelligence_spine_advisory_spec_plan(
    *,
    repo_root: str | Path,
    gap_analysis_plan_path: str | Path = GAP_ANALYSIS_PLAN_JSON,
    canon_resume_state_path: str | Path = CANON_RESUME_STATE_JSON,
    temporal_spine_precheck_path: str | Path = TEMPORAL_SPINE_PRECHECK_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_paths = {
        "gap_analysis_plan": Path(gap_analysis_plan_path).as_posix(),
        "canon_resume_state": Path(canon_resume_state_path).as_posix(),
        "temporal_spine_precheck": Path(temporal_spine_precheck_path).as_posix(),
    }
    source_hashes = {
        key: _sha256(root / path)
        for key, path in source_paths.items()
    }
    required_source_statuses = {
        key: _status_for(root / path)
        for key, path in source_paths.items()
    }
    gap_plan = _read_json(root / gap_analysis_plan_path)
    gap_plan_ready = (
        gap_plan.get("recommended_next_lane")
        == "ABX_CODEGEN_INTELLIGENCE_SPINE_ADVISORY_SPEC_PLAN"
    )
    schema_contracts = _schema_contract_records(root)
    fixtures = _fixture_records(root)
    schemas_observed = all(record["status"] == "OBSERVED" for record in schema_contracts)
    sources_observed = all(status == "OBSERVED" for status in required_source_statuses.values())
    plan_status = (
        "ABX_CODEGEN_INTELLIGENCE_SPINE_ADVISORY_SPEC_PLAN_READY"
        if gap_plan_ready and schemas_observed and fixtures and sources_observed
        else "NOT_COMPUTABLE"
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "plan_status": plan_status,
        "target_surface": "ABX_CODEGEN_INTELLIGENCE_SPINE_001",
        "target_surface_status": "ADVISORY_SPEC_STACK_REPO_ALIGNED",
        "patch_id": "PATCH-ABX-CODEGEN-INTELLIGENCE-SPINE-ADVISORY-SPEC-PLAN-001",
        "source_paths": source_paths,
        "source_hashes": source_hashes,
        "required_source_statuses": required_source_statuses,
        "notion_spec_stack": _notion_spec_stack(),
        "schema_contracts": schema_contracts,
        "fixture_harness": {
            "fixture_root": "tests/fixtures/codegen",
            "fixture_count": len(fixtures),
            "valid_fixture_count": sum(
                1 for fixture in fixtures if fixture["fixture_class"] == "VALID"
            ),
            "negative_fixture_count": sum(
                1 for fixture in fixtures if fixture["fixture_class"] == "NEGATIVE"
            ),
            "fixtures": fixtures,
            "validation_mode": "VALIDATION_ONLY_NO_REPLAY_EXECUTION",
            "uses_wall_clock": False,
            "notion_samples_copied_verbatim": False,
        },
        "shadow_replay_boundary": {
            "shadow_replay_wiring_spec_observed": True,
            "shadow_replay_execution_allowed": False,
            "shadow_replay_receipts_are_planning_fixtures_only": True,
            "recommended_future_lane": "ABX_CODEGEN_INTELLIGENCE_SPINE_SHADOW_REPLAY_WIRING_PLAN",
        },
        "meta_gate_boundary": {
            "meta_gate_spec_observed": True,
            "self_authorization_allowed": False,
            "self_improvement_requires_operator_meta_gate": True,
            "self_improvement_direct_promotion_allowed": False,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "blocked_actions": list(BLOCKED_ACTIONS),
        "recommended_next_lane": "ABX_CODEGEN_INTELLIGENCE_SPINE_FIXTURE_VALIDATION_HARNESS_PLAN",
        "recommended_next_action": (
            "use the repo schemas and fixtures to author a separate validation-only "
            "harness plan before any codegen engine implementation"
        ),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "codegen_engine_implementation_performed": False,
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_advisory_spec_plan(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    write_canonical_json(path, packet)


def write_abx_codegen_intelligence_spine_advisory_spec_plan_markdown(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    lines = [
        "# ABX Codegen Intelligence Spine Advisory Spec Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- plan_status: {packet['plan_status']}",
        f"- target_surface: {packet['target_surface']}",
        f"- target_surface_status: {packet['target_surface_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- codegen_engine_implementation_performed: {packet['codegen_engine_implementation_performed']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Schema Contracts",
    ]
    for record in packet.get("schema_contracts", []):
        if isinstance(record, dict):
            lines.append(f"- {record['path']}: {record['status']}")
    fixture_harness = packet.get("fixture_harness", {})
    if isinstance(fixture_harness, dict):
        lines.extend(
            [
                "",
                "## Fixture Harness",
                f"- fixture_count: {fixture_harness['fixture_count']}",
                f"- valid_fixture_count: {fixture_harness['valid_fixture_count']}",
                f"- negative_fixture_count: {fixture_harness['negative_fixture_count']}",
                f"- validation_mode: {fixture_harness['validation_mode']}",
            ]
        )
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- {action}")
    lines.extend(["", "## Notion Spec Stack"])
    for record in packet.get("notion_spec_stack", []):
        if isinstance(record, dict):
            lines.append(f"- {record['title']}: {record['status']}")

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
