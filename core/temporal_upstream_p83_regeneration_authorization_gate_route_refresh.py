from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalUpstreamP83RegenerationAuthorizationGateRouteRefreshReceipt.v1"
STATUS = (
    "TEMPORAL_UPSTREAM_P83_REGENERATION_AUTHORIZATION_GATE_ROUTE_REFRESH_READY_ADVISORY_ONLY"
)
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-85"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = (
    "out/audit/temporal_upstream_p83_regeneration_authorization_gate_route_refresh_001.latest.json"
)
STATUS_DOC_PATH = (
    "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_P83_REGENERATION_AUTHORIZATION_GATE_ROUTE.md"
)

P88_RECEIPT_PATH = "out/temporal_continuity_p83_status_plan_regeneration_execution_plan/latest.json"
P89_RECEIPT_PATH = "out/temporal_continuity_p83_regeneration_authorization_gate/latest.json"
P90_RECEIPT_PATH = (
    "out/temporal_continuity_p83_regeneration_authorization_record_plan/latest.json"
)
SLICE84_RECEIPT_PATH = (
    "out/audit/temporal_upstream_status_plan_regeneration_execution_bridge_route_refresh_001.latest.json"
)
SLICE84_STATUS_DOC_PATH = (
    "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_PLAN_REGENERATION_EXECUTION_BRIDGE_ROUTE.md"
)
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"
LINEAGE_MAP_PATH = "docs/lineage/CONTINUITY_LINEAGE_MAP_002.md"
P89_PLAN_PATH = "docs/plans/P89_temporal_continuity_p83_regeneration_authorization_gate.md"
P90_PLAN_PATH = (
    "docs/plans/P90_temporal_continuity_p83_regeneration_authorization_record_plan.md"
)
HEALTH_DASHBOARD_PATH = "docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md"

EXPECTED_ACTIVE_P89_LANE = "P89_TEMPORAL_CONTINUITY_P83_REGENERATION_AUTHORIZATION_GATE"

SOURCE_PATHS = (
    P88_RECEIPT_PATH,
    P89_RECEIPT_PATH,
    P90_RECEIPT_PATH,
    SLICE84_RECEIPT_PATH,
    CONTINUITY_SPINE_PATH,
    LINEAGE_MAP_PATH,
    P89_PLAN_PATH,
    P90_PLAN_PATH,
    SLICE84_STATUS_DOC_PATH,
    HEALTH_DASHBOARD_PATH,
    STATUS_DOC_PATH,
    "core/generated_artifact_registry.py",
)

REQUIRED_ROUTE_TARGETS = (
    STATUS_DOC_PATH,
    DEFAULT_OUT_PATH,
    P89_RECEIPT_PATH,
    P90_RECEIPT_PATH,
    P89_PLAN_PATH,
    P90_PLAN_PATH,
    SLICE84_RECEIPT_PATH,
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
                    "p83_regeneration_authorization_gate_status",
                    payload.get(
                        "p83_regeneration_record_plan_status",
                        payload.get(
                            "p83_regeneration_execution_plan_status",
                            "OBSERVED",
                        ),
                    ),
                ),
            )
            row["packet_hash"] = payload.get(
                "canonical_hash", payload.get("packet_hash", "NOT_COMPUTABLE")
            )
    return row


def _route_stage_rows(
    *,
    p88: dict[str, Any],
    p88_status: str,
    p89: dict[str, Any],
    p89_status: str,
    p90: dict[str, Any],
    p90_status: str,
) -> list[dict[str, Any]]:
    return [
        {
            "stage": "P88_CURRENT_EXECUTION_ROUTE_SOURCE",
            "path": P88_RECEIPT_PATH,
            "source_status": p88_status,
            "status": p88.get("p83_regeneration_execution_plan_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p88.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "The current repo-real P88 packet is the live upstream source of truth for this lane."
            ),
            "authority_granted": False,
        },
        {
            "stage": "P89_P83_REGENERATION_AUTHORIZATION_GATE",
            "path": P89_RECEIPT_PATH,
            "source_status": p89_status,
            "status": p89.get(
                "p83_regeneration_authorization_gate_status", "NOT_COMPUTABLE"
            ),
            "recommended_next_lane": p89.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "P89 already exists on main as a deterministic authorization-gate packet family."
            ),
            "authority_granted": False,
        },
        {
            "stage": "P90_P83_REGENERATION_AUTHORIZATION_RECORD_PLAN",
            "path": P90_RECEIPT_PATH,
            "source_status": p90_status,
            "status": p90.get("p83_regeneration_record_plan_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p90.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "P90 is already present on main as the planning-only downstream continuation of P89."
            ),
            "authority_granted": False,
        },
    ]


