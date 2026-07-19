from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = (
    "TemporalUpstreamStatusPlanRegenerationExecutionBridgeRouteRefreshReceipt.v1"
)
STATUS = (
    "TEMPORAL_UPSTREAM_STATUS_PLAN_REGENERATION_EXECUTION_BRIDGE_ROUTE_REFRESH_READY_ADVISORY_ONLY"
)
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-84"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = (
    "out/audit/temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh_001.latest.json"
)
STATUS_DOC_PATH = (
    "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_PLAN_REGENERATION_EXECUTION_BRIDGE_ROUTE.md"
)

P88_RECEIPT_PATH = (
    "out/temporal_continuity_p83_status_plan_regeneration_execution_plan/latest.json"
)
P84_RECEIPT_PATH = "out/temporal_continuity_p84_regeneration_plan_regeneration_plan/latest.json"
P83_ROUTE_RECEIPT_PATH = (
    "out/audit/temporal_upstream_status_plan_regeneration_execution_route_refresh_001.latest.json"
)
P84_ROUTE_RECEIPT_PATH = (
    "out/audit/temporal_upstream_regeneration_plan_regeneration_route_refresh_001.latest.json"
)
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"
LINEAGE_MAP_PATH = "docs/lineage/CONTINUITY_LINEAGE_MAP_002.md"
P88_PLAN_PATH = (
    "docs/plans/P88_temporal_continuity_p83_status_plan_regeneration_execution_plan.md"
)
P84_PLAN_PATH = (
    "docs/plans/P86_temporal_continuity_p84_regeneration_plan_regeneration_plan.md"
)
P83_ROUTE_DOC_PATH = (
    "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_PLAN_REGENERATION_EXECUTION_ROUTE.md"
)
P84_ROUTE_DOC_PATH = (
    "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_PLAN_REGENERATION_ROUTE.md"
)
HEALTH_DASHBOARD_PATH = "docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md"

SOURCE_PATHS = (
    P88_RECEIPT_PATH,
    P84_RECEIPT_PATH,
    P83_ROUTE_RECEIPT_PATH,
    P84_ROUTE_RECEIPT_PATH,
    CONTINUITY_SPINE_PATH,
    LINEAGE_MAP_PATH,
    P88_PLAN_PATH,
    P84_PLAN_PATH,
    P83_ROUTE_DOC_PATH,
    P84_ROUTE_DOC_PATH,
    HEALTH_DASHBOARD_PATH,
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
                    "p84_regeneration_plan_regeneration_status",
                    payload.get(
                        "p83_regeneration_execution_plan_status",
                        "OBSERVED",
                    ),
                ),
            )
            row["packet_hash"] = payload.get(
                "canonical_hash", payload.get("packet_hash", "NOT_COMPUTABLE")
            )
    return row


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


