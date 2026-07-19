"""WP-H: repo-side Notion readiness mapping (evidence package).

Maps discovered Notion tracker surfaces to repo evidence paths.
Does NOT perform live Notion writeback (operator-controlled; RISK-012 residual).
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_notion_readiness_mapping"
OUT_DIR_REL = Path("out/production_readiness/ws8")
MAPPING_ID = "NOTION_READINESS_MAPPING_001"

# Operator-discovered Notion surfaces (MCP search 2026-07-19). IDs are durable.
NOTION_SURFACES = [
    {
        "role": "hub_page",
        "title": "Abraxas — Production Readiness Review",
        "page_id": "3a03e8ba-2f5c-81da-bb78-c514f5ce06e2",
        "url": "https://app.notion.com/p/3a03e8ba2f5c81dabb78c514f5ce06e2",
        "type": "page",
    },
    {
        "role": "tracker_database",
        "title": "Abraxas Production Readiness Tracker",
        "page_id": "85d8639a-d397-4721-94e5-1a884dbb95f3",
        "data_source_id": "dad0cfc2-9b13-4362-9c0c-276faf984719",
        "url": "https://app.notion.com/p/85d8639ad397472194e51a884dbb95f3",
        "type": "database",
    },
    {
        "role": "reviews_database",
        "title": "Abraxas Production Readiness Reviews",
        "page_id": "2352a5ee-2a03-4e9b-b3a0-af5f02b12c3a",
        "url": "https://app.notion.com/p/2352a5ee2a034e9bb3a0af5f02b12c3a",
        "type": "database",
    },
    {
        "role": "baseline_review_page",
        "title": "Baseline Readiness Review — 2026-07-17",
        "page_id": "3a03e8ba-2f5c-81b1-8d3f-f234e53b69eb",
        "url": "https://app.notion.com/p/3a03e8ba2f5c81b18d3ff234e53b69eb",
        "type": "page",
    },
]

# Repo evidence packages operators should link into the tracker.
REPO_EVIDENCE_LINKS = [
    {
        "checkpoint_hint": "WS0 Baseline package",
        "repo_path": "out/production_readiness/baseline/",
        "evidence_state": "Partial",
        "phase": "1 — Kernel Stabilization",
        "priority": "P0",
    },
    {
        "checkpoint_hint": "WS1 Interface registry + sole-writer",
        "repo_path": "out/production_readiness/ws1/",
        "evidence_state": "Partial",
        "phase": "1 — Kernel Stabilization",
        "priority": "P0",
    },
    {
        "checkpoint_hint": "WS2 Writer triage / boundary design",
        "repo_path": "out/production_readiness/ws2/",
        "evidence_state": "Partial",
        "phase": "1 — Kernel Stabilization",
        "priority": "P1",
    },
    {
        "checkpoint_hint": "WS3 Service registry",
        "repo_path": "out/production_readiness/ws3/",
        "evidence_state": "Partial",
        "phase": "2 — Service Layer",
        "priority": "P0",
    },
    {
        "checkpoint_hint": "WS5 Neon Genie allowlist",
        "repo_path": "out/production_readiness/ws5/",
        "evidence_state": "Partial",
        "phase": "1 — Kernel Stabilization",
        "priority": "P1",
    },
    {
        "checkpoint_hint": "WS8 Threat model + recovery + Notion mapping",
        "repo_path": "out/production_readiness/ws8/",
        "evidence_state": "Partial",
        "phase": "6 — Operations",
        "priority": "P0",
    },
    {
        "checkpoint_hint": "Continuation plan v3",
        "repo_path": "out/production_readiness/CONTINUATION_PLAN.v3.md",
        "evidence_state": "Partial",
        "phase": "1 — Kernel Stabilization",
        "priority": "P0",
    },
    {
        "checkpoint_hint": "PR #971 readiness branch",
        "repo_path": "https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/971",
        "evidence_state": "Partial",
        "phase": "1 — Kernel Stabilization",
        "priority": "P0",
    },
]


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


def build_notion_readiness_mapping(
    repo_root: Path,
    *,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    """Emit repo-side Notion readiness mapping. No live Notion writes."""
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)

    present: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    for link in REPO_EVIDENCE_LINKS:
        path = link["repo_path"]
        if path.startswith("http"):
            present.append({**link, "worktree_exists": None, "kind": "external_url"})
            continue
        exists = (repo_root / path).exists()
        row = {**link, "worktree_exists": exists, "kind": "repo_path"}
        if exists:
            present.append(row)
        else:
            missing.append(row)

    mapping: dict[str, Any] = {
        "schema_version": "notion_readiness_mapping.v1",
        "mapping_id": MAPPING_ID,
        "artifact_type": "notion_readiness_mapping",
        "work_package": "WP-H_NOTION_READINESS_MAPPING",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial",
        "writeback_performed": True,
        "writeback_policy": (
            "Operator-authorized writeback (WP-H+): hub note + child evidence page + "
            "tracker Evidence/PR rows may be updated via Notion MCP. This mapping "
            "producer still does not call Notion itself; see notion_writeback_receipt.v1."
        ),
        "notion_surfaces": NOTION_SURFACES,
        "repo_evidence_links": present + missing,
        "live_writeback_refs": {
            "hub_page_id": "3a03e8ba-2f5c-81da-bb78-c514f5ce06e2",
            "evidence_child_page_id": "3a23e8ba-2f5c-81f9-bcc5-d6543296605b",
            "evidence_child_url": "https://app.notion.com/p/3a23e8ba2f5c81f9bcc5d6543296605b",
            "tracker_rows": [
                "3a23e8ba-2f5c-815e-b961-cae75e8fcd4c",
                "3a23e8ba-2f5c-8147-bfe2-de81cf947464",
                "3a23e8ba-2f5c-81e2-9feb-c66b07e7df6d",
                "3a23e8ba-2f5c-8157-9ef0-edb7528efd47",
            ],
            "pr": "https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/971",
        },
        "summary": {
            "notion_surface_count": len(NOTION_SURFACES),
            "repo_link_count": len(REPO_EVIDENCE_LINKS),
            "repo_paths_present": len(present),
            "repo_paths_missing": len(missing),
            "live_writeback": True,
        },
        "risk_012": {
            "status": "MITIGATING",
            "prior_status": "OPEN",
            "reason": (
                "Repo mapping + live Notion hub update + tracker Evidence/PR rows "
                "linked to PR #971. Full CLOSED requires operator Verified DoD "
                "on each checkpoint (not overclaimed here)."
            ),
            "close_criteria": [
                "Operator verifies tracker checkpoints meet Definition of Done",
                "Evidence State advances to Verified only with durable proof",
                "No production-ready claim without freeze decision",
            ],
        },
        "operator_actions": [
            "Review tracker rows Evidence State (remain Partial until DoD met)",
            "Review threat model decision record under ws8/",
            "Do not mark production-ready from this mapping alone",
        ],
        "notes": [
            "Mapping discovered via Notion MCP search; IDs not fabricated.",
            "WP-H+ live writeback recorded in notion_writeback_receipt.v1.json.",
            "Does not authorize production activation.",
            "Linked plan: out/production_readiness/CONTINUATION_PLAN.v4.md",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "notion_readiness_mapping.v1.json", mapping)

    return mapping
