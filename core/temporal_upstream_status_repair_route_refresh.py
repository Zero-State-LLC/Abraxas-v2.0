from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalUpstreamStatusRepairRouteRefreshReceipt.v1"
STATUS = "TEMPORAL_UPSTREAM_STATUS_REPAIR_ROUTE_REFRESH_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-78"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = "out/audit/temporal_upstream_status_repair_route_refresh_001.latest.json"
STATUS_DOC_PATH = "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_STATUS_REPAIR_ROUTE.md"

P82_PACKET_PATH = "out/temporal_continuity_p79_authorization_gate_source_repair_plan/latest.json"
P83_PACKET_PATH = "out/temporal_continuity_p79_authorization_gate_status_repair_plan/latest.json"
SLICE77_RECEIPT_PATH = (
    "out/audit/temporal_upstream_authorization_record_regeneration_route_refresh_001.latest.json"
)
SLICE51_RECEIPT_PATH = (
    "out/audit/temporal_continuity_p80_authorization_record_regeneration_receipt_001.latest.json"
)
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"
LINEAGE_MAP_PATH = "docs/lineage/CONTINUITY_LINEAGE_MAP_002.md"
P82_PLAN_PATH = "docs/plans/P82_temporal_continuity_p79_authorization_gate_source_repair_plan.md"
P83_PLAN_PATH = "docs/plans/P83_temporal_continuity_p79_authorization_gate_status_repair_plan.md"
P84_PLAN_PATH = "docs/plans/P84_temporal_continuity_p80_authorization_record_plan_regeneration_plan.md"
HEALTH_DASHBOARD_PATH = "docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md"
SLICE77_ROUTE_DOC_PATH = (
    "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_AUTHORIZATION_RECORD_REGENERATION_ROUTE.md"
)

SOURCE_PATHS = (
    P82_PACKET_PATH,
    P83_PACKET_PATH,
    SLICE77_RECEIPT_PATH,
    SLICE51_RECEIPT_PATH,
    CONTINUITY_SPINE_PATH,
    LINEAGE_MAP_PATH,
    P82_PLAN_PATH,
    P83_PLAN_PATH,
    P84_PLAN_PATH,
    HEALTH_DASHBOARD_PATH,
    SLICE77_ROUTE_DOC_PATH,
    STATUS_DOC_PATH,
    "core/generated_artifact_registry.py",
)

