#!/usr/bin/env python3
"""Validate console vizPalette hexes match design-system topology palette JSON.

Exit 0 when in sync; exit 1 with diffs otherwise.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PALETTE = ROOT / "design-system" / "viz" / "topology_palette.v1.json"
BRIDGE = ROOT / "apps" / "aal-viz-live-console" / "src" / "design" / "vizPalette.ts"


def main() -> int:
    palette = json.loads(PALETTE.read_text(encoding="utf-8"))
    ts = BRIDGE.read_text(encoding="utf-8")
    errors: list[str] = []

    for key, hex_v in palette["node_classes"].items():
        # NODE_CLASS_COLORS.KEY: '#hex' or KEY: '#hex'
        pat = re.compile(rf"\b{re.escape(key)}\s*:\s*['\"]({re.escape(hex_v)})['\"]", re.I)
        if not pat.search(ts):
            # allow any quoted hex and compare case-insensitive
            m = re.search(rf"\b{re.escape(key)}\s*:\s*['\"](#[0-9a-fA-F]{{6}})['\"]", ts)
            if not m:
                errors.append(f"missing node class {key} in vizPalette.ts")
            elif m.group(1).lower() != hex_v.lower():
                errors.append(f"node {key}: palette {hex_v} vs bridge {m.group(1)}")

    for key, hex_v in palette["integrity"].items():
        m = re.search(rf"\b{re.escape(key)}\s*:\s*['\"](#[0-9a-fA-F]{{6}})['\"]", ts)
        if not m:
            errors.append(f"missing integrity {key}")
        elif m.group(1).lower() != hex_v.lower():
            errors.append(f"integrity {key}: {hex_v} vs {m.group(1)}")

    if errors:
        print("VIZ_PALETTE_SYNC_FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print(
        json.dumps(
            {
                "status": "OK",
                "node_classes": len(palette["node_classes"]),
                "integrity": len(palette["integrity"]),
                "palette": str(PALETTE.relative_to(ROOT)),
                "bridge": str(BRIDGE.relative_to(ROOT)),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
