from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "RuntimeIntegrationGateReceipt.v1"
RECEIPT_ID = "ABRAXAS_RUNTIME_INTEGRATION_GATE_RECEIPT_001"
OUT_JSON = "out/audit/runtime_integration_gate_receipt_001.latest.json"
OUT_MD = "out/audit/runtime_integration_gate_receipt_001.latest.md"

REPO_NOTION_DIFF_JSON = "docs/audits/abraxas_repo_notion_diff_001.json"
CANON_RESUME_STATE_JSON = "out/canon_resume_state/latest.json"
TEMPORAL_SPINE_PRECHECK_JSON = "out/temporal_continuity_spine_precheck/latest.json"

_RUNTIME_SPINE_PATHS: tuple[str, ...] = (
    "core/runtime_spine/authority_router.py",
    "core/runtime_spine/router.py",
    "core/runtime_spine/models.py",
    "contracts/runtime/runtime_spine.v1.schema.json",
    "tests/test_runtime_spine_skeleton.py",
    "out/audit/runtime_spine_skeleton.latest.json",
    "out/audit/runtime_spine_audit.latest.json",
)

_REQUIRED_FIELDS: tuple[str, ...] = (
    "source_canonical_owner",
    "parent_subsystem_candidate",
    "target_runtime_surface",
    "allowed_inputs",
    "allowed_outputs",
    "forbidden_outputs",
    "governance_locks",
    "provenance_requirements",
    "validation_commands",
    "no_authority_seal",
)

_AUTHORITY_LOCKS: dict[str, bool] = {
    "advisory_only": True,
    "shadow_only": True,
    "non_authoritative": True,
    "forecast_routing": False,
    "canon_mutation": False,
    "runtime_mutation": False,
    "replay_mutation": False,
    "execution_authority": False,
    "operator_command_authority": False,
    "autonomous_action": False,
    "autonomous_promotion": False,
    "duplicate_runtime_authority_created": False,
    "mandatory_pre_dispatch_gate_enabled": False,
}

