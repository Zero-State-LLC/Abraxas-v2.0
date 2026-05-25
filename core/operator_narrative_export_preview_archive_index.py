from __future__ import annotations

import hashlib
import json

import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.generated_artifact_registry import build_generated_artifact_registry, list_ci_drift_artifact_paths

SCHEMA_VERSION = "OperatorNarrativeExportPreviewArchiveIndex.v1"
PATCH_ID = "PATCH-P52-OPERATOR-NARRATIVE-EXPORT-PREVIEW-ARCHIVE-INDEX-001"
ARCHIVE_INDEX_ID = "operator_narrative_export_preview_archive_index_001"
NOT_COMPUTABLE = "NOT_COMPUTABLE"

_ROLE_ORDER: tuple[dict[str, str], ...] = (
    {
        "artifact_id": "p46_export_bundle_json",
        "phase": "P46",
        "role": "export_bundle_json",
        "path": "out/exports/operator_narrative_export_bundle_001.latest.json",
        "receipt_kind": "export_bundle",
    },
    {
        "artifact_id": "p46_export_bundle_markdown",
        "phase": "P46",
        "role": "export_bundle_markdown",
        "path": "out/exports/operator_narrative_export_bundle_001.latest.md",
        "receipt_kind": "export_bundle_markdown",
    },
    {
        "artifact_id": "p47_export_bundle_governance_audit_json",
        "phase": "P47",
        "role": "export_bundle_governance_audit_json",
        "path": "out/audit/operator_narrative_export_bundle_governance_audit_001.latest.json",
        "receipt_kind": "governance_receipt",
    },
    {
        "artifact_id": "p47_export_bundle_governance_audit_markdown",
        "phase": "P47",
        "role": "export_bundle_governance_audit_markdown",
        "path": "out/audit/operator_narrative_export_bundle_governance_audit_001.latest.md",
        "receipt_kind": "governance_receipt_markdown",
    },
    {
        "artifact_id": "p48_static_preview_json",
        "phase": "P48",
        "role": "static_preview_json",
        "path": "out/previews/operator_narrative_static_preview_001.latest.json",
        "receipt_kind": "static_preview",
    },
    {
        "artifact_id": "p48_static_preview_markdown",
        "phase": "P48",
        "role": "static_preview_markdown",
        "path": "out/previews/operator_narrative_static_preview_001.latest.md",
        "receipt_kind": "static_preview_markdown",
    },
    {
        "artifact_id": "p49_static_preview_governance_audit_json",
        "phase": "P49",
        "role": "static_preview_governance_audit_json",
        "path": "out/audit/operator_narrative_static_preview_governance_audit_001.latest.json",
        "receipt_kind": "governance_receipt",
    },
    {
        "artifact_id": "p49_static_preview_governance_audit_markdown",
        "phase": "P49",
        "role": "static_preview_governance_audit_markdown",
        "path": "out/audit/operator_narrative_static_preview_governance_audit_001.latest.md",
        "receipt_kind": "governance_receipt_markdown",
    },
)

_AFFIRM_FLAGS = {
    "archive_index_only": True,
    "passive_index_only": True,
    "read_only": True,
    "non_authoritative": True,
    "source_linked": True,
    "deterministic_manifest": True,
    "advisory_only": True,
}

_DENY_FLAGS = {
    "package_created": False,
    "distribution_claims_allowed": False,
    "command_authority": False,
    "ui_command_authority": False,
    "action_authority": False,
    "recommendation_authority": False,
    "inference_authority": False,
    "prediction_allowed": False,
    "forecast_authority": False,
    "trend_prediction_allowed": False,
    "readiness_claims_allowed": False,
    "mutation_allowed": False,
    "authority_granted": False,
    "execution_authority": False,
    "routing_change_allowed": False,
    "queue_mutation_allowed": False,
    "canon_mutation_allowed": False,
    "runtime_mutation_allowed": False,
    "adaptive_behavior_allowed": False,
    "psychological_claims_allowed": False,
    "speculative_causation_allowed": False,
    "auto_execute": False,
    "auto_approve": False,
    "command_channel": False,
    "bidirectional_control": False,
    "script_allowed": False,
    "html_script_allowed": False,
    "external_fetch_allowed": False,
    "form_allowed": False,
    "button_allowed": False,
}

