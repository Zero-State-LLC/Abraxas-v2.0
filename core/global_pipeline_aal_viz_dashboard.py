from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

DASHBOARD_SCHEMA_VERSION = "GlobalPipelineAALVizDashboardPacket.v1"
VIEW_STATE_SCHEMA_VERSION = "GlobalPipelineAALVizViewState.v1"

REGISTRY_PATH = Path("out/global_pipeline_registry/latest.json")
DOCTRINE_PROOF_PATH = Path("out/global_pipeline_doctrine_validation/latest.json")
DOCTRINE_REVIEW_PATH = Path("out/global_pipeline_doctrine_validation/operator_review_packet.latest.json")
QUEUE_PATH = Path("out/operator_review_queue/latest.json")
PROJECTION_PATH = Path("out/projections/global_pipeline_aal_viz_projection_packet_001.latest.json")

DASHBOARD_JSON_PATH = Path("out/global_pipeline_aal_viz/dashboard_packet.latest.json")
DASHBOARD_MD_PATH = Path("out/global_pipeline_aal_viz/dashboard_packet.latest.md")
VIEW_STATE_JSON_PATH = Path("out/global_pipeline_aal_viz/view_state.latest.json")
VIEW_STATE_MD_PATH = Path("out/global_pipeline_aal_viz/view_state.latest.md")


def _read_json(root: Path, rel_path: Path) -> dict[str, Any]:
    import json

    return json.loads((root / rel_path).read_text(encoding="utf-8"))


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _panel(
    panel_id: str,
    title: str,
    status: str,
    summary: str,
    source_paths: list[str],
    metrics: dict[str, Any],
) -> dict[str, Any]:
    return {
        "panel_id": panel_id,
        "title": title,
        "status": status,
        "summary": summary,
        "source_paths": source_paths,
        "metrics": metrics,
        "projection_only": True,
        "non_authoritative": True,
    }


def _tile(
    tile_id: str,
    title: str,
    status: str,
    value: Any,
    detail: str,
) -> dict[str, Any]:
    return {
        "tile_id": tile_id,
        "title": title,
        "status": status,
        "value": value,
        "detail": detail,
        "projection_only": True,
        "non_authoritative": True,
    }


