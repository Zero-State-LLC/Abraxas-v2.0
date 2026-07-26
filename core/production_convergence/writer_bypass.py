"""Advisory scanner: direct JSON writes that bypass classified canonical writer."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash

_WRITE_PATTERNS = (
    re.compile(r"\bjson\.dump\s*\("),
    re.compile(r"\bjson\.dumps\s*\([^)]*\)\s*$"),
    re.compile(r"\.write_text\s*\("),
)

_SCAN_ROOTS = ("core", "scripts", "abraxas", "apps")
_ALLOW_PATH_FRAGMENTS = (
    "core/canonical/json.py",
    "core/file_cache.py",
    "tests/",
    ".venv/",
)


def scan_writer_bypasses(repo_root: Path) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    findings: list[dict[str, Any]] = []
    for rel_root in _SCAN_ROOTS:
        base = root / rel_root
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.py")):
            rel = path.relative_to(root).as_posix()
            if any(fragment in rel for fragment in _ALLOW_PATH_FRAGMENTS):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            if "out/" not in text and "out_dir" not in text and "OUT_DIR" not in text:
                continue
            for lineno, line in enumerate(text.splitlines(), start=1):
                if "write_canonical_json" in line or "write_canonical_artifact" in line:
                    continue
                if any(pattern.search(line) for pattern in _WRITE_PATTERNS):
                    findings.append(
                        {
                            "path": rel,
                            "line": lineno,
                            "snippet": line.strip()[:200],
                        }
                    )

    # Prefer classified writer for new governed surfaces; legacy write_canonical_json
    # remains allowed during migration.
    payload = {
        "artifact_type": "canonical_writer_bypass_advisory",
        "schema_version": "canonical_writer_bypass.v1",
        "evidence_state": "Partial",
        "mode": "advisory_report_only",
        "fail_closed": False,
        "notes": [
            "Advisory only. Classified writer API is write_canonical_artifact.",
            "Legacy write_canonical_json remains permitted during migration.",
            "Findings are heuristic (out/ mention + json.dump/write_text).",
        ],
        "summary": {"finding_count": len(findings)},
        "findings": findings[:200],
        "truncated": len(findings) > 200,
    }
    payload["canonical_hash"] = canonical_hash(
        {k: v for k, v in payload.items() if k != "canonical_hash"}
    )
    return payload
