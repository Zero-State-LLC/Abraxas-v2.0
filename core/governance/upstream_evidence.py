from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def require_upstream_packets(
    *named_lists: tuple[str, list[Any]],
    surface: str,
) -> None:
    """Fail closed when upstream evidence lists are empty or placeholder-only."""
    for label, packets in named_lists:
        if not packets:
            raise ValueError(
                f"{surface}: {label} is empty; refuse synthetic passed packet"
            )
        for index, packet in enumerate(packets):
            if not isinstance(packet, dict) or not packet:
                raise ValueError(
                    f"{surface}: {label}[{index}] is empty/malformed; "
                    "refuse synthetic passed packet"
                )


def load_required_upstream_packet(path: str | Path) -> list[dict[str, Any]]:
    """Load one required upstream JSON object as a single-item packet list."""
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(
            f"required upstream artifact missing: {target.as_posix()} "
            "(refuse empty-list synthetic passed packet)"
        )
    payload = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not payload:
        raise ValueError(
            f"required upstream artifact must be a non-empty JSON object: "
            f"{target.as_posix()}"
        )
    return [payload]
