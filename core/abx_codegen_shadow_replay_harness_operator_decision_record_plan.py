from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_advisory_spec_plan import (
    AUTHORITY_LOCKS,
    BLOCKED_ACTIONS,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenShadowReplayHarnessOperatorDecisionRecordPlan.v1"
PLAN_ID = (
    "ABX_CODEGEN_INTELLIGENCE_SPINE_SHADOW_REPLAY_HARNESS_"
    "OPERATOR_DECISION_RECORD_PLAN_001"
)
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_"
    "record_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_"
    "record_plan_001.latest.md"
)
IMPLEMENTATION_AUTHORIZATION_GATE_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_shadow_replay_harness_implementation_"
    "authorization_gate_001.latest.json"
)

NOTION_DECISION_SOURCES: tuple[dict[str, str], ...] = (
    {
        "surface_id": "37d3e8ba-2f5c-8162-b008-f2b101f38cb2",
        "title": "Operator Decision Record Template — Codegen Intelligence (incl. Meta-Gate)",
        "status": "PLANNING_TEMPLATE_ADVISORY",
        "source_observed_at": "2026-06-12T19:58:24Z",
    },
    {
        "surface_id": "37d3e8ba-2f5c-816c-a655-e99aaeb3652d",
        "title": "Meta-Gate Authorization Record Template — Codegen Intelligence Spine",
        "status": "PLANNING_TEMPLATE_ADVISORY",
        "source_observed_at": "2026-06-12T19:59:58Z",
    },
)

REQUIRED_RECORD_FIELDS: tuple[dict[str, str], ...] = (
    {"field": "record_id", "requirement": "deterministic record identifier"},
    {"field": "source_proposal_id", "requirement": "ImprovementProposal.v1 linkage"},
    {"field": "source_receipt_id", "requirement": "ShadowImprovementReceipt.v1 linkage when present"},
    {"field": "decision_type", "requirement": "Normal, Meta-Gate, or High-Risk"},
    {"field": "proposal_summary", "requirement": "proposal type, target surface, intent, self-modification risk"},
    {"field": "shadow_replay_results", "requirement": "receipt recommendation, blockers, metrics"},
    {"field": "risk_assessment", "requirement": "governance rent, complexity delta, drift risk"},
    {"field": "operator_decision", "requirement": "APPROVE, REJECT, REQUEST_REFINEMENT, ESCALATE_TO_META_GATE, or DEFER"},
    {"field": "rationale", "requirement": "human-written justification"},
    {"field": "conditions", "requirement": "operator conditions and downstream requirements"},
    {"field": "operator_attestation", "requirement": "operator identity, statement, signature or confirmation"},
    {"field": "continuity_lane", "requirement": "advisory continuity reference only"},
)

ALLOWED_DECISIONS: tuple[dict[str, str], ...] = (
    {"decision": "APPROVE", "effect": "requires downstream authorization record before implementation"},
    {"decision": "REJECT", "effect": "blocks implementation and records rationale"},
    {"decision": "REQUEST_REFINEMENT", "effect": "routes back to proposal refinement"},
    {"decision": "ESCALATE_TO_META_GATE", "effect": "requires meta-gate authorization record planning"},
    {"decision": "DEFER", "effect": "holds for more evidence without authorization"},
)

REQUIRED_ATTACHMENTS: tuple[str, ...] = (
    "ImprovementProposal.v1 JSON",
    "ShadowImprovementReceipt.v1 JSON when present",
    "relevant fixtures and test vectors",
    "implementation authorization gate packet",
)

