from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.ingest.runtime_handoff_executor import (  # noqa: E402
    build_oracle_intake_queue,
    build_runtime_handoff_receipt_set,
    build_sample_manifest_and_config,
    build_source_pull_receipt_set,
    write_runtime_handoff_outputs,
)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic scheduler-to-runtime handoff executor.")
    parser.add_argument("--manifest")
    parser.add_argument("--config")
    parser.add_argument("--out", default="out/ingest")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.manifest and args.config:
        manifest = _read_json(Path(args.manifest))
        config = _read_json(Path(args.config))
    elif args.manifest or args.config:
        raise SystemExit("provide both --manifest and --config, or neither")
    else:
        manifest, config = build_sample_manifest_and_config()

    source_pull_receipt_set = build_source_pull_receipt_set(manifest, config)
    runtime_handoff_receipt_set = build_runtime_handoff_receipt_set(
        manifest,
        config,
        source_pull_receipt_set=source_pull_receipt_set,
    )
    oracle_intake_queue = build_oracle_intake_queue(
        manifest,
        config,
        runtime_handoff_receipt_set=runtime_handoff_receipt_set,
    )
    write_runtime_handoff_outputs(
        Path(args.out),
        runtime_handoff_receipt_set=runtime_handoff_receipt_set,
        source_pull_receipt_set=source_pull_receipt_set,
        oracle_intake_queue=oracle_intake_queue,
    )
    print("AUTO_INGEST_RUNTIME_HANDOFF_READY")
    print(runtime_handoff_receipt_set["receipt_set_hash"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