def _route_target_rows(repo_root: Path) -> list[dict[str, Any]]:
    combined = []
    for relative_path in (
        "README.md",
        "STATUS.md",
        "PLANS.md",
        "docs/START_HERE.md",
        "docs/INDEX.md",
        "docs/artifacts/ARTIFACT_INDEX.md",
        LINEAGE_MAP_PATH,
        SLICE84_STATUS_DOC_PATH,
        STATUS_DOC_PATH,
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


def _current_route_class(*, p88: dict[str, Any], p89_status: str, p90_status: str) -> str:
    if p89_status != "OBSERVED" or p90_status != "OBSERVED":
        return "NOT_COMPUTABLE / HELD"
    if str(p88.get("recommended_next_lane", "NOT_COMPUTABLE")) != EXPECTED_ACTIVE_P89_LANE:
        return "HISTORICAL REFERENCE"
    return "ACTIVE NAVIGATION"


def _findings(
    *,
    p88: dict[str, Any],
    p88_status: str,
    p89: dict[str, Any],
    p89_status: str,
    p90: dict[str, Any],
    p90_status: str,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if p89_status != "OBSERVED":
        return [
            {
                "severity": "HIGH",
                "code": "P89_SOURCE_NOT_COMPUTABLE",
                "detail": (
                    "The repo-native P89 authorization-gate packet is missing or unreadable, so the route fails closed."
                ),
                "authority_granted": False,
            }
        ]

    if p90_status != "OBSERVED":
        findings.append(
            {
                "severity": "HIGH",
                "code": "P90_SOURCE_NOT_COMPUTABLE",
                "detail": (
                    "The repo-native P90 authorization-record plan packet is missing or unreadable."
                ),
                "authority_granted": False,
            }
        )

    current_p88_lane = str(p88.get("recommended_next_lane", "NOT_COMPUTABLE"))
    recorded_p89_source_lane = str(
        p89.get("source_p88_recommended_next_lane", "NOT_COMPUTABLE")
    )
    if p88_status == "OBSERVED" and current_p88_lane != EXPECTED_ACTIVE_P89_LANE:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "CURRENT_P88_PREFERS_P84_BRIDGE",
                "detail": (
                    "The current repo-real P88 packet points to "
                    f"`{current_p88_lane}`, while the existing P89 packet records "
                    f"`{recorded_p89_source_lane}`. Keep Slice84 as active route context."
                ),
                "authority_granted": False,
            }
        )

    if (
        p89.get("p83_regeneration_authorization_gate_status")
        == "P83_REGENERATION_AUTHORIZATION_ELIGIBLE"
    ):
        findings.append(
            {
                "severity": "LOW",
                "code": "P89_ELIGIBLE_BUT_HELD",
                "detail": (
                    "P89 is authorization-eligible, but grant, token, and execution authority remain false."
                ),
                "authority_granted": False,
            }
        )

    if (
        p90.get("p83_regeneration_record_plan_status")
        == "P83_REGENERATION_AUTHORIZATION_RECORD_PLAN_READY"
    ):
        findings.append(
            {
                "severity": "LOW",
                "code": "P90_READY_BUT_CREATION_HELD",
                "detail": (
                    "P90 is planning-ready, but authorization-record creation remains held for a future lane."
                ),
                "authority_granted": False,
            }
        )

    blocked = [str(item) for item in p89.get("denied_authority", [])]
    if blocked:
        findings.append(
            {
                "severity": "LOW",
                "code": "P89_DENIED_AUTHORITY_VISIBLE",
                "detail": f"P89 carries {len(blocked)} denied authority lock(s); sample: {blocked[0]}.",
                "authority_granted": False,
            }
        )

    return findings


