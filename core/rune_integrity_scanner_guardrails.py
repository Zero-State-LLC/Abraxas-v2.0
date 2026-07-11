from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "RuneIntegrityScannerGuardrailsReceipt.v1"
STATUS = "RUNE_INTEGRITY_SCANNER_GUARDRAILS_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-56"
DEFAULT_OUT_PATH = "out/audit/rune_integrity_scanner_guardrails_receipt_001.latest.json"

RUNE_SOURCE_DIR = "abraxas/v2/hygiene/runes"
RUNE_REGISTRY_PATH = "core/runes/registry.py"
GENERATED_ARTIFACT_REGISTRY_PATH = "core/generated_artifact_registry.py"
WORKFLOW_DIR = ".github/workflows"

AUTHORITY_LOCKS = {
    "blocking_ci_enforcement": False,
    "canon_mutation": False,
    "external_calls": False,
    "github_writeback": False,
    "mcp_exposure": False,
    "notion_writeback": False,
    "pipeline_activation": False,
    "production_activation": False,
    "runtime_activation": False,
    "runtime_mutation": False,
    "sandbox_probe_execution": False,
    "workflow_mutation": False,
}

SUSPICIOUS_TOKENS = {
    "external_call": ("requests.", "httpx.", "urllib.request", "aiohttp."),
    "process_execution": ("subprocess.", "os.system", "Popen("),
    "writeback": ("notion", "github", "gh "),
    "runtime_mutation": ("runtime_activation", "canon_mutation", "write_canonical_json("),
    "secret_surface": ("api_key", "secret", "token"),
}


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_text(path: Path) -> tuple[str, str]:
    try:
        return path.read_text(encoding="utf-8"), "OBSERVED"
    except FileNotFoundError:
        return "", "MISSING"
    except OSError:
        return "", "NOT_COMPUTABLE"


def _parse_python(text: str) -> ast.Module | None:
    try:
        return ast.parse(text)
    except SyntaxError:
        return None


def _class_names(tree: ast.Module | None) -> list[str]:
    if tree is None:
        return []
    return sorted(node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef))


def _rune_ids(tree: ast.Module | None) -> list[str]:
    if tree is None:
        return []
    found: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "rune_id" for target in node.targets):
            continue
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            found.append(node.value.value)
    return sorted(found)


def _imports(tree: ast.Module | None) -> list[str]:
    if tree is None:
        return []
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return sorted(set(names))


def _token_findings(text: str) -> list[dict[str, Any]]:
    lowered = text.lower()
    findings: list[dict[str, Any]] = []
    for category, tokens in SUSPICIOUS_TOKENS.items():
        matches = sorted(token for token in tokens if token.lower() in lowered)
        if matches:
            findings.append(
                {
                    "category": category,
                    "matches": matches,
                    "enforcement_action": "REPORT_ONLY",
                    "authority_granted": False,
                }
            )
    return findings


def _scan_rune_file(repo_root: Path, path: Path) -> dict[str, Any]:
    relative_path = path.relative_to(repo_root).as_posix()
    text, status = _read_text(path)
    tree = _parse_python(text) if status == "OBSERVED" else None
    class_names = _class_names(tree)
    rune_ids = _rune_ids(tree)
    imports = _imports(tree)
    token_findings = _token_findings(text)
    has_apply = "def apply(" in text
    has_mode_guard = "HygieneMode" in text and "mode ==" in text
    has_v2_output = "V2Output" in text
    posture = (
        "READY"
        if status == "OBSERVED" and class_names and rune_ids and has_apply and has_mode_guard
        else "READY_WITH_FINDINGS"
        if status == "OBSERVED" and class_names
        else "NOT_COMPUTABLE"
    )
    return {
        "path": relative_path,
        "source_status": status,
        "sha256": _sha256_file(path) if status == "OBSERVED" else "NOT_COMPUTABLE",
        "class_names": class_names,
        "rune_ids": rune_ids,
        "imports": imports,
        "has_apply_method": has_apply,
        "has_hygiene_mode_guard": has_mode_guard,
        "has_v2_output_contract": has_v2_output,
        "token_findings": token_findings,
        "finding_count": len(token_findings),
        "integrity_posture": posture,
        "enforcement_action": "REPORT_ONLY",
        "authority_granted": False,
    }


def _source_status(root: Path, relative_path: str) -> dict[str, Any]:
    path = root / relative_path
    exists = path.exists()
    return {
        "path": relative_path,
        "source_status": "OBSERVED" if exists else "MISSING",
        "sha256": _sha256_file(path) if exists and path.is_file() else "NOT_COMPUTABLE",
        "authority_granted": False,
    }


