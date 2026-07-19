#!/usr/bin/env python3
"""Sole-writer for milestone continuity packet (TD Wave 1)."""

from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.spine.milestone_continuity import validate_milestone_continuity


def main() -> None:
    packet = validate_milestone_continuity()
    write_canonical_json(
        "out/spine/milestone_continuity.latest.json", packet.model_dump()
    )
    print(packet.status)


if __name__ == "__main__":
    main()
