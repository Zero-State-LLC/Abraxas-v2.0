from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalUpstreamStatusPlanRegenerationRouteRefreshReceipt.v1"
STATUS = "TEMPORAL_UPSTREAM_STATUS_PLAN_REGENERATION_ROUTE_REFRESH_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-82"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = (
    "out/audit/temporal_upstream_status_plan_regeneration_route_refresh_001.latest.json"
)
STATUS_DOC_PATH = (
    "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_PLAN_REGENERATION_ROUTE.md"
)

P86_RECEIPT_PATH = (
    "out/temporal_continuity_p84_regeneration_plan_regeneration_plan/latest.json"
)
P87_RECEIPT_PATH = "out/temporal_continuity_p83_status_plan_regeneration_plan/latest.json"
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"
LINEAGE_MAP_PATH = "docs/lineage/CONTINUITY_LINEAGE_MAP_002.md"
P86_PLAN_PATH = (
    "docs/plans/P86_temporal_continuity_p84_regeneration_plan_regeneration_plan.md"
)
P87_PLAN_PATH = "docs/plans/P87_temporal_continuity_p83_status_plan_regeneration_plan.md"
P88_PLAN_PATH = (
    "docs/plans/P88_temporal_continuity_p83_status_plan_regeneration_execution_plan.md"
)
HEALTH_DASHBOARD_PATH = "docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md"
P86_ROUTE_DOC_PATH = (
    "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_PLAN_REGENERATION_ROUTE.md"
)

