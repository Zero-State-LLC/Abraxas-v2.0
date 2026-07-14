from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE  # noqa: E402

from core.canonical.json import canonical_hash, write_canonical_json  # noqa: E402
from core.sync.v2_hygiene_phase13_operator_intelligence_entry_receipt import (  # noqa: E402
    CONTINUITY_SPINE_PATH,
    RECEIPT_JSON_PATH,
)

PACKET_ID = "phase13_notion_sync_packet_001"
OUT_JSON_PATH = Path("out/sync/phase13_notion_sync_packet_001.latest.json")
READY_STATUS = "PHASE13_NOTION_SYNC_PACKET_READY"
BLOCKED_STATUS = "PHASE13_NOTION_SYNC_PACKET_BLOCKED"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return NOT_COMPUTABLE


def build_phase13_notion_sync_packet(
    repo_root: str | Path = ".",
    *,
    phase13_receipt_path: str | Path = RECEIPT_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    spine_path = root / CONTINUITY_SPINE_PATH
    receipt_path = Path(phase13_receipt_path)
    if not receipt_path.is_absolute():
        receipt_path = root / receipt_path
    phase13 = _read_json(receipt_path) or {}
    blockers: list[str] = []
    if not phase13:
        blockers.append("phase13_operator_intelligence_entry_receipt_missing")
    elif phase13.get("status") != (
        "V2_HYGIENE_PHASE13_OPERATOR_INTELLIGENCE_ENTRY_RECEIPT_READY"
    ):
        blockers.append("phase13_operator_intelligence_entry_receipt_not_ready")
    if phase13.get("notion_writeback_allowed") is True:
        blockers.append("phase13_notion_writeback_not_denied")
    spine_hash = _sha256(spine_path)
    if spine_hash == NOT_COMPUTABLE:
        blockers.append("continuity_spine_missing")
    blockers = sorted(set(blockers))
    ready = not blockers
    receipt_hash = str(
        phase13.get("operator_intelligence_entry_receipt_hash", NOT_COMPUTABLE)
    )
    packet: dict[str, Any] = {
        "packet_id": PACKET_ID,
        "status": READY_STATUS if ready else BLOCKED_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "manual_operator_copy_paste_only": True,
        "spine_path": CONTINUITY_SPINE_PATH.as_posix(),
        "spine_hash": spine_hash,
        "phase13_receipt_path": receipt_path.relative_to(root).as_posix()
        if receipt_path.is_relative_to(root)
        else receipt_path.as_posix(),
        "phase13_receipt_id": str(phase13.get("receipt_id", NOT_COMPUTABLE)),
        "phase13_receipt_hash": receipt_hash if ready else NOT_COMPUTABLE,
        "phase13_status": str(phase13.get("status", NOT_COMPUTABLE)),
        "operator_review_posture": "ACTIVE",
        "downstream": NOT_COMPUTABLE,
        "packet_blockers": blockers,
        "recommended_next_action": (
            "copy packet fields into Notion manually after operator review"
            if ready
            else "restore Phase 13 entry receipt before Notion sync packet emission"
        ),
        "sync_packet_hash": "",
    }
    packet["sync_packet_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "sync_packet_hash"}
    )
    return packet


def write_phase13_notion_sync_packet(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_phase13_notion_sync_packet(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / OUT_JSON_PATH, packet)
    return packet


def render_handoff_lines(packet: Mapping[str, Any]) -> list[str]:
    return [
        "# Phase 13 Notion Sync Packet Preflight",
        f"packet_id: {packet['packet_id']}",
        f"status: {packet['status']}",
        f"notion_writeback_allowed: {packet['notion_writeback_allowed']}",
        f"manual_operator_copy_paste_only: {packet['manual_operator_copy_paste_only']}",
        f"spine_hash: {packet['spine_hash']}",
        f"phase13_receipt_hash: {packet['phase13_receipt_hash']}",
        "packet_blockers:",
        *(
            [f"- {blocker}" for blocker in packet["packet_blockers"]]
            if packet["packet_blockers"]
            else ["- none"]
        ),
    ]


def main() -> int:
    packet = write_phase13_notion_sync_packet()
    print(f"wrote {OUT_JSON_PATH}")
    print("\n".join(render_handoff_lines(packet)))
    return 0 if packet["status"] == READY_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
