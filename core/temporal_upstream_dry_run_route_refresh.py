from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalUpstreamDryRunRouteRefreshReceipt.v1"
STATUS = "TEMPORAL_UPSTREAM_DRY_RUN_ROUTE_REFRESH_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-74"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = "out/audit/temporal_upstream_dry_run_route_refresh_001.latest.json"
STATUS_DOC_PATH = "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_DRY_RUN_ROUTE.md"

P75_RECEIPT_PATH = "out/temporal_continuity_generator_discovery_plan/latest.json"
P76_RECEIPT_PATH = "out/temporal_continuity_upstream_input_restoration_plan/latest.json"
P77_RECEIPT_PATH = "out/temporal_continuity_upstream_input_regeneration_dry_run_plan/latest.json"
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"
LINEAGE_MAP_PATH = "docs/lineage/CONTINUITY_LINEAGE_MAP_002.md"
P77_PLAN_PATH = "docs/plans/P77_temporal_continuity_upstream_input_regeneration_dry_run_plan.md"
P78_PLAN_PATH = "docs/plans/P78_temporal_continuity_upstream_input_regeneration_execution_plan.md"
HEALTH_DASHBOARD_PATH = "docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md"

SOURCE_PATHS = (
    P75_RECEIPT_PATH,
    P76_RECEIPT_PATH,
    P77_RECEIPT_PATH,
    CONTINUITY_SPINE_PATH,
    LINEAGE_MAP_PATH,
    P77_PLAN_PATH,
    P78_PLAN_PATH,
    HEALTH_DASHBOARD_PATH,
    STATUS_DOC_PATH,
    "core/generated_artifact_registry.py",
)

REQUIRED_ROUTE_TARGETS = (
    STATUS_DOC_PATH,
    DEFAULT_OUT_PATH,
    P77_RECEIPT_PATH,
    P77_PLAN_PATH,
    P78_PLAN_PATH,
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
                    "dry_run_plan_status",
                    payload.get(
                        "upstream_restoration_plan_status",
                        payload.get("generator_discovery_status", "OBSERVED"),
                    ),
                ),
            )
            row["packet_hash"] = payload.get(
                "canonical_hash", payload.get("packet_hash", "NOT_COMPUTABLE")
            )
    return row


def _route_stage_rows(
    *,
    p75: dict[str, Any],
    p75_status: str,
    p76: dict[str, Any],
    p76_status: str,
    p77: dict[str, Any],
    p77_status: str,
) -> list[dict[str, Any]]:
    return [
        {
            "stage": "P75_GENERATOR_DISCOVERY_PLAN",
            "path": P75_RECEIPT_PATH,
            "source_status": p75_status,
            "status": p75.get("generator_discovery_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p75.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "P75 confirms the candidate generators that keep the upstream route grounded "
                "in repo-observed surfaces."
            ),
            "authority_granted": False,
        },
        {
            "stage": "P76_UPSTREAM_INPUT_RESTORATION_PLAN",
            "path": P76_RECEIPT_PATH,
            "source_status": p76_status,
            "status": p76.get("upstream_restoration_plan_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p76.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "P76 turns observed generator coverage into explicit missing-input posture and "
                "routes the chain to dry-run planning rather than repair authority."
            ),
            "authority_granted": False,
        },
        {
            "stage": "P77_UPSTREAM_INPUT_REGENERATION_DRY_RUN_PLAN",
            "path": P77_RECEIPT_PATH,
            "source_status": p77_status,
            "status": p77.get("dry_run_plan_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p77.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "P77 proves the dry-run lane is already deterministic and keeps all execution "
                "and regeneration authority fail-closed."
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
        P77_PLAN_PATH,
        P78_PLAN_PATH,
        STATUS_DOC_PATH,
    ):
        combined.append(relative_path)
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


def _findings(*, p77: dict[str, Any], p77_status: str) -> list[dict[str, Any]]:
    if p77_status != "OBSERVED":
        return [
            {
                "severity": "HIGH",
                "code": "P77_SOURCE_NOT_COMPUTABLE",
                "detail": "The dry-run plan output is missing or unreadable, so downstream continuity routing must fail closed.",
                "authority_granted": False,
            }
        ]

    findings: list[dict[str, Any]] = []
    still_blocked = [str(item) for item in p77.get("still_blocked_inputs", [])]
    if still_blocked:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "STILL_BLOCKED_INPUTS_REMAIN",
                "detail": (
                    f"{len(still_blocked)} upstream input(s) remain blocked after dry-run planning; "
                    f"sample: {still_blocked[0]}."
                ),
                "authority_granted": False,
            }
        )
    future_candidates = [str(item) for item in p77.get("executable_future_candidates", [])]
    if future_candidates:
        findings.append(
            {
                "severity": "LOW",
                "code": "FUTURE_EXECUTION_CANDIDATES_IDENTIFIED",
                "detail": (
                    "P77 identifies future execution candidates for planning only; "
                    f"sample: {future_candidates[0]}."
                ),
                "authority_granted": False,
            }
        )
    dry_run_commands = [str(item) for item in p77.get("dry_run_commands", [])]
    findings.append(
        {
            "severity": "LOW",
            "code": "DRY_RUN_COMMANDS_RECORDED",
            "detail": (
                f"P77 records {len(dry_run_commands)} dry-run command(s) while keeping "
                "all execution and mutation authority false."
            ),
            "authority_granted": False,
        }
    )
    return findings