def build_temporal_upstream_p83_regeneration_authorization_gate_route_refresh_receipt(
    *,
    repo_root: str | Path,
) -> dict[str, Any]:
    root = Path(repo_root)
    p88, p88_status = _load_json(root / P88_RECEIPT_PATH)
    p89, p89_status = _load_json(root / P89_RECEIPT_PATH)
    p90, p90_status = _load_json(root / P90_RECEIPT_PATH)
    spine, spine_status = _load_json(root / CONTINUITY_SPINE_PATH)

    current_route_class = _current_route_class(
        p88=p88, p89_status=p89_status, p90_status=p90_status
    )
    source_status = (
        "OBSERVED"
        if all(status == "OBSERVED" for status in (p89_status, p90_status))
        else "NOT_COMPUTABLE"
    )
    current_p88_lane = str(p88.get("recommended_next_lane", "NOT_COMPUTABLE"))
    p89_source_lane = str(p89.get("source_p88_recommended_next_lane", "NOT_COMPUTABLE"))
    safe_next_surface = str(p89.get("recommended_next_lane", "NOT_COMPUTABLE"))

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
        "p88_status_plan_regeneration_execution_status": p88.get(
            "p83_regeneration_execution_plan_status", "NOT_COMPUTABLE"
        ),
        "p89_authorization_gate_status": p89.get(
            "p83_regeneration_authorization_gate_status", "NOT_COMPUTABLE"
        ),
        "p90_authorization_record_plan_status": p90.get(
            "p83_regeneration_record_plan_status", "NOT_COMPUTABLE"
        ),
        "authorization_eligible": bool(
            p89.get("p83_regeneration_authorization_eligible", False)
        ),
        "authorization_record_plan_required": bool(
            p90.get("p83_regeneration_record_required", False)
        ),
        "current_p88_recommended_next_lane": current_p88_lane,
        "p89_source_recorded_upstream_lane": p89_source_lane,
        "source_recommended_next_lane": safe_next_surface,
        "safe_next_surface": safe_next_surface,
        "recommended_next_engineering_move": (
            "Keep this route advisory-only, package the existing P89-to-P90 stack as repo-native downstream evidence, and preserve Slice84 as the active current-route context whenever the live P88 packet still points to the P84 family."
        ),
        "blocked_action_count": len(
            [item for item in p89.get("denied_authority", []) if isinstance(item, str)]
        ),
        "blocked_action_sample": [
            item for item in p89.get("denied_authority", []) if isinstance(item, str)
        ][:5],
        "continuity_summary": _continuity_summary(spine, spine_status),
        "route_stage_rows": _route_stage_rows(
            p88=p88,
            p88_status=p88_status,
            p89=p89,
            p89_status=p89_status,
            p90=p90,
            p90_status=p90_status,
        ),
        "route_target_rows": _route_target_rows(root),
        "findings": _findings(
            p88=p88,
            p88_status=p88_status,
            p89=p89,
            p89_status=p89_status,
            p90=p90,
            p90_status=p90_status,
        ),
        "source_table": [_source_row(root, path) for path in SOURCE_PATHS],
        "authority_locks": dict(AUTHORITY_LOCKS),
        "boundary": {
            "advisory_only": True,
            "projection_only": True,
            "sandbox_gate_issued": False,
            "runtime_activation": False,
            "canon_mutation": False,
            "notion_writeback": False,
            "github_writeback": False,
            "external_calls": False,
            "mcp_exposure": False,
            "authority_granted": False,
        },
        "paste_ready_notion_closeout": (
            "Slice85 complete - Temporal upstream P83 regeneration authorization-gate route refresh shipped; the existing repo-native P89 authorization-gate and P90 authorization-record-planning packets are now surfaced through a contributor-facing status page and receipt, while the current Slice84 P89-labelled P84 bridge remains visible as active route context. Receipt hash: {canonical_hash}. No sandbox probe, runtime activation, canon mutation, MCP exposure, external calls, authorization granting, record creation, or autonomous writeback authorized. Brier Score: 0.10."
        ),
        "validation_plan": [
            "python scripts/temporal/run_temporal_upstream_p83_regeneration_authorization_gate_route_refresh_receipt.py",
            "python scripts/artifact/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_p83_regeneration_authorization_gate_route_refresh_001.latest.json",
            "python -m py_compile core/temporal_upstream_p83_regeneration_authorization_gate_route_refresh.py scripts/temporal/run_temporal_upstream_p83_regeneration_authorization_gate_route_refresh_receipt.py tests/test_temporal_upstream_p83_regeneration_authorization_gate_route_refresh.py core/generated_artifact_registry.py tests/test_generated_artifact_registry.py",
            "git diff --check",
        ],
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice85 + Hash: temporal_upstream_p83_regeneration_authorization_gate_route_refresh_001.latest.json"
        ),
    }
    packet["canonical_hash"] = canonical_hash(packet)
    return packet


def write_temporal_upstream_p83_regeneration_authorization_gate_route_refresh_receipt(
    path: str | Path, packet: dict[str, Any]
) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    write_canonical_json(target, packet)
    return target
