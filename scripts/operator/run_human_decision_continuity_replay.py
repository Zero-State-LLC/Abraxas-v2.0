#!/usr/bin/env python3
"""Ensure human decision continuity packet exists; fail closed if missing."""

from __future__ import annotations

from pathlib import Path

if __name__ == "__main__":
    path = Path("out/human_decision_continuity/latest.json")
    if not path.exists():
        raise FileNotFoundError(
            "required artifact missing: out/human_decision_continuity/latest.json "
            "(refuse empty-list synthetic continuity packet)"
        )
    print(path.read_text(encoding="utf-8"))
