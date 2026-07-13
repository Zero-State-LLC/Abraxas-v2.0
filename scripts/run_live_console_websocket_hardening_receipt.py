from __future__ import annotations

from pathlib import Path

from scripts._receipt_runner import run_receipt


def run(*, repo_root: str | Path = ".", out_path: str | Path | None = None):
    return run_receipt("core.live_console_websocket_hardening", repo_root=repo_root, out_path=out_path)
