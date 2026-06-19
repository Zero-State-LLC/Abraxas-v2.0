from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ModuleNotFoundError:  # pragma: no cover - exercised by minimal system Python runs.
    Draft202012Validator = None  # type: ignore[assignment]
    FormatChecker = None  # type: ignore[assignment]

from core.abx_codegen_intelligence_spine_advisory_spec_plan import (
    AUTHORITY_LOCKS,
    BLOCKED_ACTIONS,
    validate_codegen_packet_semantics,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpinePacketValidationReceipt.v1"
RECEIPT_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_PACKET_VALIDATION_RECEIPT_001"
OUT_JSON = "out/audit/abx_codegen_intelligence_spine_packet_validation_receipt_001.latest.json"
OUT_MD = "out/audit/abx_codegen_intelligence_spine_packet_validation_receipt_001.latest.md"

ADVISORY_SPEC_PLAN_JSON = (
    "out/audit/abx_codegen_intelligence_spine_advisory_spec_plan_001.latest.json"
)
FIXTURE_VALIDATION_HARNESS_PLAN_JSON = (
    "out/audit/abx_codegen_intelligence_spine_fixture_validation_harness_plan_001.latest.json"
)
FIXTURE_ROOT = "tests/fixtures/codegen"

PACKET_SCHEMA_PATHS: dict[str, str] = {
    "GapDiagnosisPacket.v1": "contracts/canon/gap_diagnosis_packet.v1.schema.json",
    "ImprovementProposal.v1": "contracts/canon/improvement_proposal.v1.schema.json",
    "ShadowImprovementReceipt.v1": "contracts/canon/shadow_improvement_receipt.v1.schema.json",
}

EXPECTED_VALID_FIXTURES: tuple[str, ...] = (
    "gap_diagnosis_golden.v1.json",
    "improvement_proposal_golden.v1.json",
    "improvement_proposal_self_improvement_meta_gate.v1.json",
    "shadow_receipt_golden.v1.json",
    "self_improvement_meta_gate_receipt.v1.json",
)

EXPECTED_NEGATIVE_RULES: dict[str, tuple[str, ...]] = {
    "invalid_gap_diagnosis_missing_hash.v1.json": (
        "evidence_source_hash_required",
        "self_diagnosis_requires_medium_severity",
    ),
    "invalid_improvement_proposal_canon_jump.v1.json": (
        "canon_promotion_requires_prior_canary_success",
        "self_modification_requires_operator_decision",
    ),
    "invalid_improvement_proposal_missing_operator_decision.v1.json": (
        "self_modification_requires_operator_decision",
    ),
    "invalid_improvement_proposal_missing_provenance.v1.json": (
        "core_policy_auto_mutation_denied",
        "provenance_source_gap_analysis_required",
    ),
    "invalid_shadow_receipt_promote_failure.v1.json": (
        "promotion_requires_12_run_invariance",
        "promotion_requires_governance_compliance",
        "self_modification_requires_hold_recommendation",
        "self_modification_requires_operator_review",
    ),
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


def _schema_validators(repo_root: Path) -> dict[str, Any]:
    validators: dict[str, Any] = {}
    if Draft202012Validator is None or FormatChecker is None:
        return validators
    for schema_version, schema_path in sorted(PACKET_SCHEMA_PATHS.items()):
        schema = _read_json(repo_root / schema_path)
        if schema:
            validators[schema_version] = Draft202012Validator(
                schema, format_checker=FormatChecker()
            )
    return validators


def _schema_records(repo_root: Path) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for schema_version, schema_path in sorted(PACKET_SCHEMA_PATHS.items()):
        target = repo_root / schema_path
        records.append(
            {
                "schema_version": schema_version,
                "path": schema_path,
                "status": _status_for(target),
                "source_hash": _sha256(target) if target.exists() else "NOT_COMPUTABLE",
            }
        )
    return records


def _looks_like_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


def _fallback_schema_errors(packet: Mapping[str, Any]) -> list[str]:
    schema_version = packet.get("schema_version")
    errors: list[str] = []
    required_fields: Mapping[str, tuple[str, ...]] = {
        "GapDiagnosisPacket.v1": (
            "schema_version",
            "diagnosis_id",
            "timestamp",
            "detected_by",
            "gap_type",
            "target_surface",
            "description",
            "evidence_sources",
            "severity",
            "impact_assessment",
            "recommended_next_lane",
            "proposed_improvement_types",
            "self_diagnosis_flag",
            "provenance",
        ),
        "ImprovementProposal.v1": (
            "schema_version",
            "proposal_id",
            "timestamp",
            "source_gap_diagnosis_id",
            "proposal_type",
            "target_surface",
            "intent",
            "contract_deltas",
            "affected_runes",
            "affected_pipelines",
            "required_fixtures",
            "validation_invariants",
            "risk_assessment",
            "shadow_validation_plan",
            "promotion_path",
            "operator_decision_required",
            "provenance",
        ),
        "ShadowImprovementReceipt.v1": (
            "schema_version",
            "receipt_id",
            "timestamp",
            "proposal_id",
            "shadow_run_id",
            "environment",
            "validation_results",
            "metrics",
            "governance_flags",
            "rollback_info",
            "promotion_blockers",
            "provenance",
            "recommendation",
        ),
    }
    if not isinstance(schema_version, str) or schema_version not in required_fields:
        return ["unsupported_codegen_packet_schema_version"]
    for field in required_fields[schema_version]:
        if field not in packet:
            errors.append(f"{field}:required")
    id_fields = {
        "GapDiagnosisPacket.v1": ("diagnosis_id",),
        "ImprovementProposal.v1": ("proposal_id", "source_gap_diagnosis_id"),
        "ShadowImprovementReceipt.v1": ("receipt_id", "proposal_id"),
    }
    for field in id_fields[schema_version]:
        if field in packet and not _looks_like_sha256(packet[field]):
            errors.append(f"{field}:pattern")
    if schema_version == "GapDiagnosisPacket.v1":
        for index, source in enumerate(packet.get("evidence_sources", [])):
            if isinstance(source, Mapping) and not _looks_like_sha256(source.get("hash")):
                errors.append(f"evidence_sources.{index}.hash:pattern")
    return sorted(errors)


def _schema_errors(
    *,
    validators: Mapping[str, Any],
    packet: Mapping[str, Any],
) -> list[str]:
    schema_version = packet.get("schema_version")
    if not isinstance(schema_version, str) or schema_version not in validators:
        return _fallback_schema_errors(packet)
    errors = []
    for error in sorted(validators[schema_version].iter_errors(packet), key=str):
        path = ".".join(str(part) for part in error.absolute_path)
        if path:
            errors.append(f"{path}:{error.validator}")
        else:
            errors.append(str(error.validator))
    return errors


def _fixture_validation_records(repo_root: Path) -> list[dict[str, Any]]:
    fixture_root = repo_root / FIXTURE_ROOT
    validators = _schema_validators(repo_root)
    records: list[dict[str, Any]] = []
    for target in sorted(fixture_root.glob("*.json")):
        packet = _read_json(target)
        fixture_name = target.name
        schema_errors = _schema_errors(validators=validators, packet=packet)
        semantic_errors = validate_codegen_packet_semantics(packet)
        expected_rules = list(EXPECTED_NEGATIVE_RULES.get(fixture_name, ()))
        fixture_class = "VALID" if fixture_name in EXPECTED_VALID_FIXTURES else "NEGATIVE"
        expected_rules_observed = all(rule in semantic_errors for rule in expected_rules)
        if fixture_class == "VALID":
            validation_status = (
                "PASS" if not schema_errors and not semantic_errors else "FAIL"
            )
        else:
            validation_status = (
                "EXPECTED_REJECTION"
                if expected_rules and expected_rules_observed
                else "FAIL"
            )
        records.append(
            {
                "path": target.relative_to(repo_root).as_posix(),
                "fixture_name": fixture_name,
                "fixture_class": fixture_class,
                "schema_version": str(packet.get("schema_version", "NOT_COMPUTABLE")),
                "source_hash": _sha256(target),
                "schema_valid": not schema_errors,
                "schema_errors": schema_errors,
                "semantic_errors": semantic_errors,
                "expected_negative_rules": expected_rules,
                "expected_negative_rules_observed": expected_rules_observed,
                "validation_status": validation_status,
            }
        )
    return records


def build_abx_codegen_intelligence_spine_packet_validation_receipt(
    *,
    repo_root: str | Path,
    advisory_spec_plan_path: str | Path = ADVISORY_SPEC_PLAN_JSON,
    fixture_validation_harness_plan_path: str | Path = FIXTURE_VALIDATION_HARNESS_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_paths = {
        "advisory_spec_plan": Path(advisory_spec_plan_path).as_posix(),
        "fixture_validation_harness_plan": Path(
            fixture_validation_harness_plan_path
        ).as_posix(),
        "fixture_root": FIXTURE_ROOT,
    }
    source_hashes = {
        key: _sha256(root / path)
        for key, path in source_paths.items()
        if key != "fixture_root"
    }
    source_hashes["fixture_root"] = canonical_hash(
        [
            {
                "path": record["path"],
                "source_hash": record["source_hash"],
            }
            for record in _fixture_validation_records(root)
        ]
    )
    required_source_statuses = {
        key: _status_for(root / path) for key, path in source_paths.items()
    }
    advisory_spec_plan = _read_json(root / advisory_spec_plan_path)
    harness_plan = _read_json(root / fixture_validation_harness_plan_path)
    fixture_records = _fixture_validation_records(root)
    valid_records = [
        record for record in fixture_records if record["fixture_class"] == "VALID"
    ]
    negative_records = [
        record for record in fixture_records if record["fixture_class"] == "NEGATIVE"
    ]
    valid_pass_count = sum(
        1 for record in valid_records if record["validation_status"] == "PASS"
    )
    negative_rejection_count = sum(
        1
        for record in negative_records
        if record["validation_status"] == "EXPECTED_REJECTION"
    )
    validation_passed = (
        valid_pass_count == len(EXPECTED_VALID_FIXTURES)
        and negative_rejection_count == len(EXPECTED_NEGATIVE_RULES)
        and len(valid_records) == len(EXPECTED_VALID_FIXTURES)
        and len(negative_records) == len(EXPECTED_NEGATIVE_RULES)
    )
    upstream_ready = (
        advisory_spec_plan.get("plan_status")
        == "ABX_CODEGEN_INTELLIGENCE_SPINE_ADVISORY_SPEC_PLAN_READY"
        and harness_plan.get("plan_status")
        == "ABX_CODEGEN_INTELLIGENCE_SPINE_FIXTURE_VALIDATION_HARNESS_PLAN_READY"
    )
    sources_observed = all(status == "OBSERVED" for status in required_source_statuses.values())
    receipt_status = (
        "ABX_CODEGEN_INTELLIGENCE_SPINE_PACKET_VALIDATION_RECEIPT_READY"
        if upstream_ready and sources_observed and validation_passed
        else "NOT_COMPUTABLE"
    )
    authority_locks = dict(AUTHORITY_LOCKS)
    authority_locks.update(
        {
            "artifact_registry_mutation": False,
            "authorization_record_creation": False,
            "fixture_mutation": False,
            "harness_implementation": False,
            "operator_attestation_creation": False,
            "receipt_promotion": False,
            "schema_mutation": False,
        }
    )
    blocked_actions = sorted(
        set(BLOCKED_ACTIONS)
        | {
            "artifact_registry_mutation",
            "authorization_record_creation",
            "fixture_mutation",
            "harness_implementation",
            "operator_attestation_creation",
            "receipt_promotion",
            "schema_mutation",
            "shadow_replay_receipt_creation",
        }
    )
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "receipt_id": RECEIPT_ID,
        "receipt_status": receipt_status,
        "target_surface": "ABX_CODEGEN_INTELLIGENCE_SPINE_001",
        "target_surface_status": "PACKET_SCHEMA_FIXTURE_VALIDATION_OBSERVED_ADVISORY_ONLY",
        "patch_id": "PATCH-ABX-CODEGEN-INTELLIGENCE-SPINE-PACKET-VALIDATION-RECEIPT-001",
        "source_paths": source_paths,
        "source_hashes": source_hashes,
        "required_source_statuses": required_source_statuses,
        "schema_contracts": _schema_records(root),
        "fixture_validation_summary": {
            "fixture_root": FIXTURE_ROOT,
            "fixture_count": len(fixture_records),
            "valid_fixture_count": len(valid_records),
            "valid_fixture_pass_count": valid_pass_count,
            "negative_fixture_count": len(negative_records),
            "negative_fixture_expected_rejection_count": negative_rejection_count,
            "validation_passed": validation_passed,
            "validation_mode": "SCHEMA_AND_SEMANTIC_RULES_ONLY",
            "shadow_replay_executed": False,
            "wall_clock_used": False,
            "fixture_timestamps_are_source_observed": True,
        },
        "fixture_validation_records": fixture_records,
        "authority_locks": authority_locks,
        "blocked_actions": blocked_actions,
        "recommended_next_lane": "ABX_CODEGEN_INTELLIGENCE_SPINE_PHASE1_OPERATOR_AUTHORIZATION_REQUEST_PLAN",
        "recommended_next_action": (
            "keep packet validation as advisory evidence and require a separate "
            "operator authorization lane before implementation, replay, writeback, "
            "or promotion"
        ),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "schema_mutation_performed": False,
        "fixture_mutation_performed": False,
        "shadow_replay_execution_performed": False,
        "operator_decision_record_created": False,
        "meta_gate_seal_created": False,
    }
    return {**base, "receipt_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_packet_validation_receipt(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    write_canonical_json(path, packet)


def write_abx_codegen_intelligence_spine_packet_validation_receipt_markdown(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    summary = packet["fixture_validation_summary"]
    lines = [
        "# ABX Codegen Intelligence Spine Packet Validation Receipt",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- receipt_status: {packet['receipt_status']}",
        f"- target_surface: {packet['target_surface']}",
        f"- target_surface_status: {packet['target_surface_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- shadow_replay_execution_performed: {packet['shadow_replay_execution_performed']}",
        "",
        "## Fixture Validation Summary",
        f"- fixture_count: {summary['fixture_count']}",
        f"- valid_fixture_pass_count: {summary['valid_fixture_pass_count']}",
        f"- negative_fixture_expected_rejection_count: {summary['negative_fixture_expected_rejection_count']}",
        f"- validation_mode: {summary['validation_mode']}",
        f"- wall_clock_used: {summary['wall_clock_used']}",
        "",
        "## Fixture Records",
    ]
    for record in packet.get("fixture_validation_records", []):
        if isinstance(record, dict):
            lines.append(
                f"- {record['fixture_name']}: {record['validation_status']} "
                f"({record['fixture_class']})"
            )
    lines.extend(["", "## Schema Contracts"])
    for record in packet.get("schema_contracts", []):
        if isinstance(record, dict):
            lines.append(f"- {record['path']}: {record['status']}")
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- {action}")

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
