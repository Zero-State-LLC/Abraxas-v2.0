#!/usr/bin/env python3
"""Sole-writer for milestone continuity packet (TD Wave 1)."""

from __future__ import annotations

from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.spine.milestone_continuity import validate_milestone_continuity

_OUT_ROOT = Path("out")


def main() -> None:
    packet = validate_milestone_continuity()
    write_classified_json(
        "out/spine/milestone_continuity.latest.json",
        packet.model_dump(),
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    print(packet.status)


if __name__ == "__main__":
    main()
