from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.global_ingest_adapter_spine_implementation_spec import (  # noqa: E402
    write_global_ingest_adapter_spine_implementation_spec,
)


def run(*, repo_root: str | Path = ROOT, out_root: str | Path | None = None) -> dict[str, object]:
    return write_global_ingest_adapter_spine_implementation_spec(repo_root, out_root=out_root)


def main() -> int:
    packet = run()
    print(packet["status"])
    print(packet["recommended_next_patch"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
