from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "OperatorNarrativeStaticPreviewBundle.v1"
PATCH_ID = "PATCH-P48-OPERATOR-NARRATIVE-STATIC-PREVIEW-BUNDLE-001"
PREVIEW_ID = "operator_narrative_static_preview_001"
NOT_COMPUTABLE = "NOT_COMPUTABLE"

PREVIEW_SECTIONS = [
    "export_bundle_summary",
    "export_governance_audit",
    "artifact_manifest",
    "hash_inventory",
    "source_lineage",
    "governance_boundary",
    "passive_references",
    "blockers",
]

_GOVERNANCE_FLAGS = {
    "preview_only": True, "static_only": True, "passive_preview_only": True, "read_only": True, "non_interactive": True,
    "non_authoritative": True, "source_linked": True, "advisory_only": True,
    "script_allowed": False, "html_script_allowed": False, "external_fetch_allowed": False, "form_allowed": False,
    "button_allowed": False, "command_authority": False, "ui_command_authority": False, "action_authority": False,
    "recommendation_authority": False, "inference_authority": False, "prediction_allowed": False, "forecast_authority": False,
    "trend_prediction_allowed": False, "readiness_claims_allowed": False, "mutation_allowed": False, "authority_granted": False,
    "execution_authority": False, "routing_change_allowed": False, "queue_mutation_allowed": False, "canon_mutation_allowed": False,
    "runtime_mutation_allowed": False, "adaptive_behavior_allowed": False, "psychological_claims_allowed": False,
    "speculative_causation_allowed": False, "auto_execute": False, "auto_approve": False, "command_channel": False,
    "bidirectional_control": False,
}


def _read_text(path: Path) -> tuple[str | None, str]:
    try:
        return path.read_text(encoding="utf-8"), "PRESENT"
    except FileNotFoundError:
        return None, "MISSING"
    except OSError:
        return None, "CORRUPT"


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str]:
    text, status = _read_text(path)
    if status != "PRESENT" or text is None:
        return None, status
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None, "CORRUPT"
    return (payload, "PRESENT") if isinstance(payload, dict) else (None, "CORRUPT")


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_operator_narrative_static_preview_packet(*, export_bundle_path: str | Path = "out/exports/operator_narrative_export_bundle_001.latest.json", export_bundle_markdown_path: str | Path = "out/exports/operator_narrative_export_bundle_001.latest.md", export_bundle_packet: dict[str, Any] | None = None, governance_audit_path: str | Path = "out/audit/operator_narrative_export_bundle_governance_audit_001.latest.json", governance_audit_markdown_path: str | Path = "out/audit/operator_narrative_export_bundle_governance_audit_001.latest.md", governance_audit_packet: dict[str, Any] | None = None) -> dict[str, Any]:
    eb_path = Path(export_bundle_path)
    eb_md_path = Path(export_bundle_markdown_path)
    ga_path = Path(governance_audit_path)
    ga_md_path = Path(governance_audit_markdown_path)

    export_bundle, eb_status = (deepcopy(export_bundle_packet), "PRESENT") if export_bundle_packet is not None else _read_json(eb_path)
    governance_audit, ga_status = (deepcopy(governance_audit_packet), "PRESENT") if governance_audit_packet is not None else _read_json(ga_path)
    eb_md_text, eb_md_status = _read_text(eb_md_path)
    ga_md_text, ga_md_status = _read_text(ga_md_path)

    blockers: list[str] = []
    presence = {
        "export_bundle_json": eb_status,
        "export_bundle_markdown": eb_md_status,
        "governance_audit_json": ga_status,
        "governance_audit_markdown": ga_md_status,
    }
    for k, v in presence.items():
        if v != "PRESENT":
            blockers.append(f"source_{v.lower()}:{k}")

    bundle = export_bundle or {}
    audit = governance_audit or {}
    blockers.extend(str(x) for x in bundle.get("blocker_summary", []) if str(x).strip())
    blockers.extend(str(x) for x in audit.get("blocker_summary", []) if str(x).strip())

    missing_or_corrupt = eb_status != "PRESENT" or ga_status != "PRESENT"
    p46_status = str(bundle.get("final_status", NOT_COMPUTABLE))
    p47_status = str(audit.get("final_status", NOT_COMPUTABLE))
    if missing_or_corrupt:
        final_status, posture = "NOT_COMPUTABLE", "NOT_COMPUTABLE"
    elif p47_status in {"FAIL", "NOT_COMPUTABLE"} or p46_status in {"BLOCKED", "NOT_COMPUTABLE"}:
        final_status, posture = "BLOCKED", "BLOCKED"
    elif p47_status == "WARN" or p46_status == "EXPORT_DEGRADED":
        final_status, posture = "PREVIEW_DEGRADED", "DEGRADED"
    else:
        final_status, posture = "PREVIEW_ONLY", "COMPLETE"

    manifest = bundle.get("artifact_manifest", []) if isinstance(bundle.get("artifact_manifest"), list) else []
    hash_inventory = bundle.get("hash_inventory", {}) if isinstance(bundle.get("hash_inventory"), dict) else {}
    lineage = bundle.get("source_lineage_map", {}) if isinstance(bundle.get("source_lineage_map"), dict) else {}

    packet = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "preview_id": PREVIEW_ID,
        "final_status": final_status,
        "preview_posture": posture,
        "preview_sections": PREVIEW_SECTIONS,
        "static_preview_summary": {
            "artifact_manifest_count": len(manifest),
            "hash_inventory_count": len(hash_inventory),
            "lineage_key_count": len(lineage),
        },
        "manifest_preview": [{"artifact_id": str(m.get("artifact_id", "")), "role": str(m.get("role", "")), "path": str(m.get("path", "")), "sha256": str(m.get("sha256", ""))} for m in manifest if isinstance(m, dict)],
        "hash_inventory_preview": {k: hash_inventory[k] for k in sorted(hash_inventory)},
        "lineage_preview": {k: lineage[k] for k in sorted(lineage)},
        "governance_preview": deepcopy(bundle.get("governance_envelope", {})) if isinstance(bundle.get("governance_envelope"), dict) else {},
        "audit_preview": {
            "final_status": p47_status,
            "audit_posture": str(audit.get("audit_posture", NOT_COMPUTABLE)),
            "finding_counts": deepcopy(audit.get("finding_counts", {})) if isinstance(audit.get("finding_counts"), dict) else {},
        },
        "passive_references": {
            "report_json": "out/reports/operator_narrative_report_001.latest.json",
            "report_markdown": "out/reports/operator_narrative_report_001.latest.md",
            "ui_overlay_json": "out/projections/operator_narrative_report_ui_overlay_001.latest.json",
            "ui_overlay_markdown": "out/projections/operator_narrative_report_ui_overlay_001.latest.md",
            "export_bundle_json": eb_path.as_posix(),
            "export_bundle_markdown": eb_md_path.as_posix(),
            "export_bundle_governance_audit_json": ga_path.as_posix(),
            "export_bundle_governance_audit_markdown": ga_md_path.as_posix(),
        },
        "source_artifacts": {"export_bundle_json": eb_path.as_posix(), "export_bundle_markdown": eb_md_path.as_posix(), "governance_audit_json": ga_path.as_posix(), "governance_audit_markdown": ga_md_path.as_posix()},
        "source_hashes": {
            "export_bundle_json": canonical_hash(bundle) if bundle else NOT_COMPUTABLE,
            "export_bundle_markdown": _sha(eb_md_text) if eb_md_text is not None else NOT_COMPUTABLE,
            "governance_audit_json": canonical_hash(audit) if audit else NOT_COMPUTABLE,
            "governance_audit_markdown": _sha(ga_md_text) if ga_md_text is not None else NOT_COMPUTABLE,
        },
        "blocker_summary": sorted(set(b for b in blockers if str(b).strip())),
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {"source_packet_presence": presence, "deterministic": True, "preview_only": True, "read_only": True, "passive_preview_only": True, "fail_closed": True},
    }
    packet["preview_hash"] = canonical_hash(packet)
    return packet


