#!/usr/bin/env python3
"""Advisory sole-writer / write-path check for Abraxas.

This is intentionally report-only and always exits 0.
It is NOT yet wired into run_fast_ci.py.

Purpose:
  Surface potential production writes under out/ that do not appear to
  originate from the observed sole-writer pattern (scripts/run_*.py).

Design principles:
  - Small and reversible
  - Fail-open / advisory only
  - No changes to production behavior
  - Can later be promoted to a fail-closed gate after allow-list scrubbing
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_PREFIX = "out/"
REPORT_DIR = REPO_ROOT / "out" / "production_readiness" / "ws1"


@dataclass
class Finding:
    path: str
    kind: str
    detail: str
    severity: str = "advisory"


def _is_authorized_writer(rel_path: str) -> bool:
    # Primary observed pattern: scripts/run_*.py
    if rel_path.startswith("scripts/run_") and rel_path.endswith(".py"):
        return True
    # Explicit allow for the advisory checker itself and a few known runners
    if rel_path in {
        "scripts/run_sole_writer_advisory_check.py",
        "scripts/run_fast_ci.py",
        "scripts/run_artifact_regeneration.py",
    }:
        return True
    return False


def _iter_python_files(root: Path) -> Iterable[Path]:
    skip_dirs = {".git", ".venv", "venv", "node_modules", "__pycache__", ".mypy_cache", ".ruff_cache"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for name in filenames:
            if name.endswith(".py"):
                yield Path(dirpath) / name


WRITE_PATTERNS = [
    re.compile(r"""open\s*\(\s*['\"]out/"""),
    re.compile(r"""Path\s*\(\s*['\"]out/"""),
    re.compile(r"""['\"]out/[^'\"]*['\"]\s*,\s*['\"]w"""),
    re.compile(r"""\.write_text\s*\("""),
    re.compile(r"""\.write_bytes\s*\("""),
    re.compile(r"""json\.dump\s*\("""),
]


def _heuristic_scan_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [Finding(str(path.relative_to(REPO_ROOT)), "read_error", str(exc))]

    rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    if _is_authorized_writer(rel):
        return []

    # Cheap heuristic: look for out/ write indicators in non-authorized modules
    for i, line in enumerate(text.splitlines(), start=1):
        for pat in WRITE_PATTERNS:
            if pat.search(line):
                if "out/" in line or "write" in line.lower() or "dump" in line.lower():
                    findings.append(
                        Finding(
                            path=rel,
                            kind="potential_out_write",
                            detail=f"line {i}: {line.strip()[:160]}",
                            severity="advisory",
                        )
                    )
                    break
    return findings


def main() -> int:
    all_findings: list[Finding] = []
    scanned = 0

    for py_path in _iter_python_files(REPO_ROOT):
        scanned += 1
        all_findings.extend(_heuristic_scan_file(py_path))

    # Cap report size for readability
    max_findings = 50
    truncated = len(all_findings) > max_findings
    report_findings = all_findings[:max_findings]

    report = {
        "schema_version": "sole_writer_advisory_report.v1",
        "artifact_type": "sole_writer_advisory_report",
        "produced_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "producer": "scripts/run_sole_writer_advisory_check.py",
        "mode": "advisory_report_only",
        "always_exit_zero": True,
        "scanned_python_files": scanned,
        "finding_count": len(all_findings),
        "truncated": truncated,
        "findings": [asdict(f) for f in report_findings],
        "authorized_pattern": "scripts/run_*.py (primary) + small explicit allow-list",
        "notes": [
            "This check is intentionally advisory and does not fail CI.",
            "It is not yet wired into run_fast_ci.py.",
            "False positives are expected; use results to refine an allow-list before any fail-closed promotion.",
            "Neon Genie and other advisory surfaces must remain non-writing for production artifacts.",
        ],
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORT_DIR / "sole_writer_advisory_report.v1.json"
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"[sole-writer-advisory] scanned={scanned} findings={len(all_findings)} report={out_path}")
    if all_findings:
        print(f"[sole-writer-advisory] first finding: {all_findings[0].path} — {all_findings[0].detail[:100]}")
    else:
        print("[sole-writer-advisory] no potential non-authorized out/ writes detected by heuristic")

    # Always advisory
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
