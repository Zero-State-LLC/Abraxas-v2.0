from __future__ import annotations

from pathlib import Path

from core.audit.main_cleanliness_receipt import (
    DEFAULT_OUT_PATH,
    build_main_cleanliness_receipt,
    write_main_cleanliness_receipt,
)


def run(*, repo_root: str | Path = ".", out_path: str | Path | None = None):
    root = Path(repo_root)
    packet = build_main_cleanliness_receipt(repo_root=root)
    target = Path(out_path) if out_path is not None else root / DEFAULT_OUT_PATH
    write_main_cleanliness_receipt(target, packet)
    return packet


if __name__ == "__main__":
    result = run()
    print(result["status"], result["canonical_hash"][:16], result.get("commit_sha", "")[:12])
    raise SystemExit(0 if result["status"] == "PASS" else 1)
