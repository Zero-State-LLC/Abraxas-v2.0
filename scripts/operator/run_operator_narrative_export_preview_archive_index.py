from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import RuntimePaths
from core.operator_narrative_export_preview_archive_index import (
    build_operator_narrative_export_preview_archive_index_packet,
    write_operator_narrative_export_preview_archive_index,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.operator_narrative_export_preview_archive_index_latest
MARKDOWN_OUT_PATH = OUT_PATH.with_suffix(".md")


def main() -> int:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    packet = build_operator_narrative_export_preview_archive_index_packet()
    out = OUT_PATH
    write_operator_narrative_export_preview_archive_index(out, packet)
    print(f"final_status={packet['final_status']}")
    print(f"archive_posture={packet['archive_posture']}")
    print(f"wrote={out.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
