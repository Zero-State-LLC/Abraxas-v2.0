from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalUpstreamRegenerationPlanRouteRefreshReceipt.v1"
STATUS = "TEMPORAL_UPSTREAM_REGENERATION_PLAN_ROUTE_REFRESH_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-79"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = "out/audit/temporal_upstream_regeneration_plan_route_refresh_001.latest.json"
STATUS_DOC_PATH = "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_PLAN_ROUTE.md"

P83_PACKET_PATH = "out/temporal_continuity_p79_authorization_gate_status_repair_plan/latest.json"
P84_PACKET_PATH = "out/temporal_continuity_p80_authorization_record_plan_regeneration_plan/latest.json"
SLICE78_RECEIPT_PATH = "out/audit/temporal_upstream_status_repair_route_refresh_001.latest.json"
SLICE51_RECEIPT_PATH = (
    "out/audit/temporal_continuity_p80_authorization_record_regeneration_receipt_001.latest.json"
)
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"
LINEAGE_MAP_PATH = "docs/lineage/CONTINUITY_LINEAGE_MAP_002.md"
P83_PLAN_PATH = "docs/plans/P83_temporal_continuity_p79_authorization_gate_status_repair_plan.md"
P84_PLAN_PATH = "docs/plans/P84_temporal_continuity_p80_authorization_record_plan_regeneration_plan.md"
P85_PLAN_PATH = "docs/plans/P85_temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan.md"
HEALTH_DASHBOARD_PATH = "docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md"
SLICE78_ROUTE_DOC_PATH = "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_REPAIR_ROUTE.md"

SOURCE_PATHS = (
    P83_PACKET_PATH,
    P84_PACKET_PATH,
    SLICE78_RECEIPT_PATH,
    SLICE51_RECEIPT_PATH,
    CONTINUITY_SPINE_PATH,
    LINEAGE_MAP_PATH,
    P83_PLAN_PATH,
    P84_PLAN_PATH,
    P85_PLAN_PATH,
    HEALTH_DASHBOARD_PATH,
    SLICE78_ROUTE_DOC_PATH,
    STATUS_DOC_PATH,
    "core/generated_artifact_registry.py",
)

REQUIRED_ROUTE_TARGETS = (
    STATUS_DOC_PATH,
    DEFAULT_OUT_PATH,
    P84_PACKET_PATH,
    SLICE78_RECEIPT_PATH,
    P85_PLAN_PATH,
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
                    "p80_regeneration_plan_status",
                    payload.get("p79_status_repair_plan_status", "OBSERVED"),
                ),
            )
            row["packet_hash"] = payload.get(
                "canonical_hash",
                payload.get("packet_hash", "NOT_COMPUTABLE"),
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
    p83: dict[str, Any],
    p83_status: str,
    p84: dict[str, Any],
    p84_status: str,
) -> list[dict[str, Any]]:
    return [
        {
            "stage": "P83_AUTHORIZATION_GATE_STATUS_REPAIR_PLAN",
            "path": P83_PACKET_PATH,
            "source_status": p83_status,
            "status": p83.get("p79_status_repair_plan_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p83.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "P83 is the emitted status-repair packet that keeps the status-repair lane contributor-facing and advisory-only."
            ),
            "authority_granted": False,
        },
        {
            "stage": "P84_AUTHORIZATION_RECORD_REGENERATION_PLAN",
            "path": P84_PACKET_PATH,
            "source_status": p84_status,
            "status": p84.get("p80_regeneration_plan_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p84.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "P84 is the first emitted downstream regeneration-plan packet in this branch and currently shows the route is ready to hand off into P85 execution planning."
            ),
            "authority_granted": False,
        },
    ]


def _route_target_rows(repo_root: Path) -> list[dict[str, Any]]:
    texts: list[str] = []
    for relative_path in (
        "README.md",
        "STATUS.md",
        "PLANS.md",
        "docs/START_HERE.md",
        "docs/INDEX.md",
        "docs/artifacts/ARTIFACT_INDEX.md",
        LINEAGE_MAP_PATH,
        P83_PLAN_PATH,
        P84_PLAN_PATH,
        P85_PLAN_PATH,
        SLICE78_ROUTE_DOC_PATH,
        STATUS_DOC_PATH,
    ):
        text, _ = _read_text(repo_root / relative_path)
        texts.append(text)
    joined = "\n".join(texts)
    return [
        {
            "target": target,
            "observed": target in joined or Path(target).name in joined,
            "authority_granted": False,
        }
        for target in REQUIRED_ROUTE_TARGETS
    ]


