"""Emit production slice 1 surface resolution packet 001."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.surface_resolution.discovery import OUTPUT_REL, run_surface_resolution_packet


def _baseline_commit(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def main() -> None:
    repo_root = Path(".").resolve()
    commit = _baseline_commit(repo_root)
    payloads = run_surface_resolution_packet(repo_root, baseline_commit=commit)
    receipt = payloads["surface_resolution_receipt.latest.json"]
    print(f"surface resolution: {receipt['packet_status']} -> {OUTPUT_REL}")


if __name__ == "__main__":
    main()