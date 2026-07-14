from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygienePhase1AcceptanceChecklistReadinessAudit.v1"
AUDIT_ID = "v2_hygiene_phase1_acceptance_checklist_readiness_audit_001"
OUT_JSON = Path(
    "out/sync/v2_hygiene_phase1_acceptance_checklist_readiness_audit/latest.json"
)
OUT_MD = OUT_JSON.with_suffix(".md")

PHASE1_BACKLOG_PATH = "out/sync/v2_hygiene_phase1_foundation_backlog_plan/latest.json"
SCHEMA_READINESS_PATH = "out/sync/v2_hygiene_schema_contract_readiness_audit/latest.json"
VERSIONING_POLICY_PATH = (
    "out/sync/v2_hygiene_versioning_release_policy_readiness_audit/latest.json"
)
AUTHORIZATION_HOLD_PATH = (
    "out/operator_review/v2_hygiene_phase1_authorization_chain_compression_audit_001.latest.json"
)

NOTION_CHECKLIST_SOURCE = {
    "page_id": "56a5b080-8f17-4392-af50-55d19c174cc0",
    "title": "Phase 1 - Implementation Checklist",
    "source_observed_at": "2026-06-13T16:34:45Z",
    "source_hash": "68aed8065c86f7e42f316e1f00d8eac9bfb92de889a7de3d43beb9acb9d15cbd",
    "status": "TASKS_TO_DO",
}

ACCEPTANCE_GATES: tuple[dict[str, str], ...] = (
    {
        "gate_id": "phase1_acceptance_001",
        "task_id": "phase1_p0_001",
        "priority": "P0",
        "task": "Set up folder structure",
        "definition_of_done": "Folder tree exists under abraxas/v2/hygiene with runes, contracts, contracts/schemas, governance, and import init files where needed.",
        "repo_path": "abraxas/v2/hygiene",
    },
    {
        "gate_id": "phase1_acceptance_002",
        "task_id": "phase1_p0_002",
        "priority": "P0",
        "task": "Implement LoopDynamics",
        "definition_of_done": "LoopDynamics dataclass has to_dict, validation, sane defaults, and unit coverage.",
        "repo_path": "abraxas/v2/hygiene/loop_dynamics.py",
    },
    {
        "gate_id": "phase1_acceptance_003",
        "task_id": "phase1_p0_003",
        "priority": "P0",
        "task": "Implement V2Output",
        "definition_of_done": "V2Output dataclass has is_valid, optional loop_dynamics and provenance fields, and unit coverage.",
        "repo_path": "abraxas/v2/hygiene/registers.py",
    },
    {
        "gate_id": "phase1_acceptance_004",
        "task_id": "phase1_p0_004",
        "priority": "P0",
        "task": "Create V2HygieneRune base class",
        "definition_of_done": "Abstract base class has apply contract, mode support, and documented non-breaking ADVISORY behavior.",
        "repo_path": "abraxas/v2/hygiene/contracts/v2_hygiene_rune_base.py",
    },
    {
        "gate_id": "phase1_acceptance_005",
        "task_id": "phase1_p0_005",
        "priority": "P0",
        "task": "Implement HygieneMode system",
        "definition_of_done": "HygieneMode enum has OFF, ADVISORY, STRICT, defaults to ADVISORY, and supports ABX_V2_HYGIENE_MODE or equivalent config.",
        "repo_path": "abraxas/v2/governance/mode.py",
    },
    {
        "gate_id": "phase1_acceptance_006",
        "task_id": "phase1_p0_006",
        "priority": "P0",
        "task": "Implement LoopAwarenessRune",
        "definition_of_done": "LoopAwarenessRune imports cleanly and covers OFF, ADVISORY metadata with loop_dynamics, and defined STRICT behavior.",
        "repo_path": "abraxas/v2/hygiene/runes/loop_awareness.py",
    },
    {
        "gate_id": "phase1_acceptance_007",
        "task_id": "phase1_p1_007",
        "priority": "P1",
        "task": "Implement ProvenanceEnforceRune",
        "definition_of_done": "Provenance rune attaches metadata without altering primary content in ADVISORY mode and covers OFF plus ADVISORY tests.",
        "repo_path": "abraxas/v2/hygiene/runes/provenance_enforce.py",
    },
    {
        "gate_id": "phase1_acceptance_008",
        "task_id": "phase1_p1_008",
        "priority": "P1",
        "task": "Add JSON schema validation",
        "definition_of_done": "Helpers load versioned schemas, validate payloads, return actionable errors, and cover pass/fail tests.",
        "repo_path": "abraxas/v2/hygiene/contracts/schema_validator.py",
    },
    {
        "gate_id": "phase1_acceptance_009",
        "task_id": "phase1_p1_009",
        "priority": "P1",
        "task": "Write unit tests for core objects",
        "definition_of_done": "Tests under tests/v2/hygiene cover LoopDynamics, V2Output, base rune behavior, ADVISORY assumptions, and 1.x regressions where present.",
        "repo_path": "tests/v2/hygiene",
    },
    {
        "gate_id": "phase1_acceptance_010",
        "task_id": "phase1_p1_010",
        "priority": "P1",
        "task": "Implement remaining 3 runes",
        "definition_of_done": "HyperstitionTag, AdversarialAudit, and OutputRegisterEnforce each have files, tests, ADVISORY-safe defaults, and explicit STRICT behavior.",
        "repo_path": "abraxas/v2/hygiene/runes",
    },
    {
        "gate_id": "phase1_acceptance_011",
        "task_id": "phase1_p2_011",
        "priority": "P2",
        "task": "Add advisory integration hook",
        "definition_of_done": "Integration point is optional, feature-flagged, defaults OFF or ADVISORY, preserves existing 1.x outputs unless enabled, and has a test or example.",
        "repo_path": "abraxas/v2/hygiene/pipeline.py",
    },
    {
        "gate_id": "phase1_acceptance_012",
        "task_id": "phase1_p2_012",
        "priority": "P2",
        "task": "Create schema files",
        "definition_of_done": "Versioned JSON schemas exist under contracts/schemas and filenames plus version fields follow the policy.",
        "repo_path": "abraxas/v2/hygiene/contracts/schemas",
    },
    {
        "gate_id": "phase1_acceptance_013",
        "task_id": "phase1_p2_013",
        "priority": "P2",
        "task": "Documentation and examples",
        "definition_of_done": "Core classes and runes have docstrings and at least one minimal usage example or README/docs section exists.",
        "repo_path": "examples/v2_hygiene_integration.py",
    },
    {
        "gate_id": "phase1_acceptance_014",
        "task_id": "phase1_p2_014",
        "priority": "P2",
        "task": "Final review and cleanup",
        "definition_of_done": "All v2 objects/runes carry version fields, default mode remains ADVISORY, and CI gates from release policy are met.",
        "repo_path": "out/operator_review/v2_hygiene_phase1_final_review_001.latest.json",
    },
)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _source_hash(path: Path) -> str:
    value = _read_json(path)
    return canonical_hash(value) if value else NOT_COMPUTABLE


