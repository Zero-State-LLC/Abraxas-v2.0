from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import RuntimePaths
from core.temporal_state_diff_pulse_ledger import (
    build_temporal_state_diff_pulse_ledger,
    write_temporal_state_diff_pulse_ledger,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.temporal_state_diff_pulse_ledger_latest


def _parse(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build temporal state diff pulse ledger.")
    p.add_argument("--pulse", action="append", default=[], help="Temporal state diff packet path.")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse(argv)
    packet = build_temporal_state_diff_pulse_ledger(pulse_paths=[str(x) for x in args.pulse])
    write_temporal_state_diff_pulse_ledger(OUT_PATH, packet)
    logging.info("temporal_state_diff_pulse_ledger_completed pulse_count=%s", packet["pulse_count"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
