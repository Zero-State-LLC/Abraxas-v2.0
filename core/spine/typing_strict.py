from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json
from core.governance.authority import locked_authority


def run_pyright_check() -> bool:
    pyright_bin = shutil.which("pyright")
    command = [pyright_bin] if pyright_bin else [sys.executable, "-m", "pyright"]
    command.extend(["--pythonpath", sys.executable])
    completed = subprocess.run(
        command,
        cwd=Path.cwd(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return completed.returncode == 0


def emit_strict_typing_packet(pyright_clean: bool | None = None) -> dict[str, Any]:
    import json

    cfg = json.loads(Path("pyrightconfig.json").read_text(encoding="utf-8"))
    clean = run_pyright_check() if pyright_clean is None else pyright_clean
    packet = {
        "schema_version": "StrictTypingStatusPacket.v1",
        "strict_mode": cfg.get("typeCheckingMode") == "strict",
        "pyright_clean": clean,
        "included_paths": cfg.get("include", []),
        "excluded_paths": cfg.get("exclude", []),
        "total_modules_checked": len(cfg.get("include", [])),
        "authority": locked_authority(),
        "status": "passed" if clean and cfg.get("typeCheckingMode") == "strict" else "failed",
    }
    write_canonical_json("out/typing/strict_typing.latest.json", packet)
    return packet
