"""Operator review queue builder for ABRAXAS v2.0."""

from __future__ import annotations

from typing import Any

from core.governance.authority import locked_authority
from core.governance.doctrine import SCHEMA_VERSION_REVIEW_QUEUE


def _priority(gate_results: list[dict[str, Any]]) -> str:
    for g in gate_results:
        if not g["passed"]:
            reason = g.get("reason", "")
            if "authority" in reason.lower():
                return "P0"
            if any(kw in reason.lower() for kw in ("missing rune", "missing route", "proof")):
                return "P1"
    return "P2"


def build_review_queue(validation_run: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the operator review queue from a validation run result list."""
    items = []
    for result in validation_run:
        if result["status"] in ("repair_required", "not_computable"):
            priority = _priority(result.get("gate_results", []))
            items.append(
                {
                    "pipeline_id": result["pipeline_id"],
                    "status": result["status"],
                    "priority": priority,
                    "gate_results": result.get("gate_results", []),
                }
            )

    recommended = "review" if items else "hold"
    return {
        "schema_version": SCHEMA_VERSION_REVIEW_QUEUE,
        "queue_item_count": len(items),
        "items": items,
        "authority": locked_authority(),
        "recommended_next_state": recommended,
    }