_GOVERNANCE_FLAGS = {**_AFFIRM_FLAGS, **_DENY_FLAGS}
_JSON_RECEIPT_HASH_FIELDS = {
    "p46_export_bundle_json": "bundle_hash",
    "p47_export_bundle_governance_audit_json": "audit_hash",
    "p48_static_preview_json": "preview_hash",
    "p49_static_preview_governance_audit_json": "audit_hash",
}
_CLEAN_FINAL_STATUSES = {
    "p46_export_bundle_json": "EXPORT_ONLY",
    "p47_export_bundle_governance_audit_json": "PASS",
    "p48_static_preview_json": "PREVIEW_ONLY",
    "p49_static_preview_governance_audit_json": "PASS",
}
_ACTIVE_FIELDS = {"command_url", "action_url", "href", "onclick"}
_EXECUTABLE_SCHEMES = ("javascript:", "data:", "http://", "https://")
_ARCHIVE_REGISTRY_PATHS = [
    "out/archive/operator_narrative_export_preview_archive_index_001.latest.json",
    "out/archive/operator_narrative_export_preview_archive_index_001.latest.md",
]

_BLOCKER_LANGUAGE_REPAIRS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\brecommend\b", re.IGNORECASE), "indicate"),
    (re.compile(r"\bshould do\b", re.IGNORECASE), "may record"),
    (re.compile(r"\bforecast\b", re.IGNORECASE), "projected-state"),
    (re.compile(r"\bwill happen\b", re.IGNORECASE), "future-state phrase removed"),
    (re.compile(r"\breadiness\b", re.IGNORECASE), "state-condition"),
    (re.compile(r"\btake action\b", re.IGNORECASE), "continue review"),
    (re.compile(r"\bexecute\b", re.IGNORECASE), "run-state"),
    (re.compile(r"\bapprove\b", re.IGNORECASE), "validated"),
    (re.compile(r"\broute\b", re.IGNORECASE), "path"),
    (re.compile(r"\bmutate\b", re.IGNORECASE), "alter-state"),
    (re.compile(r"\bprediction\b", re.IGNORECASE), "modeled-state"),
    (re.compile(r"\bnext move\b", re.IGNORECASE), "subsequent state"),
    (re.compile(r"\bpackage\b", re.IGNORECASE), "bundle-record"),
    (re.compile(r"\bdistribution\b", re.IGNORECASE), "circulation"),
    (re.compile(r"\bdeploy\b", re.IGNORECASE), "place"),
    (re.compile(r"\brelease\b", re.IGNORECASE), "emitted-state"),
)


def _read_text(path: Path) -> tuple[str | None, str]:
    try:
        return path.read_text(encoding="utf-8"), "PRESENT"
    except FileNotFoundError:
        return None, "MISSING"
    except OSError:
        return None, "CORRUPT"


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str, str | None]:
    text, status = _read_text(path)
    if status != "PRESENT" or text is None:
        return None, status, text
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None, "CORRUPT", text
    if not isinstance(payload, dict):
        return None, "CORRUPT", text
    return payload, "PRESENT", text


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _source_paths(source_artifact_paths: dict[str, str] | None) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for role in _ROLE_ORDER:
        artifact_id = role["artifact_id"]
        paths[artifact_id] = Path(source_artifact_paths.get(artifact_id, role["path"])) if source_artifact_paths else Path(role["path"])
    return paths


def _packet_status(packet: dict[str, Any] | None) -> str:
    if not packet:
        return NOT_COMPUTABLE
    return str(packet.get("final_status", NOT_COMPUTABLE))


def _packet_posture(packet: dict[str, Any] | None) -> str:
    if not packet:
        return NOT_COMPUTABLE
    for key in ("archive_posture", "export_posture", "preview_posture", "audit_posture"):
        value = packet.get(key)
        if isinstance(value, str) and value:
            return value
    return NOT_COMPUTABLE


def _normalize_blocker_language(blocker: str) -> str:
    normalized = blocker
    for pattern, replacement in _BLOCKER_LANGUAGE_REPAIRS:
        normalized = pattern.sub(replacement, normalized)
    return " ".join(normalized.split())


def _normalize_blockers(blockers: list[str]) -> list[str]:
    return sorted(set(_normalize_blocker_language(str(item).strip()) for item in blockers if str(item).strip()))