def _route_stage_rows(
    *,
    p88: dict[str, Any],
    p88_status: str,
    p84: dict[str, Any],
    p84_status: str,
) -> list[dict[str, Any]]:
    return [
        {
            "stage": "P88_LITERAL_P89_HANDOFF",
            "path": P88_RECEIPT_PATH,
            "source_status": p88_status,
            "status": p88.get("p83_regeneration_execution_plan_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p88.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "The repo-real P88 packet uses the literal P89-labelled handoff, so the bridge "
                "must preserve that label without pretending it is a new execution or authorization "
                "surface."
            ),
            "authority_granted": False,
        },
        {
            "stage": "P84_EXISTING_REFERENCE_FAMILY",
            "path": P84_RECEIPT_PATH,
            "source_status": p84_status,
            "status": p84.get(
                "p84_regeneration_plan_regeneration_status", "NOT_COMPUTABLE"
            ),
            "recommended_next_lane": p84.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "The existing P84 regeneration-plan family is the repo-real follow-on context "
                "for the observed P89-labelled handoff and remains advisory-only."
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
        P83_ROUTE_DOC_PATH,
        P84_ROUTE_DOC_PATH,
        STATUS_DOC_PATH,
    ):
        text, _ = _read_text(repo_root / relative_path)
        combined.append(text)
    joined = "\n".join(combined)
    targets = (
        STATUS_DOC_PATH,
        DEFAULT_OUT_PATH,
        P83_ROUTE_RECEIPT_PATH,
        P83_ROUTE_DOC_PATH,
        safe_next_surface,
        P84_ROUTE_RECEIPT_PATH,
        P84_ROUTE_DOC_PATH,
        P84_PLAN_PATH,
        P84_RECEIPT_PATH,
    )
    return [
        {
            "target": target,
            "observed": target in joined or Path(target).name in joined,
            "authority_granted": False,
        }
        for target in targets
    ]


def _findings(
    *,
    p88: dict[str, Any],
    p88_status: str,
    p84: dict[str, Any],
    p84_status: str,
) -> list[dict[str, Any]]:
    if p88_status != "OBSERVED":
        return [
            {
                "severity": "HIGH",
                "code": "P88_SOURCE_NOT_COMPUTABLE",
                "detail": (
                    "The repo-real P88 packet is missing or unreadable, so the naming bridge "
                    "must fail closed and avoid fabricating a downstream route."
                ),
                "authority_granted": False,
            }
        ]

    findings: list[dict[str, Any]] = []
    if p84_status != "OBSERVED":
        findings.append(
            {
                "severity": "HIGH",
                "code": "P84_REFERENCE_FAMILY_NOT_COMPUTABLE",
                "detail": (
                    "The existing P84 regeneration-plan family is missing or unreadable, so the "
                    "observed P89-labelled handoff cannot be bridged into repo-real follow-on context."
                ),
                "authority_granted": False,
            }
        )
        return findings

    findings.append(
        {
            "severity": "MEDIUM",
            "code": "P89_LABEL_REQUIRES_NAMING_BRIDGE",
            "detail": (
                "The observed downstream lane label is "
                "`P89_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_REGENERATION_PLAN`, while the "
                "repo-real packaged family is still carried through the existing P84/P86 route "
                "surfaces. Keep both visible and bridge them explicitly."
            ),
            "authority_granted": False,
        }
    )
    findings.append(
        {
            "severity": "LOW",
            "code": "P84_REFERENCE_FAMILY_ALREADY_PACKAGED",
            "detail": (
                "The existing P84 regeneration-plan family already has a canonical packet and "
                "contributor-facing route, so this slice only needs packaging and navigation bridge work."
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
                "code": "P88_EXECUTION_STILL_NOT_REQUIRED",
                "detail": (
                    "The upstream execution-planning packet remains execution-not-required, so the "
                    "bridge stays descriptive and authority-closed."
                ),
                "authority_granted": False,
            }
        )
    if (
        p84.get("p84_regeneration_plan_regeneration_status")
        == "P84_REGENERATION_NOT_REQUIRED"
    ):
        findings.append(
            {
                "severity": "LOW",
                "code": "P84_REGENERATION_STILL_NOT_REQUIRED",
                "detail": (
                    "The repo-real P84 regeneration-plan family already resolves as not required, "
                    "so the bridge should route contributors into that held posture rather than inventing deeper work."
                ),
                "authority_granted": False,
            }
        )
    return findings


def build_temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh_receipt(
    *,
    repo_root: str | Path,
) -> dict[str, Any]:
    root = Path(repo_root)
    p88, p88_status = _load_json(root / P88_RECEIPT_PATH)
    p84, p84_status = _load_json(root / P84_RECEIPT_PATH)
    spine, spine_status = _load_json(root / CONTINUITY_SPINE_PATH)

    source_status = (
        "OBSERVED"
        if all(status == "OBSERVED" for status in (p88_status, p84_status))
        else "NOT_COMPUTABLE"
    )
    current_route_class = (
        "ACTIVE BRIDGE" if source_status == "OBSERVED" else "NOT_COMPUTABLE / HELD"
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
        "bridge_source_lane_label": safe_next_surface,
        "bridge_target_family_status": p84.get(
            "p84_regeneration_plan_regeneration_status", "NOT_COMPUTABLE"
        ),
        "bridge_target_family_recommended_next_lane": p84.get(
            "recommended_next_lane", "NOT_COMPUTABLE"
        ),
        "safe_next_surface": safe_next_surface,
        "recommended_next_engineering_move": (
            "Keep the bridge advisory-only, preserve the literal observed P89-labelled handoff, "
            "and route contributors into the existing P84 regeneration-plan family as repo-real "
            "reference context without inventing new execution, regeneration, or authorization surfaces."
        ),
        "continuity_summary": _continuity_summary(spine, spine_status),
        "route_stage_rows": _route_stage_rows(
            p88=p88,
            p88_status=p88_status,
            p84=p84,
            p84_status=p84_status,
        ),
        "route_target_rows": _route_target_rows(root, safe_next_surface),
        "findings": _findings(
            p88=p88,
            p88_status=p88_status,
            p84=p84,
            p84_status=p84_status,
        ),
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
            "Slice84 complete - Temporal upstream status-plan regeneration execution bridge route "
            "refresh shipped; the observed P89-labelled downstream handoff is now explicitly bridged "
            "into the existing P84 regeneration-plan family through a contributor-facing status page "
            "and receipt. Receipt hash: {canonical_hash}. No sandbox probe, runtime activation, "
            "canon mutation, MCP exposure, external calls, or autonomous writeback authorized. "
            "Brier Score: 0.10."
        ),
        "validation_plan": [
            "python scripts/temporal/run_temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh_receipt.py",
            "python scripts/artifact/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh_001.latest.json",
            "python -m py_compile core/temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh.py scripts/temporal/run_temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh_receipt.py tests/test_temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh.py core/generated_artifact_registry.py tests/test_generated_artifact_registry.py",
            "git diff --check",
        ],
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice84 + Hash: "
            "temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh_001.latest.json"
        ),
    }
    packet["canonical_hash"] = canonical_hash(packet)
    return packet


def write_temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh_receipt(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(Path(path), packet)
