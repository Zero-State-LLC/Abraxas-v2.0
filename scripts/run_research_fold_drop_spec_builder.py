from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.research_fold_drop_spec_builder import (  # noqa: E402
    build_research_fold_drop_spec_builder,
    write_research_fold_drop_spec_builder,
)
from scripts.common.runner import print_packet_fields, run_packet_and_write  # noqa: E402

OUT_PATH = Path("out/research_fold_drop_spec_builder/latest.json")


def run(
    *,
    p94_packet: dict[str, object] | None = None,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    return run_packet_and_write(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=OUT_PATH,
        build_packet=lambda **_: build_research_fold_drop_spec_builder(
            p94_packet=p94_packet,
        ),
        write_packet=write_research_fold_drop_spec_builder,
    )


def main() -> int:
    packet = run()
    print_packet_fields(
        packet,
        "status",
        "recommended_next_lane",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
