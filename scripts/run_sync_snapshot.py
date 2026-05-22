from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.canonical.json import write_canonical_json  # noqa: E402
from core.sync.milestone_receipt import build_artifact_hashes  # noqa: E402
from core.sync.notion_sync_packet import build_notion_sync_packet  # noqa: E402
from core.sync.repo_state_snapshot import build_repo_state_snapshot  # noqa: E402

OUT_JSON = Path("out/sync/sync_snapshot.latest.json")
OUT_MD = Path("out/sync/sync_snapshot.latest.md")


def _write_md(path: Path, packet: dict[str, object]) -> None:
    lines = [
        "# Sync Snapshot",
        "",
        f"- sync_status: {packet['sync_status']}",
        f"- notion_page_id: {packet['notion_page_id']}",
        f"- milestone: {packet['milestone']}",
        f"- repo_commit: {packet['repo_commit']}",
        f"- branch: {packet['branch']}",
        f"- ci_status: {packet['ci_status']}",
        f"- canon_status: {packet['canon_status']}",
        f"- generated_at: {packet['generated_at']}",
        f"- advisory_only: {packet['advisory_only']}",
        f"- projection_only: {packet['projection_only']}",
        "",
        "## Artifact Hashes",
    ]
    hashes = packet.get("artifact_hashes", {})
    if isinstance(hashes, dict) and hashes:
        for rel in sorted(hashes):
            lines.append(f"- {rel}: {hashes[rel]}")
    else:
        lines.append("- NOT_COMPUTABLE")
    missing = packet.get("missing_evidence", [])
    lines.append("")
    lines.append("## Missing Evidence")
    if isinstance(missing, list) and missing:
        for item in missing:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(*, repo_root: str | Path = ROOT, out_json: str | Path | None = None, out_md: str | Path | None = None, notion_page_id: str = "NOT_COMPUTABLE", milestone: str = "NOT_COMPUTABLE", ci_status: str = "NOT_COMPUTABLE", canon_status: str = "ADVISORY_ONLY", artifact_paths: list[str] | None = None) -> dict[str, object]:
    root = Path(repo_root)
    tracked = artifact_paths or ["out/canon_resume_state/latest.json"]
    repo_state = build_repo_state_snapshot(repo_root=root)
    hashes, missing_paths = build_artifact_hashes(repo_root=root, artifact_paths=tracked)
    payload = {
        "notion_page_id": notion_page_id,
        "milestone": milestone,
        "repo_commit": repo_state["repo_commit"],
        "branch": repo_state["branch"],
        "ci_status": ci_status,
        "canon_status": canon_status,
        "artifact_hashes": hashes,
    }
    packet = build_notion_sync_packet(payload=payload)
    missing_fields = packet.get("missing_evidence", [])
    merged_missing = sorted(set([*missing_paths, *(missing_fields if isinstance(missing_fields, list) else [])]))
    if merged_missing:
        packet["missing_evidence"] = merged_missing
        packet["sync_status"] = "NOT_COMPUTABLE"

    target_json = Path(out_json) if out_json else root / OUT_JSON
    target_md = Path(out_md) if out_md else root / OUT_MD
    write_canonical_json(target_json, packet)
    _write_md(target_md, packet)
    return packet


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--notion-page-id", default="NOT_COMPUTABLE")
    parser.add_argument("--milestone", default="NOT_COMPUTABLE")
    parser.add_argument("--ci-status", default="NOT_COMPUTABLE")
    parser.add_argument("--canon-status", default="ADVISORY_ONLY")
    parser.add_argument("--artifact", action="append", default=[])
    args = parser.parse_args()
    packet = run(notion_page_id=args.notion_page_id, milestone=args.milestone, ci_status=args.ci_status, canon_status=args.canon_status, artifact_paths=args.artifact)
    print(packet["sync_status"])
    print(packet["packet_hash"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
