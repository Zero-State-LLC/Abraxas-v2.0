"""Script: emit deterministic temporal upstream evidence receipt."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import RuntimePaths
from core.temporal_upstream_evidence import (
    build_temporal_upstream_evidence_receipt,
    write_temporal_upstream_evidence_receipt,
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.audit_dir / "temporal_upstream_evidence_001.latest.json"


def main(_argv: list[str] | None = None) -> None:
    receipt = build_temporal_upstream_evidence_receipt()
    write_temporal_upstream_evidence_receipt(OUT_PATH, receipt)
    logging.info("temporal_upstream_evidence_completed final_evidence_status=%s", receipt["final_evidence_status"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
