#!/usr/bin/env python3
"""Run Track B contract closure receipt generation.

Evidence-only runner. It writes a deterministic receipt under out/ and grants no
runtime, canon, production, forecast-weight, queue-write, or GitHub writeback
authority.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.track_b_contract_closure import (  # noqa: E402
    DEFAULT_OUT_PATH,
    write_track_b_contract_closure_receipt,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--out", type=Path, default=Path(DEFAULT_OUT_PATH))
    args = parser.parse_args()

    payload = write_track_b_contract_closure_receipt(args.repo_root, args.out)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "TRACK_B_CONTRACT_CLOSURE_ALIGNED_ADVISORY_ONLY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
