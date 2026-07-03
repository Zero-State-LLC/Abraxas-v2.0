from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalUpstreamStatusPlanRegenerationExecutionRouteRefreshReceipt.v1"
STATUS = (
    "TEMPORAL_UPSTREAM_STATUS_PLAN_REGENERATION_EXECUTION_ROUTE_REFRESH_READY_ADVISORY_ONLY"
)
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-83"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = (
    "out/audit/temporal_upstream_status_plan_regeneration_execution_route_refresh_001.latest.json"
)
STATUS_DOC_PATH = (
    "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_PLAN_REGENERATION_EXECUTION_ROUTE.md"
)

P87_RECEIPT_PATH = "out/temporal_continuity_p83_status_plan_regeneration_plan/latest.json"
P88_RECEIPT_PATH = (
    "out/temporal_continuity_p83_status_plan_regeneration_execution_plan/latest.json"
)
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"
LINEAGE_MAP_PATH = "docs/lineage/CONTINUITY_LINEAGE_MAP_002.md"
P87_PLAN_PATH = "docs/plans/P87_temporal_continuity_p83_status_plan_regeneration_plan.md"
P88_PLAN_PATH = (
    "docs/plans/P88_temporal_continuity_p83_status_plan_regeneration_execution_plan.md"
)
P84_ROUTE_REFERENCE_PLAN_PATH = (
    "docs/plans/P86_temporal_continuity_p84_regeneration_plan_regeneration_plan.md"
)
P84_ROUTE_REFERENCE_PACKET_PATH = (
    "out/temporal_continuity_p84_regeneration_plan_regeneration_plan/latest.json"
)
HEALTH_DASHBOARD_PATH = "docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md"
P87_ROUTE_DOC_PATH = (
    "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_PLAN_REGENERATION_ROUTE.md"
)

SOURCE_PATHS = (
    P87_RECEIPT_PATH,
    P88_RECEIPT_PATH,
    CONTINUITY_SPINE_PATH,
    LINEAGE_MAP_PATH,
    P87_PLAN_PATH,
    P88_PLAN_PATH,
    P84_ROUTE_REFERENCE_PLAN_PATH,
    P84_ROUTE_REFERENCE_PACKET_PATH,
    HEALTH_DASHBOARD_PATH,
    P87_ROUTE_DOC_PATH,
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
                    "p83_regeneration_execution_plan_status",
                    payload.get("p83_regeneration_plan_status", "OBSERVED"),
                ),
            )
            row["packet_hash"] = payload.get(
                "canonical_hash", payload.get("packet_hash", "NOT_COMPUTABLE")
            )
    return row


