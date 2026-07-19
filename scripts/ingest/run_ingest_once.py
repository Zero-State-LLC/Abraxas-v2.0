"""Script: emit deterministic local/static universal ingest receipt."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import RuntimePaths
from core.ingest.universal_ingest_receipt import (
    build_from_input_path,
    write_universal_ingest_receipt,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.out_dir / "ingest" / "universal_ingest_receipt_001.latest.json"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic local/static ingest receipt.")
    parser.add_argument(
        "--input",
        default=None,
        help="Optional local JSON payload path with an `items` array.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    input_path = Path(args.input) if isinstance(args.input, str) and args.input else None
    packet = build_from_input_path(input_path)
    write_universal_ingest_receipt(OUT_PATH, packet)
    logging.info(
        "universal_ingest_receipt_completed status=%s item_count=%s",
        packet["status"],
        packet["item_count"],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
