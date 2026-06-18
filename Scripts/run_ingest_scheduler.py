from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.ingest.scheduler import (  # noqa: E402
    build_scheduled_manifest,
    build_scheduler_receipt,
    decide_ingest_windows,
    write_scheduler_outputs,
)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic controlled ingest scheduler.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--anomaly-state", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--now", default=None)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    policy = _read_json(Path(args.policy))
    decision_set = decide_ingest_windows(
        adapter_config_set=_read_json(Path(args.config)),
        window_policy=policy,
        scheduler_state=_read_json(Path(args.state)),
        anomaly_state=_read_json(Path(args.anomaly_state)),
        now_iso=args.now or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    )
    manifest = build_scheduled_manifest(
        decision_set,
        max_concurrent_adapters=int(policy["global"]["max_concurrent_adapters"]),
        oracle_signal_module_present=(ROOT / "core/oracle_signal.py").exists(),
    )
    receipt = build_scheduler_receipt(decision_set, manifest)
    write_scheduler_outputs(Path(args.out), decision_set=decision_set, manifest=manifest, receipt=receipt)
    print("CONTROLLED_INGEST_SCHEDULER_READY")
    print(receipt["receipt_hash"])


if __name__ == "__main__":
    main()
