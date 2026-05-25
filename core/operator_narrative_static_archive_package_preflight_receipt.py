from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "OperatorNarrativeStaticArchivePackagePreflightReceipt.v1"
PATCH_ID = "PATCH-P62-OPERATOR-NARRATIVE-STATIC-ARCHIVE-PACKAGE-PREFLIGHT-RECEIPT-001"
RECEIPT_ID = "operator_narrative_static_archive_package_preflight_receipt_001"
_NOT_COMPUTABLE = "NOT_COMPUTABLE"

_PACKAGE_PATH_PATTERNS = ["out/package", "out/packages", "out/archive_package", "out/static_archive_package", "out/static_archive", "out/distribution", "out/release"]
_REQUIRED_P60_TOKENS = ["P60_PLAN_READY", "P60_IMPLEMENTATION_PLANNING_REQUIRED"]
_REQUIRED_P60_CLAIMS = ["planning-only", "creates no package", "creates no package artifacts", "creates no package directories", "creates no package registry entries", "makes no distribution claim", "makes no release-readiness claim", "not mutate P52–P59 artifacts", "not suppress observed blockers"]
_REQUIRED_MANIFEST_FIELDS = ["schema_version", "patch_id", "package_id", "package_created", "package_mode", "static_only", "executable_payloads_present", "distribution_claims_allowed", "release_readiness_claimed", "artifact_role_order", "package_manifest", "source_hashes", "blocker_preservation_summary", "governance_flags", "package_hash"]
_REQUIRED_ENTRY_FIELDS = ["artifact_id", "source_patch", "role", "source_path", "included_as", "sha256", "canonical_hash", "exists", "readable", "sealed_reference_only", "executable_content_present", "active_surface_present"]
_REQUIRED_GATES = ["Static Archive Package Governance Audit", "Static Archive Package Language Boundary Audit", "Static Archive Package Stability Receipt", "Static Archive Package Global Verification Receipt"]
_DENY_FALSE = {"package_created", "package_implementation_allowed", "package_artifacts_created", "distribution_claims_allowed", "release_readiness_claimed", "command_authority", "ui_command_authority", "action_authority", "recommendation_authority", "inference_authority", "prediction_allowed", "forecast_authority", "trend_prediction_allowed", "readiness_claims_allowed", "mutation_allowed", "authority_granted", "execution_authority", "routing_change_allowed", "queue_mutation_allowed", "canon_mutation_allowed", "runtime_mutation_allowed"}
_GOVERNANCE_FLAGS = {
    "preflight_receipt_only": True, "package_preflight_only": True, "advisory_only": True, "read_only": True, "non_authoritative": True,
    "source_linked": True, "deterministic_receipt": True, "package_absence_checked": True, "boundary_receipt_checked": True, "implementation_planning_checked": True,
    "package_created": False, "distribution_claims_allowed": False, "release_readiness_claimed": False, "package_implementation_allowed": False, "package_artifacts_created": False,
    "command_authority": False, "ui_command_authority": False, "action_authority": False, "recommendation_authority": False, "inference_authority": False,
    "prediction_allowed": False, "forecast_authority": False, "trend_prediction_allowed": False, "readiness_claims_allowed": False, "mutation_allowed": False,
    "authority_granted": False, "execution_authority": False, "routing_change_allowed": False, "queue_mutation_allowed": False, "canon_mutation_allowed": False,
    "runtime_mutation_allowed": False, "adaptive_behavior_allowed": False, "psychological_claims_allowed": False, "speculative_causation_allowed": False,
    "auto_execute": False, "auto_approve": False, "command_channel": False, "bidirectional_control": False, "script_allowed": False,
    "html_script_allowed": False, "external_fetch_allowed": False, "form_allowed": False, "button_allowed": False,
}


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "MISSING"
    except (OSError, json.JSONDecodeError):
        return None, "CORRUPT"
    return (payload, "PRESENT") if isinstance(payload, dict) else (None, "CORRUPT")


