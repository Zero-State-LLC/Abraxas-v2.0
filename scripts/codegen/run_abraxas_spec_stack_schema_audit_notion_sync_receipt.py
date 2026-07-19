from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.abraxas_spec_stack_schema_audit_notion_sync_receipt import (  # noqa: E402
    write_abraxas_spec_stack_schema_audit_notion_sync_receipt,
)


def run(*, repo_root: str | Path = ROOT, out_root: str | Path | None = None) -> dict:
    return write_abraxas_spec_stack_schema_audit_notion_sync_receipt(
        repo_root,
        out_root=out_root,
    )


def main() -> int:
    packet = run()
    print(packet["receipt_id"])
    print(packet["status"])
    print(packet["recommended_next_lane"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
