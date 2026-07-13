from __future__ import annotations

from pathlib import Path

from core.continuity_namespace_migration_runner import (
    build_continuity_namespace_migration_run_receipt,
    write_continuity_namespace_migration_run_receipt,
)


def run(
    *,
    repo_root: str | Path = ".",
    output_path: str | Path | None = None,
):
    packet = build_continuity_namespace_migration_run_receipt(repo_root=repo_root)
    target = Path(output_path or "out/audit/continuity_namespace_migration_run_001.latest.json")
    write_continuity_namespace_migration_run_receipt(target, packet)
    return packet
