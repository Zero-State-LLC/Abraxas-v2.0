"""Workstream 1/2 — boundary advisory checks (fail-open by default).

Surfaces:
  - prohibited import patterns (skills/apps → deep core internals without allow)
  - unregistered high-signal public roots vs interface registry
  - optional reuse of sole-writer heuristic counts

Always advisory unless fail_closed=True.
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from core.canonical.json import write_canonical_json

PRODUCER = "run_boundary_advisory_check"
WS1_DIR_REL = Path("out/production_readiness/ws1")

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    ".codebase-memory",
    ".tmp",
}

# Modules outside these roots that import these targets are flagged (advisory).
SENSITIVE_CORE_PREFIXES = (
    "core.canonical",
    "core.governance",
    "core.config",
)

# Files under these prefixes are scanned for sensitive imports.
EXTERNALISH_PREFIXES = (
    "skills/",
    "apps/",
    "abx-afe/",
    "examples/",
)

# Allowlisted relative paths that may import sensitive core modules.
# Seeded from first live boundary scan (WS1.5). Paths here are known
# skill/API adapters that intentionally use canonical JSON or RuntimePaths.
# New sensitive imports outside this set remain advisory findings.
IMPORT_ALLOWLIST = frozenset(
    {
        # Hermes skill evolution — deterministic skill artifacts via canonical JSON
        "skills/abx-hermes-skill-evolution/abx_skill_live_brier_ledger.py",
        "skills/abx-hermes-skill-evolution/abx_skill_formal_operator_decision_validator.py",
        "skills/abx-hermes-skill-evolution/abx_skill_extended_canary_observer.py",
        "skills/abx-hermes-skill-evolution/abx_skill_patch_generator.py",
        # Stabilization readiness skill — contract inventory / conformance
        "skills/abx-stabilization-readiness/reproducibility_auditor.py",
        "skills/abx-stabilization-readiness/conformance_harness.py",
        "skills/abx-stabilization-readiness/models.py",
        "skills/abx-stabilization-readiness/contract_inventory.py",
        "skills/abx-stabilization-readiness/director.py",
        # FastAPI app — RuntimePaths via core.config
        "apps/api/deps.py",
        "apps/api/routers/validation.py",
        "apps/api/routers/registry.py",
    }
)

# High-signal roots already registered (or intentionally deferred) so they
# are not reported as unregistered_public_candidate once present in registry.
REGISTERED_OR_DEFERRED_ROOTS = frozenset(
    {
        "contracts/pipelines",
        "contracts/yggdrasil",
        "docs/workflows/cli-operator-layer.md",
        "contracts/runes/catalog.v1.json",
        "scripts/run_fast_ci.py",
        "scripts/run_production_readiness_baseline.py",
        "scripts/run_abx_neon_genie.py",
        "core/canonical/json.py",
    }
)


@dataclass
class Finding:
    path: str
    kind: str
    detail: str
    severity: str = "advisory"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git_sha(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"


def _rel(repo_root: Path, path: Path) -> str:
    return str(path.relative_to(repo_root)).replace("\\", "/")


def _iter_python_files(repo_root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith(".py"):
                yield Path(dirpath) / name


def scan_prohibited_imports(repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in _iter_python_files(repo_root):
        rel = _rel(repo_root, path)
        if not any(rel.startswith(p) for p in EXTERNALISH_PREFIXES):
            continue
        if rel in IMPORT_ALLOWLIST:
            continue
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source)
        except (OSError, SyntaxError) as exc:
            findings.append(
                Finding(rel, "parse_error", str(exc)[:160], severity="info")
            )
            continue
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module)
            elif isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            for mod in modules:
                for prefix in SENSITIVE_CORE_PREFIXES:
                    if mod == prefix or mod.startswith(prefix + "."):
                        findings.append(
                            Finding(
                                path=rel,
                                kind="sensitive_core_import",
                                detail=f"imports {mod} (prefix {prefix})",
                                severity="advisory",
                            )
                        )
    return findings


def scan_unregistered_surfaces(repo_root: Path) -> list[Finding]:
    registry_path = (
        repo_root / "out" / "production_readiness" / "ws1" / "interface_registry_snapshot.v1.json"
    )
    registered: set[str] = set()
    if registry_path.is_file():
        try:
            data = json.loads(registry_path.read_text(encoding="utf-8"))
            for entry in data.get("entries", []):
                registered.add(entry.get("path", ""))
                registered.add(entry.get("contract_id", ""))
        except (OSError, json.JSONDecodeError):
            pass

    findings: list[Finding] = []
    candidates = [
        "contracts/pipelines",
        "contracts/yggdrasil",
        "docs/workflows/cli-operator-layer.md",
        "contracts/runes/catalog.v1.json",
        "scripts/run_fast_ci.py",
        "scripts/run_production_readiness_baseline.py",
        "scripts/run_abx_neon_genie.py",
        "core/canonical/json.py",
    ]
    for rel in candidates:
        if not (repo_root / rel).exists():
            continue
        if rel in REGISTERED_OR_DEFERRED_ROOTS:
            # Still require registry presence when snapshot exists; if snapshot
            # missing (first run), treat as deferred rather than noisy.
            if not registry_path.is_file():
                continue
        if rel in registered or Path(rel).name in registered:
            continue
        if any(rel == r or r.endswith(rel) for r in registered):
            continue
        # Match directory roots registered with trailing content
        if any(r.startswith(rel.rstrip("/") + "/") for r in registered if r):
            continue
        findings.append(
            Finding(
                path=rel,
                kind="unregistered_public_candidate",
                detail="high-signal surface not present in interface registry snapshot",
                severity="advisory",
            )
        )
    return findings


def resolve_fail_closed(explicit: bool | None = None) -> bool:
    """WP-E: fail-closed is opt-in via env; default False.

    ABRAXAS_BOUNDARY_FAIL_CLOSED=1|true|yes enables fail-closed for this check only.
    Operator approval required before enabling in shared CI.
    """
    if explicit is not None:
        return explicit
    return os.environ.get("ABRAXAS_BOUNDARY_FAIL_CLOSED", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def build_boundary_report(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
    fail_closed: bool | None = None,
    max_findings: int = 80,
) -> tuple[dict[str, Any], int]:
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)
    fail_closed_effective = resolve_fail_closed(fail_closed)

    import_findings = scan_prohibited_imports(repo_root)
    unregistered = scan_unregistered_surfaces(repo_root)
    all_findings = import_findings + unregistered
    truncated = len(all_findings) > max_findings
    capped = all_findings[:max_findings]

    report: dict[str, Any] = {
        "schema_version": "boundary_advisory_report.v1",
        "artifact_type": "boundary_advisory_report",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "PARTIAL",
        "mode": "fail_closed" if fail_closed_effective else "advisory_report_only",
        "always_exit_zero": not fail_closed_effective,
        "summary": {
            "sensitive_import_findings": len(import_findings),
            "unregistered_surface_findings": len(unregistered),
            "finding_count": len(all_findings),
            "truncated": truncated,
        },
        "policy": {
            "sensitive_core_prefixes": list(SENSITIVE_CORE_PREFIXES),
            "externalish_prefixes": list(EXTERNALISH_PREFIXES),
            "import_allowlist_size": len(IMPORT_ALLOWLIST),
            "import_allowlist_sample": sorted(IMPORT_ALLOWLIST)[:20],
            "wired_into_fast_ci": "report_only",
            "fail_closed_env": "ABRAXAS_BOUNDARY_FAIL_CLOSED",
            "fail_closed_default": False,
            "fail_closed_effective": fail_closed_effective,
            "fail_closed_ready": False,
            "notes": [
                "WP-E: fail-closed is opt-in via ABRAXAS_BOUNDARY_FAIL_CLOSED (default off).",
                "run_fast_ci must NOT set the env flag; remains report-only.",
                "RISK-008 status: MITIGATING.",
                "Operator approval required before enabling fail-closed in shared CI.",
            ],
        },
        "findings": [asdict(f) for f in capped],
    }

    if write:
        out_dir = repo_root / WS1_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "boundary_advisory_report.v1.json", report)

    exit_code = 0
    if fail_closed_effective and all_findings:
        exit_code = 1
    return report, exit_code
