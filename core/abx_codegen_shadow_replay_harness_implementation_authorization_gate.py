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

ARTIFACT_TYPE = (
    "AbxCodegenIntelligenceSpineShadowReplayHarnessImplementationAuthorizationGate.v1"
)
GATE_ID = (
    "ABX_CODEGEN_INTELLIGENCE_SPINE_SHADOW_REPLAY_HARNESS_IMPLEMENTATION_"
    "AUTHORIZATION_GATE_001"
)
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_shadow_replay_harness_implementation_"
    "authorization_gate_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_shadow_replay_harness_implementation_"
    "authorization_gate_001.latest.md"
)
FIXTURE_VALIDATION_HARNESS_PLAN_JSON = (
    "out/audit/abx_codegen_intelligence_spine_fixture_validation_harness_plan_001.latest.json"
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


def build_abx_codegen_shadow_replay_harness_implementation_authorization_gate(
    *,
    repo_root: str | Path,
    fixture_validation_harness_plan_path: str | Path = FIXTURE_VALIDATION_HARNESS_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_paths = {
        "fixture_validation_harness_plan": Path(
            fixture_validation_harness_plan_path
        ).as_posix()
    }
    source_hashes = {key: _sha256(root / path) for key, path in source_paths.items()}
    required_source_statuses = {
        key: _status_for(root / path)
        for key, path in source_paths.items()
    }
    harness_plan = _read_json(root / fixture_validation_harness_plan_path)
    upstream_ready = (
        harness_plan.get("recommended_next_lane")
        == "ABX_CODEGEN_INTELLIGENCE_SPINE_SHADOW_REPLAY_HARNESS_IMPLEMENTATION_AUTHORIZATION_GATE"
    )
    sources_observed = all(status == "OBSERVED" for status in required_source_statuses.values())
    authorization_gate_status = (
        "SHADOW_REPLAY_HARNESS_IMPLEMENTATION_AUTHORIZATION_HELD_FOR_OPERATOR"
        if upstream_ready and sources_observed
        else "NOT_COMPUTABLE"
    )

    authority_locks = dict(AUTHORITY_LOCKS)
    authority_locks.update(
        {
            "authorization_record_creation": False,
            "harness_implementation": False,
            "operator_decision_attestation": False,
            "receipt_creation": False,
        }
    )
    blocked_actions = sorted(
        set(BLOCKED_ACTIONS)
        | {
            "authorization_record_creation",
            "harness_implementation",
            "operator_decision_attestation",
            "receipt_creation",
        }
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "gate_id": GATE_ID,
        "authorization_gate_status": authorization_gate_status,
        "target_surface": "ABX_CODEGEN_INTELLIGENCE_SPINE_001",
        "target_module": "core/codegen_shadow_replay_harness.py",
        "patch_id": (
            "PATCH-ABX-CODEGEN-SHADOW-REPLAY-HARNESS-IMPLEMENTATION-"
            "AUTHORIZATION-GATE-001"
        ),
        "source_paths": source_paths,
        "source_hashes": source_hashes,
        "required_source_statuses": required_source_statuses,
        "implementation_scope": {
            "phase": "PHASE_1_CORE_FOUNDATION",
            "planned_interfaces": [
                "run_codegen_shadow_replay",
                "_validate_proposal",
                "_build_replay_config",
                "_evaluate_proof_flags",
                "_determine_recommendation",
                "_build_receipt",
            ],
            "planned_output": "ShadowImprovementReceipt.v1",
            "requires_12_run_invariance": True,
            "requires_24_run_meta_gate_invariance": True,
            "requires_artifact_registry_registration_plan": True,
        },
        "authorization_findings": [
            {
                "finding_id": "implementation_spec_observed",
                "finding_status": "READY_FOR_OPERATOR_REVIEW",
                "summary": (
                    "Notion provides detailed Phase 1 harness interfaces, proof flags, "
                    "failure taxonomy, and testing strategy."
                ),
            },
            {
                "finding_id": "repo_authority_missing",
                "finding_status": "AUTHORIZATION_NOT_GRANTED",
                "summary": (
                    "Repo-visible advisory lanes deny harness implementation, receipt "
                    "creation, shadow replay execution, and self-authorization."
                ),
            },
            {
                "finding_id": "operator_decision_required",
                "finding_status": "HELD_FOR_OPERATOR",
                "summary": (
                    "A future human/operator decision record is required before creating "
                    "core/codegen_shadow_replay_harness.py."
                ),
            },
        ],
        "operator_review_required": True,
        "implementation_authorization_granted": False,
        "record_creation_authorized": False,
        "authority_locks": authority_locks,
        "blocked_actions": blocked_actions,
        "recommended_next_lane": (
            "ABX_CODEGEN_INTELLIGENCE_SPINE_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_PLAN"
        ),
        "recommended_next_action": (
            "plan the operator decision record requirements without creating a decision "
            "record or implementing the harness"
        ),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "harness_implementation_performed": False,
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_shadow_replay_harness_implementation_authorization_gate(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    write_canonical_json(path, packet)


def write_abx_codegen_shadow_replay_harness_implementation_authorization_gate_markdown(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    lines = [
        "# ABX Codegen Shadow Replay Harness Implementation Authorization Gate",
        "",
        f"- gate_id: {packet['gate_id']}",
        f"- authorization_gate_status: {packet['authorization_gate_status']}",
        f"- target_surface: {packet['target_surface']}",
        f"- target_module: {packet['target_module']}",
        f"- implementation_authorization_granted: {packet['implementation_authorization_granted']}",
        f"- record_creation_authorized: {packet['record_creation_authorized']}",
        f"- operator_review_required: {packet['operator_review_required']}",
        f"- harness_implementation_performed: {packet['harness_implementation_performed']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        "",
        "## Authorization Findings",
    ]
    for finding in packet.get("authorization_findings", []):
        if isinstance(finding, dict):
            lines.append(
                f"- {finding['finding_id']}: {finding['finding_status']} "
                f"({finding['summary']})"
            )
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- {action}")

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
