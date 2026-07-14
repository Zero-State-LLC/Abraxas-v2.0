from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

ARTIFACT_TYPE = "V2HygieneRegistrationReadinessAudit.v1"
AUDIT_ID = "V2_HYGIENE_REGISTRATION_READINESS_AUDIT_001"
OUT_JSON = "out/sync/v2_hygiene_registration_readiness_audit/latest.json"
OUT_MD = "out/sync/v2_hygiene_registration_readiness_audit/latest.md"

V2_RECONCILIATION_JSON = "out/sync/v2_upgrade_completion_reconciliation/latest.json"
V2_OPERATOR_GATE_JSON = "out/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate_001.latest.json"
RUNE_CATALOG_JSON = "contracts/runes/catalog.v1.json"
PIPELINE_REGISTRY_PY = "core/pipelines/registry.py"

EXPECTED_MODULES = (
    "Retrocausal Signal Hygiene Module",
    "Mandatory Output Schema Enforcer",
    "Self-Adversarial Testing Loop",
    "Hyperstition Potency Evaluator",
)

EXPECTED_RUNES = (
    "RUNE.LOOP_AWARENESS",
    "RUNE.HYPERSTITION_TAG",
    "RUNE.PROVENANCE_ENFORCE",
    "RUNE.ADVERSARIAL_AUDIT",
    "RUNE.OUTPUT_REGISTER_ENFORCE",
)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _source_hash(path: Path) -> str:
    if path.suffix == ".json":
        data = _read_json(path)
        return canonical_hash(data) if data else NOT_COMPUTABLE
    text = _read_text(path)
    return canonical_hash({"path": path.as_posix(), "content": text}) if text else NOT_COMPUTABLE


def _authority_locks() -> dict[str, bool]:
    return {
        "auto_continuation": False,
        "auto_patch_generation": False,
        "canon_mutation": False,
        "execution_authority": False,
        "forecast_routing": False,
        "github_writeback": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_authorization_record_creation": False,
        "projection_surface_mutation": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_mutation": False,
        "token_minting": False,
        "v2_module_registration": False,
    }


def _observed_rune_ids(catalog: Mapping[str, Any]) -> set[str]:
    runes = catalog.get("runes", [])
    if not isinstance(runes, list):
        return set()
    return {
        str(item.get("rune_id"))
        for item in runes
        if isinstance(item, Mapping) and isinstance(item.get("rune_id"), str)
    }


def _name_records(names: tuple[str, ...], observed_text: str) -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "repo_observed": name in observed_text,
            "registration_ready": False,
            "blocked_until": "V2_HYGIENE_LOOP_AWARENESS_OPERATOR_AUTHORIZATION_GATE",
        }
        for name in names
    ]


def _rune_records(expected_runes: tuple[str, ...], observed_runes: set[str]) -> list[dict[str, Any]]:
    return [
        {
            "rune_id": rune_id,
            "repo_observed": rune_id in observed_runes,
            "registration_ready": False,
            "blocked_until": "V2_HYGIENE_LOOP_AWARENESS_OPERATOR_AUTHORIZATION_GATE",
        }
        for rune_id in expected_runes
    ]