_SUBSYSTEM_BINDINGS: tuple[dict[str, Any], ...] = (
    {
        "subsystem_id": "GLOBAL_INGEST_ADAPTER_SPINE_001",
        "source_canonical_owner": "Oracle Signal Layer v2",
        "parent_subsystem_candidate": "Global Ingest Adapter Spine",
        "target_runtime_surface": "ingest shadow handoff and operator-reviewed Oracle intake queue",
        "allowed_inputs": ["operator-scoped ingest evidence", "shadow handoff receipts"],
        "allowed_outputs": ["advisory ingest receipts", "operator review requests"],
        "forbidden_outputs": ["autonomous scraping", "unscoped live ingest", "source truth validation"],
        "provenance_requirements": ["operator scope", "source receipt", "policy boundary"],
        "validation_commands": [
            "python scripts/run_global_ingest_adapter_spine_alignment_plan.py",
            "python scripts/run_oracle_signal_intake_boundary_implementation_plan.py",
        ],
    },
    {
        "subsystem_id": "BELIEF_GRAPH_ENGINE_001",
        "source_canonical_owner": "Oracle Signal Layer v2",
        "parent_subsystem_candidate": "Belief Graph Engine",
        "target_runtime_surface": "advisory belief graph packet and receipt planning surfaces",
        "allowed_inputs": ["Oracle Signal evidence", "research replay evidence"],
        "allowed_outputs": ["advisory graph packets", "planning receipts"],
        "forbidden_outputs": ["claim validation", "theory promotion", "forecast routing"],
        "provenance_requirements": ["evidence object", "theory object", "operator review boundary"],
        "validation_commands": [
            "python scripts/run_belief_graph_engine_gap_analysis_plan.py",
            "python scripts/run_belief_graph_engine_advisory_spec_plan.py",
        ],
    },
    {
        "subsystem_id": "RESEARCH_SHADOW_REPLAY_ENGINE_001",
        "source_canonical_owner": "Recursive Cognition & Replay Governance",
        "parent_subsystem_candidate": "Research Shadow Replay Engine",
        "target_runtime_surface": "research replay and stabilization evidence chain",
        "allowed_inputs": ["research drop packets", "replay fixtures", "stabilization receipts"],
        "allowed_outputs": ["shadow replay audits", "promotion blocker evidence"],
        "forbidden_outputs": ["canon promotion", "autonomous promotion", "replay mutation"],
        "provenance_requirements": ["replay source", "stabilization receipt", "operator boundary"],
        "validation_commands": [
            "python scripts/run_research_shadow_replay_audit.py",
            "python scripts/run_research_promotion_blocker_ledger.py",
        ],
    },
    {
        "subsystem_id": "PHASE_PERCOLATION_ENGINE_001",
        "source_canonical_owner": "P27 Temporal Resonance and Coherence Field Topology",
        "parent_subsystem_candidate": "Phase Percolation Engine",
        "target_runtime_surface": "temporal regime and phase-planning projections",
        "allowed_inputs": ["temporal resonance artifacts", "coherence field topology evidence"],
        "allowed_outputs": ["advisory phase plans", "projection packets"],
        "forbidden_outputs": ["runtime mutation", "forecast mutation", "autonomous optimization"],
        "provenance_requirements": ["temporal source artifact", "projection boundary", "operator review"],
        "validation_commands": [
            "python scripts/run_temporal_regime_transition_detector_contract.py",
            "python scripts/run_temporal_resonance_coherence.py",
        ],
    },
    {
        "subsystem_id": "AAL_VIZ_PROJECTION_SPINE_001",
        "source_canonical_owner": "AAL-Viz Projection Spine",
        "parent_subsystem_candidate": "AAL-Viz Projection Spine",
        "target_runtime_surface": "packet-derived projection and visualization outputs",
        "allowed_inputs": ["projection packets", "warning-bearing upstream artifacts"],
        "allowed_outputs": ["read-only projections", "visual summaries"],
        "forbidden_outputs": ["authority by visualization", "command semantics", "runtime mutation"],
        "provenance_requirements": ["projection packet", "source warning preservation"],
        "validation_commands": [
            "python scripts/run_aal_viz_runtime_projection.py",
            "python scripts/run_aal_viz_graph_render_packet.py",
        ],
    },
    {
        "subsystem_id": "SITUATION_RUNTIME_ENGINE_001",
        "source_canonical_owner": "Situation Runtime / Proactive Coordination research fold",
        "parent_subsystem_candidate": "Situation Runtime Engine",
        "target_runtime_surface": "operator runtime console and advisory situation packets",
        "allowed_inputs": ["operator context packets", "Oracle Signal advisory evidence"],
        "allowed_outputs": ["implementation plans", "operator-facing advisory summaries"],
        "forbidden_outputs": [
            "autonomous action",
            "surveillance authority",
            "persuasion optimization",
            "command authority",
        ],
        "provenance_requirements": ["operator context provenance", "packet contract stability"],
        "validation_commands": [
            "python scripts/run_operator_runtime_console.py",
            "python scripts/run_runtime_inventory.py",
        ],
    },
    {
        "subsystem_id": "ABX_CODEGEN_INTELLIGENCE_SPINE_001",
        "source_canonical_owner": "ABX Codegen Intelligence Spine",
        "parent_subsystem_candidate": "Codegen Intelligence Spine",
        "target_runtime_surface": "governed code-drop and patch-contract planning handoff",
        "allowed_inputs": ["CodeIR doctrine", "incremental patch doctrine", "readiness packets"],
        "allowed_outputs": ["advisory codegen plans", "operator review packets"],
        "forbidden_outputs": [
            "autonomous patch application",
            "autonomous PR merge",
            "canon mutation",
            "file writeback without operator review",
        ],
        "provenance_requirements": ["code-drop envelope", "operator review", "generated artifact policy"],
        "validation_commands": [
            "python scripts/run_abx_codegen_intelligence_spine_gap_analysis_plan.py",
            "python scripts/run_artifact_regeneration.py --check-drift",
        ],
    },
)


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


def _notion_surface_record(repo_notion_diff: Mapping[str, Any]) -> Mapping[str, Any]:
    targets = repo_notion_diff.get("notion_targets", [])
    if not isinstance(targets, list):
        return {}
    for target in targets:
        if (
            isinstance(target, dict)
            and target.get("notion_surface") == "ABRAXAS_RUNTIME_INTEGRATION_GATE_001"
        ):
            return target
    return {}


