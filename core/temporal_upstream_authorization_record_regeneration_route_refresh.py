from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalUpstreamAuthorizationRecordRegenerationRouteRefreshReceipt.v1"
STATUS = (
    "TEMPORAL_UPSTREAM_AUTHORIZATION_RECORD_REGENERATION_ROUTE_REFRESH_READY_"
    "ADVISORY_ONLY"
)
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-77"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = (
    "out/audit/temporal_upstream_authorization_record_regeneration_route_refresh_001.latest.json"
)
STATUS_DOC_PATH = (
    "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_AUTHORIZATION_RECORD_REGENERATION_ROUTE.md"
)

P79_RECEIPT_PATH = (
    "out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json"
)
SLICE50_RECEIPT_PATH = (
    "out/audit/temporal_continuity_authorization_source_status_audit_001.latest.json"
)
SLICE51_RECEIPT_PATH = (
    "out/audit/temporal_continuity_p80_authorization_record_regeneration_receipt_001.latest.json"
)
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"
LINEAGE_MAP_PATH = "docs/lineage/CONTINUITY_LINEAGE_MAP_002.md"
P80_PLAN_PATH = (
    "docs/plans/P80_temporal_continuity_upstream_input_regeneration_authorization_record_plan.md"
)
P81_PLAN_PATH = (
    "docs/plans/P81_temporal_continuity_authorization_record_plan_source_status_audit.md"
)
P83_PLAN_PATH = (
    "docs/plans/P83_temporal_continuity_p79_authorization_gate_status_repair_plan.md"
)
P84_PLAN_PATH = (
    "docs/plans/P84_temporal_continuity_p80_authorization_record_plan_regeneration_plan.md"
)
HEALTH_DASHBOARD_PATH = "docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md"
P79_ROUTE_DOC_PATH = "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_AUTHORIZATION_GATE_ROUTE.md"

SOURCE_PATHS = (
    P79_RECEIPT_PATH,
    SLICE50_RECEIPT_PATH,
    SLICE51_RECEIPT_PATH,
    CONTINUITY_SPINE_PATH,
    LINEAGE_MAP_PATH,
    P80_PLAN_PATH,
    P81_PLAN_PATH,
    P83_PLAN_PATH,
    P84_PLAN_PATH,
    HEALTH_DASHBOARD_PATH,
    STATUS_DOC_PATH,
    "core/generated_artifact_registry.py",
)

REQUIRED_ROUTE_TARGETS = (
    STATUS_DOC_PATH,
    DEFAULT_OUT_PATH,
    SLICE50_RECEIPT_PATH,
    SLICE51_RECEIPT_PATH,
    P83_PLAN_PATH,
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
                    "authorization_gate_status",
                    payload.get("source_chain_status", "OBSERVED"),
                ),
            )
            row["packet_hash"] = payload.get(
                "canonical_hash", payload.get("packet_hash", "NOT_COMPUTABLE")
            )
    return row


def _route_stage_rows(
    *,
    p79: dict[str, Any],
    p79_status: str,
    slice50: dict[str, Any],
    slice50_status: str,
    slice51: dict[str, Any],
    slice51_status: str,
) -> list[dict[str, Any]]:
    return [
        {
            "stage": "P79_UPSTREAM_INPUT_REGENERATION_AUTHORIZATION_GATE",
            "path": P79_RECEIPT_PATH,
            "source_status": p79_status,
            "status": p79.get("authorization_gate_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p79.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "P79 records that authorization review is structurally eligible while "
                "keeping authorization and execution authority false."
            ),
            "authority_granted": False,
        },
        {
            "stage": "P81_AUTHORIZATION_RECORD_PLAN_SOURCE_STATUS_AUDIT",
            "path": SLICE50_RECEIPT_PATH,
            "source_status": slice50_status,
            "status": slice50.get("source_chain_summary", {}).get(
                "source_chain_status", "NOT_COMPUTABLE"
            ),
            "recommended_next_lane": slice50.get("source_chain_summary", {}).get(
                "recommended_next_lane", "NOT_COMPUTABLE"
            ),
            "why_this_matters": (
                "Slice50 confirms the P80 artifact is still missing and turns that fact "
                "into a fail-closed contributor-facing audit route."
            ),
            "authority_granted": False,
        },
        {
            "stage": "P80_AUTHORIZATION_RECORD_PLAN_REGENERATION_RECEIPT",
            "path": SLICE51_RECEIPT_PATH,
            "source_status": slice51_status,
            "status": slice51.get("p80_regeneration_summary", {}).get(
                "p80_regeneration_plan_status", "NOT_COMPUTABLE"
            ),
            "recommended_next_lane": slice51.get("p80_regeneration_summary", {}).get(
                "recommended_next_lane", "NOT_COMPUTABLE"
            ),
            "why_this_matters": (
                "Slice51 packages the current P80 regeneration route and makes the "
                "handoff to P83 status repair explicit when the deeper source chain is still incomplete."
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
        STATUS_DOC_PATH,
        P79_ROUTE_DOC_PATH,
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


def _findings(
    *,
    slice50: dict[str, Any],
    slice50_status: str,
    slice51: dict[str, Any],
    slice51_status: str,
) -> list[dict[str, Any]]:
    if slice50_status != "OBSERVED" or slice51_status != "OBSERVED":
        return [
            {
                "severity": "HIGH",
                "code": "P80_ROUTE_SOURCES_NOT_COMPUTABLE",
                "detail": (
                    "The existing Slice50/Slice51 route evidence is missing or unreadable, "
                    "so downstream continuity routing must fail closed."
                ),
                "authority_granted": False,
            }
        ]

    findings: list[dict[str, Any]] = []
    not_computable_reasons = [
        str(item)
        for item in slice50.get("source_chain_summary", {}).get(
            "not_computable_reasons", []
        )
    ]
    if not_computable_reasons:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "P80_SOURCE_STILL_MISSING",
                "detail": (
                    f"P81 still reports {len(not_computable_reasons)} not-computable "
                    f"reason(s); sample: {not_computable_reasons[0]}."
                ),
                "authority_granted": False,
            }
        )
    blocked_reasons = [
        str(item)
        for item in slice51.get("p80_regeneration_summary", {}).get(
            "blocked_regeneration_reasons", []
        )
    ]
    if blocked_reasons:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "P80_REGENERATION_BLOCKED",
                "detail": (
                    f"P80 regeneration remains blocked by {len(blocked_reasons)} "
                    f"reason(s); sample: {blocked_reasons[0]}."
                ),
                "authority_granted": False,
            }
        )
    if (
        slice51.get("p80_regeneration_summary", {}).get("p80_regeneration_plan_status")
        == "NOT_COMPUTABLE"
    ):
        findings.append(
            {
                "severity": "LOW",
                "code": "P80_REGENERATION_ROUTE_HELD",
                "detail": (
                    "The current P80 regeneration route is present as contributor-facing "
                    "evidence only and still denies repair, regeneration execution, and authorization."
                ),
                "authority_granted": False,
            }
        )
    return findings


