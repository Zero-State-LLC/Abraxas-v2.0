"""AAL-Viz projection packet builder for ABRAXAS v2.0.

AAL-Viz is PROJECTION-ONLY.  It has no inference authority.
"""

from __future__ import annotations

from typing import Any

from core.governance.authority import locked_authority
from core.governance.doctrine import SCHEMA_VERSION_AAL_VIZ


def build_projection_packet(
    registry: dict[str, Any],
    validation: list[dict[str, Any]],
    queue: dict[str, Any],
) -> dict[str, Any]:
    """Build the AAL-Viz projection packet.

    Raises ValueError if projection_only would be False or inference_authority True.
    """
    projection_only = True
    inference_authority = False

    if not projection_only:
        raise ValueError("AAL-Viz projection_only must be True")
    if inference_authority:
        raise ValueError("AAL-Viz inference_authority must be False")

    total = registry.get("pipeline_count", 0)
    compliant = sum(1 for r in validation if r.get("status") == "doctrine_compliant")
    repair = sum(1 for r in validation if r.get("status") == "repair_required")
    not_computable = sum(1 for r in validation if r.get("status") == "not_computable")

    panels = []
    for result in validation:
        panels.append(
            {
                "pipeline_id": result["pipeline_id"],
                "status": result["status"],
                "gate_summary": [
                    {"gate": g["gate"], "passed": g["passed"]}
                    for g in result.get("gate_results", [])
                ],
            }
        )

    packet = {
        "schema_version": SCHEMA_VERSION_AAL_VIZ,
        "projection_only": projection_only,
        "inference_authority": inference_authority,
        "summary": {
            "total_pipelines": total,
            "doctrine_compliant": compliant,
            "repair_required": repair,
            "not_computable": not_computable,
            "queue_items": queue.get("queue_item_count", 0),
        },
        "panels": panels,
        "authority": locked_authority(),
    }

    # Final invariant checks
    if packet["projection_only"] is not True:
        raise ValueError("projection_only must be True")
    if packet["inference_authority"] is not False:
        raise ValueError("inference_authority must be False")
    auth = packet["authority"]
    bad = [k for k, v in auth.items() if v is True]
    if bad:
        raise ValueError(f"Authority flags must all be False; found: {bad}")

    return packet