def build_v2_hygiene_registration_readiness_audit(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    reconciliation = _read_json(root / V2_RECONCILIATION_JSON)
    operator_gate = _read_json(root / V2_OPERATOR_GATE_JSON)
    catalog = _read_json(root / RUNE_CATALOG_JSON)
    registry_text = _read_text(root / PIPELINE_REGISTRY_PY)

    module_records = _name_records(EXPECTED_MODULES, registry_text)
    rune_records = _rune_records(EXPECTED_RUNES, _observed_rune_ids(catalog))
    missing_modules = [item["name"] for item in module_records if not item["repo_observed"]]
    missing_runes = [item["rune_id"] for item in rune_records if not item["repo_observed"]]

    operator_gate_held = (
        operator_gate.get("gate_status")
        == "V2_HYGIENE_LOOP_AWARENESS_OPERATOR_AUTHORIZATION_GATE_HELD_FOR_OPERATOR"
        and operator_gate.get("authorization_granted") is False
        and operator_gate.get("v2_module_registration_authorized") is False
        and operator_gate.get("rune_registration_authorized") is False
    )
    source_ready = bool(reconciliation) and bool(operator_gate) and bool(catalog) and bool(registry_text)
    audit_status = (
        "V2_HYGIENE_REGISTRATION_READINESS_AUDIT_HELD_FOR_OPERATOR"
        if source_ready and operator_gate_held
        else NOT_COMPUTABLE
    )

    findings = [
        {
            "finding_id": "notion_v2_completion_reconciliation_observed",
            "finding_status": "PASS" if bool(reconciliation) else "FAIL_CLOSED",
            "authority_granted": False,
        },
        {
            "finding_id": "repo_v2_module_registry_entries_absent",
            "finding_status": "OBSERVED" if missing_modules else "NOT_OBSERVED",
            "authority_granted": False,
        },
        {
            "finding_id": "repo_v2_rune_catalog_entries_absent",
            "finding_status": "OBSERVED" if missing_runes else "NOT_OBSERVED",
            "authority_granted": False,
        },
        {
            "finding_id": "operator_gate_blocks_registration",
            "finding_status": "PASS" if operator_gate_held else "FAIL_CLOSED",
            "authority_granted": False,
        },
    ]

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "audit_id": AUDIT_ID,
        "audit_status": audit_status,
        "source_paths": {
            "v2_completion_reconciliation": V2_RECONCILIATION_JSON,
            "v2_operator_gate": V2_OPERATOR_GATE_JSON,
            "rune_catalog": RUNE_CATALOG_JSON,
            "pipeline_registry": PIPELINE_REGISTRY_PY,
        },
        "source_artifact_hashes": {
            V2_RECONCILIATION_JSON: _source_hash(root / V2_RECONCILIATION_JSON),
            V2_OPERATOR_GATE_JSON: _source_hash(root / V2_OPERATOR_GATE_JSON),
            RUNE_CATALOG_JSON: _source_hash(root / RUNE_CATALOG_JSON),
            PIPELINE_REGISTRY_PY: _source_hash(root / PIPELINE_REGISTRY_PY),
        },
        "notion_core_directive_context": {
            "page_title": "Abraxas v2.0 Core Directive",
            "page_id": "37e3e8ba-2f5c-811e-93f1-c45ad28f5057",
            "required_registers": ["OBSERVED", "INFERRED", "SPECULATIVE"],
            "required_loop_fields": [
                "retrocausal risk",
                "hyperstitional charge",
                "mitigation",
            ],
            "authority_boundary": "Core Directive defines output discipline; Canon Spine and rune catalog remain repo-side registry truth until governed mutation.",
        },
        "expected_module_records": module_records,
        "expected_rune_records": rune_records,
        "missing_module_registrations": missing_modules,
        "missing_rune_registrations": missing_runes,
        "registration_findings": findings,
        "registration_readiness": {
            "repo_module_entries_ready": False,
            "repo_rune_entries_ready": False,
            "operator_authorization_required": True,
            "operator_authorization_observed": False,
            "safe_to_register_modules": False,
            "safe_to_register_runes": False,
        },
        "recommended_next_action": (
            "maintain repo-side registration hold until explicit external operator authorization "
            "permits separate v2 hygiene module/rune registration planning"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "operator_authorization_observed": False,
        "operator_authorization_record_created": False,
        "authorization_granted": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "projection_surface_mutation_authorized": False,
        "schema_mutation_authorized": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
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
        "forecast_routing": False,
        "authority_locks": _authority_locks(),
        "downstream": NOT_COMPUTABLE,
    }
    return {**base, "audit_hash": canonical_hash(base)}


def write_v2_hygiene_registration_readiness_audit(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_v2_hygiene_registration_readiness_audit_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Registration Readiness Audit",
        "",
        f"- audit_id: {packet['audit_id']}",
        f"- audit_status: {packet['audit_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- recommended_next_patch: {packet['recommended_next_patch']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        "",
        "## Findings",
    ]
    for finding in packet.get("registration_findings", []):
        if isinstance(finding, Mapping):
            lines.append(f"- {finding['finding_id']}: {finding['finding_status']}")
    lines.extend(["", "## Missing Module Registrations"])
    for name in packet.get("missing_module_registrations", []):
        lines.append(f"- {name}")
    lines.extend(["", "## Missing Rune Registrations"])
    for rune_id in packet.get("missing_rune_registrations", []):
        lines.append(f"- {rune_id}")
    return lines


def write_v2_hygiene_registration_readiness_audit_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(render_v2_hygiene_registration_readiness_audit_markdown(packet)) + "\n",
        encoding="utf-8",
    )
