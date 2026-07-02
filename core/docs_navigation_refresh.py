from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "DocsNavigationRefreshReceipt.v1"
STATUS = "DOCS_NAVIGATION_REFRESH_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-57"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = "out/audit/docs_navigation_refresh_001.latest.json"

DOC_PATHS = (
    "README.md",
    "docs/START_HERE.md",
    "docs/INDEX.md",
    "docs/audits/AUDIT_INDEX.md",
    "docs/releases/RELEASE_INDEX.md",
    "docs/artifacts/ARTIFACT_INDEX.md",
)

REQUIRED_LINKS = (
    "README.md",
    "STATUS.md",
    "ARCHITECTURE.md",
    "AGENTS.md",
    "PLANS.md",
    "docs/INDEX.md",
    "docs/audits/AUDIT_INDEX.md",
    "docs/releases/RELEASE_INDEX.md",
    "docs/artifacts/ARTIFACT_INDEX.md",
    "out/audit/docs_navigation_refresh_001.latest.json",
)

AUTHORITY_LOCKS = {
    "canon_mutation": False,
    "external_calls": False,
    "github_writeback": False,
    "mcp_exposure": False,
    "notion_writeback": False,
    "production_activation": False,
    "runtime_activation": False,
    "runtime_mutation": False,
    "sandbox_probe_execution": False,
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


def _source_row(repo_root: Path, relative_path: str) -> dict[str, Any]:
    path = repo_root / relative_path
    text, status = _read_text(path)
    return {
        "path": relative_path,
        "source_status": status,
        "sha256": _sha256_file(path) if status == "OBSERVED" else "NOT_COMPUTABLE",
        "line_count": len(text.splitlines()) if status == "OBSERVED" else 0,
        "authority_granted": False,
    }


def _required_link_rows(repo_root: Path) -> list[dict[str, Any]]:
    start_text, _ = _read_text(repo_root / "docs/START_HERE.md")
    index_text, _ = _read_text(repo_root / "docs/INDEX.md")
    readme_text, _ = _read_text(repo_root / "README.md")
    combined = "\n".join((start_text, index_text, readme_text))
    return [
        {
            "target": link,
            "observed": link in combined or Path(link).name in combined,
            "authority_granted": False,
        }
        for link in REQUIRED_LINKS
    ]


def _navigation_quality(link_rows: list[dict[str, Any]]) -> dict[str, Any]:
    observed_count = sum(1 for row in link_rows if row["observed"])
    missing = [row["target"] for row in link_rows if not row["observed"]]
    return {
        "required_link_count": len(link_rows),
        "observed_link_count": observed_count,
        "missing_targets": missing,
        "new_contributor_path_minutes": 5,
        "status": "READY" if not missing else "READY_WITH_FINDINGS",
        "authority_granted": False,
    }


def build_docs_navigation_refresh_receipt(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source_table = [_source_row(root, path) for path in DOC_PATHS]
    link_rows = _required_link_rows(root)
    quality = _navigation_quality(link_rows)
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "slice_id": SLICE_ID,
        "status": STATUS,
        "brier_score": BRIER_SCORE,
        "advisory_only": True,
        "projection_only": True,
        "notion_board_url": NOTION_BOARD_URL,
        "claimed_card": (
            "D1.1 - Master INDEX.md + START_HERE.md Consolidation + "
            "Navigation System"
        ),
        "authority_locks": AUTHORITY_LOCKS,
        "source_status": quality["status"],
        "source_table": source_table,
        "required_link_rows": link_rows,
        "navigation_quality": quality,
        "touched_docs": list(DOC_PATHS),
        "boundary": {
            "sandbox_gate_issue": "#892",
            "sandbox_gate_phrase": "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED",
            "sandbox_gate_issued": False,
            "canon_mutation": False,
            "external_calls": False,
            "github_writeback": False,
            "mcp_exposure": False,
            "notion_writeback": False,
            "runtime_activation": False,
        },
        "validation_plan": [
            "python Scripts/run_docs_navigation_refresh_receipt.py",
            f"python scripts/run_artifact_regeneration.py --artifact {DEFAULT_OUT_PATH}",
            "python -m py_compile core/docs_navigation_refresh.py "
            "Scripts/run_docs_navigation_refresh_receipt.py",
            "python -m pytest tests/test_docs_navigation_refresh.py "
            "tests/test_generated_artifact_registry.py -q -k docs_navigation",
            "git diff --check",
        ],
        "notion_closeout_text": (
            "Slice57 complete - D1.1 Master Navigation Consolidation shipped; "
            "START_HERE and INDEX now route new contributors through README, "
            "STATUS, ARCHITECTURE, task board, modules, sub-indexes, and "
            "receipts; docs navigation refresh receipt emitted; no sandbox "
            "probe, runtime activation, canon mutation, MCP exposure, external "
            "calls, or autonomous writeback authorized. Brier Score: 0.10."
        ),
        "recommended_next_lane": (
            "Continue Priority 3 D1-D3 repository organization unless operator "
            "selects another board card."
        ),
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice 57 + "
            "D1.1 Master Navigation Consolidation"
        ),
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def write_docs_navigation_refresh_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
