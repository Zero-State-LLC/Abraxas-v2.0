from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.continuity_namespace_migration_runner import (  # noqa: E402
    DEFAULT_OUT_PATH,
    build_continuity_namespace_migration_run_receipt,
    write_continuity_namespace_migration_run_receipt,
)

OUT_PATH = Path(DEFAULT_OUT_PATH)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Emit the advisory continuity namespace migration run receipt."
    )
    parser.add_argument(
        "--requested-mode",
        choices=("advisory", "execute-like"),
        default="advisory",
        help="Execution-style requests remain blocked in this slice.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=OUT_PATH,
        help="Optional output path for the generated receipt.",
    )
    return parser.parse_args(argv)


def run(
    *,
    repo_root: Path | str | None = None,
    output_path: Path | str | None = None,
    requested_mode: str = "advisory",
) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else ROOT
    target = root / (Path(output_path) if output_path is not None else OUT_PATH)
    packet = build_continuity_namespace_migration_run_receipt(
        repo_root=root,
        requested_mode=requested_mode,
    )
    write_continuity_namespace_migration_run_receipt(target, packet)
    return packet


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    packet = run(output_path=args.out, requested_mode=args.requested_mode)
    print(f"status: {packet['status']}")
    print(f"canonical_hash: {packet['canonical_hash']}")
    print(f"receipt_path: {args.out}")
    print(
        "execution_request_result: "
        f"{packet['requested_execution_posture']['result']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