def build_global_pipeline_aal_viz_dashboard_packet(
    root: Path | str = ".",
    *,
    source_root: Path | str | None = None,
) -> dict[str, Any]:
    base = Path(root)
    source_base = Path(source_root) if source_root is not None else base

    registry = _read_json(source_base, REGISTRY_PATH)
    doctrine = _read_json(source_base, DOCTRINE_PROOF_PATH)
    review = _read_json(source_base, DOCTRINE_REVIEW_PATH)
    queue = _read_json(source_base, QUEUE_PATH)
    projection = _read_json(source_base, PROJECTION_PATH)

    review_required = review.get("state") in {"repair_required", "held", "rejected"}
    blocked_pipeline_count = doctrine["missing_contract_count"] + doctrine["missing_validation_count"]
    held_count = int(queue["state_counts"].get("held", 0))
    p0_count = int(queue.get("p0_count", projection["priority_counts"].get("P0", 0)))

    operator_review_summary = (
        "Operator review remains fail-closed behind a held P0 Global Ingest decision and unresolved doctrine gaps."
        if review.get("state") == "held"
        else "Operator review remains fail-closed until doctrine gaps are acknowledged or repaired."
    )

    panels = [
        _panel(
            "registry_overview",
            "Global pipeline registry",
            "OBSERVED",
            "Global pipeline inventory is widened and deterministic.",
            [REGISTRY_PATH.as_posix()],
            {
                "pipeline_count": registry["pipeline_count"],
                "tier_counts": registry["tier_counts"],
                "recommended_next_state": registry["recommended_next_state"],
            },
        ),
        _panel(
            "doctrine_proof",
            "Doctrine validation proof",
            "REPAIR_REQUIRED" if review_required else "OBSERVED",
            "Doctrine proof exposes missing contracts and validation coverage without authority leakage.",
            [DOCTRINE_PROOF_PATH.as_posix()],
            {
                "pipeline_count": doctrine["pipeline_count"],
                "observed_validation_count": doctrine["observed_validation_count"],
                "missing_contract_count": doctrine["missing_contract_count"],
                "missing_validation_count": doctrine["missing_validation_count"],
                "legacy_contract_posture_count": doctrine["legacy_contract_posture_count"],
                "authority_violation_count": doctrine["authority_violation_count"],
            },
        ),
        _panel(
            "operator_review_gate",
            "Doctrine operator review",
            review["state"].upper(),
            operator_review_summary,
            [DOCTRINE_REVIEW_PATH.as_posix()],
            {
                "priority": review["priority"],
                "state": review["state"],
                "blocked_reasons": review["blocked_reasons"],
                "required_operator_actions": review["required_operator_actions"],
            },
        ),
        _panel(
            "queue_projection",
            "Queue and projection posture",
            projection["recommended_next_state"].upper(),
            "Review queue stays advisory-only and now exposes the held P0 Global Ingest decision alongside existing review items."
            if held_count > 0
            else "Review queue stays advisory-only and exposes the next visible pipeline posture for AAL-Viz.",
            [QUEUE_PATH.as_posix(), PROJECTION_PATH.as_posix()],
            {
                "queue_item_count": queue["queue_item_count"],
                "state_counts": queue["state_counts"],
                "priority_counts": projection["priority_counts"],
                "stabilization_ready_count": projection["stabilization_ready_count"],
            },
        ),
    ]

    tiles = [
        _tile(
            "authority_lock_panel",
            "Authority Lock",
            "LOCKED",
            "LOCKED",
            "All dashboard surfaces remain projection-only and non-authoritative.",
        ),
        _tile(
            "registry_panel",
            "Registry Coverage",
            "OBSERVED",
            registry["pipeline_count"],
            "Global pipeline registry entries observed.",
        ),
        _tile(
            "doctrine_gap_panel",
            "Doctrine Gaps",
            "REPAIR_REQUIRED" if review_required else "OBSERVED",
            blocked_pipeline_count,
            "Missing contract plus validation coverage count across the pipeline inventory.",
        ),
        _tile(
            "queue_review_panel",
            "Queue Review State",
            "HELD" if held_count > 0 else review["state"].upper(),
            queue["recommended_next_state"],
            "Operator review queue remains the next advisory posture, with the highest-priority item held for explicit operator decision."
            if held_count > 0
            else "Operator review queue remains the next advisory posture.",
        ),
        _tile(
            "projection_panel",
            "Projection Readiness",
            "PROJECTION_ONLY",
            projection["queue_item_count"],
            "AAL-Viz projection packet is available without forecast or execution authority.",
        ),
    ]

    alerts: list[dict[str, Any]] = []
    if doctrine["missing_contract_count"] > 0:
        alerts.append(
            {
                "alert_id": "missing_contracts",
                "severity": "WARN",
                "message": "Global pipeline contracts are still missing for part of the inventory.",
                "count": doctrine["missing_contract_count"],
                "projection_only": True,
            }
        )
    if doctrine["missing_validation_count"] > 0:
        alerts.append(
            {
                "alert_id": "missing_validation",
                "severity": "WARN",
                "message": "Validation coverage is still incomplete across the global pipeline inventory.",
                "count": doctrine["missing_validation_count"],
                "projection_only": True,
            }
        )
    if review_required:
        alerts.append(
            {
                "alert_id": "operator_review_required",
                "severity": "BLOCKED",
                "message": (
                    "Dashboard is visible, but physical repo execution remains blocked behind a held P0 operator decision request."
                    if review.get("state") == "held"
                    else "Dashboard is visible, but physical repo execution remains blocked pending operator review and repair."
                ),
                "count": held_count if review.get("state") == "held" else len(review["blocked_reasons"]),
                "projection_only": True,
            }
        )

    packet: dict[str, Any] = {
        "schema_version": DASHBOARD_SCHEMA_VERSION,
        "dashboard_id": "",
        "status": "GLOBAL_PIPELINE_AAL_VIZ_DASHBOARD_PACKET_EMITTED",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "forecast_weight_allowed": False,
        "promotion_allowed": False,
        "source_hashes": {
            "registry": registry["registry_id"],
            "doctrine_proof": doctrine["proof_id"],
            "doctrine_review": review["review_packet_id"],
            "queue_run": queue["run_id"],
            "projection": projection["projection_id"],
        },
        "summary": {
            "pipeline_count": registry["pipeline_count"],
            "queue_item_count": queue["queue_item_count"],
            "doctrine_compliant_count": doctrine["doctrine_compliant_count"],
            "missing_contract_count": doctrine["missing_contract_count"],
            "missing_validation_count": doctrine["missing_validation_count"],
            "legacy_contract_posture_count": doctrine["legacy_contract_posture_count"],
            "held_queue_item_count": held_count,
            "p0_queue_item_count": p0_count,
            "stabilization_ready_count": projection["stabilization_ready_count"],
            "authority_violation_count": doctrine["authority_violation_count"],
        },
        "panels": panels,
        "tiles": tiles,
        "alerts": alerts,
        "recommended_next_state": "review" if review_required else "hold",
        "recommended_next_commands": (
            ["HOLD_FOR_OPERATOR_REVIEW", "COLLECT_OPERATOR_DECISION_EVIDENCE"]
            if review.get("state") == "held"
            else ["HOLD_FOR_OPERATOR_REVIEW", "REQUEST_GLOBAL_PIPELINE_REPAIR"]
            if review_required
            else ["RUN_GLOBAL_PIPELINE_REPO_EXECUTION_PREP_001"]
        ),
        "physical_repo_implementation_ready": False,
        "blocked_reasons": review["blocked_reasons"],
    }
    packet["dashboard_id"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "dashboard_id"}
    )
    return packet


