from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.generated_artifact_registry import build_generated_artifact_registry

PATCH_ID = "PATCH-P46-OPERATOR-NARRATIVE-EXPORT-BUNDLE-001"
SCHEMA_VERSION = "OperatorNarrativeExportBundle.v1"
BUNDLE_ID = "operator_narrative_export_bundle_001"
NOT_COMPUTABLE = "NOT_COMPUTABLE"

_ROLE_ORDER: tuple[tuple[str, str, str], ...] = (
    ("p42_report_json", "report_json", "out/reports/operator_narrative_report_001.latest.json"),
    ("p42_report_markdown", "report_markdown", "out/reports/operator_narrative_report_001.latest.md"),
    ("p43_report_governance_audit_json", "report_governance_audit_json", "out/audit/operator_narrative_report_governance_audit_001.latest.json"),
    ("p43_report_governance_audit_markdown", "report_governance_audit_markdown", "out/audit/operator_narrative_report_governance_audit_001.latest.md"),
    ("p44_ui_overlay_json", "ui_overlay_json", "out/projections/operator_narrative_report_ui_overlay_001.latest.json"),
    ("p44_ui_overlay_markdown", "ui_overlay_markdown", "out/projections/operator_narrative_report_ui_overlay_001.latest.md"),
    ("p45_ui_overlay_governance_audit_json", "ui_overlay_governance_audit_json", "out/audit/operator_narrative_report_ui_overlay_governance_audit_001.latest.json"),
    ("p45_ui_overlay_governance_audit_markdown", "ui_overlay_governance_audit_markdown", "out/audit/operator_narrative_report_ui_overlay_governance_audit_001.latest.md"),
)