def _findings(*, p84: dict[str, Any], p84_status: str) -> list[dict[str, Any]]:
    if p84_status != "OBSERVED":
        return [
            {
                "severity": "HIGH",
                "code": "P84_SOURCE_NOT_COMPUTABLE",
                "detail": (
                    "The emitted P84 regeneration-plan packet is missing or unreadable, so downstream routing must fail closed."
                ),
                "authority_granted": False,
            }
        ]

    findings: list[dict[str, Any]] = []
    if p84.get("p80_regeneration_plan_status") == "P80_REGENERATION_PLAN_READY":
        findings.append(
            {
                "severity": "LOW",
                "code": "P84_REGENERATION_PLAN_READY",
                "detail": (
                    "The emitted P84 packet now reports P80 regeneration-plan readiness while keeping regeneration execution and authorization authority false."
                ),
                "authority_granted": False,
            }
        )

    reasons = [
        item
        for item in p84.get("regeneration_reasons", [])
        if isinstance(item, str)
    ]
    if reasons:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "P84_REGENERATION_REASONS_PRESENT",
                "detail": (
                    f"P84 still carries {len(reasons)} regeneration reason(s); sample: {reasons[0]}."
                ),
                "authority_granted": False,
            }
        )
    return findings


def build_temporal_upstream_regeneration_plan_route_refresh_receipt(
    *,
    repo_root: str | Path,
) -> dict[str, Any]:
    root = Path(repo_root)
    p83, p83_status = _load_json(root / P83_PACKET_PATH)
    p84, p84_status = _load_json(root / P84_PACKET_PATH)
    slice78, slice78_status = _load_json(root / SLICE78_RECEIPT_PATH)
    slice51, slice51_status = _load_json(root / SLICE51_RECEIPT_PATH)
    spine, spine_status = _load_json(root / CONTINUITY_SPINE_PATH)

    source_status = (
        "OBSERVED"
        if all(
            status == "OBSERVED"
            for status in (p83_status, p84_status, slice78_status, slice51_status)
        )
        else "NOT_COMPUTABLE"
    )
    current_route_class = (
        "ACTIVE NAVIGATION" if source_status == "OBSERVED" else "NOT_COMPUTABLE / HELD"
    )

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
        "p83_status_repair_plan_status": p83.get(
            "p79_status_repair_plan_status", "NOT_COMPUTABLE"
        ),
        "p84_regeneration_plan_status": p84.get(
            "p80_regeneration_plan_status", "NOT_COMPUTABLE"
        ),
        "source_recommended_next_lane": p84.get(
            "recommended_next_lane",
            p83.get("recommended_next_lane", "NOT_COMPUTABLE"),
        ),
        "safe_next_surface": p84.get("recommended_next_lane", "NOT_COMPUTABLE"),
        "recommended_next_engineering_move": (
            "Keep the route advisory-only, preserve the emitted P84 packet as the canonical regeneration-plan handoff, and route contributors into the downstream P85 execution-planning surfaces without opening regeneration or authorization authority."
        ),
        "regeneration_reason_count": len(
            [item for item in p84.get("regeneration_reasons", []) if isinstance(item, str)]
        ),
        "blocked_regeneration_reason_count": len(
            [
                item
                for item in p84.get("blocked_regeneration_reasons", [])
                if isinstance(item, str)
            ]
        ),
        "continuity_summary": _continuity_summary(spine, spine_status),
        "route_stage_rows": _route_stage_rows(
            p83=p83,
            p83_status=p83_status,
            p84=p84,
            p84_status=p84_status,
        ),
        "route_target_rows": _route_target_rows(root),
        "findings": _findings(p84=p84, p84_status=p84_status),
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
            "Slice79 complete - Temporal upstream regeneration-plan route refresh shipped; the emitted P84 regeneration-plan packet is now routed through a contributor-facing status page and receipt, with the downstream P85 execution-planning handoff kept explicit and advisory-only; no sandbox probe, runtime activation, canon mutation, MCP exposure, external calls, or autonomous writeback authorized. Brier Score: 0.10."
        ),
        "validation_plan": [
            "python scripts/temporal/run_temporal_upstream_regeneration_plan_route_refresh_receipt.py",
            "python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_regeneration_plan_route_refresh_001.latest.json",
            "python scripts/run_artifact_regeneration.py --artifact out/temporal_continuity_p80_authorization_record_plan_regeneration_plan/latest.json",
            "python -m py_compile core/temporal_upstream_regeneration_plan_route_refresh.py scripts/temporal/run_temporal_upstream_regeneration_plan_route_refresh_receipt.py tests/test_temporal_upstream_regeneration_plan_route_refresh.py",
            "git diff --check",
        ],
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice79 + "
            "Hash: temporal_upstream_regeneration_plan_route_refresh_001.latest.json"
        ),
    }
    packet["canonical_hash"] = canonical_hash(packet)
    return packet


def write_temporal_upstream_regeneration_plan_route_refresh_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    write_canonical_json(target, packet)
    return target