def _authority_locks() -> dict[str, bool]:
    return {
        "activation": False,
        "advisory_integration_hook_authorized": False,
        "auto_continuation": False,
        "auto_patch_generation": False,
        "canon_mutation": False,
        "checklist_completion_attestation": False,
        "execution_authority": False,
        "github_writeback": False,
        "hygiene_code_creation": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_authorization_record_creation": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_file_creation": False,
        "schema_mutation": False,
        "strict_mode_enablement": False,
        "test_file_creation": False,
        "v2_module_registration": False,
    }


def _acceptance_records(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for gate in ACCEPTANCE_GATES:
        repo_observed = (root / gate["repo_path"]).exists()
        records.append(
            {
                **gate,
                "repo_observed": repo_observed,
                "checklist_status": (
                    "REPO_EVIDENCE_OBSERVED_HELD_FOR_OPERATOR"
                    if repo_observed
                    else "NOTION_CHECKLIST_TO_DO_REPO_MISSING_HELD"
                ),
                "implementation_authorized": False,
                "checklist_completion_attested": False,
                "authority_granted": False,
            }
        )
    return records


def build_v2_hygiene_phase1_acceptance_checklist_readiness_audit(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    backlog = _read_json(root / PHASE1_BACKLOG_PATH)
    schema_readiness = _read_json(root / SCHEMA_READINESS_PATH)
    versioning_policy = _read_json(root / VERSIONING_POLICY_PATH)
    hold = _read_json(root / AUTHORIZATION_HOLD_PATH)
    checklist_in_backlog = any(
        isinstance(source, Mapping)
        and source.get("page_id") == NOTION_CHECKLIST_SOURCE["page_id"]
        and source.get("status") == "TASKS_TO_DO"
        for source in backlog.get("notion_phase1_sources", [])
    )
    source_ready = (
        backlog.get("status") == "V2_HYGIENE_PHASE1_FOUNDATION_BACKLOG_PLAN_READY"
        and checklist_in_backlog
        and schema_readiness.get("status")
        == "V2_HYGIENE_SCHEMA_CONTRACT_READINESS_AUDIT_HELD_FOR_OPERATOR"
        and versioning_policy.get("status")
        == "V2_HYGIENE_VERSIONING_RELEASE_POLICY_READINESS_AUDIT_HELD_FOR_OPERATOR"
        and hold.get("status")
        == "V2_HYGIENE_PHASE1_AUTHORIZATION_CHAIN_COMPRESSION_AUDIT_HELD_FOR_OPERATOR"
        and hold.get("valid_for_implementation") is False
        and hold.get("safe_to_auto_continue") is False
    )
    records = _acceptance_records(root)
    missing = [record["gate_id"] for record in records if not record["repo_observed"]]
    p0_missing = [
        record["gate_id"]
        for record in records
        if record["priority"] == "P0" and not record["repo_observed"]
    ]
    findings = [
        {
            "finding_id": "notion_phase1_checklist_source_observed",
            "finding_status": "PASS" if checklist_in_backlog else "FAIL_CLOSED",
            "authority_granted": False,
        },
        {
            "finding_id": "phase1_backlog_ready",
            "finding_status": "PASS" if backlog else "FAIL_CLOSED",
            "authority_granted": False,
        },
        {
            "finding_id": "schema_and_policy_readiness_held",
            "finding_status": "PASS" if schema_readiness and versioning_policy else "FAIL_CLOSED",
            "authority_granted": False,
        },
        {
            "finding_id": "p0_acceptance_gates_missing",
            "finding_status": "HELD_FOR_OPERATOR" if p0_missing else "NOT_OBSERVED",
            "authority_granted": False,
        },
        {
            "finding_id": "checklist_completion_attestation_denied",
            "finding_status": "ENFORCED",
            "authority_granted": False,
        },
        {
            "finding_id": "implementation_and_execution_denied",
            "finding_status": "ENFORCED",
            "authority_granted": False,
        },
    ]
    base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "audit_id": AUDIT_ID,
        "status": (
            "V2_HYGIENE_PHASE1_ACCEPTANCE_CHECKLIST_READINESS_AUDIT_HELD_FOR_OPERATOR"
            if source_ready
            else NOT_COMPUTABLE
        ),
        "notion_checklist_source": NOTION_CHECKLIST_SOURCE,
        "source_paths": {
            "phase1_backlog": PHASE1_BACKLOG_PATH,
            "schema_contract_readiness": SCHEMA_READINESS_PATH,
            "versioning_release_policy_readiness": VERSIONING_POLICY_PATH,
            "authorization_hold": AUTHORIZATION_HOLD_PATH,
        },
        "source_hashes": {
            PHASE1_BACKLOG_PATH: _source_hash(root / PHASE1_BACKLOG_PATH),
            SCHEMA_READINESS_PATH: _source_hash(root / SCHEMA_READINESS_PATH),
            VERSIONING_POLICY_PATH: _source_hash(root / VERSIONING_POLICY_PATH),
            AUTHORIZATION_HOLD_PATH: _source_hash(root / AUTHORIZATION_HOLD_PATH),
        },
        "source_ready": source_ready,
        "acceptance_records": records,
        "acceptance_summary": {
            "total_gate_count": len(records),
            "repo_observed_gate_count": sum(1 for record in records if record["repo_observed"]),
            "missing_gate_count": len(missing),
            "p0_gate_count": sum(1 for record in records if record["priority"] == "P0"),
            "p0_missing_gate_count": len(p0_missing),
            "missing_gate_ids": missing,
            "p0_missing_gate_ids": p0_missing,
        },
        "recommended_execution_order": [
            "complete P0 foundation tasks before P1/P2",
            "add tests early rather than at final review",
            "implement runes in LoopAwareness, ProvenanceEnforce, remaining-three order",
            "keep all development assumptions in ADVISORY mode by default",
        ],
        "readiness_findings": findings,
        "recommended_next_action": (
            "keep the Phase 1 implementation checklist as an acceptance-gate "
            "readiness audit until explicit external operator authorization "
            "permits a separate v2 implementation lane"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "operator_review_required": True,
        "operator_input_required": True,
        "operator_attestation_created": False,
        "authorization_record_created": False,
        "checklist_completion_attested": False,
        "schema_file_creation_authorized": False,
        "schema_mutation_authorized": False,
        "test_file_creation_authorized": False,
        "implementation_authorized": False,
        "hygiene_code_creation_authorized": False,
        "advisory_integration_hook_authorized": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "strict_mode_enablement_authorized": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_patch": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "authority_locks": _authority_locks(),
    }
    return {**base, "audit_hash": canonical_hash(base)}


def render_v2_hygiene_phase1_acceptance_checklist_readiness_audit_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Phase 1 Acceptance Checklist Readiness Audit",
        "",
        f"- audit_id: {packet['audit_id']}",
        f"- status: {packet['status']}",
        f"- source_ready: {packet['source_ready']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        "",
        "## Acceptance Summary",
    ]
    summary = packet["acceptance_summary"]
    for key in (
        "total_gate_count",
        "repo_observed_gate_count",
        "missing_gate_count",
        "p0_missing_gate_count",
    ):
        lines.append(f"- {key}: {summary[key]}")
    lines.extend(["", "## Acceptance Gates"])
    for record in packet["acceptance_records"]:
        lines.append(
            f"- {record['gate_id']} {record['task']}: {record['checklist_status']} "
            f"(repo_observed={record['repo_observed']})"
        )
    return lines


def write_v2_hygiene_phase1_acceptance_checklist_readiness_audit(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_acceptance_checklist_readiness_audit(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / OUT_JSON, packet)
    md_path = root / OUT_MD
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_acceptance_checklist_readiness_audit_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
