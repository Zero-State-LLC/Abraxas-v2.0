from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.abx_artifact_lineage_registry_direct_repair_approval_validation_dry_run import (  # noqa: E402
    OUT_JSON,
    OUT_MD,
    write_abx_artifact_lineage_registry_direct_repair_approval_validation_dry_run,
)


def run(
    *,
    repo_root: str | Path = ROOT,
    out_json: str | Path | None = None,
    out_md: str | Path | None = None,
):
    root = Path(repo_root)
    json_path = Path(out_json) if out_json is not None else root / OUT_JSON
    md_path = Path(out_md) if out_md is not None else root / OUT_MD
    return write_abx_artifact_lineage_registry_direct_repair_approval_validation_dry_run(json_path, md_path)


def main() -> int:
    packet = run()
    print(json.dumps({"dry_run_id": packet["dry_run_id"], "status": packet["status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