def _find_package_surfaces(root: Path) -> list[str]:
    found = []
    for rel in _PACKAGE_PATH_PATTERNS:
        if (root / rel).exists():
            found.append(rel)
    found.extend(str(p.relative_to(root)).replace("\\", "/") for p in root.glob("packages/operator_narrative_static_archive_package*"))
    found.extend(str(p.relative_to(root)).replace("\\", "/") for p in root.glob("docs/plans/P62_static_archive_package_implementation*"))
    found.extend(str(p.relative_to(root)).replace("\\", "/") for p in root.glob("**/operator_narrative_static_archive_package_*.latest.json") if "boundary_receipt" not in p.name and "preflight_receipt" not in p.name)
    found.extend(str(p.relative_to(root)).replace("\\", "/") for p in root.glob("**/operator_narrative_static_archive_package_*.latest.md") if "boundary_receipt" not in p.name and "preflight_receipt" not in p.name)
    return sorted(set(found))


def build_operator_narrative_static_archive_package_preflight_receipt_packet(*, p60_planning_path: str | Path = "docs/plans/P60_planning_gate_static_archive_package_implementation.md", p59_receipt_path: str | Path = "out/audit/operator_narrative_static_archive_package_boundary_receipt_001.latest.json", repo_root: str | Path = ".") -> dict[str, Any]:
    root = Path(repo_root)
    p60_path = root / Path(p60_planning_path)
    p59_path = root / Path(p59_receipt_path)
    blockers: list[str] = []
    try:
        p60_text = p60_path.read_text(encoding="utf-8")
        p60_status = "PRESENT"
    except FileNotFoundError:
        p60_text = ""
        p60_status = "MISSING"
        blockers.append("p60 planning doc missing")
    except OSError:
        p60_text = ""
        p60_status = "CORRUPT"
        blockers.append("p60 planning doc unreadable")

    p59, p59_status = _read_json(p59_path)
    if p59_status != "PRESENT":
        blockers.append(f"p59 boundary receipt json unreadable ({p59_status})")

    for token in _REQUIRED_P60_TOKENS + _REQUIRED_P60_CLAIMS + _REQUIRED_MANIFEST_FIELDS + _REQUIRED_ENTRY_FIELDS + _REQUIRED_GATES:
        if p60_status == "PRESENT" and token not in p60_text:
            blockers.append(f"missing p60 required token: {token}")

    if p59:
        if p59.get("final_status") != "BOUNDARY_RECEIPT_PASS":
            blockers.append("p59 final_status must be BOUNDARY_RECEIPT_PASS")
        if p59.get("boundary_posture") != "BOUNDARY_VERIFIED":
            blockers.append("p59 boundary_posture must be BOUNDARY_VERIFIED")
        flags = p59.get("governance_flags", {}) if isinstance(p59.get("governance_flags"), dict) else {}
        for key in _DENY_FALSE:
            if flags.get(key) is not False:
                blockers.append(f"p59 governance flag not denied: {key}")

    package_surfaces = _find_package_surfaces(root)
    if package_surfaces:
        blockers.append("package-like surfaces present")

    registry_path = root / "core/generated_artifact_registry.py"
    registry_text = registry_path.read_text(encoding="utf-8") if registry_path.exists() else ""
    registry_hits = []
    for line in registry_text.splitlines():
        if "operator_narrative_static_archive_package_" in line and "boundary_receipt" not in line and "preflight_receipt" not in line:
            registry_hits.append(line.strip())
        if "static_archive_package_manifest" in line or "archive_package_manifest" in line:
            registry_hits.append(line.strip())
    if registry_hits:
        blockers.append("generated artifact registry contains package artifact naming")

    if p60_status != "PRESENT" or p59_status != "PRESENT":
        final_status, posture = "NOT_COMPUTABLE", "NOT_COMPUTABLE"
    elif blockers:
        final_status, posture = "PREFLIGHT_RECEIPT_FAIL", "PREFLIGHT_FAILED"
    else:
        final_status, posture = "PREFLIGHT_RECEIPT_PASS", "PREFLIGHT_VERIFIED"

    packet = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "receipt_id": RECEIPT_ID,
        "final_status": final_status,
        "preflight_posture": posture,
        "checked_artifacts": {"p60_planning_path": p60_path.as_posix(), "p59_boundary_json_path": p59_path.as_posix(), "registry_path": registry_path.as_posix()},
        "p60_planning_summary": {"presence": p60_status, "decision_labels_checked": deepcopy(_REQUIRED_P60_TOKENS)},
        "p59_boundary_summary": {"presence": p59_status, "final_status": (p59 or {}).get("final_status", _NOT_COMPUTABLE), "boundary_posture": (p59 or {}).get("boundary_posture", _NOT_COMPUTABLE)},
        "package_absence_summary": {"package_surfaces_found": package_surfaces, "package_surfaces_absent": not package_surfaces},
        "implementation_boundary_summary": {"required_planning_claims": deepcopy(_REQUIRED_P60_CLAIMS)},
        "reference_manifest_summary": {"required_manifest_fields": deepcopy(_REQUIRED_MANIFEST_FIELDS), "required_manifest_entry_fields": deepcopy(_REQUIRED_ENTRY_FIELDS)},
        "required_future_gate_summary": {"required_gates": deepcopy(_REQUIRED_GATES)},
        "governance_boundary_summary": {"forbidden_authority_flags_false": sorted(_DENY_FALSE), "no_authority_escalation": True},
        "registry_absence_summary": {"registry_package_tokens": registry_hits, "registry_package_surface_absent": not registry_hits},
        "source_hashes": {"p60_planning_doc": canonical_hash({"text": p60_text}) if p60_status == "PRESENT" else _NOT_COMPUTABLE, "p59_boundary_receipt": canonical_hash(p59) if p59 else _NOT_COMPUTABLE, "generated_artifact_registry": canonical_hash({"text": registry_text}) if registry_text else _NOT_COMPUTABLE},
        "blocker_summary": sorted(set(blockers)),
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {"deterministic": True, "read_only": True, "source_linked": True, "non_authoritative": True, "fail_closed": True},
    }
    packet["preflight_hash"] = canonical_hash(packet)
    return packet


