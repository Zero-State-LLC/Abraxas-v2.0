from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "V2HygieneSchemaContractReadinessAudit.v1"
AUDIT_ID = "v2_hygiene_schema_contract_readiness_audit_001"
OUT_JSON = Path("out/sync/v2_hygiene_schema_contract_readiness_audit/latest.json")
OUT_MD = OUT_JSON.with_suffix(".md")
NOT_COMPUTABLE = "NOT_COMPUTABLE"

PHASE1_BACKLOG_PATH = "out/sync/v2_hygiene_phase1_foundation_backlog_plan/latest.json"
AUTHORIZATION_HOLD_PATH = (
    "out/operator_review/v2_hygiene_phase1_authorization_chain_compression_audit_001.latest.json"
)

NOTION_SCHEMA_CONTRACT_SOURCE = {
    "page_id": "37e3e8ba-2f5c-8136-9cec-c0482fd71a8e",
    "title": "v2.0 Schema Contracts",
    "source_observed_at": "2026-06-13T16:27:39Z",
    "canon_status": "Technical Reference Surface",
}

EXPECTED_CONTRACTS: tuple[dict[str, str], ...] = (
    {
        "contract_id": "loop_dynamics",
        "notion_status": "DEFINED",
        "repo_path": "abraxas/v2/hygiene/contracts/schemas/loop_dynamics.v1.json",
        "required_fields": "retrocausal_risk, hyperstitional_charge, mitigation, version",
    },
    {
        "contract_id": "v2_output",
        "notion_status": "DEFINED",
        "repo_path": "abraxas/v2/hygiene/contracts/schemas/v2_output.v1.json",
        "required_fields": "observed, inferred, speculative, loop_dynamics, provenance, version",
    },
    {
        "contract_id": "v2_hygiene_rune_base",
        "notion_status": "DEFINED",
        "repo_path": "abraxas/v2/hygiene/contracts/v2_hygiene_rune_base.py",
        "required_fields": "version, owner_module, apply(content, context)",
    },
    {
        "contract_id": "hygiene_mode",
        "notion_status": "DEFINED",
        "repo_path": "abraxas/v2/governance/mode.py",
        "required_fields": "OFF, ADVISORY, STRICT",
    },
    {
        "contract_id": "individual_hygiene_rune_contracts",
        "notion_status": "TO_BE_DEFINED",
        "repo_path": "abraxas/v2/hygiene/runes",
        "required_fields": "LOOP_AWARENESS, HYPERSTITION_TAG, PROVENANCE_ENFORCE, ADVERSARIAL_AUDIT, OUTPUT_REGISTER_ENFORCE",
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


def _contract_records(repo_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for contract in EXPECTED_CONTRACTS:
        repo_path = contract["repo_path"]
        observed = (repo_root / repo_path).exists()
        records.append(
            {
                **contract,
                "repo_observed": observed,
                "readiness_status": (
                    "REPO_CONTRACT_OBSERVED_HELD_FOR_AUTHORIZATION"
                    if observed
                    else "NOTION_CONTRACT_DEFINED_REPO_CONTRACT_MISSING_HELD"
                ),
                "schema_file_creation_authorized": False,
                "implementation_authorized": False,
                "authority_granted": False,
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
        "v2_module_registration": False,
    }


def build_v2_hygiene_schema_contract_readiness_audit(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    backlog = _read_json(root / PHASE1_BACKLOG_PATH)
    hold = _read_json(root / AUTHORIZATION_HOLD_PATH)
    source_ready = (
        backlog.get("status") == "V2_HYGIENE_PHASE1_FOUNDATION_BACKLOG_PLAN_READY"
        and isinstance(backlog.get("authority_locks"), Mapping)
        and backlog["authority_locks"].get("schema_file_creation") is False
        and backlog.get("valid_for_implementation") is False
        and hold.get("status")
        == "V2_HYGIENE_PHASE1_AUTHORIZATION_CHAIN_COMPRESSION_AUDIT_HELD_FOR_OPERATOR"
        and hold.get("valid_for_implementation") is False
        and hold.get("safe_to_auto_continue") is False
    )
    records = _contract_records(root)
    missing = [record["contract_id"] for record in records if not record["repo_observed"]]
    findings = [
        {
            "finding_id": "notion_schema_contract_source_observed",
            "finding_status": "OBSERVED",
            "authority_granted": False,
        },
        {
            "finding_id": "phase1_backlog_ready",
            "finding_status": "PASS" if backlog else "FAIL_CLOSED",
            "authority_granted": False,
        },
        {
            "finding_id": "phase1_authorization_hold_active",
            "finding_status": "PASS" if hold else "FAIL_CLOSED",
            "authority_granted": False,
        },
        {
            "finding_id": "repo_schema_contracts_missing",
            "finding_status": "OBSERVED" if missing else "NOT_OBSERVED",
            "authority_granted": False,
        },
        {
            "finding_id": "schema_creation_denied",
            "finding_status": "ENFORCED",
            "authority_granted": False,
        },
    ]
    base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "audit_id": AUDIT_ID,
        "status": (
            "V2_HYGIENE_SCHEMA_CONTRACT_READINESS_AUDIT_HELD_FOR_OPERATOR"
            if source_ready
            else NOT_COMPUTABLE
        ),
        "notion_schema_contract_source": {
            **NOTION_SCHEMA_CONTRACT_SOURCE,
            "source_hash": canonical_hash(NOTION_SCHEMA_CONTRACT_SOURCE),
        },
        "source_paths": {
            "phase1_backlog": PHASE1_BACKLOG_PATH,
            "authorization_hold": AUTHORIZATION_HOLD_PATH,
        },
        "source_hashes": {
            PHASE1_BACKLOG_PATH: _source_hash(root / PHASE1_BACKLOG_PATH),
            AUTHORIZATION_HOLD_PATH: _source_hash(root / AUTHORIZATION_HOLD_PATH),
        },
        "source_ready": source_ready,
        "contract_records": records,
        "contract_summary": {
            "expected_contract_count": len(records),
            "repo_observed_count": sum(1 for record in records if record["repo_observed"]),
            "missing_contract_count": len(missing),
            "missing_contract_ids": missing,
        },
        "readiness_findings": findings,
        "recommended_next_action": (
            "keep v2 hygiene schema contracts as Notion-defined, repo-missing work "
            "until explicit external operator authorization permits a separate "
            "schema-contract implementation lane"
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


def render_v2_hygiene_schema_contract_readiness_audit_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Schema Contract Readiness Audit",
        "",
        f"- audit_id: {packet['audit_id']}",
        f"- status: {packet['status']}",
        f"- source_ready: {packet['source_ready']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        "",
        "## Contract Summary",
    ]
    summary = packet["contract_summary"]
    for key in (
        "expected_contract_count",
        "repo_observed_count",
        "missing_contract_count",
    ):
        lines.append(f"- {key}: {summary[key]}")
    lines.extend(["", "## Contract Records"])
    for record in packet["contract_records"]:
        lines.append(
            f"- {record['contract_id']}: {record['readiness_status']} "
            f"(repo_observed={record['repo_observed']})"
        )
    return lines


def write_v2_hygiene_schema_contract_readiness_audit(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_schema_contract_readiness_audit(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / OUT_JSON, packet)
    md_path = root / OUT_MD
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(render_v2_hygiene_schema_contract_readiness_audit_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
    return packet
