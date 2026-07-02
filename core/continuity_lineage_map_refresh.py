from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "ContinuityLineageMapRefreshReceipt.v1"
STATUS = "CONTINUITY_LINEAGE_MAP_REFRESH_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-60"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = "out/audit/continuity_lineage_map_refresh_001.latest.json"

LINEAGE_DOC_PATH = "docs/lineage/CONTINUITY_LINEAGE_MAP_002.md"
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"

SOURCE_PATHS = (
    LINEAGE_DOC_PATH,
    CONTINUITY_SPINE_PATH,
    "docs/plans/P74_temporal_continuity_missing_evidence_restoration_plan.md",
    "docs/plans/P80_temporal_continuity_upstream_input_regeneration_authorization_record_plan.md",
    "docs/plans/P81_temporal_continuity_authorization_record_plan_source_status_audit.md",
    "docs/plans/P102G_temporal_continuity_historical_recovery_audit.md",
    "out/temporal_continuity_missing_evidence_restoration_plan/latest.json",
    "out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json",
    "out/temporal_continuity_authorization_record_plan_source_status_audit/latest.json",
    "out/temporal_continuity_p80_authorization_record_plan_regeneration_plan/latest.json",
    "out/temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan/latest.json",
    "out/temporal_continuity_historical_recovery_audit/latest.json",
)

REQUIRED_ROUTE_TARGETS = (
    "docs/lineage/CONTINUITY_LINEAGE_MAP_002.md",
    "docs/status/continuity-spine.json",
    "docs/plans/P74_temporal_continuity_missing_evidence_restoration_plan.md",
    "docs/plans/P80_temporal_continuity_upstream_input_regeneration_authorization_record_plan.md",
    "docs/plans/P81_temporal_continuity_authorization_record_plan_source_status_audit.md",
    "docs/plans/P102G_temporal_continuity_historical_recovery_audit.md",
    "out/audit/continuity_lineage_map_refresh_001.latest.json",
)

ROUTE_GROUPS = (
    {
        "label": "P71-P76 binder/evidence/restoration chain",
        "span": "P71-P76",
        "lane_ids": ("P71", "P72", "P73", "P74", "P75", "P76"),
        "route_class": "ACTIVE_NAVIGATION",
        "primary_route": "docs/plans/P74_temporal_continuity_missing_evidence_restoration_plan.md",
        "receipt_path": "out/temporal_continuity_missing_evidence_restoration_plan/latest.json",
        "why_this_matters": (
            "This is the earliest repo-native restoration route for missing temporal evidence."
        ),
        "next_action": (
            "Use P74/P75 as the root repair route before downstream authorization and regeneration planning."
        ),
    },
    {
        "label": "P77-P85 upstream regeneration and authorization chain",
        "span": "P77-P85",
        "lane_ids": ("P77", "P78", "P79", "P80", "P81", "P82", "P83", "P84", "P85"),
        "route_class": "ACTIVE_NAVIGATION",
        "primary_route": "docs/plans/P81_temporal_continuity_authorization_record_plan_source_status_audit.md",
        "receipt_path": "out/temporal_continuity_authorization_record_plan_source_status_audit/latest.json",
        "why_this_matters": (
            "This route explains why the authorization record plan chain is blocked and where regeneration must restart."
        ),
        "next_action": (
            "Use P81/P84/P85 findings to route missing P80 and blocked regeneration edges without creating authorization artifacts."
        ),
    },
    {
        "label": "P86-P101 regeneration and readiness planning chain",
        "span": "P86-P101",
        "lane_ids": tuple(f"P{lane}" for lane in range(86, 102)),
        "route_class": "HISTORICAL_REFERENCE",
        "primary_route": "PLANS.md",
        "receipt_path": None,
        "why_this_matters": (
            "This planning chain preserves the downstream regeneration and readiness logic after the first blocked edges appear."
        ),
        "next_action": (
            "Use these plans as reference context once the earlier missing and blocked routes are resolved."
        ),
    },
    {
        "label": "P102-P102G repair router and historical recovery chain",
        "span": "P102-P102G",
        "lane_ids": ("P102", "P102A", "P102B", "P102C", "P102D", "P102E", "P102F", "P102G"),
        "route_class": "ACTIVE_NAVIGATION",
        "primary_route": "docs/plans/P102G_temporal_continuity_historical_recovery_audit.md",
        "receipt_path": "out/temporal_continuity_historical_recovery_audit/latest.json",
        "why_this_matters": (
            "This chain compresses the late-stage repair router and preserves disputed historical continuity as explicit audit evidence."
        ),
        "next_action": (
            "Treat P102G as a historical interpretation route only; it keeps downstream continuity not computable."
        ),
    },
)