def _path_records(repo_root: Path, paths: tuple[str, ...]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in paths:
        target = repo_root / path
        observed = target.exists()
        records.append(
            {
                "path": path,
                "status": "OBSERVED" if observed else "MISSING",
                "source_hash": _sha256(target) if observed else "NOT_COMPUTABLE",
            }
        )
    return records


def _binding_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for binding in _SUBSYSTEM_BINDINGS:
        record = dict(binding)
        record["governance_locks"] = dict(_AUTHORITY_LOCKS)
        record["no_authority_seal"] = {
            "runtime_integration_status": "BOUND_TO_EXISTING_CANONICAL_SYSTEMS_ADVISORY_ONLY",
            "duplicate_runtime_authority_created": False,
            "forecast_routing": False,
            "canon_mutation": False,
            "runtime_mutation": False,
            "replay_mutation": False,
            "execution_authority": False,
            "mandatory_pre_dispatch_gate_enabled": False,
        }
        record["declared_fields"] = list(_REQUIRED_FIELDS)
        record["field_completeness"] = "COMPLETE"
        records.append(record)
    return sorted(records, key=lambda item: str(item["subsystem_id"]))


def build_runtime_integration_gate_receipt(
    *,
    repo_root: str | Path,
    repo_notion_diff_path: str | Path = REPO_NOTION_DIFF_JSON,
    canon_resume_state_path: str | Path = CANON_RESUME_STATE_JSON,
    temporal_spine_precheck_path: str | Path = TEMPORAL_SPINE_PRECHECK_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    repo_notion_diff = _read_json(root / repo_notion_diff_path)
    canon_resume = _read_json(root / canon_resume_state_path)
    temporal_precheck = _read_json(root / temporal_spine_precheck_path)
    notion_record = _notion_surface_record(repo_notion_diff)
    runtime_spine_records = _path_records(root, _RUNTIME_SPINE_PATHS)
    observed_runtime_paths = sum(1 for record in runtime_spine_records if record["status"] == "OBSERVED")
    binding_records = _binding_records()
    required_source_statuses = {
        "repo_notion_diff": "OBSERVED" if repo_notion_diff else "MISSING",
        "canon_resume_state": "OBSERVED" if canon_resume else "MISSING",
        "temporal_spine_precheck": "OBSERVED" if temporal_precheck else "MISSING",
    }
    required_sources_observed = all(status == "OBSERVED" for status in required_source_statuses.values())
    receipt_status = (
        "RUNTIME_INTEGRATION_GATE_RECEIPT_READY_ADVISORY_ONLY"
        if required_sources_observed and observed_runtime_paths == len(runtime_spine_records)
        else "NOT_COMPUTABLE"
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "receipt_id": RECEIPT_ID,
        "receipt_status": receipt_status,
        "target_surface": "ABRAXAS_RUNTIME_INTEGRATION_GATE_001",
        "target_surface_status": "RECEIPT_READY_MANDATORY_GATE_NOT_ENABLED",
        "notion_source": "ABRAXAS_RUNTIME_INTEGRATION_GATE_001",
        "patch_id": "PATCH-ABX-RUNTIME-INTEGRATION-GATE-RECEIPT-001",
        "source_paths": {
            "repo_notion_diff": Path(repo_notion_diff_path).as_posix(),
            "canon_resume_state": Path(canon_resume_state_path).as_posix(),
            "temporal_spine_precheck": Path(temporal_spine_precheck_path).as_posix(),
        },
        "source_hashes": {
            "repo_notion_diff": _sha256(root / repo_notion_diff_path),
            "canon_resume_state": _sha256(root / canon_resume_state_path),
            "temporal_spine_precheck": _sha256(root / temporal_spine_precheck_path),
        },
        "required_source_statuses": required_source_statuses,
        "notion_gap_evidence": {
            "repo_equivalent_found": bool(notion_record.get("repo_equivalent_found", False)),
            "implementation_status": str(notion_record.get("implementation_status", "NOT_COMPUTABLE")),
            "match_strength": str(notion_record.get("match_strength", "NOT_COMPUTABLE")),
            "recommended_action": str(notion_record.get("recommended_action", "NOT_COMPUTABLE")),
            "missing_elements": [
                str(item)
                for item in notion_record.get("missing_elements", [])
                if isinstance(item, str)
            ],
        },
        "runtime_spine_evidence": {
            "runtime_spine_paths_observed": observed_runtime_paths,
            "runtime_spine_paths_total": len(runtime_spine_records),
            "mandatory_pre_dispatch_gate_present": False,
            "mandatory_pre_dispatch_gate_enabled": False,
            "runtime_spine_remains_skeleton": True,
        },
        "runtime_spine_path_records": runtime_spine_records,
        "required_declaration_fields": list(_REQUIRED_FIELDS),
        "covered_subsystem_count": len(binding_records),
        "covered_subsystems": binding_records,
        "gate_policy": {
            "allowed_patch_classes": [
                "CONTRACTS_ONLY",
                "METADATA_ONLY",
                "IMPLEMENTATION_PLAN_ONLY",
                "FAIL_CLOSED_ADAPTER_WITH_NO_LIVE_BEHAVIOR",
            ],
            "blocked_patch_classes": [
                "LIVE_RUNTIME_MUTATION",
                "AUTONOMOUS_ACTION",
                "FORECAST_ROUTING",
                "CANON_PROMOTION",
                "MANDATORY_PRE_DISPATCH_WIRING",
            ],
            "operator_review_required_where_behavior_changes": True,
        },
        "receipt_summary": {
            "all_subsystems_declare_required_fields": all(
                record["field_completeness"] == "COMPLETE" for record in binding_records
            ),
            "runtime_spine_evidence_observed": observed_runtime_paths == len(runtime_spine_records),
            "duplicate_runtime_authority_created": False,
            "mandatory_gate_enabled": False,
            "ready_for_live_runtime_wiring": False,
        },
        "recommended_next_lane": "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_OR_ADVISORY_SPEC_PLAN",
        "recommended_next_action": (
            "hold for operator review before any mandatory pre-dispatch runtime wiring"
        ),
        "advisory_only": True,
        "shadow_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "valid_for_execution": False,
        "valid_for_runtime_wiring": False,
        "forecast_routing_allowed": False,
        "canon_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "replay_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "execution_authority": False,
        "operator_command_authority": False,
        "autonomous_action_allowed": False,
        "autonomous_promotion_allowed": False,
        "duplicate_runtime_authority_created": False,
        "mandatory_pre_dispatch_gate_enabled": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "authority_locks": dict(_AUTHORITY_LOCKS),
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_runtime_integration_gate_receipt(path: str | Path, packet: Mapping[str, Any]) -> None:
    write_canonical_json(path, packet)


def write_runtime_integration_gate_receipt_markdown(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    lines = [
        "# Runtime Integration Gate Receipt 001",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- receipt_status: {packet['receipt_status']}",
        f"- target_surface: {packet['target_surface']}",
        f"- target_surface_status: {packet['target_surface_status']}",
        f"- covered_subsystem_count: {packet['covered_subsystem_count']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- valid_for_runtime_wiring: {packet['valid_for_runtime_wiring']}",
        f"- mandatory_pre_dispatch_gate_enabled: {packet['mandatory_pre_dispatch_gate_enabled']}",
        f"- duplicate_runtime_authority_created: {packet['duplicate_runtime_authority_created']}",
        f"- execution_authority: {packet['execution_authority']}",
        "",
        "## Runtime Spine Evidence",
    ]
    evidence = packet.get("runtime_spine_evidence", {})
    if isinstance(evidence, dict):
        for key in sorted(evidence):
            lines.append(f"- {key}: {evidence[key]}")
    lines.extend(["", "## Covered Subsystems"])
    for record in packet.get("covered_subsystems", []):
        if isinstance(record, dict):
            lines.append(
                "- "
                f"{record['subsystem_id']}: {record['field_completeness']} "
                f"(owner={record['source_canonical_owner']})"
            )
    lines.extend(["", "## Gate Policy"])
    policy = packet.get("gate_policy", {})
    if isinstance(policy, dict):
        lines.append("- allowed_patch_classes: " + ", ".join(policy["allowed_patch_classes"]))
        lines.append("- blocked_patch_classes: " + ", ".join(policy["blocked_patch_classes"]))
        lines.append(
            "- operator_review_required_where_behavior_changes: "
            f"{policy['operator_review_required_where_behavior_changes']}"
        )
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
