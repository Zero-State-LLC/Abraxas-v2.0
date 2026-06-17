from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_advisory_spec_plan import (
    AUTHORITY_LOCKS,
    BLOCKED_ACTIONS,
    NOTION_SPEC_STACK,
)
from core.abx_codegen_intelligence_spine_packet_validation_receipt import (
    EXPECTED_NEGATIVE_RULES,
    EXPECTED_VALID_FIXTURES,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineNotionStackAlignmentAudit.v1"
AUDIT_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_NOTION_STACK_ALIGNMENT_AUDIT_001"
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_notion_stack_alignment_audit_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_notion_stack_alignment_audit_001.latest.md"
)

PACKET_VALIDATION_RECEIPT_JSON = (
    "out/audit/abx_codegen_intelligence_spine_packet_validation_receipt_001.latest.json"
)
PHASE1_HELD_REVIEW_JSON = (
    "out/operator_review/"
    "abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_"
    "dry_run_review_001.latest.json"
)

EXPECTED_PACKET_RECEIPT_STATUS = (
    "ABX_CODEGEN_INTELLIGENCE_SPINE_PACKET_VALIDATION_RECEIPT_READY"
)
EXPECTED_HELD_REVIEW_STATUS = (
    "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_REVIEW_"
    "EVIDENCE_DRY_RUN_REVIEW_HELD_FOR_OPERATOR"
)

REQUIRED_SCHEMA_PATHS: tuple[str, ...] = (
    "contracts/canon/gap_diagnosis_packet.v1.schema.json",
    "contracts/canon/improvement_proposal.v1.schema.json",
    "contracts/canon/shadow_improvement_receipt.v1.schema.json",
)

