"""AAL-Viz projection packet builder for ABRAXAS v2.0."""

from __future__ import annotations

from typing import Any

from core.governance.authority import locked_authority
from core.governance.doctrine import SCHEMA_VERSION_AAL_VIZ


def build_projection_packet(
    registry: dict[str, Any],
    validation: list[dict[str, Any]],
    queue: dict[str, Any],
    continuity: dict[str, Any] | None = None,
    typing_status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    projection_only = True
    inference_authority = False

    total = registry.get("pipeline_count", 0)
    compliant = sum(1 for r in validation if r.get("status") == "doctrine_compliant")
    repair = sum(1 for r in validation if r.get("status") == "repair_required")
    not_computable = sum(1 for r in validation if r.get("status") == "not_computable")

    panels = [{"pipeline_id": r["pipeline_id"], "status": r["status"], "gate_summary": [{"gate": g["gate"], "passed": g["passed"]} for g in r.get("gate_results", [])]} for r in validation]
    continuity = continuity or {}

    typing_status = typing_status or {}
    packet: dict[str, Any] = {
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
        "continuity_summary": {
            "prior_scripts_present": not continuity.get("missing_scripts", [1]),
            "prior_artifacts_present": not continuity.get("missing_artifacts", [1]),
            "prior_routes_present": not continuity.get("missing_routes", [1]),
            "continuity_failures": len(continuity.get("missing_scripts", [])) + len(continuity.get("missing_artifacts", [])) + len(continuity.get("missing_routes", [])),
        },
        "typing_summary": {"strict_mode_enabled": typing_status.get("strict_mode", False), "pyright_errors": 0 if typing_status.get("pyright_clean") else 1, "pyright_warnings": 0, "excluded_paths": typing_status.get("excluded_paths", []), "typing_gate_status": typing_status.get("status", "unknown")},
        "panels": panels,
        "authority": locked_authority(),
    }
    return packet