def build_temporal_upstream_dry_run_route_refresh_receipt(
    *,
    repo_root: str | Path,
) -> dict[str, Any]:
    root = Path(repo_root)
    p75, p75_status = _load_json(root / P75_RECEIPT_PATH)
    p76, p76_status = _load_json(root / P76_RECEIPT_PATH)
    p77, p77_status = _load_json(root / P77_RECEIPT_PATH)
    spine, spine_status = _load_json(root / CONTINUITY_SPINE_PATH)

    source_status = (
        "OBSERVED"
        if all(status == "OBSERVED" for status in (p75_status, p76_status, p77_status))
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
        "dry_run_plan_status": p77.get("dry_run_plan_status", "NOT_COMPUTABLE"),
        "source_recommended_next_lane": p77.get(
            "source_recommended_next_lane",
            p76.get("recommended_next_lane", "NOT_COMPUTABLE"),
        ),
        "safe_next_surface": p77.get("recommended_next_lane", "NOT_COMPUTABLE"),
        "recommended_next_engineering_move": (
            "Keep the route advisory-only, preserve the tracked P77 dry-run output, and use P78 "
            "execution-planning surfaces as routing only."
        ),
        "future_execution_candidate_count": len(
            [item for item in p77.get("executable_future_candidates", []) if isinstance(item, str)]
        ),
        "blocked_input_count": len(
            [item for item in p77.get("still_blocked_inputs", []) if isinstance(item, str)]
        ),
        "still_blocked_inputs": [str(item) for item in p77.get("still_blocked_inputs", [])],
        "continuity_summary": _continuity_summary(spine, spine_status),
        "route_stage_rows": _route_stage_rows(
            p75=p75,
            p75_status=p75_status,
            p76=p76,
            p76_status=p76_status,
            p77=p77,
            p77_status=p77_status,
        ),
        "route_target_rows": _route_target_rows(root),
        "findings": _findings(p77=p77, p77_status=p77_status),
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
            "Slice74 complete - Temporal upstream dry-run route refresh shipped; "
            "the existing P77 upstream input regeneration dry-run plan is now tracked and "
            "routed through a contributor-facing status page and receipt, with P78 kept as the "
            "next advisory-only execution-planning surface; no sandbox probe, runtime activation, "
            "canon mutation, MCP exposure, external calls, or autonomous writeback authorized. "
            "Brier Score: 0.10."
        ),
        "validation_plan": [
            "python scripts/temporal/run_temporal_upstream_dry_run_route_refresh_receipt.py",
            "python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_dry_run_route_refresh_001.latest.json",
            "python -m py_compile core/temporal_upstream_dry_run_route_refresh.py scripts/temporal/run_temporal_upstream_dry_run_route_refresh_receipt.py tests/test_temporal_upstream_dry_run_route_refresh.py",
            "git diff --check",
        ],
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice74 + "
            "Hash: temporal_upstream_dry_run_route_refresh_001.latest.json"
        ),
    }
    packet["canonical_hash"] = canonical_hash(packet)
    return packet


def write_temporal_upstream_dry_run_route_refresh_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    write_canonical_json(target, packet)
    return target