SOURCE_NOTION_PAGES: tuple[dict[str, str], ...] = (
    {
        "page_id": "37d3e8ba-2f5c-816d-8ccc-c0b46b9a2760",
        "title": "ABX_CODEGEN_INTELLIGENCE_SPINE_001",
        "status": "ADVISORY_DRAFT_PLANNING_ONLY",
        "source_observed_at": "2026-06-12T19:57:22Z",
    },
    {
        "page_id": "37d3e8ba-2f5c-81bc-8cc8-e5399d20e21a",
        "title": "ABX_CODEGEN_INTELLIGENCE_SPINE_ADVISORY_SPEC_PLAN_001",
        "status": "ADVISORY_PLANNING_READY",
        "source_observed_at": "2026-06-12T19:57:18Z",
    },
    {
        "page_id": "37d3e8ba-2f5c-81d8-bfea-c295f875e36d",
        "title": "Codegen Intelligence Spine Sample Fixtures And Test Vectors v1",
        "status": "ADVISORY_PLANNING_SAMPLES",
        "source_observed_at": "2026-06-12T19:58:18Z",
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


def _status_for(path: Path) -> str:
    return "OBSERVED" if path.exists() else "MISSING"


def _source_page_records() -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    by_id = {record["surface_id"]: record for record in NOTION_SPEC_STACK}
    for page in SOURCE_NOTION_PAGES:
        matching_spec = by_id.get(page["page_id"], {})
        record = {
            "page_id": page["page_id"],
            "title": page["title"],
            "status": page["status"],
            "source_observed_at": page["source_observed_at"],
            "repo_spec_stack_status": str(
                matching_spec.get("status", "NOT_COMPUTABLE")
            ),
        }
        record["source_hash"] = canonical_hash(record)
        records.append(record)
    return records


def _schema_records(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in REQUIRED_SCHEMA_PATHS:
        target = root / path
        records.append(
            {
                "path": path,
                "status": _status_for(target),
                "source_hash": _sha256(target),
                "advisory_contract_only": True,
                "grants_runtime_authority": False,
            }
        )
    return records


def _fixture_records(root: Path) -> list[dict[str, Any]]:
    fixture_root = root / "tests/fixtures/codegen"
    records: list[dict[str, Any]] = []
    for fixture in sorted(fixture_root.glob("*.json")):
        records.append(
            {
                "path": fixture.relative_to(root).as_posix(),
                "fixture_name": fixture.name,
                "fixture_class": (
                    "NEGATIVE" if fixture.name.startswith("invalid_") else "VALID"
                ),
                "source_hash": _sha256(fixture),
            }
        )
    return records


def _all_false(value: object) -> bool:
    return isinstance(value, Mapping) and bool(value) and all(
        item is False for item in value.values()
    )


def _expected_fixture_shape(records: list[dict[str, Any]]) -> bool:
    fixture_names = {str(record["fixture_name"]) for record in records}
    return set(EXPECTED_VALID_FIXTURES) <= fixture_names and set(
        EXPECTED_NEGATIVE_RULES
    ) <= fixture_names


def build_abx_codegen_intelligence_spine_notion_stack_alignment_audit(
    *,
    repo_root: str | Path,
    packet_validation_receipt_path: str | Path = PACKET_VALIDATION_RECEIPT_JSON,
    phase1_held_review_path: str | Path = PHASE1_HELD_REVIEW_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    packet_receipt_path = root / packet_validation_receipt_path
    held_review_path = root / phase1_held_review_path
    packet_receipt = _read_json(packet_receipt_path)
    held_review = _read_json(held_review_path)
    schema_records = _schema_records(root)
    fixture_records = _fixture_records(root)

    packet_receipt_ready = (
        packet_receipt.get("receipt_status") == EXPECTED_PACKET_RECEIPT_STATUS
        and packet_receipt.get("advisory_only") is True
        and packet_receipt.get("projection_only") is True
        and packet_receipt.get("non_authoritative") is True
        and packet_receipt.get("valid_for_implementation") is False
        and packet_receipt.get("valid_for_execution") is False
        and packet_receipt.get("shadow_replay_execution_performed") is False
    )
    held_review_ready = (
        held_review.get("status") == EXPECTED_HELD_REVIEW_STATUS
        and held_review.get("operator_input_required") is True
        and held_review.get("operator_attestations_present") is False
        and held_review.get("decision_record_created") is False
        and held_review.get("authorization_record_created") is False
        and held_review.get("implementation_authorized") is False
        and held_review.get("shadow_replay_execution_authorized") is False
        and held_review.get("valid_for_implementation") is False
        and held_review.get("valid_for_execution") is False
    )
    schemas_observed = all(record["status"] == "OBSERVED" for record in schema_records)
    fixtures_observed = _expected_fixture_shape(fixture_records)
    authority_locks = dict(AUTHORITY_LOCKS)
    authority_locks.update(
        {
            "artifact_registry_mutation": False,
            "authorization_record_creation": False,
            "evidence_bundle_creation": False,
            "fixture_mutation": False,
            "operator_attestation_creation": False,
            "operator_decision_record_creation": False,
            "schema_mutation": False,
        }
    )
    alignment_checks = [
        {
            "check_id": "notion_source_pages_observed_in_repo_stack",
            "passed": all(
                record["repo_spec_stack_status"] != "NOT_COMPUTABLE"
                for record in _source_page_records()
            ),
        },
        {"check_id": "packet_schema_contracts_observed", "passed": schemas_observed},
        {"check_id": "fixture_vectors_observed", "passed": fixtures_observed},
        {
            "check_id": "packet_validation_receipt_ready_advisory_only",
            "passed": packet_receipt_ready,
        },
        {
            "check_id": "phase1_operator_review_held_without_authority",
            "passed": held_review_ready,
        },
        {
            "check_id": "authority_locks_all_false",
            "passed": _all_false(authority_locks),
        },
    ]
    blockers = [
        str(check["check_id"]) for check in alignment_checks if check["passed"] is not True
    ]
    audit_status = (
        "ABX_CODEGEN_INTELLIGENCE_SPINE_NOTION_STACK_ALIGNMENT_AUDIT_READY"
        if not blockers
        else "ABX_CODEGEN_INTELLIGENCE_SPINE_NOTION_STACK_ALIGNMENT_AUDIT_BLOCKED"
    )
    blocked_actions = sorted(
        set(BLOCKED_ACTIONS)
        | {
            "artifact_registry_mutation",
            "authorization_record_creation",
            "evidence_bundle_creation",
            "operator_attestation_creation",
            "operator_decision_record_creation",
            "schema_mutation",
        }
    )
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "audit_id": AUDIT_ID,
        "audit_status": audit_status,
        "target_surface": "ABX_CODEGEN_INTELLIGENCE_SPINE_001",
        "source_notion_pages": _source_page_records(),
        "source_repo_artifacts": {
            "packet_validation_receipt": Path(packet_validation_receipt_path).as_posix(),
            "phase1_held_review": Path(phase1_held_review_path).as_posix(),
        },
        "source_hashes": {
            "packet_validation_receipt": _sha256(packet_receipt_path),
            "phase1_held_review": _sha256(held_review_path),
        },
        "schema_contracts": schema_records,
        "fixture_vectors": {
            "fixture_root": "tests/fixtures/codegen",
            "fixture_count": len(fixture_records),
            "valid_fixture_count": sum(
                1 for record in fixture_records if record["fixture_class"] == "VALID"
            ),
            "negative_fixture_count": sum(
                1
                for record in fixture_records
                if record["fixture_class"] == "NEGATIVE"
            ),
            "expected_valid_fixtures": list(EXPECTED_VALID_FIXTURES),
            "expected_negative_fixtures": sorted(EXPECTED_NEGATIVE_RULES),
            "notion_samples_copied_verbatim": False,
            "fixtures": fixture_records,
        },
        "alignment_checks": alignment_checks,
        "alignment_blockers": blockers,
        "current_edge": {
            "packet_validation_receipt_status": str(
                packet_receipt.get("receipt_status", "NOT_COMPUTABLE")
            ),
            "phase1_operator_review_status": str(
                held_review.get("status", "NOT_COMPUTABLE")
            ),
            "downstream": "NOT_COMPUTABLE",
            "required_before_next_step": (
                "explicit external operator attestations and a governed operator "
                "decision record"
            ),
        },
        "authority_locks": authority_locks,
        "blocked_actions": blocked_actions,
        "recommended_next_lane": "NOT_COMPUTABLE",
        "recommended_next_action": (
            "maintain the Codegen advisory hold until explicit operator attestations "
            "and governed decision-record evidence are present"
        ),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "code_generation_authorized": False,
        "file_writeback_authorized": False,
        "shadow_replay_execution_authorized": False,
        "implementation_authorized": False,
        "scheduler_mutation_authorized": False,
        "queue_mutation_authorized": False,
        "runtime_mutation_authorized": False,
        "canon_mutation_authorized": False,
        "forecast_routing_authorized": False,
        "activation_authorized": False,
        "execution_authority": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
    }
    return {**base, "audit_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_notion_stack_alignment_audit(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    write_canonical_json(path, packet)


def write_abx_codegen_intelligence_spine_notion_stack_alignment_audit_markdown(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    fixture_vectors = packet["fixture_vectors"]
    lines = [
        "# ABX Codegen Intelligence Spine Notion Stack Alignment Audit",
        "",
        f"- audit_id: {packet['audit_id']}",
        f"- audit_status: {packet['audit_status']}",
        f"- target_surface: {packet['target_surface']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- implementation_authorized: {packet['implementation_authorized']}",
        f"- execution_authority: {packet['execution_authority']}",
        "",
        "## Current Edge",
    ]
    current_edge = packet["current_edge"]
    for key in (
        "packet_validation_receipt_status",
        "phase1_operator_review_status",
        "downstream",
        "required_before_next_step",
    ):
        lines.append(f"- {key}: {current_edge[key]}")
    lines.extend(["", "## Alignment Checks"])
    for check in packet.get("alignment_checks", []):
        if isinstance(check, Mapping):
            lines.append(f"- {check['check_id']}: {check['passed']}")
    lines.extend(["", "## Schema Contracts"])
    for record in packet.get("schema_contracts", []):
        if isinstance(record, Mapping):
            lines.append(f"- {record['path']}: {record['status']}")
    lines.extend(
        [
            "",
            "## Fixture Vectors",
            f"- fixture_count: {fixture_vectors['fixture_count']}",
            f"- valid_fixture_count: {fixture_vectors['valid_fixture_count']}",
            f"- negative_fixture_count: {fixture_vectors['negative_fixture_count']}",
            f"- notion_samples_copied_verbatim: {fixture_vectors['notion_samples_copied_verbatim']}",
            "",
            "## Blocked Actions",
        ]
    )
    for action in packet.get("blocked_actions", []):
        lines.append(f"- {action}")

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