def build_operator_narrative_static_preview_markdown(packet: dict[str, Any]) -> str:
    lines = ["# P48 Operator Narrative Static Preview Bundle", "", f"- preview_id: `{packet.get('preview_id','')}`", f"- final_status: `{packet.get('final_status','')}`", f"- preview_posture: `{packet.get('preview_posture','')}`", f"- preview_hash: `{packet.get('preview_hash','')}`", ""]
    for section in PREVIEW_SECTIONS:
        lines.append(f"## {section}")
        if section == "export_bundle_summary":
            s = packet.get("static_preview_summary", {})
            lines.extend([f"- artifact_manifest_count: `{s.get('artifact_manifest_count',0)}`", f"- hash_inventory_count: `{s.get('hash_inventory_count',0)}`", f"- lineage_key_count: `{s.get('lineage_key_count',0)}`"])
        elif section == "export_governance_audit":
            a = packet.get("audit_preview", {})
            lines.extend([f"- final_status: `{a.get('final_status','')}`", f"- audit_posture: `{a.get('audit_posture','')}`", f"- finding_counts: `{a.get('finding_counts',{})}`"])
        elif section == "artifact_manifest":
            for m in packet.get("manifest_preview", []):
                lines.append(f"- `{m.get('artifact_id','')}` :: `{m.get('role','')}` :: `{m.get('path','')}` :: `{m.get('sha256','')}`")
        elif section == "hash_inventory":
            for k, v in packet.get("hash_inventory_preview", {}).items():
                lines.append(f"- `{k}`: `{v}`")
        elif section == "source_lineage":
            for k, v in packet.get("lineage_preview", {}).items():
                lines.append(f"- `{k}`: `{v}`")
        elif section == "governance_boundary":
            for k, v in sorted(packet.get("governance_flags", {}).items()):
                lines.append(f"- `{k}`: `{v}`")
        elif section == "passive_references":
            for k, v in packet.get("passive_references", {}).items():
                lines.append(f"- `{k}`: `{v}`")
        elif section == "blockers":
            blockers = packet.get("blocker_summary", [])
            lines.extend([f"- `{b}`" for b in blockers] if blockers else ["- none"])
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def write_operator_narrative_static_preview_bundle(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_narrative_static_preview_markdown(packet), encoding="utf-8")
