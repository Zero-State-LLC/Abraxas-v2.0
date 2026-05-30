#!/usr/bin/env python3
"""Runner: emit NormGeometryBaselinePromotionGate.v1 artifact."""
from __future__ import annotations

import json
import logging
import sys

from core.config import RuntimePaths
from core.norm_geometry_baseline_promotion_gate import (
    NormGeometryBaselinePromotionGateError,
    build_baseline_promotion_gate,
    validate_baseline_promotion_gate,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)


def main() -> None:
    paths = RuntimePaths.from_env()
    out_path = paths.norm_geometry_baseline_promotion_gate_latest

    log.info("Building NormGeometryBaselinePromotionGate.v1 ...")
    gate = build_baseline_promotion_gate()

    log.info("Validating ...")
    try:
        validate_baseline_promotion_gate(gate)
    except NormGeometryBaselinePromotionGateError as exc:
        log.error("Validation failed: %s", exc)
        sys.exit(1)

    log.info(
        "all_gate_passed=%s  decision=%s  closure=%s  current_pack=%s  scope=%s",
        gate["all_gate_passed"],
        gate["decision_review"]["decision_review_passed"],
        gate["closure_review"]["closure_review_passed"],
        gate["current_baseline_pack_review"]["current_pack_review_passed"],
        gate["authorized_pack_update_scope"]["pack_update_scope_passed"],
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(gate, indent=4) + "\n")
    log.info(
        "Wrote %s  canonical_hash=%s  status=%s",
        out_path,
        gate["canonical_hash"][:16] + "…",
        gate["gate_status"],
    )


if __name__ == "__main__":
    main()
