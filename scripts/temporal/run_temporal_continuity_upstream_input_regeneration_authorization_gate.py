from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.temporal_continuity_upstream_input_regeneration_authorization_gate import build_temporal_continuity_upstream_input_regeneration_authorization_gate, write_temporal_continuity_upstream_input_regeneration_authorization_gate  # noqa: E402
from scripts.common.runner import print_packet_fields, run_packet_and_write  # noqa: E402

OUT_PATH = Path("out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json")


def run(
    *,
    repo_root: str | Path = ROOT,
    out_path: str | Path | None = None,
) -> dict[str, object]:
    return run_packet_and_write(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=OUT_PATH,
        build_packet=build_temporal_continuity_upstream_input_regeneration_authorization_gate,
        write_packet=write_temporal_continuity_upstream_input_regeneration_authorization_gate,
    )


def main() -> int:
    packet = run()
    print_packet_fields(
        packet,
        "authorization_gate_status",
        "recommended_next_lane",
        "canonical_status",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
