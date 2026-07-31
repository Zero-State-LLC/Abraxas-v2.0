from __future__ import annotations

import argparse
from pathlib import Path

from core.audit.fast_ci_receipt import (
    DEFAULT_OUT_PATH,
    build_fast_ci_receipt,
    write_fast_ci_receipt,
)


def run(
    *,
    repo_root: str | Path = ".",
    out_path: str | Path | None = None,
    execute_smoke: bool = False,
):
    root = Path(repo_root)
    packet = build_fast_ci_receipt(repo_root=root, execute_smoke=execute_smoke)
    target = Path(out_path) if out_path is not None else root / DEFAULT_OUT_PATH
    write_fast_ci_receipt(target, packet)
    return packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit FastCiReceipt.v0 (advisory)")
    parser.add_argument(
        "--execute-smoke",
        action="store_true",
        help="Run bounded smoke checks (pytest main-scope + ruff audit modules + import)",
    )
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    packet = run(
        repo_root=args.repo_root,
        out_path=args.out,
        execute_smoke=args.execute_smoke,
    )
    print(
        packet["status"],
        packet["mode"],
        packet["canonical_hash"][:16],
        (packet.get("commit_sha") or "")[:12],
    )
    if packet["status"] == "PASS":
        return 0
    if packet["status"] == "FAIL":
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