def build_operator_narrative_static_archive_package_preflight_receipt_markdown(packet: dict[str, Any]) -> str:
    lines = ["# P62 Static Archive Package Preflight Receipt", "", f"- receipt_id: `{packet.get('receipt_id', '')}`", f"- final_status: `{packet.get('final_status', '')}`", f"- preflight_posture: `{packet.get('preflight_posture', '')}`", f"- preflight_hash: `{packet.get('preflight_hash', '')}`", "", "## Preflight Checks"]
    for k, v in (packet.get("checked_artifacts") or {}).items():
        lines.append(f"- `{k}`: `{v}`")
    lines.extend(["", "## Package Preflight Denied Surfaces"])
    pas = packet.get("package_absence_summary", {})
    if pas.get("package_surfaces_found"):
        for item in pas["package_surfaces_found"]:
            lines.append(f"- found: `{item}`")
    else:
        lines.append("- no package artifacts/directories created")
    lines.extend(["", "## Blockers"])
    blockers = packet.get("blocker_summary", [])
    lines.extend([f"- `{b}`" for b in blockers] if blockers else ["- none"])
    lines.extend(["", "## Governance Flags"])
    for k, v in (packet.get("governance_flags") or {}).items():
        lines.append(f"- `{k}`: `{v}`")
    return "\n".join(lines).rstrip("\n") + "\n"


def write_operator_narrative_static_archive_package_preflight_receipt(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_narrative_static_archive_package_preflight_receipt_markdown(packet), encoding="utf-8")
