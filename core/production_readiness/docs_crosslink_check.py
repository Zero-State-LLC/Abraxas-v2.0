"""Validate markdown relative links for production readiness docs."""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_production_readiness_docs_crosslink_check"
OUT_DIR_REL = Path("out/production_readiness/ws8")

# Markdown files that form the readiness documentation surface.
DOC_GLOBS = [
    "out/production_readiness/README.md",
    "out/production_readiness/CONTINUATION_PLAN.v8.md",
    "out/production_readiness/ws8/supported_surface_operator_runbook.v1.md",
    "docs/production_readiness/INDEX.md",
    "docs/production_readiness/ENGINEERING_GUIDEBOOK.md",
]

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


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


def _is_external(target: str) -> bool:
    t = target.strip()
    return (
        t.startswith("http://")
        or t.startswith("https://")
        or t.startswith("mailto:")
        or t.startswith("#")
    )


def build_docs_crosslink_check(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    checked: list[dict[str, Any]] = []
    broken: list[dict[str, Any]] = []
    link_count = 0

    for rel in DOC_GLOBS:
        path = repo_root / rel
        if not path.is_file():
            broken.append(
                {
                    "source": rel,
                    "target": rel,
                    "reason": "source_doc_missing",
                }
            )
            continue
        text = path.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            label, target = match.group(1), match.group(2).strip()
            # strip optional title
            if " " in target and not target.startswith("http"):
                target = target.split(" ", 1)[0]
            target = target.strip("<>\"'")
            if _is_external(target):
                continue
            # fragment-only already skipped; strip #fragment for file resolve
            file_part = target.split("#", 1)[0]
            if not file_part:
                continue
            link_count += 1
            resolved = (path.parent / file_part).resolve()
            try:
                resolved.relative_to(repo_root)
            except ValueError:
                broken.append(
                    {
                        "source": rel,
                        "target": target,
                        "label": label,
                        "reason": "escapes_repo",
                    }
                )
                continue
            if not resolved.exists():
                broken.append(
                    {
                        "source": rel,
                        "target": target,
                        "label": label,
                        "reason": "missing",
                        "resolved": str(resolved.relative_to(repo_root)),
                    }
                )
            else:
                checked.append(
                    {
                        "source": rel,
                        "target": target,
                        "ok": True,
                    }
                )

    report: dict[str, Any] = {
        "schema_version": "production_readiness_docs_crosslink_check.v1",
        "artifact_type": "docs_crosslink_check",
        "work_package": "WP-DOCS_CROSSLINK_CHECK",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial" if broken else "Partial",
        "summary": {
            "docs_scanned": len(DOC_GLOBS),
            "internal_links_checked": link_count,
            "ok_count": len(checked),
            "broken_count": len(broken),
            "all_ok": len(broken) == 0,
        },
        "broken_links": broken,
        "notes": [
            "Checks relative markdown links in the production readiness doc surface.",
            "External http(s) links are not fetched.",
            "evidence_state remains Partial (docs are Partial-track documentation).",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(
            out_dir / "docs_crosslink_check.v1.json",
            report,
        )
        # documentation overhaul receipt
        receipt = {
            "schema_version": "production_readiness_documentation_receipt.v1",
            "artifact_type": "documentation_receipt",
            "work_package": "WP-DOCS_OVERHAUL",
            "produced_at": produced_at,
            "producer": PRODUCER,
            "repository_sha": sha,
            "evidence_state": "Partial",
            "documents": [
                "out/production_readiness/README.md",
                "docs/production_readiness/ENGINEERING_GUIDEBOOK.md",
                "docs/production_readiness/INDEX.md",
                "out/production_readiness/CONTINUATION_PLAN.v8.md",
            ],
            "crosslink_check": report["summary"],
            "posture_snapshot": {
                "baseline_evidence_state": "Partial",
                "release_decision": "see ws8/release_decision.v1.json",
                "production_activation": "DENIED",
                "overclaim_avoided": True,
            },
            "notes": [
                "Sandbox /home/workdir/artifacts was not present; docs grounded in live repo receipts.",
                "Does not claim Verified baseline or production go-live.",
            ],
        }
        write_canonical_json(
            out_dir / "documentation_overhaul_receipt.v1.json",
            receipt,
        )

    return report
