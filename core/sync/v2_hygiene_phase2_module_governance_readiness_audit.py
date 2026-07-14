from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygienePhase2ModuleGovernanceReadinessAudit.v1"
AUDIT_ID = "v2_hygiene_phase2_module_governance_readiness_audit_001"
OUT_JSON = Path("out/sync/v2_hygiene_phase2_module_governance_readiness_audit/latest.json")
OUT_MD = OUT_JSON.with_suffix(".md")

PHASE2_BACKLOG_PATH = "out/sync/v2_hygiene_phase2_module_skeleton_backlog_plan/latest.json"
PHASE1_CHECKLIST_PATH = (
    "out/sync/v2_hygiene_phase1_acceptance_checklist_readiness_audit/latest.json"
)
VERSIONING_POLICY_PATH = (
    "out/sync/v2_hygiene_versioning_release_policy_readiness_audit/latest.json"
)
AUTHORIZATION_HOLD_PATH = (
    "out/operator_review/v2_hygiene_phase1_authorization_chain_compression_audit_001.latest.json"
)

NOTION_PHASE2_SOURCE = {
    "page_id": "37e3e8ba-2f5c-8100-8c1e-fff304c1f8d9",
    "title": "Phase 2: Module Skeletons & Governance Hooks",
    "source_observed_at": "2026-06-13T16:43:43Z",
    "source_hash": "4f328ec88fe280b06c048baec8afc139699cd47d45f7e178345462043d2ad28d",
    "status": "READY_FOR_ADVISORY_BACKLOG",
}

