from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "V2HygieneVersioningReleasePolicyReadinessAudit.v1"
AUDIT_ID = "v2_hygiene_versioning_release_policy_readiness_audit_001"
OUT_JSON = Path("out/sync/v2_hygiene_versioning_release_policy_readiness_audit/latest.json")
OUT_MD = OUT_JSON.with_suffix(".md")
NOT_COMPUTABLE = "NOT_COMPUTABLE"

PHASE1_BACKLOG_PATH = "out/sync/v2_hygiene_phase1_foundation_backlog_plan/latest.json"
SCHEMA_READINESS_PATH = "out/sync/v2_hygiene_schema_contract_readiness_audit/latest.json"
AUTHORIZATION_HOLD_PATH = (
    "out/operator_review/v2_hygiene_phase1_authorization_chain_compression_audit_001.latest.json"
)

NOTION_POLICY_SOURCE = {
    "page_id": "37e3e8ba-2f5c-816d-a703-cabbdbf431fc",
    "title": "Versioning & Release Hygiene Policy",
    "source_observed_at": "2026-06-13T16:26:28Z",
    "source_hash": "fccb87d455f6af5c599682b374a9b9fe192d5f36246d8cbb4ea5fc45a7a2c071",
    "canon_status": "Governance / Policy Surface",
    "status": "ACTIVE_POLICY",
}

