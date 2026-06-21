from __future__ import annotations

from typing import Any, Mapping, Sequence

from core.canonical.json import canonical_hash

DRYRUN_SCHEMA_VERSION = "CodegenNotionReconciliationDryRun.v1"
DEFAULT_SURFACES: tuple[str, ...] = (
    "V2.5 Technical Debt Board",
    "Sprint 001 Hub",
    "Abraxas Master System",
)


def _phase_line(phase: str, status: str, merge_sha: str) -> str:
    return f"- {phase}: {status} ({merge_sha})"


def build_notion_reconciliation_dryrun(
    *,
    timestamp: str,
    phase_statuses: Mapping[str, str],
    merge_shas: Mapping[str, str],
    target_surfaces: Sequence[str] = DEFAULT_SURFACES,
) -> dict[str, Any]:
    phase_lines = [
        _phase_line(phase, status, str(merge_shas.get(phase, "NOT_RECORDED")))
        for phase, status in sorted(phase_statuses.items())
    ]
    sync_text_lines = [
        "ABX Codegen Intelligence Spine reconciliation dry run",
        f"Timestamp: {timestamp}",
        "Status: PHASE_5_NOTION_RECONCILIATION_DRYRUN",
        "Boundary: paste-ready text only; no Notion writeback performed.",
        "",
        "Merged / staged phase status:",
        *phase_lines,
        "",
        "Authority locks:",
        "- CANON_MUTATION=false",
        "- RUNTIME_MUTATION=false",
        "- EXECUTION_AUTHORITY=false",
        "- GITHUB_WRITEBACK=false",
        "- NOTION_WRITEBACK=false",
        "",
        "Recommended next:",
        "- Operator may manually paste this block into the listed Notion surfaces.",
        "- No automated sync, promotion, runtime activation, or canon mutation is granted.",
        "",
        "Brier Score: 0.10",
    ]
    base: dict[str, Any] = {
        "schema_version": DRYRUN_SCHEMA_VERSION,
        "status": "NOTION_RECONCILIATION_DRYRUN_READY",
        "timestamp": timestamp,
        "target_surfaces": list(target_surfaces),
        "phase_statuses": dict(phase_statuses),
        "merge_shas": {key: str(value) for key, value in merge_shas.items()},
        "sync_text": "\n".join(sync_text_lines),
        "advisory_only": True,
        "notion_writeback": False,
        "github_writeback": False,
        "execution_authority": False,
        "runtime_mutation": False,
        "canon_mutation": False,
        "production_activation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}