LINEAGE_REQUIREMENTS: tuple[str, ...] = (
    "must link to implementation authorization gate",
    "must link to source ImprovementProposal.v1",
    "must link to source ShadowImprovementReceipt.v1 when present",
    "must preserve continuity lane reference",
    "must remain queryable by proposal_id and receipt_id",
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


def _status_for(path: Path) -> str:
    return "OBSERVED" if path.exists() else "MISSING"


def _source_records(records: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    enriched: list[dict[str, str]] = []
    for item in records:
        record = dict(item)
        record["source_hash"] = canonical_hash(item)
        enriched.append(record)
    return enriched


def build_abx_codegen_shadow_replay_harness_operator_decision_record_plan(
    *,
    repo_root: str | Path,
    implementation_authorization_gate_path: str | Path = IMPLEMENTATION_AUTHORIZATION_GATE_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_paths = {
        "implementation_authorization_gate": Path(
            implementation_authorization_gate_path
        ).as_posix()
    }
    source_hashes = {key: _sha256(root / path) for key, path in source_paths.items()}
    required_source_statuses = {
        key: _status_for(root / path)
        for key, path in source_paths.items()
    }
    gate = _read_json(root / implementation_authorization_gate_path)
    upstream_ready = gate.get("recommended_next_lane") in {
        "ABX_CODEGEN_INTELLIGENCE_SPINE_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_PLAN",
        "CORE_CODEGEN_SHADOW_REPLAY_HARNESS_IMPLEMENTATION",
    }
    sources_observed = all(status == "OBSERVED" for status in required_source_statuses.values())
    implementation_authorized = gate.get("implementation_authorization_granted") is True
    plan_status = (
        "ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_PLAN_READY"
        if upstream_ready and sources_observed
        else "NOT_COMPUTABLE"
    )

    authority_locks = dict(AUTHORITY_LOCKS)
    authority_locks.update(
        {
            "authorization_record_creation": False,
            "decision_record_creation": False,
            "harness_implementation": False,
            "meta_gate_authorization": False,
            "operator_decision_attestation": False,
            "receipt_creation": False,
        }
    )
    blocked_actions = sorted(
        set(BLOCKED_ACTIONS)
        | {
            "authorization_record_creation",
            "decision_record_creation",
            "harness_implementation",
            "meta_gate_authorization",
            "operator_decision_attestation",
            "receipt_creation",
        }
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "operator_decision_record_plan_status": plan_status,
        "target_surface": "ABX_CODEGEN_INTELLIGENCE_SPINE_001",
        "target_module": "core/codegen_shadow_replay_harness.py",
        "patch_id": (
            "PATCH-ABX-CODEGEN-SHADOW-REPLAY-HARNESS-OPERATOR-"
            "DECISION-RECORD-PLAN-001"
        ),
        "source_paths": source_paths,
        "source_hashes": source_hashes,
        "required_source_statuses": required_source_statuses,
        "notion_decision_sources": _source_records(NOTION_DECISION_SOURCES),
        "planned_record_type": "CodegenOperatorDecisionRecord.v1",
        "required_record_fields": list(REQUIRED_RECORD_FIELDS),
        "allowed_decisions": list(ALLOWED_DECISIONS),
        "meta_gate_requirements": {
            "meta_gate_section_required_for_self_modification": True,
            "positive_meta_gate_decision_is_not_promotion_authority": True,
            "meta_gate_authorization_record_required_after_positive_decision": True,
            "codegen_spine_self_authorization_allowed": False,
            "future_template": "MetaGateAuthorizationRecord.v1",
        },
        "required_attachments": list(REQUIRED_ATTACHMENTS),
        "lineage_requirements": list(LINEAGE_REQUIREMENTS),
        "operator_attestation_requirements": {
            "human_operator_required": True,
            "operator_id_required": True,
            "human_rationale_required": True,
            "signature_or_confirmation_required": True,
            "codex_or_spine_attestation_allowed": False,
        },
        "record_creation_authorized": False,
        "operator_decision_attested": False,
        "implementation_authorization_granted": implementation_authorized,
        "authority_locks": authority_locks,
        "blocked_actions": blocked_actions,
        "recommended_next_lane": (
            "ABX_CODEGEN_INTELLIGENCE_SPINE_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_DRY_RUN"
        ),
        "recommended_next_action": (
            "dry-run the operator decision record shape with simulated evidence only; "
            "do not create a decision record or authorize harness implementation"
        ),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "valid_for_execution": False,
        "valid_for_implementation": implementation_authorized,
        "decision_record_created": False,
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_shadow_replay_harness_operator_decision_record_plan(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    write_canonical_json(path, packet)


def write_abx_codegen_shadow_replay_harness_operator_decision_record_plan_markdown(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    lines = [
        "# ABX Codegen Shadow Replay Harness Operator Decision Record Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- operator_decision_record_plan_status: {packet['operator_decision_record_plan_status']}",
        f"- planned_record_type: {packet['planned_record_type']}",
        f"- target_surface: {packet['target_surface']}",
        f"- target_module: {packet['target_module']}",
        f"- record_creation_authorized: {packet['record_creation_authorized']}",
        f"- operator_decision_attested: {packet['operator_decision_attested']}",
        f"- implementation_authorization_granted: {packet['implementation_authorization_granted']}",
        f"- decision_record_created: {packet['decision_record_created']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        "",
        "## Required Record Fields",
    ]
    for field in packet.get("required_record_fields", []):
        if isinstance(field, dict):
            lines.append(f"- {field['field']}: {field['requirement']}")
    lines.extend(["", "## Allowed Decisions"])
    for decision in packet.get("allowed_decisions", []):
        if isinstance(decision, dict):
            lines.append(f"- {decision['decision']}: {decision['effect']}")
    lines.extend(["", "## Required Attachments"])
    for attachment in packet.get("required_attachments", []):
        lines.append(f"- {attachment}")
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- {action}")

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