AUTHORITY_LOCKS = {
    "canon_mutation": False,
    "external_calls": False,
    "github_writeback": False,
    "mcp_exposure": False,
    "notion_writeback": False,
    "production_activation": False,
    "runtime_activation": False,
    "runtime_mutation": False,
    "sandbox_probe_execution": False,
}


def _read_text(path: Path) -> tuple[str, str]:
    try:
        return path.read_text(encoding="utf-8"), "OBSERVED"
    except FileNotFoundError:
        return "", "MISSING"
    except OSError:
        return "", "NOT_COMPUTABLE"


def _load_json(path: Path) -> tuple[dict[str, Any], str]:
    text, status = _read_text(path)
    if status != "OBSERVED":
        return {}, status
    try:
        import json

        data = json.loads(text)
    except Exception:
        return {}, "NOT_COMPUTABLE"
    if not isinstance(data, dict):
        return {}, "NOT_COMPUTABLE"
    return data, "OBSERVED"


def _source_row(repo_root: Path, relative_path: str) -> dict[str, Any]:
    path = repo_root / relative_path
    text, status = _read_text(path)
    row: dict[str, Any] = {
        "path": relative_path,
        "source_status": status,
        "line_count": len(text.splitlines()) if status == "OBSERVED" else 0,
        "authority_granted": False,
    }
    if relative_path.endswith(".json") and status == "OBSERVED":
        data, json_status = _load_json(path)
        row["source_status"] = json_status
        row["top_level_key_count"] = len(data) if json_status == "OBSERVED" else 0
    return row


def _route_target_rows(repo_root: Path) -> list[dict[str, Any]]:
    combined = []
    for relative_path in (
        "README.md",
        "PLANS.md",
        "docs/START_HERE.md",
        "docs/INDEX.md",
        "docs/artifacts/ARTIFACT_INDEX.md",
        LINEAGE_DOC_PATH,
    ):
        text, _ = _read_text(repo_root / relative_path)
        combined.append(text)
    joined = "\n".join(combined)
    return [
        {
            "target": target,
            "observed": target in joined or Path(target).name in joined,
            "authority_granted": False,
        }
        for target in REQUIRED_ROUTE_TARGETS
    ]


def _continuity_spine_summary(data: dict[str, Any], status: str) -> dict[str, Any]:
    if status != "OBSERVED":
        return {
            "lane_count": 0,
            "highest_observed_lane": "NOT_COMPUTABLE",
            "schema_version": "NOT_COMPUTABLE",
            "mock_data": "NOT_COMPUTABLE",
            "authority_granted": False,
        }
    return {
        "lane_count": int(data.get("lane_count", 0)),
        "highest_observed_lane": data.get("highest_lane", "NOT_COMPUTABLE"),
        "schema_version": data.get("schema_version", "NOT_COMPUTABLE"),
        "mock_data": data.get("mock_data", "NOT_COMPUTABLE"),
        "authority_granted": False,
    }


