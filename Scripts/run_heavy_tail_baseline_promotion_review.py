from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import RuntimePaths
from core.heavy_tail_baseline_promotion_review import (
    build_heavy_tail_baseline_promotion_review,
    validate_heavy_tail_baseline_promotion_review,
)


def main() -> int:
    paths = RuntimePaths.from_env()
    out_path = paths.heavy_tail_baseline_promotion_review_001_latest
    review = build_heavy_tail_baseline_promotion_review()
    validate_heavy_tail_baseline_promotion_review(review)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(review, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("heavy_tail_baseline_promotion_review_written", out_path)
    print("canonical_hash", review["canonical_hash"])
    print("recommended_next_step", review["recommended_next_step"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
