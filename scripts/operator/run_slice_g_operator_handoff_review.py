#!/usr/bin/env python3
"""Run Slice G operator handoff review receipt generation.

SHADOW/advisory-only. Writes deterministic HandoffEnvelope.v1 and
SkillPatchCandidate evidence for operator review. Grants no execution,
promotion, mount, canon, CLEAR, production, GitHub, or Notion authority.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.slice_g_operator_handoff import (
    DEFAULT_FIXTURE,
    DEFAULT_MD_PATH,
    DEFAULT_OUT_PATH,
    write_slice_g_operator_handoff_review,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--fixture", type=Path, default=Path(DEFAULT_FIXTURE))
    parser.add_argument("--out", type=Path, default=Path(DEFAULT_OUT_PATH))
    parser.add_argument("--md", type=Path, default=Path(DEFAULT_MD_PATH))
    args = parser.parse_args(argv)

    receipt = write_slice_g_operator_handoff_review(
        repo_root=args.repo_root,
        fixture_path=args.fixture,
        out_path=args.out,
        md_path=args.md,
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["status"] == "SLICE_G_OPERATOR_HANDOFF_READY_ADVISORY_ONLY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
