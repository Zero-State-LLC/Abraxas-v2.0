from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.generated_artifact_registry import build_generated_artifact_registry

SCHEMA_VERSION = "OperatorNarrativeStaticArchivePackageLanguageBoundaryAudit.v1"
PATCH_ID = "PATCH-P66-OPERATOR-NARRATIVE-STATIC-ARCHIVE-PACKAGE-LANGUAGE-BOUNDARY-AUDIT-001"
AUDIT_ID = "operator_narrative_static_archive_package_language_boundary_audit_001"

FORBIDDEN_PHRASES = [
    "distribute", "distribution approved", "release ready", "release-ready", "readiness approved", "deploy", "deployment", "recommend", "should use", "take action", "execute", "command authority", "forecast", "prediction", "will happen", "approve for use", "production ready", "final release", "shipment", "publish now",
]
_ALLOWED_CONTEXT_TOKENS = [
    "distribution_claims_allowed=false", "release_readiness_claimed=false", "no distribution claim", "no release-readiness claim", "not release-ready", "non-distribution", "forbidden", "denied", "false", "boundary", "audit-only", "non-authoritative", "static-only", "no command/action/forecast/readiness authority",
]
_SKIP_KEY_SUBSTRINGS = ["status", "posture", "schema_version", "patch_id", "audit_id"]

def _finding_id(category: str, message: str, refs: list[str]) -> str:
    basis = f"{category}|{' '.join(message.split()).strip().lower()}|{'|'.join(sorted(refs))}"
    return hashlib.sha256(basis.encode()).hexdigest()


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str, str]:
    try:
        txt = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None, "MISSING", ""
    except OSError:
        return None, "CORRUPT", ""
    try:
        data = json.loads(txt)
    except json.JSONDecodeError:
        return None, "CORRUPT", txt
    return (data if isinstance(data, dict) else None), ("PRESENT" if isinstance(data, dict) else "CORRUPT"), txt


def _allowed_context(text: str) -> bool:
    low = text.lower()
    return any(token in low for token in _ALLOWED_CONTEXT_TOKENS)


def _extract_json_strings(value: Any, path: str = "$") -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for k, v in value.items():
            out.extend(_extract_json_strings(v, f"{path}.{k}"))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            out.extend(_extract_json_strings(v, f"{path}[{i}]"))
    elif isinstance(value, str):
        out.append((path, value))
    return out


def _should_scan_json_path(path: str, text: str) -> bool:
    low_path = path.lower()
    if any(token in low_path for token in _SKIP_KEY_SUBSTRINGS):
        return False
    if any(token in low_path for token in ["distribution_claims_allowed", "release_readiness_claimed", "readiness_claims_allowed"]):
        return False
    if text.strip().lower() in {"false", "denied", "forbidden", "not created", "not release-ready", "non-distribution", "boundary", "audit-only", "non-authoritative", "static-only"}:
        return False
    return True


def _scan_text(surface: str, source_label: str, findings: list[dict[str, Any]], add_blocker: callable) -> dict[str, int]:
    counts = {"checked": 0, "flagged": 0}
    lines = surface.splitlines()
    for i, line in enumerate(lines, 1):
        low = line.lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase in low:
                counts["checked"] += 1
                if _allowed_context(line):
                    continue
                counts["flagged"] += 1
                msg = f"forbidden unnegated phrase '{phrase}' in {source_label}:{i}"
                ref = f"{source_label}:{i}"
                findings.append({"finding_id": _finding_id("LANGUAGE", msg, [ref]), "severity": "FAIL", "category": "LANGUAGE", "message": msg, "evidence_refs": [ref]})
                add_blocker(msg)
    return counts


