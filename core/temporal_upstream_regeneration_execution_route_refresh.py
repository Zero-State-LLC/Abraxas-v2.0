from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalUpstreamRegenerationExecutionRouteRefreshReceipt.v1"
STATUS = "TEMPORAL_UPSTREAM_REGENERATION_EXECUTION_ROUTE_REFRESH_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-80"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = (
    "out/audit/temporal_upstream_regeneration_execution_route_refresh_001.latest.json"
)
STATUS_DOC_PATH = (
    "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_EXECUTION_ROUTE.md"
)

P84_RECEIPT_PATH = (
    "out/temporal_continuity_p80_authorization_record_plan_regeneration_plan/latest.json"
)
P85_RECEIPT_PATH = (
    "out/temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan/latest.json"
)
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"
LINEAGE_MAP_PATH = "docs/lineage/CONTINUITY_LINEAGE_MAP_002.md"
P84_PLAN_PATH = (
    "docs/plans/P84_temporal_continuity_p80_authorization_record_plan_regeneration_plan.md"
)
P85_PLAN_PATH = (
    "docs/plans/P85_temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan.md"
)
P86_PLAN_PATH = (
    "docs/plans/P86_temporal_continuity_p84_regeneration_plan_regeneration_plan.md"
)
HEALTH_DASHBOARD_PATH = "docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md"
P84_ROUTE_DOC_PATH = "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_PLAN_ROUTE.md"

SOURCE_PATHS = (
    P84_RECEIPT_PATH,
    P85_RECEIPT_PATH,
    CONTINUITY_SPINE_PATH,
    LINEAGE_MAP_PATH,
    P84_PLAN_PATH,
    P85_PLAN_PATH,
    P86_PLAN_PATH,
    HEALTH_DASHBOARD_PATH,
    P84_ROUTE_DOC_PATH,
    STATUS_DOC_PATH,
    "core/generated_artifact_registry.py",
)

REQUIRED_ROUTE_TARGETS = (
    STATUS_DOC_PATH,
    DEFAULT_OUT_PATH,
    P85_RECEIPT_PATH,
    P84_ROUTE_DOC_PATH,
    P86_PLAN_PATH,
)

PACKAGED_SAFE_NEXT_SURFACE = (
    "P86_TEMPORAL_CONTINUITY_P84_REGENERATION_PLAN_REGENERATION_PLAN"
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
                    "p80_regeneration_execution_plan_status",
                    payload.get("p80_regeneration_plan_status", "OBSERVED"),
                ),
            )
            row["packet_hash"] = payload.get(
                "canonical_hash", payload.get("packet_hash", "NOT_COMPUTABLE")
            )
    return row