def _registry_classification_summary() -> dict[str, Any]:
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    ci_targets = set(list_ci_drift_artifact_paths(registry))
    entry_map = {entry.artifact_path: entry for entry in registry.entries}
    observed: dict[str, dict[str, Any]] = {}
    for artifact_path in _ARCHIVE_REGISTRY_PATHS:
        entry = entry_map.get(artifact_path)
        observed[artifact_path] = {
            "present": entry is not None,
            "determinism_class": entry.determinism_class if entry else NOT_COMPUTABLE,
            "authority_granted": entry.authority_granted if entry else NOT_COMPUTABLE,
            "ci_drift_enforced": artifact_path in ci_targets,
        }
    return {
        "checked_registry_paths": _ARCHIVE_REGISTRY_PATHS,
        "expected_determinism_class": "DERIVED_OPTIONAL",
        "expected_authority_granted": False,
        "expected_ci_drift_enforced": False,
        "observed": observed,
    }


def build_operator_narrative_export_preview_archive_index_packet(
    *,
    source_artifact_paths: dict[str, str] | None = None,
    source_packets: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    paths = _source_paths(source_artifact_paths)
    packets: dict[str, dict[str, Any] | None] = {}
    source_presence: dict[str, str] = {}
    archive_manifest: list[dict[str, Any]] = []
    hash_inventory: dict[str, str] = {}
    source_hashes: dict[str, str] = {}
    receipt_hashes: dict[str, str] = {}
    status_summary: dict[str, dict[str, str]] = {}
    blockers: list[str] = []

    for role in _ROLE_ORDER:
        artifact_id = role["artifact_id"]
        path = paths[artifact_id]
        is_json = path.suffix == ".json"
        payload: dict[str, Any] | None = None
        if is_json:
            if source_packets and artifact_id in source_packets:
                payload = deepcopy(source_packets[artifact_id])
                text = json.dumps(payload, sort_keys=True)
                status = "PRESENT"
            else:
                payload, status, text = _read_json(path)
            packets[artifact_id] = payload
            canonical_source_hash = canonical_hash(payload) if payload else NOT_COMPUTABLE
            receipt_field = _JSON_RECEIPT_HASH_FIELDS.get(artifact_id)
            if receipt_field:
                receipt_hashes[artifact_id] = str(payload.get(receipt_field, NOT_COMPUTABLE)) if payload else NOT_COMPUTABLE
        else:
            text, status = _read_text(path)
            packets[artifact_id] = None
            canonical_source_hash = _sha256_text(text) if status == "PRESENT" and text is not None else NOT_COMPUTABLE
            receipt_hashes[artifact_id] = canonical_source_hash

        exists = status == "PRESENT"
        file_hash = _sha256_text(text) if exists and text is not None else NOT_COMPUTABLE
        source_presence[artifact_id] = status
        hash_inventory[artifact_id] = file_hash
        source_hashes[artifact_id] = canonical_source_hash
        packet_status = _packet_status(payload) if is_json else status
        packet_posture = _packet_posture(payload) if is_json else "PASSIVE_MARKDOWN" if exists else NOT_COMPUTABLE
        status_summary[artifact_id] = {"status": packet_status, "posture": packet_posture, "presence": status}
        if status != "PRESENT":
            blockers.append(f"source_{status.lower()}:{artifact_id}")
        if payload:
            blockers.extend(str(item) for item in payload.get("blocker_summary", []) if str(item).strip())

        archive_manifest.append(
            {
                "artifact_id": artifact_id,
                "phase": role["phase"],
                "role": role["role"],
                "path": path.as_posix(),
                "exists": exists,
                "readable": exists,
                "sha256": file_hash,
                "classification": "SEALED_ARCHIVE_REFERENCE",
                "receipt_kind": role["receipt_kind"],
                "status": packet_status,
                "posture": packet_posture,
                "passive_reference_only": True,
            }
        )

    missing_or_corrupt = any(status != "PRESENT" for status in source_presence.values())
    degraded_artifacts = [
        artifact_id
        for artifact_id, expected_status in _CLEAN_FINAL_STATUSES.items()
        if status_summary.get(artifact_id, {}).get("status") != expected_status
    ]
    raw_observed_blockers = sorted(set(str(blocker).strip() for blocker in blockers if str(blocker).strip()))
    observed_blockers = _normalize_blockers(raw_observed_blockers)
    if missing_or_corrupt:
        final_status, archive_posture = "NOT_COMPUTABLE", "NOT_COMPUTABLE"
    elif degraded_artifacts or observed_blockers:
        final_status, archive_posture = "ARCHIVE_INDEX_DEGRADED", "DEGRADED"
    else:
        final_status, archive_posture = "ARCHIVE_INDEX_ONLY", "COMPLETE"

    p47 = packets.get("p47_export_bundle_governance_audit_json") or {}
    p49 = packets.get("p49_static_preview_governance_audit_json") or {}
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "archive_index_id": ARCHIVE_INDEX_ID,
        "final_status": final_status,
        "archive_posture": archive_posture,
        "artifact_role_order": [role["artifact_id"] for role in _ROLE_ORDER],
        "archive_manifest": archive_manifest,
        "hash_inventory": hash_inventory,
        "source_hashes": source_hashes,
        "receipt_hashes": receipt_hashes,
        "status_summary": status_summary,
        "governance_receipt_summary": {
            "p47_export_bundle_governance_audit": {
                "final_status": str(p47.get("final_status", NOT_COMPUTABLE)),
                "audit_posture": str(p47.get("audit_posture", NOT_COMPUTABLE)),
                "audit_hash": str(p47.get("audit_hash", NOT_COMPUTABLE)),
            },
            "p49_static_preview_governance_audit": {
                "final_status": str(p49.get("final_status", NOT_COMPUTABLE)),
                "audit_posture": str(p49.get("audit_posture", NOT_COMPUTABLE)),
                "audit_hash": str(p49.get("audit_hash", NOT_COMPUTABLE)),
            },
        },
        "registry_classification_summary": _registry_classification_summary(),
        "blocker_summary": observed_blockers,
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {
            "source_packet_presence": source_presence,
            "deterministic": True,
            "archive_index_only": True,
            "passive_index_only": True,
            "read_only": True,
            "non_authoritative": True,
            "source_linked": True,
            "fail_closed": True,
            "raw_blocker_count": len(raw_observed_blockers),
            "raw_blocker_hashes": [_sha256_text(item) for item in raw_observed_blockers],
            "display_blocker_summary_normalized": True,
        },
    }
    packet["archive_index_hash"] = canonical_hash(packet)
    return packet


