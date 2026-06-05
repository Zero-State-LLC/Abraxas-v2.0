from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.sync.oracle_confidence_calibration_contract_dry_run import (  # noqa: E402
    OUT_JSON,
    OUT_MD,
    build_oracle_confidence_calibration_contract_dry_run,
    write_oracle_confidence_calibration_contract_dry_run,
    write_oracle_confidence_calibration_contract_dry_run_markdown,
)


def run(*, repo_root: str | Path = ROOT, out_json: str | Path | None = None, out_md: str | Path | None = None):
    root = Path(repo_root)
    packet = build_oracle_confidence_calibration_contract_dry_run(repo_root=root)
    json_target = Path(out_json) if out_json is not None else root / OUT_JSON
    md_target = Path(out_md) if out_md is not None else root / OUT_MD
    write_oracle_confidence_calibration_contract_dry_run(json_target, packet)
    write_oracle_confidence_calibration_contract_dry_run_markdown(md_target, packet)
    return packet


def main() -> int:
    packet = run()
    print(json.dumps({"dry_run_id": packet["dry_run_id"], "dry_run_status": packet["dry_run_status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