def build_global_pipeline_aal_viz_view_state(
    dashboard_packet: dict[str, Any],
) -> dict[str, Any]:
    highlighted_pipeline_ids = [
        "aal_viz_projection",
        "operator_review_queue",
        "oracle_signal",
        "universal_ingest",
        "research_intake",
    ]
    view_state: dict[str, Any] = {
        "schema_version": VIEW_STATE_SCHEMA_VERSION,
        "view_state_id": "",
        "dashboard_id": dashboard_packet["dashboard_id"],
        "status": "GLOBAL_PIPELINE_AAL_VIZ_VIEW_STATE_EMITTED",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "default_view": "overview",
        "selected_panel_id": "operator_review_gate",
        "selected_tile_id": "authority_lock_panel",
        "tabs": [
            {"tab_id": "overview", "title": "Overview"},
            {"tab_id": "doctrine", "title": "Doctrine"},
            {"tab_id": "queue", "title": "Queue"},
            {"tab_id": "blocked", "title": "Blocked"},
        ],
        "filters": {
            "tier_options": ["1", "2", "3"],
            "lane_options": ["PROJECTION", "GOVERNANCE", "GOVERNANCE_SHADOW", "SHADOW", "FORECAST_GATED"],
            "state_options": [
                "eligible_for_operator_review",
                "eligible_for_shadow_stabilization",
                "repair_required",
                "held",
                "rejected",
            ],
        },
        "focus": {
            "review_state": dashboard_packet["recommended_next_state"],
            "highlighted_pipeline_ids": highlighted_pipeline_ids,
            "blocked_reason_count": len(dashboard_packet["blocked_reasons"]),
            "authority_lock_status": "LOCKED",
        },
    }
    view_state["view_state_id"] = canonical_hash(
        {key: value for key, value in view_state.items() if key != "view_state_id"}
    )
    return view_state


def write_global_pipeline_aal_viz_dashboard_artifacts(
    root: Path | str = ".",
    *,
    source_root: Path | str | None = None,
) -> dict[str, dict[str, Any]]:
    base = Path(root)
    dashboard_packet = build_global_pipeline_aal_viz_dashboard_packet(
        base,
        source_root=source_root,
    )
    view_state = build_global_pipeline_aal_viz_view_state(dashboard_packet)

    write_canonical_json(base / DASHBOARD_JSON_PATH, dashboard_packet)
    _write_markdown(
        base / DASHBOARD_MD_PATH,
        [
            "# Global Pipeline AAL-Viz Dashboard Packet",
            "",
            f"- `status`: `{dashboard_packet['status']}`",
            f"- `recommended_next_state`: `{dashboard_packet['recommended_next_state']}`",
            f"- `physical_repo_implementation_ready`: `{dashboard_packet['physical_repo_implementation_ready']}`",
            "",
            "## Blocked Reasons",
            *(
                [f"- `{reason}`" for reason in dashboard_packet["blocked_reasons"]]
                if dashboard_packet["blocked_reasons"]
                else ["- none"]
            ),
        ],
    )

    write_canonical_json(base / VIEW_STATE_JSON_PATH, view_state)
    _write_markdown(
        base / VIEW_STATE_MD_PATH,
        [
            "# Global Pipeline AAL-Viz View State",
            "",
            f"- `default_view`: `{view_state['default_view']}`",
            f"- `selected_panel_id`: `{view_state['selected_panel_id']}`",
            f"- `selected_tile_id`: `{view_state['selected_tile_id']}`",
            "",
            "## Highlighted Pipelines",
            *[f"- `{pipeline_id}`" for pipeline_id in view_state["focus"]["highlighted_pipeline_ids"]],
        ],
    )

    return {
        "dashboard_packet": dashboard_packet,
        "view_state": view_state,
    }