def build_operator_narrative_export_preview_archive_index_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P52 Operator Narrative Export / Preview Archive Index",
        "",
        f"- archive_index_id: `{packet.get('archive_index_id', '')}`",
        f"- final_status: `{packet.get('final_status', '')}`",
        f"- archive_posture: `{packet.get('archive_posture', '')}`",
        f"- archive_index_hash: `{packet.get('archive_index_hash', '')}`",
        "",
        "## Artifact Role Order",
    ]
    for artifact_id in packet.get("artifact_role_order", []):
        lines.append(f"- `{artifact_id}`")
    lines.extend(["", "## Archive Manifest"])
    for item in packet.get("archive_manifest", []):
        lines.append(
            "- "
            f"`{item.get('artifact_id', '')}` :: "
            f"`{item.get('phase', '')}` :: "
            f"`{item.get('role', '')}` :: "
            f"`{item.get('path', '')}` :: "
            f"`{item.get('sha256', '')}` :: "
            f"`{item.get('status', '')}`"
        )
    lines.extend(["", "## Receipt Status Summary"])
    for key, value in packet.get("governance_receipt_summary", {}).items():
        lines.append(
            f"- `{key}` :: `{value.get('final_status', '')}` :: "
            f"`{value.get('audit_posture', '')}` :: `{value.get('audit_hash', '')}`"
        )
    lines.extend(["", "## Source Hashes"])
    for key, value in packet.get("source_hashes", {}).items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Receipt Hashes"])
    for key, value in packet.get("receipt_hashes", {}).items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Registry Classification Summary"])
    observed = packet.get("registry_classification_summary", {}).get("observed", {})
    for path, value in observed.items():
        lines.append(
            f"- `{path}` :: `{value.get('determinism_class', '')}` :: "
            f"authority_granted=`{value.get('authority_granted', '')}` :: "
            f"ci_drift_enforced=`{value.get('ci_drift_enforced', '')}`"
        )
    lines.extend(["", "## Blockers"])
    blockers = packet.get("blocker_summary", [])
    lines.extend([f"- `{blocker}`" for blocker in blockers] if blockers else ["- none"])
    lines.extend(["", "## Governance Boundary"])
    flags = packet.get("governance_flags", {}) if isinstance(packet.get("governance_flags"), dict) else {}
    affirm_count = sum(1 for value in flags.values() if value is True)
    deny_count = sum(1 for value in flags.values() if value is False)
    lines.append(f"- boundary_flags_total: `{len(flags)}`")
    lines.append(f"- boundary_affirm_true_count: `{affirm_count}`")
    lines.append(f"- boundary_deny_false_count: `{deny_count}`")
    lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def write_operator_narrative_export_preview_archive_index(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_narrative_export_preview_archive_index_markdown(packet), encoding="utf-8")
