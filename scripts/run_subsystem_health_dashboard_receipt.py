from __future__ import annotations

from pathlib import Path

from core.subsystem_health_dashboard import (
    DEFAULT_OUT_PATH,
    build_subsystem_health_dashboard_receipt,
    write_subsystem_health_dashboard_receipt,
)


def run(*, repo_root: str | Path = ".", out_path: str | Path | None = None):
    packet = build_subsystem_health_dashboard_receipt(repo_root=repo_root)
    write_subsystem_health_dashboard_receipt(
        Path(out_path) if out_path is not None else DEFAULT_OUT_PATH,
        packet,
    )
    return packet
