from __future__ import annotations

from pathlib import Path

from core.live_console_migration_preflight_projection import (
    DEFAULT_OUT_PATH,
    build_live_console_migration_preflight_projection_receipt,
    write_live_console_migration_preflight_projection_receipt,
)


def run(*, repo_root: str | Path = ".", out_path: str | Path | None = None):
    packet = build_live_console_migration_preflight_projection_receipt(
        repo_root=repo_root
    )
    write_live_console_migration_preflight_projection_receipt(
        Path(out_path) if out_path is not None else DEFAULT_OUT_PATH,
        packet,
    )
    return packet
