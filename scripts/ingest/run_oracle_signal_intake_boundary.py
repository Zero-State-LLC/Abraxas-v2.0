from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.oracle_signal_intake_boundary import write_oracle_signal_intake_receipt  # noqa: E402


def run(
    *,
    repo_root: str | Path | None = None,
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
    out_json: str | Path | None = None,
    out_md: str | Path | None = None,
):
    if repo_root is not None:
        source_root = repo_root
    kwargs = {"source_root": source_root, "out_root": out_root}
    if out_json is not None:
        kwargs["out_json"] = out_json
    if out_md is not None:
        kwargs["out_md"] = out_md
    return write_oracle_signal_intake_receipt(**kwargs)


def main(argv: list[str] | None = None) -> None:
    del argv
    run()


if __name__ == "__main__":
    main()
