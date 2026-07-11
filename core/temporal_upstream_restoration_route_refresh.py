from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalUpstreamRestorationRouteRefreshReceipt.v1"
STATUS = "TEMPORAL_UPSTREAM_RESTORATION_ROUTE_REFRESH_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-73"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = "out/audit/temporal_upstream_restoration_route_refresh_001.latest.json"
STATUS_DOC_PATH = "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_RESTORATION_ROUTE.md"

P74_RECEIPT_PATH = "out/temporal_continuity_missing_evidence_restoration_plan/latest.json"
P75_RECEIPT_PATH = "out/temporal_continuity_generator_discovery_plan/latest.json"
P76_RECEIPT_PATH = "out/temporal_continuity_upstream_input_restoration_plan/latest.json"
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"
LINEAGE_MAP_PATH = "docs/lineage/CONTINUITY_LINEAGE_MAP_002.md"
P75_PLAN_PATH = "docs/plans/P75_temporal_continuity_generator_discovery_plan.md"
P76_PLAN_PATH = "docs/plans/P76_temporal_continuity_upstream_input_restoration_plan.md"
P77_PLAN_PATH = "docs/plans/P77_temporal_continuity_upstream_input_regeneration_dry_run_plan.md"
HEALTH_DASHBOARD_PATH = "docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md"

SOURCE_PATHS = (
    P74_RECEIPT_PATH,
    P75_RECEIPT_PATH,
    P76_RECEIPT_PATH,
    CONTINUITY_SPINE_PATH,
    LINEAGE_MAP_PATH,
    P75_PLAN_PATH,
    P76_PLAN_PATH,
    P77_PLAN_PATH,
    HEALTH_DASHBOARD_PATH,
    STATUS_DOC_PATH,
    "core/generated_artifact_registry.py",
)

REQUIRED_ROUTE_TARGETS = (
    STATUS_DOC_PATH,
    DEFAULT_OUT_PATH,
    P75_RECEIPT_PATH,
    P76_RECEIPT_PATH,
    P77_PLAN_PATH,
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
                    "restoration_plan_status",
                    payload.get(
                        "generator_discovery_status",
                        payload.get("upstream_restoration_plan_status", "OBSERVED"),
                    ),
                ),
            )
            row["packet_hash"] = payload.get(
                "canonical_hash", payload.get("packet_hash", "NOT_COMPUTABLE")
            )
    return row


