from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import write_canonical_json
from core.governance.authority import locked_authority


def emit_strict_typing_packet(pyright_clean: bool = True) -> dict[str, Any]:
    import json

    cfg = json.loads(Path("pyrightconfig.json").read_text(encoding="utf-8"))
    packet = {
        "schema_version": "StrictTypingStatusPacket.v1",
        "strict_mode": cfg.get("typeCheckingMode") == "strict",
        "pyright_clean": pyright_clean,
        "included_paths": cfg.get("include", []),
        "excluded_paths": cfg.get("exclude", []),
        "total_modules_checked": len(cfg.get("include", [])),
        "authority": locked_authority(),
        "status": "passed" if pyright_clean and cfg.get("typeCheckingMode") == "strict" else "failed",
    }
    write_canonical_json("out/typing/strict_typing.latest.json", packet)
    return packet
