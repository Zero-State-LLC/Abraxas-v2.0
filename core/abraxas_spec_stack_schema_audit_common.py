from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash

NOT_COMPUTABLE = "NOT_COMPUTABLE"


def spec_stack_governance_envelope() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "execution_allowed": False,
        "authority_granted": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "scheduler_allowed": False,
        "queue_mutation_allowed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "downstream_status": NOT_COMPUTABLE,
    }


def authority_locks() -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "execution_authority": False,
        "github_writeback": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "queue_mutation": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_file_creation": False,
        "schema_mutation": False,
        "shadow_binding_creation": False,
    }


def schema_parse_ok(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return isinstance(parsed, dict) and "$schema" in parsed


def contract_record(
    *,
    contract_id: str,
    repo_path: str,
    repo_root: Path,
    contract_kind: str = "schema",
    integration_point_id: str | None = None,
) -> dict[str, Any]:
    target = repo_root / repo_path
    observed = target.exists()
    if contract_kind == "schema":
        parse_ok = schema_parse_ok(target)
    elif contract_kind == "artifact":
        parse_ok = observed and bool(_read_json(target))
    else:
        parse_ok = observed
    readiness_status = (
        "REPO_CONTRACT_OBSERVED_ADVISORY_ONLY"
        if observed and parse_ok
        else "REPO_CONTRACT_MISSING_OR_UNPARSEABLE"
    )
    record: dict[str, Any] = {
        "contract_id": contract_id,
        "repo_path": repo_path,
        "contract_kind": contract_kind,
        "repo_observed": observed,
        "schema_parse_ok": parse_ok,
        "readiness_status": readiness_status,
        "authority_granted": False,
    }
    if integration_point_id is not None:
        record["integration_point_id"] = integration_point_id
    return record


def gap_finding(
    *,
    finding_id: str,
    repo_path: str,
    repo_root: Path,
    finding_kind: str = "shadow_binding_gap",
) -> dict[str, Any]:
    observed = (repo_root / repo_path).exists()
    return {
        "finding_id": finding_id,
        "finding_kind": finding_kind,
        "repo_path": repo_path,
        "finding_status": "OBSERVED" if observed else "MISSING",
        "authority_granted": False,
        "repair_authorized": False,
    }


def contract_summary(records: list[Mapping[str, Any]]) -> dict[str, Any]:
    missing = [
        str(record["contract_id"])
        for record in records
        if not record.get("repo_observed") or not record.get("schema_parse_ok", True)
    ]
    observed_count = sum(
        1
        for record in records
        if record.get("repo_observed") and record.get("schema_parse_ok", True)
    )
    return {
        "expected_contract_count": len(records),
        "repo_observed_count": observed_count,
        "missing_contract_count": len(missing),
        "missing_contract_ids": sorted(missing),
    }


def artifact_validation_finding(
    *,
    artifact_path: str,
    repo_root: Path,
    schema_path: str | None = None,
) -> dict[str, Any]:
    artifact = repo_root / artifact_path
    if not artifact.exists():
        return {
            "finding_id": f"artifact_validation_{artifact_path.replace('/', '_')}",
            "finding_kind": "sample_artifact_validation",
            "repo_path": artifact_path,
            "finding_status": "MISSING",
            "schema_validation_ok": False,
            "authority_granted": False,
        }
    schema_validation_ok = False
    if schema_path is not None:
        schema_file = repo_root / schema_path
        artifact_data = _read_json(artifact)
        schema_data = _read_json(schema_file)
        if artifact_data and schema_data:
            try:
                from jsonschema import validate

                validate(artifact_data, schema_data)
                schema_validation_ok = True
            except Exception:
                schema_validation_ok = False
    return {
        "finding_id": f"artifact_validation_{artifact_path.replace('/', '_')}",
        "finding_kind": "sample_artifact_validation",
        "repo_path": artifact_path,
        "finding_status": "OBSERVED",
        "schema_validation_ok": schema_validation_ok,
        "authority_granted": False,
    }


def finalize_audit_packet(packet: dict[str, Any], *, hash_field: str = "audit_hash") -> dict[str, Any]:
    base = dict(packet)
    base[hash_field] = canonical_hash({key: value for key, value in base.items() if key != hash_field})
    return base


def render_audit_markdown(title: str, packet: Mapping[str, Any]) -> list[str]:
    identifier = packet.get("audit_id", packet.get("receipt_id", "unknown"))
    lines = [
        f"# {title}",
        "",
        f"- id: {identifier}",
        f"- status: {packet['status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
    ]
    if "domain" in packet:
        lines.insert(3, f"- domain: {packet['domain']}")
    if "stack_summary" in packet:
        lines.extend(["", "## Stack Summary"])
        for key, value in packet["stack_summary"].items():
            lines.append(f"- {key}: {value}")
        lines.extend(["", "## Domain Audits"])
        for audit in packet["domain_audits"]:
            lines.append(
                f"- {audit['domain']}: {audit['status']} "
                f"(missing={audit['missing_contract_count']})"
            )
        return lines
    lines.extend(["", "## Contract Summary"])
    summary = packet["contract_summary"]
    for key in (
        "expected_contract_count",
        "repo_observed_count",
        "missing_contract_count",
    ):
        lines.append(f"- {key}: {summary[key]}")
    lines.extend(["", "## Contract Records"])
    for record in packet["contract_records"]:
        label = record.get("contract_id", record.get("integration_point_id", "unknown"))
        lines.append(
            f"- {label}: {record['readiness_status']} "
            f"(repo_observed={record['repo_observed']})"
        )
    if packet.get("findings"):
        lines.extend(["", "## Findings"])
        for finding in packet["findings"]:
            lines.append(
                f"- {finding['finding_id']}: {finding['finding_status']}"
            )
    has_binding_refs = any("integration_point_id" in record for record in packet["contract_records"])
    if has_binding_refs:
        lines.extend(["", "## Shadow Binding Refs"])
        for record in packet["contract_records"]:
            if "integration_point_id" in record:
                lines.append(
                    f"- {record['integration_point_id']}: {record['readiness_status']}"
                )
    return lines


def write_audit_outputs(
    packet: dict[str, Any],
    *,
    out_json: Path,
    title: str,
) -> dict[str, Any]:
    from core.canonical.json import write_canonical_json

    out_json.parent.mkdir(parents=True, exist_ok=True)
    write_canonical_json(out_json, packet)
    out_md = out_json.with_suffix(".md")
    out_md.write_text("\n".join(render_audit_markdown(title, packet)) + "\n", encoding="utf-8")
    return packet


def _read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}