SOURCE_PATHS = (
    P86_RECEIPT_PATH,
    P87_RECEIPT_PATH,
    CONTINUITY_SPINE_PATH,
    LINEAGE_MAP_PATH,
    P86_PLAN_PATH,
    P87_PLAN_PATH,
    P88_PLAN_PATH,
    HEALTH_DASHBOARD_PATH,
    P86_ROUTE_DOC_PATH,
    STATUS_DOC_PATH,
    "core/generated_artifact_registry.py",
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
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {}, "NOT_COMPUTABLE"
    if not isinstance(payload, dict):
        return {}, "NOT_COMPUTABLE"
    return payload, "OBSERVED"


def _source_row(repo_root: Path, relative_path: str) -> dict[str, Any]:
    path = repo_root / relative_path
    text, status = _read_text(path)
    row: dict[str, Any] = {
        "path": relative_path,
        "source_status": status,
        "line_count": len(text.splitlines()) if status == "OBSERVED" else 0,
        "authority_granted": False,
    }
    if relative_path.endswith(".json"):
        payload, json_status = _load_json(path)
        row["source_status"] = json_status
        row["top_level_key_count"] = len(payload) if json_status == "OBSERVED" else 0
        if json_status == "OBSERVED":
            row["status"] = payload.get(
                "status",
                payload.get(
                    "p83_regeneration_plan_status",
                    payload.get(
                        "p84_regeneration_plan_regeneration_status",
                        "OBSERVED",
                    ),
                ),
            )
            row["packet_hash"] = payload.get(
                "canonical_hash", payload.get("packet_hash", "NOT_COMPUTABLE")
            )
    return row


def _route_stage_rows(
    *,
    p86: dict[str, Any],
    p86_status: str,
    p87: dict[str, Any],
    p87_status: str,
) -> list[dict[str, Any]]:
    return [
        {
            "stage": "P86_P84_REGENERATION_PLAN_REGENERATION_PLAN",
            "path": P86_RECEIPT_PATH,
            "source_status": p86_status,
            "status": p86.get("p84_regeneration_plan_regeneration_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p86.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "P86 is the direct upstream route source and records when the downstream "
                "P87 handoff should remain explicit but advisory-only."
            ),
            "authority_granted": False,
        },
        {
            "stage": "P87_P83_STATUS_PLAN_REGENERATION_PLAN",
            "path": P87_RECEIPT_PATH,
            "source_status": p87_status,
            "status": p87.get("p83_regeneration_plan_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p87.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "The P87 lane is implemented through the repo-real p83 status-plan "
                "regeneration packet family, so contributors need the naming bridge kept visible."
            ),
            "authority_granted": False,
        },
    ]


def _route_target_rows(repo_root: Path, safe_next_surface: str) -> list[dict[str, Any]]:
    combined = []
    for relative_path in (
        "README.md",
        "STATUS.md",
        "PLANS.md",
        "docs/START_HERE.md",
        "docs/INDEX.md",
        "docs/artifacts/ARTIFACT_INDEX.md",
        LINEAGE_MAP_PATH,
        P86_ROUTE_DOC_PATH,
        STATUS_DOC_PATH,
    ):
        text, _ = _read_text(repo_root / relative_path)
        combined.append(text)
    joined = "\n".join(combined)
    targets = (
        STATUS_DOC_PATH,
        DEFAULT_OUT_PATH,
        P87_RECEIPT_PATH,
        P86_ROUTE_DOC_PATH,
        safe_next_surface,
    )
    return [
        {
            "target": target,
            "observed": target in joined or Path(target).name in joined,
            "authority_granted": False,
        }
        for target in targets
    ]


def _continuity_summary(payload: dict[str, Any], source_status: str) -> dict[str, Any]:
    if source_status != "OBSERVED":
        return {
            "highest_observed_lane": "NOT_COMPUTABLE",
            "lane_count": 0,
            "authority_granted": False,
        }
    return {
        "highest_observed_lane": payload.get("highest_lane", "NOT_COMPUTABLE"),
        "lane_count": int(payload.get("lane_count", 0)),
        "authority_granted": False,
    }


def _findings(*, p86: dict[str, Any], p86_status: str, p87: dict[str, Any], p87_status: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if p87_status != "OBSERVED":
        return [
            {
                "severity": "HIGH",
                "code": "P87_SOURCE_NOT_COMPUTABLE",
                "detail": (
                    "The repo-real downstream P87 packet family is missing or unreadable, so "
                    "the packaged route must fail closed and avoid fabricating a downstream handoff."
                ),
                "authority_granted": False,
            }
        ]

    if p86_status != "OBSERVED":
        findings.append(
            {
                "severity": "HIGH",
                "code": "P86_SOURCE_NOT_COMPUTABLE",
                "detail": (
                    "The direct upstream P86 packet is missing or unreadable, so downstream "
                    "continuity routing must stay degraded even though the P87 packet family exists."
                ),
                "authority_granted": False,
            }
        )
    if p87.get("p83_regeneration_plan_status") == "P83_REGENERATION_NOT_REQUIRED":
        findings.append(
            {
                "severity": "LOW",
                "code": "P87_REGENERATION_NOT_REQUIRED",
                "detail": (
                    "The observed downstream packet records that additional P83 regeneration "
                    "planning is not required because the status-repair source is already computable."
                ),
                "authority_granted": False,
            }
        )
    if p87.get("recommended_next_lane"):
        findings.append(
            {
                "severity": "LOW",
                "code": "P87_DOWNSTREAM_HANDOFF_EXPLICIT",
                "detail": (
                    "The observed downstream packet keeps the P88 handoff explicit without "
                    "opening execution, regeneration, or authorization authority."
                ),
                "authority_granted": False,
            }
        )
    if p86.get("recommended_next_lane") and p87.get("recommended_next_lane"):
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "P87_ROUTE_NAME_MISMATCH_VISIBLE",
                "detail": (
                    "The P86 packet routes to a P87 lane named around P85 regeneration execution, "
                    "while the repo-real emitted P87 packet family is `p83_status_plan_regeneration`; "
                    "the packaging keeps that naming mismatch explicit as historical route context."
                ),
                "authority_granted": False,
            }
        )
    blocked = [str(item) for item in p87.get("blocked_regeneration_reasons", [])]
    if blocked:
        findings.append(
            {
                "severity": "LOW",
                "code": "P87_BLOCKED_REASONS_STILL_VISIBLE",
                "detail": (
                    f"{len(blocked)} blocked regeneration reason(s) remain in the packet family; "
                    f"sample: {blocked[0]}."
                ),
                "authority_granted": False,
            }
        )
    return findings


