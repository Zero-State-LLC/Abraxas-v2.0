from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "OperatorNarrativeStaticArchivePackageBoundaryReceipt.v1"
PATCH_ID = "PATCH-P59-OPERATOR-NARRATIVE-STATIC-ARCHIVE-PACKAGE-BOUNDARY-RECEIPT-001"
RECEIPT_ID = "operator_narrative_static_archive_package_boundary_receipt_001"

_NOT_COMPUTABLE = "NOT_COMPUTABLE"
_PACKAGE_PATH_PATTERNS = [
    "out/package",
    "out/packages",
    "out/archive_package",
    "out/static_archive_package",
    "out/static_archive",
    "out/distribution",
    "out/release",
]
_REQUIRED_P58_TOKENS = ["P58_PLAN_READY", "P58_PACKAGE_PLANNING_REQUIRED"]
_REQUIRED_P58_BOUNDARY = [
    "Package planning is not package creation.",
    "P58 does **not** create package artifacts.",
    "No package generation.",
    "No distribution or release-readiness claim.",
    "No mutation of P52–P57 artifacts.",
    "No blocker suppression.",
]
_REQUIRED_P58_CONSTRAINTS = [
    "static-only",
    "non-executable",
    "hash-manifested",
    "source-linked",
    "blocker-preserving",
    "built only from pre-existing sealed artifacts or passive references",
    "governance-audited in a later package governance audit lane",
]
_REQUIRED_P58_FORBIDDEN = [
    "contain scripts",
    "contain forms",
    "contain buttons",
    "perform external fetch",
    "contain executable payloads",
    "assert distribution readiness",
    "assert release readiness",
    "suppress blockers",
    "mutate P52–P57 artifacts",
    "free of command/action/recommendation/forecast/readiness authority",
]
_DENY_FALSE = {
    "package_created",
    "distribution_claims_allowed",
    "release_readiness_claimed",
    "command_authority",
    "ui_command_authority",
    "action_authority",
    "recommendation_authority",
    "inference_authority",
    "prediction_allowed",
    "forecast_authority",
    "trend_prediction_allowed",
    "readiness_claims_allowed",
    "mutation_allowed",
    "authority_granted",
    "execution_authority",
    "routing_change_allowed",
    "queue_mutation_allowed",
    "canon_mutation_allowed",
    "runtime_mutation_allowed",
}
_GOVERNANCE_FLAGS = {
    "boundary_receipt_only": True,
    "package_boundary_only": True,
    "advisory_only": True,
    "read_only": True,
    "non_authoritative": True,
    "source_linked": True,
    "deterministic_receipt": True,
    "package_absence_checked": True,
    "global_verification_checked": True,
    "package_created": False,
    "distribution_claims_allowed": False,
    "release_readiness_claimed": False,
    "package_implementation_allowed": False,
    "package_artifacts_created": False,
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
    found.extend(str(p.relative_to(root)).replace("\\", "/") for p in root.glob("docs/plans/P59_static_archive_package_implementation*"))
    found.extend(str(p.relative_to(root)).replace("\\", "/") for p in root.glob("**/operator_narrative_static_archive_package_*.latest.json") if "boundary_receipt" not in p.name)
    found.extend(str(p.relative_to(root)).replace("\\", "/") for p in root.glob("**/operator_narrative_static_archive_package_*.latest.md") if "boundary_receipt" not in p.name)
    return sorted(set(found))


def build_operator_narrative_static_archive_package_boundary_receipt_packet(*, p58_planning_path: str | Path = "docs/plans/P58_planning_gate_static_archive_package.md", p57_receipt_path: str | Path = "out/audit/operator_narrative_archive_chain_global_verification_001.latest.json", repo_root: str | Path = ".") -> dict[str, Any]:
    root = Path(repo_root)
    p58_path = root / Path(p58_planning_path)
    p57_path = root / Path(p57_receipt_path)
    blockers: list[str] = []

    try:
        p58_text = p58_path.read_text(encoding="utf-8")
        p58_status = "PRESENT"
    except FileNotFoundError:
        p58_text = ""
        p58_status = "MISSING"
        blockers.append("p58 planning doc missing")
    except OSError:
        p58_text = ""
        p58_status = "CORRUPT"
        blockers.append("p58 planning doc unreadable")

    p57, p57_status = _read_json(p57_path)
    if p57_status != "PRESENT":
        blockers.append(f"p57 global verification json unreadable ({p57_status})")

    for token in _REQUIRED_P58_TOKENS:
        if p58_status == "PRESENT" and token not in p58_text:
            blockers.append(f"missing p58 decision label: {token}")
    for token in _REQUIRED_P58_BOUNDARY:
        if p58_status == "PRESENT" and token not in p58_text:
            blockers.append(f"missing p58 boundary claim: {token}")
    for token in _REQUIRED_P58_CONSTRAINTS:
        if p58_status == "PRESENT" and token not in p58_text:
            blockers.append(f"missing p58 package constraint: {token}")
    for token in _REQUIRED_P58_FORBIDDEN:
        if p58_status == "PRESENT" and token not in p58_text:
            blockers.append(f"missing p58 forbidden scope: {token}")

    if p57:
        if p57.get("final_status") != "GLOBAL_VERIFICATION_PASS":
            blockers.append("p57 final_status must be GLOBAL_VERIFICATION_PASS")
        if p57.get("verification_posture") != "VERIFIED":
            blockers.append("p57 verification_posture must be VERIFIED")
        flags = p57.get("governance_flags", {}) if isinstance(p57.get("governance_flags"), dict) else {}
        for key in _DENY_FALSE:
            if flags.get(key) is not False:
                blockers.append(f"p57 governance flag not denied: {key}")

    package_surfaces = _find_package_surfaces(root)
    if package_surfaces:
        blockers.append("package-like surfaces present")

    registry_path = root / "core/generated_artifact_registry.py"
    registry_text = registry_path.read_text(encoding="utf-8") if registry_path.exists() else ""
    registry_hits = []
    for line in registry_text.splitlines():
        if "operator_narrative_static_archive_package_" in line and "boundary_receipt" not in line:
            registry_hits.append(line.strip())
        if "package_manifest" in line and "operator_narrative" in line:
            registry_hits.append(line.strip())
    if registry_hits:
        blockers.append("generated artifact registry contains package artifact naming")

    not_computable = p58_status != "PRESENT" or p57_status != "PRESENT"
    if not_computable:
        final_status, posture = "NOT_COMPUTABLE", "NOT_COMPUTABLE"
    elif blockers:
        final_status, posture = "BOUNDARY_RECEIPT_FAIL", "BOUNDARY_FAILED"
    else:
        final_status, posture = "BOUNDARY_RECEIPT_PASS", "BOUNDARY_VERIFIED"

    packet = {
        "schema_version": SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "receipt_id": RECEIPT_ID,
        "final_status": final_status,
        "boundary_posture": posture,
        "checked_artifacts": {
            "p58_planning_path": p58_path.as_posix(),
            "p57_verification_json_path": p57_path.as_posix(),
            "registry_path": registry_path.as_posix(),
        },
        "p58_boundary_summary": {"presence": p58_status, "decision_labels_checked": deepcopy(_REQUIRED_P58_TOKENS)},
        "p57_verification_summary": {
            "presence": p57_status,
            "final_status": (p57 or {}).get("final_status", _NOT_COMPUTABLE),
            "verification_posture": (p57 or {}).get("verification_posture", _NOT_COMPUTABLE),
        },
        "package_absence_summary": {"package_surfaces_found": package_surfaces, "package_surfaces_absent": not package_surfaces},
        "package_constraint_summary": {"required_constraints": deepcopy(_REQUIRED_P58_CONSTRAINTS)},
        "forbidden_scope_summary": {"required_forbidden_scope": deepcopy(_REQUIRED_P58_FORBIDDEN)},
        "governance_boundary_summary": {"forbidden_authority_flags_false": sorted(_DENY_FALSE), "no_authority_escalation": True},
        "registry_absence_summary": {"registry_package_tokens": registry_hits, "registry_package_surface_absent": not registry_hits},
        "source_hashes": {
            "p58_planning_doc": canonical_hash({"text": p58_text}) if p58_status == "PRESENT" else _NOT_COMPUTABLE,
            "p57_global_verification": canonical_hash(p57) if p57 else _NOT_COMPUTABLE,
            "generated_artifact_registry": canonical_hash({"text": registry_text}) if registry_text else _NOT_COMPUTABLE,
        },
        "blocker_summary": sorted(set(blockers)),
        "governance_flags": deepcopy(_GOVERNANCE_FLAGS),
        "provenance": {"deterministic": True, "read_only": True, "source_linked": True, "non_authoritative": True, "fail_closed": True},
    }
    packet["boundary_hash"] = canonical_hash(packet)
    return packet


def build_operator_narrative_static_archive_package_boundary_receipt_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# P59 Static Archive Package Governance Boundary Receipt",
        "",
        f"- receipt_id: `{packet.get('receipt_id', '')}`",
        f"- final_status: `{packet.get('final_status', '')}`",
        f"- boundary_posture: `{packet.get('boundary_posture', '')}`",
        f"- boundary_hash: `{packet.get('boundary_hash', '')}`",
        "",
        "## Boundary Checks",
    ]
    for k, v in (packet.get("checked_artifacts") or {}).items():
        lines.append(f"- `{k}`: `{v}`")
    lines.extend(["", "## Package Boundary Denied Surfaces"])
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


def write_operator_narrative_static_archive_package_boundary_receipt(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(
        build_operator_narrative_static_archive_package_boundary_receipt_markdown(packet), encoding="utf-8"
    )