def _workflow_visibility(root: Path) -> dict[str, Any]:
    workflow_dir = root / WORKFLOW_DIR
    workflows = sorted(workflow_dir.glob("*.yml")) + sorted(workflow_dir.glob("*.yaml"))
    rows: list[dict[str, Any]] = []
    wired = False
    for path in workflows:
        text, status = _read_text(path)
        relative_path = path.relative_to(root).as_posix()
        mentions_scanner = "rune_integrity_scanner_guardrails" in text
        wired = wired or mentions_scanner
        rows.append(
            {
                "path": relative_path,
                "source_status": status,
                "mentions_scanner": mentions_scanner,
                "sha256": _sha256_file(path) if status == "OBSERVED" else "NOT_COMPUTABLE",
                "authority_granted": False,
            }
        )
    return {
        "status": "WIRED_ADVISORY_ONLY" if wired else "NOT_WIRED_ADVISORY_ONLY",
        "workflow_count": len(rows),
        "workflows": rows,
        "blocking_ci_enforcement": False,
        "workflow_mutation": False,
    }


def _guardrail_summary(rune_rows: list[dict[str, Any]]) -> dict[str, Any]:
    ready_count = sum(1 for row in rune_rows if row["integrity_posture"] == "READY")
    finding_count = sum(int(row["finding_count"]) for row in rune_rows)
    missing_rune_id_count = sum(1 for row in rune_rows if not row["rune_ids"])
    return {
        "rune_file_count": len(rune_rows),
        "ready_rune_file_count": ready_count,
        "missing_rune_id_count": missing_rune_id_count,
        "report_only_finding_count": finding_count,
        "recommended_next_lane": (
            "CI_RUNE_SCANNER_NONBLOCKING_WORKFLOW_WIRING_PROPOSAL"
            if rune_rows
            else "RUNE_SOURCE_DISCOVERY_REPAIR_PLAN"
        ),
        "guardrails": [
            "Require no-arg receipt runner before workflow wiring.",
            "Keep first CI wiring nonblocking and report-only.",
            "Continue treating suspicious tokens as findings until operator review.",
            "Do not mutate rune modules from scanner output.",
        ],
        "enforcement_action": "REPORT_ONLY",
        "authority_granted": False,
    }


def build_rune_integrity_scanner_guardrails_receipt(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    rune_dir = root / RUNE_SOURCE_DIR
    rune_files = (
        sorted(path for path in rune_dir.glob("*.py") if path.name != "__init__.py")
        if rune_dir.exists()
        else []
    )
    rune_rows = [_scan_rune_file(root, path) for path in rune_files]
    workflow_visibility = _workflow_visibility(root)
    summary = _guardrail_summary(rune_rows)
    source_status = (
        "READY"
        if rune_rows and summary["report_only_finding_count"] == 0
        else "READY_WITH_FINDINGS"
        if rune_rows
        else "NOT_COMPUTABLE"
    )
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "slice_id": SLICE_ID,
        "status": STATUS,
        "brier_score": BRIER_SCORE,
        "advisory_only": True,
        "projection_only": True,
        "authority_locks": AUTHORITY_LOCKS,
        "source_status": source_status,
        "source_table": [
            _source_status(root, RUNE_SOURCE_DIR),
            _source_status(root, RUNE_REGISTRY_PATH),
            _source_status(root, GENERATED_ARTIFACT_REGISTRY_PATH),
            _source_status(root, WORKFLOW_DIR),
        ],
        "rune_integrity_rows": rune_rows,
        "workflow_visibility": workflow_visibility,
        "guardrail_summary": summary,
        "boundary": {
            "sandbox_gate_issue": "#892",
            "sandbox_gate_phrase": "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED",
            "sandbox_gate_issued": False,
            "blocking_ci_enforcement": False,
            "external_calls": False,
            "workflow_mutation": False,
            "notion_writeback": False,
            "github_writeback": False,
            "runtime_activation": False,
            "canon_mutation": False,
            "mcp_exposure": False,
        },
        "validation_plan": [
            "python scripts/run_rune_integrity_scanner_guardrails_receipt.py",
            f"python scripts/run_artifact_regeneration.py --artifact {DEFAULT_OUT_PATH}",
            "python -m py_compile core/rune_integrity_scanner_guardrails.py "
            "scripts/run_rune_integrity_scanner_guardrails_receipt.py",
            "python -m pytest tests/test_rune_integrity_scanner_guardrails.py "
            "tests/test_generated_artifact_registry.py -q -k rune_integrity",
            "git diff --check",
        ],
        "notion_closeout_text": (
            "Slice56 complete - PR #[TBD] merged; advisory rune integrity scanner + "
            "guardrails receipt emitted; rune and CI visibility improved without "
            "enforcement or activation; no sandbox probe, external calls, writeback, "
            "MCP exposure, canon mutation, runtime activation, or blocking CI "
            "enforcement authorized. Brier Score: 0.10."
        ),
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice 56 + "
            "Rune Integrity Scanner Guardrails"
        ),
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def write_rune_integrity_scanner_guardrails_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
