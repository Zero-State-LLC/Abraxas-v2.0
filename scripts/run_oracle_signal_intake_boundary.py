from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.oracle_signal_intake_boundary import (  # noqa: E402
    QUEUE_JSON_PATH,
    RECEIPT_JSON_PATH,
    RECEIPT_MD_PATH,
    SPEC_JSON_PATH,
    write_oracle_signal_intake_receipt,
)


def run(
    *,
    repo_root: str | Path = ROOT,
    out_root: str | Path | None = None,
    queue_path: str | Path = QUEUE_JSON_PATH,
    spec_path: str | Path = SPEC_JSON_PATH,
    out_json: str | Path = RECEIPT_JSON_PATH,
    out_md: str | Path = RECEIPT_MD_PATH,
) -> dict[str, object]:
    return write_oracle_signal_intake_receipt(
        source_root=repo_root,
        out_root=out_root,
        queue_path=queue_path,
        spec_path=spec_path,
        out_json=out_json,
        out_md=out_md,
    )


def main() -> int:
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