def build_temporal_upstream_authorization_record_regeneration_route_refresh_receipt(
    *,
    repo_root: str | Path,
) -> dict[str, Any]:
    root = Path(repo_root)
    p79, p79_status = _load_json(root / P79_RECEIPT_PATH)
    slice50, slice50_status = _load_json(root / SLICE50_RECEIPT_PATH)
    slice51, slice51_status = _load_json(root / SLICE51_RECEIPT_PATH)
    spine, spine_status = _load_json(root / CONTINUITY_SPINE_PATH)

    source_status = (
        "OBSERVED"
        if all(
            status == "OBSERVED"
            for status in (p79_status, slice50_status, slice51_status)
        )
        else "NOT_COMPUTABLE"
    )
    current_route_class = (
        "ACTIVE NAVIGATION" if source_status == "OBSERVED" else "NOT_COMPUTABLE / HELD"
    )
    source_chain_summary = slice50.get("source_chain_summary", {})
    regeneration_summary = slice51.get("p80_regeneration_summary", {})

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
        "authorization_gate_status": p79.get(
            "authorization_gate_status", "NOT_COMPUTABLE"
        ),
        "source_chain_status": source_chain_summary.get(
            "source_chain_status", "NOT_COMPUTABLE"
        ),
        "p80_regeneration_plan_status": regeneration_summary.get(
            "p80_regeneration_plan_status", "NOT_COMPUTABLE"
        ),
        "source_recommended_next_lane": source_chain_summary.get(
            "recommended_next_lane",
            p79.get("recommended_next_lane", "NOT_COMPUTABLE"),
        ),
        "safe_next_surface": regeneration_summary.get(
            "recommended_next_lane", "NOT_COMPUTABLE"
        ),
        "recommended_next_engineering_move": (
            "Keep the route advisory-only, preserve the tracked Slice50/Slice51 "
            "blockage evidence, and use the P83 status-repair planning surface as routing only."
        ),
        "not_computable_reason_count": len(
            [
                item
                for item in source_chain_summary.get("not_computable_reasons", [])
                if isinstance(item, str)
            ]
        ),
        "blocked_regeneration_reason_count": len(
            [
                item
                for item in regeneration_summary.get(
                    "blocked_regeneration_reasons", []
                )
                if isinstance(item, str)
            ]
        ),
        "continuity_summary": _continuity_summary(spine, spine_status),
        "route_stage_rows": _route_stage_rows(
            p79=p79,
            p79_status=p79_status,
            slice50=slice50,
            slice50_status=slice50_status,
            slice51=slice51,
            slice51_status=slice51_status,
        ),
        "route_target_rows": _route_target_rows(root),
        "findings": _findings(
            slice50=slice50,
            slice50_status=slice50_status,
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
            "Slice77 complete - Temporal upstream authorization-record regeneration route "
            "refresh shipped; the existing Slice50/Slice51 evidence now routes the missing P80 "
            "authorization-record-plan chain through a contributor-facing status page and receipt, "
            "with P83 kept as the next advisory-only status-repair-planning surface; no sandbox "
            "probe, runtime activation, canon mutation, MCP exposure, external calls, or autonomous "
            "writeback authorized. Brier Score: 0.10."
        ),
        "validation_plan": [
            "python Scripts/run_temporal_upstream_authorization_record_regeneration_route_refresh_receipt.py",
            "python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_authorization_record_regeneration_route_refresh_001.latest.json",
            "python -m py_compile core/temporal_upstream_authorization_record_regeneration_route_refresh.py Scripts/run_temporal_upstream_authorization_record_regeneration_route_refresh_receipt.py tests/test_temporal_upstream_authorization_record_regeneration_route_refresh.py",
            "git diff --check",
        ],
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice77 + "
            "Hash: temporal_upstream_authorization_record_regeneration_route_refresh_001.latest.json"
        ),
    }
    packet["canonical_hash"] = canonical_hash(packet)
    return packet


def write_temporal_upstream_authorization_record_regeneration_route_refresh_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    write_canonical_json(target, packet)
    return target
