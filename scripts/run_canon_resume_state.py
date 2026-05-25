from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.canon_resume_state import build_canon_resume_state, write_canon_resume_state  # noqa: E402
from scripts.common.runner import print_packet_fields, run_packet_and_write  # noqa: E402

OUT_PATH = Path("out/canon_resume_state/latest.json")


def run(
    *,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    return run_packet_and_write(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=OUT_PATH,
        build_packet=build_canon_resume_state,
        write_packet=write_canon_resume_state,
    )


def main() -> int:
    packet = run()
    print_packet_fields(
        packet,
        "recommended_resume_lane",
        "canonical_status",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