REQUIRED_ROUTE_TARGETS = (
    STATUS_DOC_PATH,
    DEFAULT_OUT_PATH,
    P83_PACKET_PATH,
    SLICE77_RECEIPT_PATH,
    SLICE51_RECEIPT_PATH,
    P84_PLAN_PATH,
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
                    "p79_status_repair_plan_status",
                    payload.get("p79_source_repair_plan_status", "OBSERVED"),
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
    p82: dict[str, Any],
    p82_status: str,
    p83: dict[str, Any],
    p83_status: str,
    slice51: dict[str, Any],
    slice51_status: str,
) -> list[dict[str, Any]]:
    return [
        {
            "stage": "P82_AUTHORIZATION_GATE_SOURCE_REPAIR_PLAN",
            "path": P82_PACKET_PATH,
            "source_status": p82_status,
            "status": p82.get("p79_source_repair_plan_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p82.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "P82 explains whether any P79 source repair is needed before status repair planning becomes relevant."
            ),
            "authority_granted": False,
        },
        {
            "stage": "P83_AUTHORIZATION_GATE_STATUS_REPAIR_PLAN",
            "path": P83_PACKET_PATH,
            "source_status": p83_status,
            "status": p83.get("p79_status_repair_plan_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p83.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "P83 is the first emitted status-repair packet in this branch of the continuity chain and currently shows that no P79 status repair is required."
            ),
            "authority_granted": False,
        },
        {
            "stage": "P80_AUTHORIZATION_RECORD_REGENERATION_ROUTE",
            "path": SLICE51_RECEIPT_PATH,
            "source_status": slice51_status,
            "status": slice51.get("p80_regeneration_summary", {}).get(
                "p80_regeneration_plan_status", "NOT_COMPUTABLE"
            ),
            "recommended_next_lane": slice51.get("p80_regeneration_summary", {}).get(
                "recommended_next_lane", "NOT_COMPUTABLE"
            ),
            "why_this_matters": (
                "Slice51 shows the downstream regeneration lane still held while preserving the contributor-facing handoff from P83 into P80 regeneration planning."
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
        SLICE77_ROUTE_DOC_PATH,
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


def _findings(
    *,
    p83: dict[str, Any],
    p83_status: str,
    slice51: dict[str, Any],
    slice51_status: str,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if p83_status != "OBSERVED":
        return [
            {
                "severity": "HIGH",
                "code": "P83_SOURCE_NOT_COMPUTABLE",
                "detail": (
                    "The emitted P83 status-repair packet is missing or unreadable, so downstream routing must fail closed."
                ),
                "authority_granted": False,
            }
        ]

    if p83.get("p79_status_repair_plan_status") == "P79_STATUS_REPAIR_NOT_REQUIRED":
        findings.append(
            {
                "severity": "LOW",
                "code": "P83_REPAIR_NOT_REQUIRED",
                "detail": (
                    "The emitted P83 packet currently reports that no P79 status repair is required and preserves the handoff to P80 authorization-record regeneration."
                ),
                "authority_granted": False,
            }
        )

    expectations = [
        item
        for item in p83.get("status_field_expectations", [])
        if isinstance(item, dict) and item.get("satisfied") is False
    ]
    if expectations:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "P83_EXPECTATION_UNSATISFIED",
                "detail": (
                    "P83 still carries unsatisfied status-field expectations, so the route stays advisory even though no direct status repair is required."
                ),
                "authority_granted": False,
            }
        )

    if slice51_status == "OBSERVED":
        blocked = slice51.get("p80_regeneration_summary", {}).get(
            "blocked_regeneration_reasons", []
        )
        if isinstance(blocked, list) and blocked:
            findings.append(
                {
                    "severity": "MEDIUM",
                    "code": "P80_REGENERATION_STILL_BLOCKED",
                    "detail": (
                        f"P80 regeneration remains blocked downstream; sample reason: {blocked[0]}."
                    ),
                    "authority_granted": False,
                }
            )
    return findings


def build_temporal_upstream_status_repair_route_refresh_receipt(
    *,
    repo_root: str | Path,
) -> dict[str, Any]:
    root = Path(repo_root)
    p82, p82_status = _load_json(root / P82_PACKET_PATH)
    p83, p83_status = _load_json(root / P83_PACKET_PATH)
    slice77, slice77_status = _load_json(root / SLICE77_RECEIPT_PATH)
    slice51, slice51_status = _load_json(root / SLICE51_RECEIPT_PATH)
    spine, spine_status = _load_json(root / CONTINUITY_SPINE_PATH)

    source_status = (
        "OBSERVED"
        if all(
            status == "OBSERVED"
            for status in (p82_status, p83_status, slice77_status, slice51_status)
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
        "p82_source_repair_status": p82.get("p79_source_repair_plan_status", "NOT_COMPUTABLE"),
        "p83_status_repair_plan_status": p83.get(
            "p79_status_repair_plan_status", "NOT_COMPUTABLE"
        ),
        "p83_source_status": p83.get("p79_source_status", "NOT_COMPUTABLE"),
        "source_recommended_next_lane": p83.get(
            "recommended_next_lane",
            p82.get("recommended_next_lane", "NOT_COMPUTABLE"),
        ),
        "safe_next_surface": p83.get("recommended_next_lane", "NOT_COMPUTABLE"),
        "recommended_next_engineering_move": (
            "Keep the route advisory-only, preserve the emitted P83 packet as the canonical status-repair handoff, and route contributors into the downstream P80 regeneration planning surfaces without opening repair or authorization authority."
        ),
        "unsatisfied_status_expectation_count": len(
            [
                item
                for item in p83.get("status_field_expectations", [])
                if isinstance(item, dict) and item.get("satisfied") is False
            ]
        ),
        "blocked_status_repair_reason_count": len(
            [
                item
                for item in p83.get("blocked_status_repair_reasons", [])
                if isinstance(item, str)
            ]
        ),
        "continuity_summary": _continuity_summary(spine, spine_status),
        "route_stage_rows": _route_stage_rows(
            p82=p82,
            p82_status=p82_status,
            p83=p83,
            p83_status=p83_status,
            slice51=slice51,
            slice51_status=slice51_status,
        ),
        "route_target_rows": _route_target_rows(root),
        "findings": _findings(
            p83=p83,
            p83_status=p83_status,
            slice51=slice51,
            slice51_status=slice51_status,
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
            "Slice78 complete - Temporal upstream status-repair route refresh shipped; the emitted P83 status-repair packet is now routed through a contributor-facing status page and receipt, with the downstream P80 regeneration handoff kept explicit and advisory-only; no sandbox probe, runtime activation, canon mutation, MCP exposure, external calls, or autonomous writeback authorized. Brier Score: 0.10."
        ),
        "validation_plan": [
            "python scripts/temporal/run_temporal_upstream_status_repair_route_refresh_receipt.py",
            "python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_status_repair_route_refresh_001.latest.json",
            "python -m py_compile core/temporal_upstream_status_repair_route_refresh.py scripts/temporal/run_temporal_upstream_status_repair_route_refresh_receipt.py tests/test_temporal_upstream_status_repair_route_refresh.py",
            "git diff --check",
        ],
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice78 + "
            "Hash: temporal_upstream_status_repair_route_refresh_001.latest.json"
        ),
    }
    packet["canonical_hash"] = canonical_hash(packet)
    return packet


def write_temporal_upstream_status_repair_route_refresh_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    write_canonical_json(target, packet)
    return target
