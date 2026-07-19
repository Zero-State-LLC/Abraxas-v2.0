"""Sole-writer advisory check (WS1.7).

Surfaces non-allowlisted modules that appear to write production artifacts
under ``out/``. Report-only / fail-open by default.

Noise reduction relative to the original heuristic:
  - exclude tests/, fixtures/, caches
  - require a write API *and* an out/ path marker on the same line
  - authorize scripts/run_*.py + explicit production-readiness writers
  - summarize findings by top-level package
"""

from __future__ import annotations

import os
import re
import subprocess
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from core.canonical.json import write_canonical_json

PRODUCER = "run_sole_writer_advisory_check"
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
    "out",
}

# Paths that may write under out/ without being scripts/run_*.py.
WRITER_ALLOWLIST = frozenset(
    {
        "scripts/run_sole_writer_advisory_check.py",
        "scripts/run_fast_ci.py",
        "scripts/run_artifact_regeneration.py",
        "scripts/run_production_readiness_baseline.py",
        "scripts/run_interface_registry_snapshot.py",
        "scripts/run_boundary_advisory_check.py",
        "core/canonical/json.py",
        "core/production_readiness/baseline_generator.py",
        "core/production_readiness/interface_registry.py",
        "core/production_readiness/boundary_check.py",
        "core/production_readiness/sole_writer_check.py",
    }
)

SKIP_PATH_PREFIXES = (
    "tests/",
    "fixtures/",
    "apps/aal-viz-live-console/node_modules/",
)

# Same-line write + out-path markers (reduces read-only Path("out/...") noise).
WRITE_API = re.compile(
    r"""(
        \.write_text\s*\(
        | \.write_bytes\s*\(
        | json\.dump\s*\(
        | write_canonical_json(?:_if_changed)?\s*\(
        | open\s*\([^\n]*['\"]w
    )""",
    re.VERBOSE,
)
OUT_MARKER = re.compile(
    r"""(
        ['\"]out/
        | Path\s*\(\s*['\"]out/
        | \bOUT_PATH\b
        | \bout_path\b
        | \bout_dir\b
        | \bOUT\s*=
    )""",
    re.VERBOSE,
)


@dataclass
class Finding:
    path: str
    kind: str
    detail: str
    severity: str = "advisory"
    package: str = ""


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


def is_authorized_writer(rel_path: str) -> bool:
    if rel_path.startswith("scripts/run_") and rel_path.endswith(".py"):
        return True
    if rel_path in WRITER_ALLOWLIST:
        return True
    return False


def _iter_python_files(repo_root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if name.endswith(".py"):
                yield Path(dirpath) / name


def scan_file(repo_root: Path, path: Path) -> list[Finding]:
    rel = _rel(repo_root, path)
    if any(rel.startswith(p) for p in SKIP_PATH_PREFIXES):
        return []
    if is_authorized_writer(rel):
        return []

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [Finding(rel, "read_error", str(exc)[:160], package=rel.split("/")[0])]

    findings: list[Finding] = []
    package = rel.split("/")[0] if "/" in rel else rel
    for i, line in enumerate(text.splitlines(), start=1):
        if not WRITE_API.search(line):
            continue
        if not OUT_MARKER.search(line) and "out/" not in line:
            continue
        findings.append(
            Finding(
                path=rel,
                kind="potential_out_write",
                detail=f"line {i}: {line.strip()[:160]}",
                severity="advisory",
                package=package,
            )
        )
    return findings


def build_sole_writer_report(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
    max_findings: int = 50,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    all_findings: list[Finding] = []
    scanned = 0
    for py_path in _iter_python_files(repo_root):
        scanned += 1
        all_findings.extend(scan_file(repo_root, py_path))

    by_package = Counter(f.package or "unknown" for f in all_findings)
    truncated = len(all_findings) > max_findings
    # Prefer non-test packages already excluded; sort by package then path
    ordered = sorted(all_findings, key=lambda f: (f.package, f.path, f.detail))
    capped = ordered[:max_findings]

    report: dict[str, Any] = {
        "schema_version": "sole_writer_advisory_report.v1",
        "artifact_type": "sole_writer_advisory_report",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "PARTIAL",
        "mode": "advisory_report_only",
        "always_exit_zero": True,
        "wired_into_fast_ci": "report_only",
        "scanned_python_files": scanned,
        "finding_count": len(all_findings),
        "truncated": truncated,
        "by_package": dict(by_package.most_common()),
        "policy": {
            "authorized_pattern": "scripts/run_*.py + WRITER_ALLOWLIST",
            "writer_allowlist_size": len(WRITER_ALLOWLIST),
            "skip_path_prefixes": list(SKIP_PATH_PREFIXES),
            "heuristic": "same-line WRITE_API + out/ marker",
            "fail_closed_ready": False,
            "notes": [
                "WS1.7: tests/ excluded; read-only Path('out/...') no longer flagged.",
                "core/ findings often are builders that should only return dicts — debt, not instant fail.",
                "Do not fail-close until finding_count is stable and allow-list reviewed.",
            ],
        },
        "findings": [asdict(f) for f in capped],
        "notes": [
            "Advisory only; wired into run_fast_ci as report-only fail-open.",
            "Neon Genie and other advisory surfaces must not gain ungoverned production writes.",
        ],
    }

    if write:
        out_dir = repo_root / WS1_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "sole_writer_advisory_report.v1.json", report)

    return report