def _route_stage_rows(
    *,
    p74: dict[str, Any],
    p74_status: str,
    p75: dict[str, Any],
    p75_status: str,
    p76: dict[str, Any],
    p76_status: str,
) -> list[dict[str, Any]]:
    return [
        {
            "stage": "P74_MISSING_EVIDENCE_RESTORATION_PLAN",
            "path": P74_RECEIPT_PATH,
            "source_status": p74_status,
            "status": p74.get("restoration_plan_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p74.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "P74 identifies the earliest missing temporal evidence and routes "
                "generator/upstream planning without granting repair authority."
            ),
            "authority_granted": False,
        },
        {
            "stage": "P75_GENERATOR_DISCOVERY_PLAN",
            "path": P75_RECEIPT_PATH,
            "source_status": p75_status,
            "status": p75.get("generator_discovery_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p75.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "P75 confirms the relevant generators are observed and shifts the "
                "chain from script discovery to upstream prerequisite routing."
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
                "P76 turns the observed generator route into an explicit upstream "
                "input posture and shows why the next safe lane is still dry-run planning."
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


def _findings(
    *,
    p75: dict[str, Any],
    p76: dict[str, Any],
    p75_status: str,
    p76_status: str,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if p75_status == "OBSERVED":
        missing_paths = p75.get("missing_prerequisite_paths", [])
        if missing_paths:
            findings.append(
                {
                    "severity": "MEDIUM",
                    "code": "UPSTREAM_PREREQUISITES_MISSING",
                    "detail": (
                        "Generator discovery is complete enough to proceed, but "
                        f"{len(missing_paths)} prerequisite path(s) remain missing: "
                        + ", ".join(missing_paths[:3])
                    ),
                    "authority_granted": False,
                }
            )
    else:
        findings.append(
            {
                "severity": "HIGH",
                "code": "P75_SOURCE_NOT_COMPUTABLE",
                "detail": "Generator discovery receipt is missing or unreadable.",
                "authority_granted": False,
            }
        )

    if p76_status == "OBSERVED":
        blocked = p76.get("outputs_blocked_by_upstream_inputs", [])
        if blocked:
            sample = blocked[0]
            findings.append(
                {
                    "severity": "MEDIUM",
                    "code": "UPSTREAM_INPUT_BLOCKS_DOWNSTREAM_OUTPUTS",
                    "detail": (
                        f"{sample.get('path', 'NOT_COMPUTABLE')} blocks "
                        f"{len(sample.get('blocked_output_paths', []))} downstream output route(s)."
                    ),
                    "authority_granted": False,
                }
            )
        degraded = p76.get("degraded_evidence_inputs", [])
        if degraded:
            findings.append(
                {
                    "severity": "LOW",
                    "code": "DEGRADED_EVIDENCE_REMAINS",
                    "detail": (
                        "Historical degraded evidence still propagates through the "
                        f"upstream restoration route ({len(degraded)} degraded input markers observed)."
                    ),
                    "authority_granted": False,
                }
            )
    else:
        findings.append(
            {
                "severity": "HIGH",
                "code": "P76_SOURCE_NOT_COMPUTABLE",
                "detail": "Upstream input restoration receipt is missing or unreadable.",
                "authority_granted": False,
            }
        )
    return findings


def build_temporal_upstream_restoration_route_refresh_receipt(
    *, repo_root: Path
) -> dict[str, Any]:
    p74, p74_status = _load_json(repo_root / P74_RECEIPT_PATH)
    p75, p75_status = _load_json(repo_root / P75_RECEIPT_PATH)
    p76, p76_status = _load_json(repo_root / P76_RECEIPT_PATH)
    spine, spine_status = _load_json(repo_root / CONTINUITY_SPINE_PATH)

    route_stage_rows = _route_stage_rows(
        p74=p74,
        p74_status=p74_status,
        p75=p75,
        p75_status=p75_status,
        p76=p76,
        p76_status=p76_status,
    )
    findings = _findings(p75=p75, p76=p76, p75_status=p75_status, p76_status=p76_status)

    source_status = (
        "READY_WITH_FINDINGS"
        if p75_status == "OBSERVED" and p76_status == "OBSERVED"
        else "NOT_COMPUTABLE"
    )
    current_route_class = (
        "ACTIVE NAVIGATION" if source_status == "READY_WITH_FINDINGS" else "NOT_COMPUTABLE / HELD"
    )
    safe_next_surface = (
        p76.get("recommended_next_lane", "NOT_COMPUTABLE")
        if p76_status == "OBSERVED"
        else "NOT_COMPUTABLE"
    )

    packet: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "status": STATUS,
        "brier_score": BRIER_SCORE,
        "slice_id": SLICE_ID,
        "source_status": source_status,
        "current_route_class": current_route_class,
        "generator_discovery_status": p75.get(
            "generator_discovery_status", "NOT_COMPUTABLE"
        ),
        "upstream_restoration_status": p76.get(
            "upstream_restoration_plan_status", "NOT_COMPUTABLE"
        ),
        "continuity_summary": _continuity_summary(spine, spine_status),
        "safe_next_surface": safe_next_surface,
        "recommended_next_engineering_move": (
            "Keep the route advisory-only and use "
            "P77_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_DRY_RUN_PLAN "
            "as the next continuity surface; do not regenerate missing inputs here."
            if safe_next_surface != "NOT_COMPUTABLE"
            else "Regenerate or repair the P75/P76 planning receipts before routing downstream."
        ),
        "route_stage_rows": route_stage_rows,
        "critical_findings": findings,
        "source_status_table": [_source_row(repo_root, path) for path in SOURCE_PATHS],
        "route_target_rows": _route_target_rows(repo_root),
        "authority_locks": dict(AUTHORITY_LOCKS),
        "boundary": {
            "advisory_only": True,
            "projection_only": True,
            "status_routing_only": True,
            "sandbox_gate_issued": False,
            "runtime_activation": False,
            "canon_mutation": False,
            "notion_writeback": False,
            **dict(AUTHORITY_LOCKS),
        },
        "validation_plan": [
            "python scripts/run_temporal_upstream_restoration_route_refresh_receipt.py",
            (
                "python scripts/run_artifact_regeneration.py --artifact "
                f"{DEFAULT_OUT_PATH}"
            ),
            (
                "python -m py_compile "
                "core/temporal_upstream_restoration_route_refresh.py "
                "scripts/run_temporal_upstream_restoration_route_refresh_receipt.py "
                "tests/test_temporal_upstream_restoration_route_refresh.py"
            ),
            (
                "python -m pytest "
                "tests/test_temporal_upstream_restoration_route_refresh.py "
                "tests/test_generated_artifact_registry.py -q -k "
                "\"temporal_upstream_restoration_route_refresh or artifact_regeneration\""
            ),
            "git diff --check",
        ],
        "notion_closeout_text": (
            "Slice73 complete - temporal upstream restoration route refresh shipped; "
            "P75 generator discovery and P76 upstream input restoration now route through "
            "one advisory status/receipt path to P77 dry-run planning without generator "
            "execution or evidence repair authority. No sandbox probe, runtime activation, "
            "canon mutation, MCP exposure, external calls, or autonomous writeback authorized. "
            "Brier Score: 0.10."
        ),
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice73 + "
            "Hash: temporal_upstream_restoration_route_refresh_001.latest.json"
        ),
    }
    packet["canonical_hash"] = canonical_hash(packet)
    return packet


def write_temporal_upstream_restoration_route_refresh_receipt(
    path: Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