def build_operator_narrative_static_archive_package_language_boundary_audit_packet(*, package_json_path: str | Path = "out/package/operator_narrative_static_archive_package_001.latest.json", package_md_path: str | Path = "out/package/operator_narrative_static_archive_package_001.latest.md", p65_json_path: str | Path = "out/audit/operator_narrative_static_archive_package_governance_audit_001.latest.json", p65_md_path: str | Path = "out/audit/operator_narrative_static_archive_package_governance_audit_001.latest.md", repo_root: str | Path = ".") -> dict[str, Any]:
    root = Path(repo_root)
    p64j, p64m, p65j, p65m = root / Path(package_json_path), root / Path(package_md_path), root / Path(p65_json_path), root / Path(p65_md_path)
    findings: list[dict[str, Any]] = []
    blockers: list[str] = []
    add_blocker = blockers.append

    p64_data, p64_status, p64_raw = _read_json(p64j)
    p65_data, p65_status, p65_raw = _read_json(p65j)
    p64_md = p64m.read_text(encoding="utf-8") if p64m.exists() else ""
    p65_md = p65m.read_text(encoding="utf-8") if p65m.exists() else ""

    if p64_status != "PRESENT" or not p64m.exists():
        findings.append({"finding_id": _finding_id("SURFACE", "p64 surface missing or corrupt", [p64j.as_posix(), p64m.as_posix()]), "severity": "FAIL", "category": "SURFACE", "message": "p64 surface missing or corrupt", "evidence_refs": [p64j.as_posix(), p64m.as_posix()]})
        blockers.append("p64 surface missing or corrupt")
    if p65_status != "PRESENT" or not p65m.exists():
        findings.append({"finding_id": _finding_id("SURFACE", "p65 surface missing or corrupt", [p65j.as_posix(), p65m.as_posix()]), "severity": "FAIL", "category": "SURFACE", "message": "p65 surface missing or corrupt", "evidence_refs": [p65j.as_posix(), p65m.as_posix()]})
        blockers.append("p65 surface missing or corrupt")

    if p65_data:
        if p65_data.get("final_status") != "PACKAGE_GOVERNANCE_AUDIT_PASS":
            blockers.append("p65 final_status not PACKAGE_GOVERNANCE_AUDIT_PASS")
        if p65_data.get("audit_posture") != "PACKAGE_GOVERNANCE_CLEAN":
            blockers.append("p65 audit_posture not PACKAGE_GOVERNANCE_CLEAN")

    scan_summary = {"p64_md": {"checked": 0, "flagged": 0}, "p65_md": {"checked": 0, "flagged": 0}, "p64_json": {"checked": 0, "flagged": 0}, "p65_json": {"checked": 0, "flagged": 0}}
    scan_summary["p64_md"] = _scan_text(p64_md, p64m.as_posix(), findings, add_blocker)
    scan_summary["p65_md"] = _scan_text(p65_md, p65m.as_posix(), findings, add_blocker)

    for label, payload in [("p64_json", p64_data), ("p65_json", p65_data)]:
        if not payload:
            continue
        strings = _extract_json_strings(payload)
        for path, text in strings:
            if not _should_scan_json_path(path, text):
                continue
            scan_summary[label]["checked"] += 1
            low = text.lower()
            for phrase in FORBIDDEN_PHRASES:
                if phrase in low and not _allowed_context(text):
                    scan_summary[label]["flagged"] += 1
                    msg = f"forbidden unnegated phrase '{phrase}' in {label}{path}"
                    ref = f"{label}{path}"
                    findings.append({"finding_id": _finding_id("LANGUAGE", msg, [ref]), "severity": "FAIL", "category": "LANGUAGE", "message": msg, "evidence_refs": [ref]})
                    blockers.append(msg)

    counts = {"PASS": 0, "WARN": 0, "FAIL": sum(1 for f in findings if f["severity"] == "FAIL")}
    not_comp = p64_status != "PRESENT" or p65_status != "PRESENT" or not p64m.exists() or not p65m.exists()
    if not_comp:
        final_status, posture = "NOT_COMPUTABLE", "NOT_COMPUTABLE"
    elif blockers:
        final_status, posture = "PACKAGE_LANGUAGE_BOUNDARY_FAIL", "LANGUAGE_BOUNDARY_FAILED"
    else:
        final_status, posture = "PACKAGE_LANGUAGE_BOUNDARY_PASS", "LANGUAGE_BOUNDARY_CLEAN"

    reg = build_generated_artifact_registry(root)
    emap = {e.artifact_path: e for e in reg.entries}

    gflags = {"audit_only": True, "language_boundary_audit_only": True, "advisory_only": True, "read_only": True, "non_authoritative": True, "source_linked": True, "deterministic_audit": True,
        "package_created": False, "package_artifacts_created": False, "distribution_claims_allowed": False, "release_readiness_claimed": False, "command_authority": False, "ui_command_authority": False, "action_authority": False, "recommendation_authority": False, "inference_authority": False, "prediction_allowed": False, "forecast_authority": False, "trend_prediction_allowed": False, "readiness_claims_allowed": False, "mutation_allowed": False, "authority_granted": False, "execution_authority": False, "routing_change_allowed": False, "queue_mutation_allowed": False, "canon_mutation_allowed": False, "runtime_mutation_allowed": False, "adaptive_behavior_allowed": False, "auto_execute": False, "auto_approve": False, "command_channel": False, "bidirectional_control": False, "script_allowed": False, "html_script_allowed": False, "external_fetch_allowed": False, "form_allowed": False, "button_allowed": False}

    packet = {"schema_version": SCHEMA_VERSION, "patch_id": PATCH_ID, "audit_id": AUDIT_ID, "final_status": final_status, "audit_posture": posture,
              "checked_artifacts": {"p64_json": p64j.as_posix(), "p64_md": p64m.as_posix(), "p65_json": p65j.as_posix(), "p65_md": p65m.as_posix()},
              "findings": findings, "finding_counts": counts, "language_scan_summary": scan_summary,
              "allowed_context_summary": {"allowed_context_tokens": _ALLOWED_CONTEXT_TOKENS},
              "p65_dependency_summary": {"final_status": (p65_data or {}).get("final_status", "NOT_COMPUTABLE"), "audit_posture": (p65_data or {}).get("audit_posture", "NOT_COMPUTABLE")},
              "package_status_summary": {"final_status": (p64_data or {}).get("final_status", "NOT_COMPUTABLE"), "package_created": (p64_data or {}).get("package_created", "NOT_COMPUTABLE")},
              "source_hashes": {"p64_json": hashlib.sha256(p64_raw.encode()).hexdigest() if p64_raw else "NOT_COMPUTABLE", "p64_md": hashlib.sha256(p64_md.encode()).hexdigest() if p64_md else "NOT_COMPUTABLE", "p65_json": hashlib.sha256(p65_raw.encode()).hexdigest() if p65_raw else "NOT_COMPUTABLE", "p65_md": hashlib.sha256(p65_md.encode()).hexdigest() if p65_md else "NOT_COMPUTABLE"},
              "blocker_summary": sorted(set(blockers)), "governance_flags": gflags,
              "provenance": {"deterministic": True, "read_only": True, "source_linked": True, "non_authoritative": True, "fail_closed": True}}
    packet["audit_hash"] = canonical_hash(packet)
    _ = emap
    return packet


def build_operator_narrative_static_archive_package_language_boundary_audit_markdown(packet: dict[str, Any]) -> str:
    lines = ["# P66 Static Archive Package Language Boundary Audit", "", f"- audit_id: `{packet.get('audit_id','')}`", f"- final_status: `{packet.get('final_status','')}`", f"- audit_posture: `{packet.get('audit_posture','')}`", f"- audit_hash: `{packet.get('audit_hash','')}`", "", "## Findings"]
    if packet.get("findings"):
        for f in packet["findings"]:
            lines.append(f"- [{f['severity']}] {f['category']}: {f['message']}")
    else:
        lines.append("- none")
    return "\n".join(lines).rstrip("\n") + "\n"


def write_operator_narrative_static_archive_package_language_boundary_audit(path: Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
    path.with_suffix(".md").write_text(build_operator_narrative_static_archive_package_language_boundary_audit_markdown(packet), encoding="utf-8")
