from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.sync.v2_hygiene_phase1_clean_frontier_operator_authorization_bridge import (  # noqa: E402
    BRIDGE_JSON_PATH,
    write_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge,
)


def run(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    return write_v2_hygiene_phase1_clean_frontier_operator_authorization_bridge(
        repo_root,
        out_root=out_root,
    )


def main() -> None:
    packet = run()
    print(f"wrote {BRIDGE_JSON_PATH}")
    print(f"status={packet['status']}")
    print(f"bridge_hash={packet['bridge_hash']}")


if __name__ == "__main__":
    main()