def _route_stage_rows(
    *,
    p84: dict[str, Any],
    p84_status: str,
    p85: dict[str, Any],
    p85_status: str,
) -> list[dict[str, Any]]:
    return [
        {
            "stage": "P84_AUTHORIZATION_RECORD_REGENERATION_PLAN",
            "path": P84_RECEIPT_PATH,
            "source_status": p84_status,
            "status": p84.get("p80_regeneration_plan_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p84.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "P84 records the regeneration-plan posture and remains the prerequisite "
                "source packet for any downstream P85 execution-planning interpretation."
            ),
            "authority_granted": False,
        },
        {
            "stage": "P85_AUTHORIZATION_RECORD_REGENERATION_EXECUTION_PLAN",
            "path": P85_RECEIPT_PATH,
            "source_status": p85_status,
            "status": p85.get("p80_regeneration_execution_plan_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p85.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "P85 packages the held execution-planning surface and keeps regeneration, "
                "authorization, and mutation authority false even when the route is blocked."
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
        P84_ROUTE_DOC_PATH,
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


def _findings(*, p85: dict[str, Any], p85_status: str) -> list[dict[str, Any]]:
    if p85_status != "OBSERVED":
        return [
            {
                "severity": "HIGH",
                "code": "P85_SOURCE_NOT_COMPUTABLE",
                "detail": (
                    "The emitted P85 execution-planning packet is missing or unreadable, "
                    "so downstream continuity routing must fail closed."
                ),
                "authority_granted": False,
            }
        ]

    findings: list[dict[str, Any]] = []
    blocked_reasons = [str(item) for item in p85.get("blocked_execution_reasons", [])]
    if blocked_reasons:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "P85_BLOCKED_EXECUTION_REASONS_PRESENT",
                "detail": (
                    f"{len(blocked_reasons)} blocked execution reason(s) remain in P85; "
                    f"sample: {blocked_reasons[0]}."
                ),
                "authority_granted": False,
            }
        )
    if (
        p85.get("p80_regeneration_execution_plan_status")
        == "P80_REGENERATION_EXECUTION_PLAN_BLOCKED"
    ):
        findings.append(
            {
                "severity": "LOW",
                "code": "P85_ROUTE_BLOCKED_BUT_OBSERVED",
                "detail": (
                    "The P85 packet is observed and contributor-facing, but its current "
                    "execution-plan posture remains blocked and advisory-only."
                ),
                "authority_granted": False,
            }
        )
    if p85.get("source_p84_regeneration_plan_status"):
        findings.append(
            {
                "severity": "LOW",
                "code": "P85_SOURCE_P84_STATUS_VISIBLE",
                "detail": (
                    "P85 keeps the upstream P84 status explicit, which makes the handoff back "
                    "to the P86 regeneration-planning surface deterministic."
                ),
                "authority_granted": False,
            }
        )
    return findings


def build_temporal_upstream_regeneration_execution_route_refresh_receipt(
    *,
    repo_root: str | Path,
) -> dict[str, Any]:
    root = Path(repo_root)
    p84, p84_status = _load_json(root / P84_RECEIPT_PATH)
    p85, p85_status = _load_json(root / P85_RECEIPT_PATH)
    spine, spine_status = _load_json(root / CONTINUITY_SPINE_PATH)

    source_status = (
        "OBSERVED"
        if all(status == "OBSERVED" for status in (p84_status, p85_status))
        else "NOT_COMPUTABLE"
    )
    current_route_class = (
        "ACTIVE NAVIGATION" if p85_status == "OBSERVED" else "NOT_COMPUTABLE / HELD"
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
        "p84_regeneration_plan_status": p84.get(
            "p80_regeneration_plan_status", "NOT_COMPUTABLE"
        ),
        "p85_regeneration_execution_plan_status": p85.get(
            "p80_regeneration_execution_plan_status", "NOT_COMPUTABLE"
        ),
        "source_recommended_next_lane": p85.get(
            "recommended_next_lane", p84.get("recommended_next_lane", "NOT_COMPUTABLE")
        ),
        "safe_next_surface": (
            PACKAGED_SAFE_NEXT_SURFACE if p85_status == "OBSERVED" else "NOT_COMPUTABLE"
        ),
        "recommended_next_engineering_move": (
            "Keep the route advisory-only, preserve the emitted P85 execution-planning packet, "
            "and use the P86 regeneration-planning surface as routing only while all execution "
            "and authorization flags remain false."
        ),
        "blocked_execution_reason_count": len(
            [item for item in p85.get("blocked_execution_reasons", []) if isinstance(item, str)]
        ),
        "preflight_check_count": len(
            [item for item in p85.get("preflight_checks", []) if isinstance(item, dict)]
        ),
        "post_run_validation_count": len(
            [item for item in p85.get("post_run_validations", []) if isinstance(item, dict)]
        ),
        "continuity_summary": _continuity_summary(spine, spine_status),
        "route_stage_rows": _route_stage_rows(
            p84=p84,
            p84_status=p84_status,
            p85=p85,
            p85_status=p85_status,
        ),
        "route_target_rows": _route_target_rows(root),
        "findings": _findings(p85=p85, p85_status=p85_status),
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
            "Slice80 complete - Temporal upstream regeneration execution route refresh shipped; "
            "the existing P85 regeneration execution-planning packet is now routed through a "
            "contributor-facing status page and receipt, with the downstream P86 regeneration-"
            "planning handoff kept explicit and advisory-only; no sandbox probe, runtime "
            "activation, canon mutation, MCP exposure, external calls, or autonomous writeback "
            "authorized. Brier Score: 0.10."
        ),
        "validation_plan": [
            "python scripts/temporal/run_temporal_upstream_regeneration_execution_route_refresh_receipt.py",
            "python scripts/artifact/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_regeneration_execution_route_refresh_001.latest.json",
            "python -m py_compile core/temporal_upstream_regeneration_execution_route_refresh.py scripts/temporal/run_temporal_upstream_regeneration_execution_route_refresh_receipt.py tests/test_temporal_upstream_regeneration_execution_route_refresh.py",
            "git diff --check",
        ],
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice80 + "
            "Hash: temporal_upstream_regeneration_execution_route_refresh_001.latest.json"
        ),
    }
    packet["canonical_hash"] = canonical_hash(packet)
    return packet


def write_temporal_upstream_regeneration_execution_route_refresh_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    write_canonical_json(target, packet)
    return target