def _route_stage_rows(
    *,
    p87: dict[str, Any],
    p87_status: str,
    p88: dict[str, Any],
    p88_status: str,
) -> list[dict[str, Any]]:
    return [
        {
            "stage": "P87_P83_STATUS_PLAN_REGENERATION_PLAN",
            "path": P87_RECEIPT_PATH,
            "source_status": p87_status,
            "status": p87.get("p83_regeneration_plan_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p87.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "P87 remains the direct prerequisite packet and records whether the downstream "
                "execution-planning handoff should stay explicit but authority-closed."
            ),
            "authority_granted": False,
        },
        {
            "stage": "P88_P83_STATUS_PLAN_REGENERATION_EXECUTION_PLAN",
            "path": P88_RECEIPT_PATH,
            "source_status": p88_status,
            "status": p88.get("p83_regeneration_execution_plan_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p88.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "The P88 packet is the canonical downstream route even when execution planning "
                "is not required, and its observed handoff must stay explicit without inventing "
                "authorization or execution authority."
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
        P87_ROUTE_DOC_PATH,
        STATUS_DOC_PATH,
    ):
        text, _ = _read_text(repo_root / relative_path)
        combined.append(text)
    joined = "\n".join(combined)
    targets = (
        STATUS_DOC_PATH,
        DEFAULT_OUT_PATH,
        P88_RECEIPT_PATH,
        P87_ROUTE_DOC_PATH,
        safe_next_surface,
        P84_ROUTE_REFERENCE_PLAN_PATH,
        P84_ROUTE_REFERENCE_PACKET_PATH,
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


def _findings(
    *,
    p87: dict[str, Any],
    p87_status: str,
    p88: dict[str, Any],
    p88_status: str,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if p88_status != "OBSERVED":
        return [
            {
                "severity": "HIGH",
                "code": "P88_SOURCE_NOT_COMPUTABLE",
                "detail": (
                    "The repo-real downstream P88 execution-planning packet is missing or "
                    "unreadable, so the packaged route must fail closed and avoid fabricating a "
                    "downstream bridge."
                ),
                "authority_granted": False,
            }
        ]

    if p87_status != "OBSERVED":
        findings.append(
            {
                "severity": "HIGH",
                "code": "P87_SOURCE_NOT_COMPUTABLE",
                "detail": (
                    "The direct upstream P87 packet is missing or unreadable, so downstream "
                    "execution-planning routing must stay degraded even though the P88 packet family exists."
                ),
                "authority_granted": False,
            }
        )
    if (
        p88.get("p83_regeneration_execution_plan_status")
        == "P83_REGENERATION_EXECUTION_NOT_REQUIRED"
    ):
        findings.append(
            {
                "severity": "LOW",
                "code": "P88_EXECUTION_NOT_REQUIRED_VISIBLE",
                "detail": (
                    "The observed P88 packet now reports regeneration execution not required, so "
                    "the contributor-facing route must stay advisory-only and avoid pretending an "
                    "execution or authorization gate is next."
                ),
                "authority_granted": False,
            }
        )
    blocked = [str(item) for item in p88.get("blocked_execution_reasons", [])]
    if blocked:
        findings.append(
            {
                "severity": "LOW",
                "code": "P88_BLOCKED_EXECUTION_REASONS_VISIBLE",
                "detail": (
                    f"{len(blocked)} blocked execution reason(s) remain in the packet family; "
                    f"sample: {blocked[0]}."
                ),
                "authority_granted": False,
            }
        )
    allowlist = [item for item in p88.get("command_allowlist", []) if isinstance(item, dict)]
    if allowlist:
        findings.append(
            {
                "severity": "LOW",
                "code": "P88_COMMAND_ALLOWLIST_ADVISORY_ONLY",
                "detail": (
                    "The packet carries an exact future command allowlist for reproducibility, "
                    "but every allowlist entry remains execution-authorized false in this slice."
                ),
                "authority_granted": False,
            }
        )
    if p88.get("recommended_next_lane"):
        downstream_lane = str(p88.get("recommended_next_lane"))
        if (
            downstream_lane
            == "P89_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_REGENERATION_PLAN"
        ):
            findings.append(
                {
                    "severity": "MEDIUM",
                    "code": "P88_P89_LABEL_POINTS_TO_P84_ROUTE",
                    "detail": (
                        "The observed downstream lane uses a P89-labelled handoff into the "
                        "existing P84 regeneration-plan family. Keep that label visible, but "
                        "treat the current P84 reference surfaces as the repo-real follow-on "
                        "until a dedicated bridge package lands."
                    ),
                    "authority_granted": False,
                }
            )
        else:
            findings.append(
                {
                    "severity": "LOW",
                    "code": "P88_DOWNSTREAM_HANDOFF_EXPLICIT",
                    "detail": (
                        "The observed downstream packet keeps its next-lane handoff explicit "
                        "without opening execution, regeneration, or authorization authority."
                    ),
                    "authority_granted": False,
                }
            )
    return findings


def build_temporal_upstream_status_plan_regeneration_execution_route_refresh_receipt(
    *,
    repo_root: str | Path,
) -> dict[str, Any]:
    root = Path(repo_root)
    p87, p87_status = _load_json(root / P87_RECEIPT_PATH)
    p88, p88_status = _load_json(root / P88_RECEIPT_PATH)
    spine, spine_status = _load_json(root / CONTINUITY_SPINE_PATH)

    source_status = (
        "OBSERVED"
        if all(status == "OBSERVED" for status in (p87_status, p88_status))
        else "NOT_COMPUTABLE"
    )
    current_route_class = (
        "ACTIVE NAVIGATION" if p88_status == "OBSERVED" else "NOT_COMPUTABLE / HELD"
    )
    safe_next_surface = str(p88.get("recommended_next_lane", "NOT_COMPUTABLE"))

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
        "p87_status_plan_regeneration_status": p87.get(
            "p83_regeneration_plan_status", "NOT_COMPUTABLE"
        ),
        "p88_status_plan_regeneration_execution_status": p88.get(
            "p83_regeneration_execution_plan_status", "NOT_COMPUTABLE"
        ),
        "source_recommended_next_lane": safe_next_surface,
        "safe_next_surface": safe_next_surface,
        "recommended_next_engineering_move": (
            "Keep the route advisory-only, preserve the repo-real P88 execution-planning packet, "
            "and if temporal continuity remains the active board lane, package a dedicated bridge "
            "from the observed P89-labelled P84 handoff into the existing P84 regeneration-plan "
            "family before any deeper downstream packaging."
        ),
        "blocked_execution_reason_count": len(
            [item for item in p88.get("blocked_execution_reasons", []) if isinstance(item, str)]
        ),
        "command_allowlist_count": len(
            [item for item in p88.get("command_allowlist", []) if isinstance(item, dict)]
        ),
        "preflight_check_count": len(
            [item for item in p88.get("preflight_checks", []) if isinstance(item, dict)]
        ),
        "post_run_validation_count": len(
            [item for item in p88.get("post_run_validations", []) if isinstance(item, dict)]
        ),
        "continuity_summary": _continuity_summary(spine, spine_status),
        "route_stage_rows": _route_stage_rows(
            p87=p87,
            p87_status=p87_status,
            p88=p88,
            p88_status=p88_status,
        ),
        "route_target_rows": _route_target_rows(root, safe_next_surface),
        "findings": _findings(p87=p87, p87_status=p87_status, p88=p88, p88_status=p88_status),
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
            "Slice83 complete - Temporal upstream status-plan regeneration execution route refresh "
            "shipped; the repo-real downstream P88 execution-planning packet is now packaged through "
            "a contributor-facing status page and receipt, with the observed P89-labelled P84 "
            "regeneration-plan handoff kept explicit and advisory-only. Receipt hash: "
            "{canonical_hash}. No sandbox probe, runtime activation, canon mutation, MCP exposure, "
            "external calls, or autonomous writeback authorized. Brier Score: 0.10."
        ),
        "validation_plan": [
            "python Scripts/run_temporal_upstream_status_plan_regeneration_execution_route_refresh_receipt.py",
            "python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_status_plan_regeneration_execution_route_refresh_001.latest.json",
            "python scripts/run_artifact_regeneration.py --artifact out/temporal_continuity_p83_status_plan_regeneration_execution_plan/latest.json",
            "python -m py_compile core/temporal_upstream_status_plan_regeneration_execution_route_refresh.py Scripts/run_temporal_upstream_status_plan_regeneration_execution_route_refresh_receipt.py tests/test_temporal_upstream_status_plan_regeneration_execution_route_refresh.py core/generated_artifact_registry.py tests/test_generated_artifact_registry.py",
            "git diff --check",
        ],
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice83 + Hash: "
            "temporal_upstream_status_plan_regeneration_execution_route_refresh_001.latest.json"
        ),
    }
    packet["canonical_hash"] = canonical_hash(packet)
    packet["paste_ready_notion_closeout"] = packet["paste_ready_notion_closeout"].format(
        canonical_hash=packet["canonical_hash"]
    )
    return packet


def write_temporal_upstream_status_plan_regeneration_execution_route_refresh_receipt(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(Path(path), packet)