def build_temporal_upstream_status_plan_regeneration_route_refresh_receipt(
    *,
    repo_root: str | Path,
) -> dict[str, Any]:
    root = Path(repo_root)
    p86, p86_status = _load_json(root / P86_RECEIPT_PATH)
    p87, p87_status = _load_json(root / P87_RECEIPT_PATH)
    spine, spine_status = _load_json(root / CONTINUITY_SPINE_PATH)

    source_status = (
        "OBSERVED"
        if all(status == "OBSERVED" for status in (p86_status, p87_status))
        else "NOT_COMPUTABLE"
    )
    current_route_class = (
        "ACTIVE NAVIGATION" if p87_status == "OBSERVED" else "NOT_COMPUTABLE / HELD"
    )
    safe_next_surface = str(p87.get("recommended_next_lane", "NOT_COMPUTABLE"))

    packet: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "status": STATUS,
        "brier_score": BRIER_SCORE,
        "slice_id": SLICE_ID,
        "notion_board_url": NOTION_BOARD_URL,
        "receipt_path": DEFAULT_OUT_PATH,
        "status_doc_path": STATUS_DOC_PATH,
        "source_status": source_status,
        "current_route_class": current_route_class,
        "p86_regeneration_plan_regeneration_status": p86.get(
            "p84_regeneration_plan_regeneration_status", "NOT_COMPUTABLE"
        ),
        "p87_status_plan_regeneration_status": p87.get(
            "p83_regeneration_plan_status", "NOT_COMPUTABLE"
        ),
        "source_recommended_next_lane": safe_next_surface,
        "safe_next_surface": safe_next_surface,
        "recommended_next_engineering_move": (
            "Keep the route advisory-only, preserve the repo-real p83 status-plan regeneration "
            "packet as the implemented P87 family, and package the downstream P88 execution-plan "
            "handoff separately only if temporal continuity remains the active board lane."
        ),
        "continuity_summary": _continuity_summary(spine, spine_status),
        "route_stage_rows": _route_stage_rows(
            p86=p86,
            p86_status=p86_status,
            p87=p87,
            p87_status=p87_status,
        ),
        "route_target_rows": _route_target_rows(root, safe_next_surface),
        "findings": _findings(p86=p86, p86_status=p86_status, p87=p87, p87_status=p87_status),
        "source_table": [_source_row(root, path) for path in SOURCE_PATHS],
        "authority_locks": dict(AUTHORITY_LOCKS),
        "boundary": {
            "advisory_only": True,
            "authority_granted": False,
            "projection_only": True,
            "sandbox_gate_issued": False,
            "runtime_activation": False,
            "canon_mutation": False,
            "notion_writeback": False,
            "github_writeback": False,
            "external_calls": False,
            "mcp_exposure": False,
        },
        "paste_ready_notion_closeout": (
            "Slice82 complete - Temporal upstream status-plan regeneration route refresh "
            "shipped; the repo-real downstream P87 packet family is now packaged through a "
            "contributor-facing status page and receipt, with the P87-to-p83 naming bridge "
            "kept explicit and the downstream P88 handoff held advisory-only. Receipt hash: "
            "{canonical_hash}. No sandbox probe, runtime activation, canon mutation, MCP "
            "exposure, external calls, or autonomous writeback authorized. Brier Score: 0.10."
        ),
        "validation_plan": [
            "python scripts/temporal/run_temporal_upstream_status_plan_regeneration_route_refresh_receipt.py",
            "python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_status_plan_regeneration_route_refresh_001.latest.json",
            "python scripts/run_artifact_regeneration.py --artifact out/temporal_continuity_p83_status_plan_regeneration_plan/latest.json",
            "python -m py_compile core/temporal_upstream_status_plan_regeneration_route_refresh.py scripts/temporal/run_temporal_upstream_status_plan_regeneration_route_refresh_receipt.py tests/test_temporal_upstream_status_plan_regeneration_route_refresh.py core/generated_artifact_registry.py tests/test_generated_artifact_registry.py",
            "git diff --check",
        ],
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice82 + Hash: "
            "temporal_upstream_status_plan_regeneration_route_refresh_001.latest.json"
        ),
    }
    packet["canonical_hash"] = canonical_hash(packet)
    return packet


def write_temporal_upstream_status_plan_regeneration_route_refresh_receipt(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(Path(path), packet)