_GOVERNANCE_FLAGS: dict[str, Any] = {
    "export_only": True,
    "passive_bundle_only": True,
    "read_only": True,
    "advisory_only": True,
    "non_authoritative": True,
    "source_linked": True,
    "deterministic_manifest": True,
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


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_operator_narrative_export_bundle_packet(*, source_artifact_paths: dict[str, str] | None = None, source_packets: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    src_paths = {k: (Path(v) if source_artifact_paths and k in source_artifact_paths else Path(default)) for k, _, default in _ROLE_ORDER for v in [source_artifact_paths.get(k, default) if source_artifact_paths else default]}

    json_payloads: dict[str, dict[str, Any] | None] = {}
    presence: dict[str, str] = {}
    manifest: list[dict[str, Any]] = []
    source_hashes: dict[str, str] = {}
    blockers: list[str] = []

    for artifact_id, role, _ in _ROLE_ORDER:
        path = src_paths[artifact_id]
        if role.endswith("_json"):
            if source_packets and artifact_id in source_packets:
                payload = deepcopy(source_packets[artifact_id])
                text = json.dumps(payload, sort_keys=True)
                status = "PRESENT"
            else:
                payload, status = _read_json(path)
                text = json.dumps(payload, sort_keys=True) if isinstance(payload, dict) else ""
            json_payloads[artifact_id] = payload
        else:
            payload = None
            text, status = _read_text(path)
            json_payloads[artifact_id] = None
        presence[artifact_id] = status
        exists = status == "PRESENT"
        if status != "PRESENT":
            blockers.append(f"source_{status.lower()}:{artifact_id}")
        sha = _sha256_text(text) if exists and text is not None else NOT_COMPUTABLE
        source_hashes[artifact_id] = sha
        manifest.append({
            "artifact_id": artifact_id,
            "role": role,
            "path": path.as_posix(),
            "exists": exists,
            "readable": exists,
            "sha256": sha,
            "classification": "SEALED_SOURCE_ARTIFACT",
            "passive_reference_only": True,
        })

    p42 = json_payloads.get("p42_report_json") or {}
    p43 = json_payloads.get("p43_report_governance_audit_json") or {}
    p44 = json_payloads.get("p44_ui_overlay_json") or {}
    p45 = json_payloads.get("p45_ui_overlay_governance_audit_json") or {}

    for packet in (p42, p43, p44, p45):
        blockers.extend(str(b) for b in packet.get("blocker_summary", []) if str(b).strip())

    missing_or_corrupt = any(v != "PRESENT" for v in presence.values())
    p43_status = str(p43.get("final_status", NOT_COMPUTABLE))
    p45_status = str(p45.get("final_status", NOT_COMPUTABLE))
    p42_status = str(p42.get("final_status", NOT_COMPUTABLE))
    p44_status = str(p44.get("final_status", NOT_COMPUTABLE))

    if missing_or_corrupt:
        final_status, export_posture = "NOT_COMPUTABLE", "NOT_COMPUTABLE"
    elif p43_status in {"FAIL", "NOT_COMPUTABLE"} or p45_status in {"FAIL", "NOT_COMPUTABLE"}:
        final_status, export_posture = "BLOCKED", "BLOCKED"
    elif p43_status == "WARN" or p45_status == "WARN" or p42_status == "REPORT_DEGRADED" or p44_status == "PROJECTION_DEGRADED":
        final_status, export_posture = "EXPORT_DEGRADED", "DEGRADED"
    else:
        final_status, export_posture = "EXPORT_ONLY", "COMPLETE"

    source_lineage_map = {
        "p42_report_hash": str(p42.get("report_hash", NOT_COMPUTABLE)),
        "p42_source_hash_lineage": deepcopy(p42.get("source_hash_lineage", {})) if isinstance(p42.get("source_hash_lineage"), dict) else {},
        "p43_audit_hash": str(p43.get("audit_hash", NOT_COMPUTABLE)),
        "p44_overlay_hash": str(p44.get("overlay_hash", NOT_COMPUTABLE)),
        "p44_source_hash_lineage": deepcopy(p44.get("source_hash_lineage", {})) if isinstance(p44.get("source_hash_lineage"), dict) else {},
        "p45_audit_hash": str(p45.get("audit_hash", NOT_COMPUTABLE)),
        "p45_source_hash_lineage": deepcopy(p45.get("source_hash_lineage", {})) if isinstance(p45.get("source_hash_lineage"), dict) else {},
    }

    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    emap = {e.artifact_path: e for e in registry.entries}
    registry_classification_summary = {
        m["artifact_id"]: {
            "artifact_path": m["path"],
            "determinism_class": emap.get(m["path"]).determinism_class if emap.get(m["path"]) else "NOT_COMPUTABLE",
            "registry_final_status": emap.get(m["path"]).final_status if emap.get(m["path"]) else "untracked",
        }
        for m in manifest
    }

    packet = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "bundle_id": BUNDLE_ID,
        "final_status": final_status,
        "export_posture": export_posture,
        "artifact_manifest": manifest,
        "hash_inventory": {m["artifact_id"]: m["sha256"] for m in manifest},
        "source_lineage_map": {k: source_lineage_map[k] for k in sorted(source_lineage_map)},
        "governance_envelope": deepcopy(_GOVERNANCE_FLAGS),
        "registry_classification_summary": registry_classification_summary,
        "passive_export_notes": [
            "bundle is read-only and passive",
            "bundle packages sealed source artifacts by path and hash",
            "bundle contains no command or control semantics",
        ],
        "source_artifacts": {m["artifact_id"]: m["path"] for m in manifest},
        "source_hashes": {k: source_hashes[k] for k in sorted(source_hashes)},
        "blocker_summary": sorted(set(str(x).strip() for x in blockers if str(x).strip())),
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {
            "source_packet_presence": presence,
            "deterministic": True,
            "export_only": True,
            "read_only": True,
            "passive_bundle_only": True,
            "fail_closed": True,
        },
    }
    packet["bundle_hash"] = canonical_hash(packet)
    return packet


def build_operator_narrative_export_bundle_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P46 Operator Narrative Export Bundle",
        "",
        f"- bundle_id: `{packet.get('bundle_id', '')}`",
        f"- final_status: `{packet.get('final_status', '')}`",
        f"- export_posture: `{packet.get('export_posture', '')}`",
        f"- bundle_hash: `{packet.get('bundle_hash', '')}`",
        "",
        "## Artifact Manifest",
    ]
    for m in packet.get("artifact_manifest", []):
        lines.append(f"- `{m.get('artifact_id','')}` :: `{m.get('role','')}` :: `{m.get('path','')}` :: `{m.get('sha256','')}`")
    lines.extend(["", "## Passive Export Notes"])
    for n in packet.get("passive_export_notes", []):
        lines.append(f"- {n}")
    lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def write_operator_narrative_export_bundle_packet(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_narrative_export_bundle_markdown(packet), encoding="utf-8")
