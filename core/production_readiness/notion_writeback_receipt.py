"""WP-H+: receipt for live Notion readiness writeback (operator-authorized)."""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json

PRODUCER = "run_notion_writeback_receipt"
OUT_DIR_REL = Path("out/production_readiness/ws8")
RECEIPT_ID = "NOTION_READINESS_WRITEBACK_RECEIPT_001"


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


def build_notion_writeback_receipt(
    repo_root: Path,
    *,
    actions: list[dict[str, Any]],
    hub_page_id: str,
    tracker_data_source_id: str,
    produced_at: str | None = None,
    write: bool = True,
) -> dict[str, Any]:
    """Record which Notion surfaces were updated and with what evidence links."""
    repo_root = Path(repo_root).resolve()
    produced_at = produced_at or _utc_now()
    sha = _git_sha(repo_root)
    ok = [a for a in actions if a.get("status") == "OK"]
    failed = [a for a in actions if a.get("status") != "OK"]

    receipt: dict[str, Any] = {
        "schema_version": "notion_writeback_receipt.v1",
        "receipt_id": RECEIPT_ID,
        "artifact_type": "notion_writeback_receipt",
        "work_package": "WP-H_PLUS_NOTION_WRITEBACK",
        "produced_at": produced_at,
        "producer": PRODUCER,
        "repository_sha": sha,
        "evidence_state": "Partial" if ok and not failed else ("Partial" if ok else "Missing"),
        "writeback_performed": bool(ok),
        "hub_page_id": hub_page_id,
        "tracker_data_source_id": tracker_data_source_id,
        "summary": {
            "action_count": len(actions),
            "ok_count": len(ok),
            "fail_count": len(failed),
        },
        "actions": actions,
        "risk_012": {
            "status": "MITIGATING" if ok else "OPEN",
            "reason": (
                "Live Notion hub update and/or tracker evidence rows linked to "
                "PR #971 and out/production_readiness/. Full Verified closure "
                "still requires operator review of each checkpoint Definition of Done."
            ),
        },
        "notes": [
            "Does not mark overall readiness Verified or production-ready.",
            "Linked mapping: out/production_readiness/ws8/notion_readiness_mapping.v1.json",
            "PR: https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/971",
        ],
    }

    if write:
        out_dir = repo_root / OUT_DIR_REL
        out_dir.mkdir(parents=True, exist_ok=True)
        write_canonical_json(out_dir / "notion_writeback_receipt.v1.json", receipt)

    return receipt