GOVERNANCE_REQUIREMENTS: tuple[dict[str, str], ...] = (
    {
        "requirement_id": "default_advisory_mode",
        "notion_rule": "Default mode = ADVISORY.",
        "repo_evidence_path": "abraxas/v2/modules",
        "readiness_blocker": "module skeletons are repo-missing and default mode cannot be attested",
    },
    {
        "requirement_id": "no_output_mutation_without_configuration",
        "notion_rule": "Modules must not mutate outputs unless explicitly configured.",
        "repo_evidence_path": "abraxas/v2/modules/*/module.py",
        "readiness_blocker": "module process/evaluate methods are repo-missing and non-mutation behavior cannot be tested",
    },
    {
        "requirement_id": "metadata_version_owner_posture",
        "notion_rule": "Modules must expose version, owner_runes, and posture.",
        "repo_evidence_path": "abraxas/v2/modules/*/config.py",
        "readiness_blocker": "module configuration metadata is repo-missing",
    },
    {
        "requirement_id": "hygiene_pipeline_interaction",
        "notion_rule": "Modules should establish how they interact with the HygienePipeline from Phase 1.",
        "repo_evidence_path": "abraxas/v2/modules/*/module.py",
        "readiness_blocker": "HygienePipeline integration remains held and module files are repo-missing",
    },
    {
        "requirement_id": "promotion_governance_review",
        "notion_rule": "Promotion from advisory to limited to full requires explicit governance review.",
        "repo_evidence_path": "docs/v2_hygiene/module_promotion_criteria.md",
        "readiness_blocker": "promotion criteria documentation is repo-missing and promotion remains denied",
    },
    {
        "requirement_id": "module_boundary_tests",
        "notion_rule": "Basic tests should ensure module skeletons respect mode and authority boundaries.",
        "repo_evidence_path": "tests/v2/modules",
        "readiness_blocker": "module boundary tests are repo-missing because module/test creation is not authorized",
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
        "auto_continuation": False,
        "auto_patch_generation": False,
        "canon_mutation": False,
        "execution_authority": False,
        "github_writeback": False,
        "hygiene_pipeline_integration": False,
        "implementation_authorization": False,
        "module_code_creation": False,
        "module_registration": False,
        "module_test_creation": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_authorization_record_creation": False,
        "promotion": False,
        "queue_mutation": False,
        "rune_binding_mutation": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_mutation": False,
        "strict_mode_enablement": False,
        "v2_module_registration": False,
    }


def _repo_path_observed(root: Path, repo_path: str) -> bool:
    if "*" not in repo_path:
        return (root / repo_path).exists()
    prefix, _, suffix = repo_path.partition("*")
    base = root / prefix.rstrip("/")
    if not base.exists():
        return False
    suffix_path = suffix.lstrip("/")
    return any(
        (candidate / suffix_path).exists()
        for candidate in sorted(base.iterdir())
        if candidate.is_dir()
    )


def _governance_records(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for requirement in GOVERNANCE_REQUIREMENTS:
        repo_observed = _repo_path_observed(root, requirement["repo_evidence_path"])
        records.append(
            {
                **requirement,
                "repo_observed": repo_observed,
                "readiness_status": (
                    "GOVERNANCE_CONTROL_EVIDENCE_OBSERVED_HELD"
                    if repo_observed
                    else "GOVERNANCE_CONTROL_REPO_MISSING_HELD"
                ),
                "implementation_authorized": False,
                "promotion_authorized": False,
                "authority_granted": False,
            }
        )
    return records


def build_v2_hygiene_phase2_module_governance_readiness_audit(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    phase2 = _read_json(root / PHASE2_BACKLOG_PATH)
    checklist = _read_json(root / PHASE1_CHECKLIST_PATH)
    policy = _read_json(root / VERSIONING_POLICY_PATH)
    hold = _read_json(root / AUTHORIZATION_HOLD_PATH)
    source_ready = (
        phase2.get("status") == "V2_HYGIENE_PHASE2_MODULE_SKELETON_BACKLOG_PLAN_READY"
        and phase2.get("valid_for_implementation") is False
        and checklist.get("status")
        == "V2_HYGIENE_PHASE1_ACCEPTANCE_CHECKLIST_READINESS_AUDIT_HELD_FOR_OPERATOR"
        and checklist.get("valid_for_implementation") is False
        and policy.get("status")
        == "V2_HYGIENE_VERSIONING_RELEASE_POLICY_READINESS_AUDIT_HELD_FOR_OPERATOR"
        and policy.get("valid_for_implementation") is False
        and hold.get("status")
        == "V2_HYGIENE_PHASE1_AUTHORIZATION_CHAIN_COMPRESSION_AUDIT_HELD_FOR_OPERATOR"
        and hold.get("safe_to_auto_continue") is False
    )
    records = _governance_records(root)
    missing = [record["requirement_id"] for record in records if not record["repo_observed"]]
    findings = [
        {
            "finding_id": "phase2_notion_source_observed",
            "finding_status": "OBSERVED",
            "authority_granted": False,
        },
        {
            "finding_id": "phase2_backlog_ready",
            "finding_status": "PASS" if phase2 else "FAIL_CLOSED",
            "authority_granted": False,
        },
        {
            "finding_id": "phase1_acceptance_still_held",
            "finding_status": "PASS" if checklist else "FAIL_CLOSED",
            "authority_granted": False,
        },
        {
            "finding_id": "module_governance_controls_missing",
            "finding_status": "HELD_FOR_OPERATOR" if missing else "NOT_OBSERVED",
            "authority_granted": False,
        },
        {
            "finding_id": "promotion_and_execution_denied",
            "finding_status": "ENFORCED",
            "authority_granted": False,
        },
    ]
    base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "audit_id": AUDIT_ID,
        "status": (
            "V2_HYGIENE_PHASE2_MODULE_GOVERNANCE_READINESS_AUDIT_HELD_FOR_OPERATOR"
            if source_ready
            else NOT_COMPUTABLE
        ),
        "notion_phase2_source": NOTION_PHASE2_SOURCE,
        "source_paths": {
            "phase2_backlog": PHASE2_BACKLOG_PATH,
            "phase1_acceptance_checklist": PHASE1_CHECKLIST_PATH,
            "versioning_policy": VERSIONING_POLICY_PATH,
            "authorization_hold": AUTHORIZATION_HOLD_PATH,
        },
        "source_hashes": {
            PHASE2_BACKLOG_PATH: _source_hash(root / PHASE2_BACKLOG_PATH),
            PHASE1_CHECKLIST_PATH: _source_hash(root / PHASE1_CHECKLIST_PATH),
            VERSIONING_POLICY_PATH: _source_hash(root / VERSIONING_POLICY_PATH),
            AUTHORIZATION_HOLD_PATH: _source_hash(root / AUTHORIZATION_HOLD_PATH),
        },
        "source_ready": source_ready,
        "governance_records": records,
        "governance_summary": {
            "expected_governance_control_count": len(records),
            "repo_observed_control_count": sum(1 for record in records if record["repo_observed"]),
            "missing_control_count": len(missing),
            "missing_requirement_ids": missing,
        },
        "readiness_findings": findings,
        "recommended_next_action": (
            "keep Phase 2 module governance as a readiness audit until explicit "
            "external operator authorization permits module skeleton implementation"
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
        "module_code_creation_authorized": False,
        "module_test_creation_authorized": False,
        "module_registration_authorized": False,
        "hygiene_pipeline_integration_authorized": False,
        "promotion_authorized": False,
        "implementation_authorized": False,
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


def render_v2_hygiene_phase2_module_governance_readiness_audit_markdown(
    packet: dict[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Phase 2 Module Governance Readiness Audit",
        "",
        f"- audit_id: {packet['audit_id']}",
        f"- status: {packet['status']}",
        f"- source_ready: {packet['source_ready']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        "",
        "## Governance Summary",
    ]
    summary = packet["governance_summary"]
    for key in (
        "expected_governance_control_count",
        "repo_observed_control_count",
        "missing_control_count",
    ):
        lines.append(f"- {key}: {summary[key]}")
    lines.extend(["", "## Governance Controls"])
    for record in packet["governance_records"]:
        lines.append(
            f"- {record['requirement_id']}: {record['readiness_status']} "
            f"(repo_observed={record['repo_observed']})"
        )
    return lines


def write_v2_hygiene_phase2_module_governance_readiness_audit(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase2_module_governance_readiness_audit(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / OUT_JSON, packet)
    md_path = root / OUT_MD
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(render_v2_hygiene_phase2_module_governance_readiness_audit_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
    return packet