POLICY_REQUIREMENTS: tuple[dict[str, str], ...] = (
    {
        "requirement_id": "protect_1x_surfaces",
        "notion_rule": "Protect existing functionality first; no breaking changes to current rune contracts, YGGDRASIL routing, or output surfaces.",
        "repo_evidence_path": "contracts/runes/catalog.v1.json",
        "readiness_blocker": "v2 implementation remains held; no regression gate for v2 changes has been authorized",
    },
    {
        "requirement_id": "parallel_2x_capability",
        "notion_rule": "Treat the v2 hygiene layer as a parallel 2.x capability rather than modifying existing code paths.",
        "repo_evidence_path": "abraxas/v2/hygiene",
        "readiness_blocker": "parallel v2 package path is repo-missing and code creation remains denied",
    },
    {
        "requirement_id": "hygiene_mode_flag",
        "notion_rule": "All new v2 behavior must respect OFF / ADVISORY / STRICT mode through ABX_V2_HYGIENE_MODE or equivalent config.",
        "repo_evidence_path": "abraxas/v2/governance/mode.py",
        "readiness_blocker": "HygieneMode implementation and feature-flag wiring remain held",
    },
    {
        "requirement_id": "advisory_default",
        "notion_rule": "New v2 features default to ADVISORY mode; STRICT is only after promotion.",
        "repo_evidence_path": "tests/v2/hygiene",
        "readiness_blocker": "advisory-default tests are not present because v2 code/test creation is not authorized",
    },
    {
        "requirement_id": "explicit_version_fields",
        "notion_rule": "Every new object, rune, and module must carry explicit versioning.",
        "repo_evidence_path": "abraxas/v2/hygiene/contracts/v2_hygiene_rune_base.py",
        "readiness_blocker": "version-bearing base contract remains repo-missing and held",
    },
    {
        "requirement_id": "versioned_schema_files",
        "notion_rule": "Schema files should be versioned in the filename and new schema versions should not modify old versions in place.",
        "repo_evidence_path": "abraxas/v2/hygiene/contracts/schemas",
        "readiness_blocker": "versioned schema files remain repo-missing and schema creation is denied",
    },
    {
        "requirement_id": "ci_release_gates",
        "notion_rule": "All new v2 code must pass schema validation, unit coverage, advisory-default tests, 1.x regression tests, linting, and type checking before merge.",
        "repo_evidence_path": "scripts/run_fast_ci.py",
        "readiness_blocker": "repo has fast CI, but no authorized v2 implementation patch exists for policy-specific gates to validate",
    },
    {
        "requirement_id": "rollout_promotion_controls",
        "notion_rule": "Alpha requires feature flag plus ADVISORY mode; Beta requires operator approval and monitoring; Stable requires promotion review and documentation.",
        "repo_evidence_path": "out/operator_review/v2_hygiene_phase1_authorization_chain_compression_audit_001.latest.json",
        "readiness_blocker": "operator authorization hold remains active and promotion/default-on lanes are not computable",
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


def _policy_records(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for requirement in POLICY_REQUIREMENTS:
        observed = (root / requirement["repo_evidence_path"]).exists()
        records.append(
            {
                **requirement,
                "repo_observed": observed,
                "readiness_status": (
                    "POLICY_CONTROL_EVIDENCE_OBSERVED_HELD"
                    if observed
                    else "POLICY_CONTROL_REPO_MISSING_HELD"
                ),
                "authority_granted": False,
                "implementation_authorized": False,
                "release_authorized": False,
                "strict_mode_authorized": False,
            }
        )
    return records


def _authority_locks() -> dict[str, bool]:
    return {
        "activation": False,
        "auto_continuation": False,
        "auto_patch_generation": False,
        "canon_mutation": False,
        "execution_authority": False,
        "feature_flag_enablement": False,
        "github_writeback": False,
        "hygiene_code_creation": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_authorization_record_creation": False,
        "promotion": False,
        "queue_mutation": False,
        "release_authorization": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_file_creation": False,
        "schema_mutation": False,
        "strict_mode_enablement": False,
        "v2_module_registration": False,
    }


def build_v2_hygiene_versioning_release_policy_readiness_audit(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    backlog = _read_json(root / PHASE1_BACKLOG_PATH)
    schema_readiness = _read_json(root / SCHEMA_READINESS_PATH)
    hold = _read_json(root / AUTHORIZATION_HOLD_PATH)
    policy_in_backlog = any(
        isinstance(source, Mapping)
        and source.get("page_id") == NOTION_POLICY_SOURCE["page_id"]
        and source.get("status") == "ACTIVE_POLICY"
        for source in backlog.get("notion_phase1_sources", [])
    )
    source_ready = (
        backlog.get("status") == "V2_HYGIENE_PHASE1_FOUNDATION_BACKLOG_PLAN_READY"
        and policy_in_backlog
        and schema_readiness.get("status")
        == "V2_HYGIENE_SCHEMA_CONTRACT_READINESS_AUDIT_HELD_FOR_OPERATOR"
        and schema_readiness.get("valid_for_implementation") is False
        and hold.get("status")
        == "V2_HYGIENE_PHASE1_AUTHORIZATION_CHAIN_COMPRESSION_AUDIT_HELD_FOR_OPERATOR"
        and hold.get("valid_for_implementation") is False
        and hold.get("safe_to_auto_continue") is False
    )
    records = _policy_records(root)
    missing = [
        record["requirement_id"]
        for record in records
        if record["readiness_status"] == "POLICY_CONTROL_REPO_MISSING_HELD"
    ]
    observed = [record["requirement_id"] for record in records if record["repo_observed"]]
    findings = [
        {
            "finding_id": "notion_versioning_policy_source_observed",
            "finding_status": "PASS" if policy_in_backlog else "FAIL_CLOSED",
            "authority_granted": False,
        },
        {
            "finding_id": "phase1_backlog_ready",
            "finding_status": "PASS" if backlog else "FAIL_CLOSED",
            "authority_granted": False,
        },
        {
            "finding_id": "schema_contract_readiness_held",
            "finding_status": "PASS" if schema_readiness else "FAIL_CLOSED",
            "authority_granted": False,
        },
        {
            "finding_id": "phase1_authorization_hold_active",
            "finding_status": "PASS" if hold else "FAIL_CLOSED",
            "authority_granted": False,
        },
        {
            "finding_id": "versioning_policy_controls_not_implementation_ready",
            "finding_status": "HELD_FOR_OPERATOR",
            "authority_granted": False,
        },
        {
            "finding_id": "release_and_strict_mode_denied",
            "finding_status": "ENFORCED",
            "authority_granted": False,
        },
    ]
    base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "audit_id": AUDIT_ID,
        "status": (
            "V2_HYGIENE_VERSIONING_RELEASE_POLICY_READINESS_AUDIT_HELD_FOR_OPERATOR"
            if source_ready
            else NOT_COMPUTABLE
        ),
        "notion_versioning_policy_source": NOTION_POLICY_SOURCE,
        "source_paths": {
            "phase1_backlog": PHASE1_BACKLOG_PATH,
            "schema_contract_readiness": SCHEMA_READINESS_PATH,
            "authorization_hold": AUTHORIZATION_HOLD_PATH,
        },
        "source_hashes": {
            PHASE1_BACKLOG_PATH: _source_hash(root / PHASE1_BACKLOG_PATH),
            SCHEMA_READINESS_PATH: _source_hash(root / SCHEMA_READINESS_PATH),
            AUTHORIZATION_HOLD_PATH: _source_hash(root / AUTHORIZATION_HOLD_PATH),
        },
        "source_ready": source_ready,
        "policy_records": records,
        "policy_summary": {
            "expected_policy_control_count": len(records),
            "repo_observed_control_count": len(observed),
            "missing_or_held_control_count": len(missing),
            "repo_observed_requirement_ids": observed,
            "missing_or_held_requirement_ids": missing,
        },
        "readiness_findings": findings,
        "recommended_next_action": (
            "keep the Notion versioning and release hygiene policy as a "
            "repo-visible readiness audit until explicit external operator "
            "authorization permits a separate v2 implementation lane"
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
        "feature_flag_enablement_authorized": False,
        "release_authorized": False,
        "promotion_authorized": False,
        "schema_file_creation_authorized": False,
        "schema_mutation_authorized": False,
        "implementation_authorized": False,
        "hygiene_code_creation_authorized": False,
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


def render_v2_hygiene_versioning_release_policy_readiness_audit_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Versioning Release Policy Readiness Audit",
        "",
        f"- audit_id: {packet['audit_id']}",
        f"- status: {packet['status']}",
        f"- source_ready: {packet['source_ready']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        "",
        "## Policy Summary",
    ]
    summary = packet["policy_summary"]
    for key in (
        "expected_policy_control_count",
        "repo_observed_control_count",
        "missing_or_held_control_count",
    ):
        lines.append(f"- {key}: {summary[key]}")
    lines.extend(["", "## Policy Records"])
    for record in packet["policy_records"]:
        lines.append(
            f"- {record['requirement_id']}: {record['readiness_status']} "
            f"(repo_observed={record['repo_observed']})"
        )
    return lines


def write_v2_hygiene_versioning_release_policy_readiness_audit(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_versioning_release_policy_readiness_audit(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / OUT_JSON, packet)
    md_path = root / OUT_MD
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_versioning_release_policy_readiness_audit_markdown(packet)
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