def _build_route_groups(
    *,
    continuity_spine: dict[str, Any],
    source_packets: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    lane_map = {
        item.get("lane_id"): item
        for item in continuity_spine.get("continuity_lanes", [])
        if isinstance(item, dict)
    }
    rows: list[dict[str, Any]] = []
    for group in ROUTE_GROUPS:
        observed = [lane_id for lane_id in group["lane_ids"] if lane_id in lane_map]
        posture = "REFERENCE_ONLY"
        recommended_next_lane = "NOT_COMPUTABLE"
        supporting_findings: list[str] = []

        if group["span"] == "P71-P76":
            packet = source_packets["P74"]
            posture = packet.get("restoration_plan_status", "NOT_COMPUTABLE")
            recommended_next_lane = packet.get("recommended_next_lane", "NOT_COMPUTABLE")
            supporting_findings.append(
                packet.get("source_evidence_index_status", "NOT_COMPUTABLE")
            )
        elif group["span"] == "P77-P85":
            p81 = source_packets["P81"]
            p84 = source_packets["P84"]
            p85 = source_packets["P85"]
            posture = p81.get("source_chain_status", "NOT_COMPUTABLE")
            recommended_next_lane = p81.get("recommended_next_lane", "NOT_COMPUTABLE")
            supporting_findings.extend(
                [
                    f"P80 source: {'OBSERVED' if source_packets['P80_PRESENT'] else 'MISSING'}",
                    f"P84: {p84.get('p80_regeneration_plan_status', 'NOT_COMPUTABLE')}",
                    f"P85: {p85.get('p80_regeneration_execution_plan_status', 'NOT_COMPUTABLE')}",
                ]
            )
        elif group["span"] == "P86-P101":
            posture = (
                "HISTORICAL_REFERENCE_CHAIN_PRESENT"
                if observed
                else "NOT_COMPUTABLE"
            )
            recommended_next_lane = "REFERENCE_ONLY"
            supporting_findings.append("Use downstream regeneration/readiness plans as reference context only.")
        elif group["span"] == "P102-P102G":
            packet = source_packets["P102G"]
            posture = packet.get(
                "historical_recovery_status",
                packet.get("recommended_next_lane", "NOT_COMPUTABLE"),
            )
            recommended_next_lane = packet.get("recommended_next_lane", "NOT_COMPUTABLE")
            supporting_findings.append(
                packet.get(
                    "recommended_next_action",
                    "KEEP_DOWNSTREAM_NOT_COMPUTABLE",
                )
            )

        rows.append(
            {
                "label": group["label"],
                "span": group["span"],
                "route_class": group["route_class"],
                "lane_count_expected": len(group["lane_ids"]),
                "lane_count_observed": len(observed),
                "observed_lane_ids": observed,
                "primary_route": group["primary_route"],
                "receipt_path": group["receipt_path"],
                "current_posture": posture,
                "recommended_next_lane": recommended_next_lane,
                "supporting_findings": supporting_findings,
                "why_this_matters": group["why_this_matters"],
                "next_action": group["next_action"],
                "authority_granted": False,
            }
        )
    return rows


def _build_blocked_edges(source_packets: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    blocked: list[dict[str, Any]] = []
    p74 = source_packets["P74"]
    if p74.get("restoration_plan_status") != "RESTORATION_NOT_REQUIRED":
        blocked.append(
            {
                "edge_id": "P74_RESTORATION_PENDING",
                "route_class": "NOT_COMPUTABLE_OR_BLOCKED",
                "current_posture": p74.get("restoration_plan_status", "NOT_COMPUTABLE"),
                "recommended_next_lane": p74.get("recommended_next_lane", "NOT_COMPUTABLE"),
                "detail": (
                    "Missing evidence remains in the earliest restoration lane, so downstream continuity remains advisory and incomplete."
                ),
                "authority_granted": False,
            }
        )

    if not source_packets["P80_PRESENT"]:
        blocked.append(
            {
                "edge_id": "P80_SOURCE_MISSING",
                "route_class": "NOT_COMPUTABLE_OR_BLOCKED",
                "current_posture": "MISSING",
                "recommended_next_lane": source_packets["P81"].get(
                    "recommended_next_lane",
                    "NOT_COMPUTABLE",
                ),
                "detail": (
                    "The P80 authorization record plan output is absent, so the source-status audit keeps the chain fail-closed."
                ),
                "authority_granted": False,
            }
        )

    p84 = source_packets["P84"]
    if p84.get("p80_regeneration_plan_status") != "P80_REGENERATION_PLAN_READY":
        blocked.append(
            {
                "edge_id": "P84_REGENERATION_PLAN_NOT_READY",
                "route_class": "NOT_COMPUTABLE_OR_BLOCKED",
                "current_posture": p84.get("p80_regeneration_plan_status", "NOT_COMPUTABLE"),
                "recommended_next_lane": p84.get("recommended_next_lane", "NOT_COMPUTABLE"),
                "detail": (
                    "P84 reports the P80 regeneration plan as not computable, pushing the chain back to earlier status-repair planning."
                ),
                "authority_granted": False,
            }
        )

    p85 = source_packets["P85"]
    if p85.get("p80_regeneration_execution_plan_status") != "P80_REGENERATION_EXECUTION_PLAN_READY":
        blocked.append(
            {
                "edge_id": "P85_EXECUTION_PLAN_BLOCKED",
                "route_class": "NOT_COMPUTABLE_OR_BLOCKED",
                "current_posture": p85.get(
                    "p80_regeneration_execution_plan_status",
                    "NOT_COMPUTABLE",
                ),
                "recommended_next_lane": p85.get("recommended_next_lane", "NOT_COMPUTABLE"),
                "detail": (
                    "P85 stays blocked because the preceding regeneration plan is not ready."
                ),
                "authority_granted": False,
            }
        )

    p102g = source_packets["P102G"]
    if p102g.get("recommended_next_lane") == "NOT_COMPUTABLE":
        blocked.append(
            {
                "edge_id": "P102G_HISTORICAL_RECOVERY_HELD",
                "route_class": "NOT_COMPUTABLE_OR_BLOCKED",
                "current_posture": p102g.get(
                    "historical_recovery_status",
                    "NOT_COMPUTABLE",
                ),
                "recommended_next_lane": "NOT_COMPUTABLE",
                "detail": p102g.get(
                    "recommended_next_action",
                    "Historical recovery remains held for operator evidence.",
                ),
                "authority_granted": False,
            }
        )

    return blocked


def build_continuity_lineage_map_refresh_receipt(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source_table = [_source_row(root, path) for path in SOURCE_PATHS]
    route_target_rows = _route_target_rows(root)

    continuity_spine, continuity_spine_status = _load_json(root / CONTINUITY_SPINE_PATH)
    p74, _ = _load_json(
        root / "out/temporal_continuity_missing_evidence_restoration_plan/latest.json"
    )
    p81, _ = _load_json(
        root / "out/temporal_continuity_authorization_record_plan_source_status_audit/latest.json"
    )
    p84, _ = _load_json(
        root / "out/temporal_continuity_p80_authorization_record_plan_regeneration_plan/latest.json"
    )
    p85, _ = _load_json(
        root
        / "out/temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan/latest.json"
    )
    p102g, _ = _load_json(root / "out/temporal_continuity_historical_recovery_audit/latest.json")
    p80_path = root / "out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json"

    source_packets: dict[str, Any] = {
        "P74": p74,
        "P81": p81,
        "P84": p84,
        "P85": p85,
        "P102G": p102g,
        "P80_PRESENT": p80_path.exists(),
    }
    route_groups = _build_route_groups(
        continuity_spine=continuity_spine,
        source_packets=source_packets,
    )
    blocked_edges = _build_blocked_edges(source_packets)

    if continuity_spine_status != "OBSERVED":
        source_status = "NOT_COMPUTABLE"
        recommended_next_lane = "NOT_COMPUTABLE"
        recommended_reason = "Continuity spine source is missing or unreadable."
    elif blocked_edges:
        source_status = "READY_WITH_FINDINGS"
        recommended_next_lane = p74.get("recommended_next_lane", "NOT_COMPUTABLE")
        recommended_reason = (
            "Earliest restoration route still reports missing evidence, so downstream continuity remains advisory-only."
        )
    else:
        source_status = "READY"
        recommended_next_lane = "REFERENCE_ONLY"
        recommended_reason = "Continuity lineage routes are present and currently navigable."

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "slice_id": SLICE_ID,
        "status": STATUS,
        "brier_score": BRIER_SCORE,
        "advisory_only": True,
        "projection_only": True,
        "notion_board_url": NOTION_BOARD_URL,
        "claimed_card": "Priority 3 - D3 Continuity Lineage Map",
        "authority_locks": AUTHORITY_LOCKS,
        "source_status": source_status,
        "source_table": source_table,
        "continuity_spine_summary": _continuity_spine_summary(
            continuity_spine,
            continuity_spine_status,
        ),
        "route_groups": route_groups,
        "blocked_edges": blocked_edges,
        "route_target_rows": route_target_rows,
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_reason,
        "boundary": {
            "sandbox_gate_issue": "#892",
            "sandbox_gate_phrase": "ORACLE_SANDBOX_PROBE_GATE_CONFIRMED",
            "sandbox_gate_issued": False,
            "canon_mutation": False,
            "external_calls": False,
            "github_writeback": False,
            "mcp_exposure": False,
            "notion_writeback": False,
            "runtime_activation": False,
        },
        "validation_plan": [
            "python Scripts/run_continuity_lineage_map_refresh_receipt.py",
            f"python scripts/run_artifact_regeneration.py --artifact {DEFAULT_OUT_PATH}",
            "python -m py_compile core/continuity_lineage_map_refresh.py Scripts/run_continuity_lineage_map_refresh_receipt.py tests/test_continuity_lineage_map_refresh.py",
            "python -m pytest tests/test_continuity_lineage_map_refresh.py tests/test_generated_artifact_registry.py -q -k continuity_lineage_map_refresh",
            "git diff --check",
        ],
        "notion_closeout_text": (
            "Slice60 complete - D3 Continuity Lineage Map Refresh shipped; continuity lineage now compresses the repo-native temporal spine through current route groups, blocked edges, and historical recovery references; no sandbox probe, runtime activation, canon mutation, MCP exposure, external calls, or autonomous writeback authorized. Brier Score: 0.10."
        ),
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice60 + "
            "D3 Continuity Lineage Map Refresh"
        ),
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def write_continuity_lineage_map_refresh_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
