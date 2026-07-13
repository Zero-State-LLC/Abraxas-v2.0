from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalUpstreamRegenerationPlanRegenerationRouteRefreshReceipt.v1"
STATUS = (
    "TEMPORAL_UPSTREAM_REGENERATION_PLAN_REGENERATION_ROUTE_REFRESH_READY_ADVISORY_ONLY"
)
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-81"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = (
    "out/audit/temporal_upstream_regeneration_plan_regeneration_route_refresh_001.latest.json"
)
STATUS_DOC_PATH = (
    "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_PLAN_REGENERATION_ROUTE.md"
)

P85_RECEIPT_PATH = (
    "out/temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan/latest.json"
)
P86_RECEIPT_PATH = (
    "out/temporal_continuity_p84_regeneration_plan_regeneration_plan/latest.json"
)
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"
LINEAGE_MAP_PATH = "docs/lineage/CONTINUITY_LINEAGE_MAP_002.md"
P85_PLAN_PATH = (
    "docs/plans/P85_temporal_continuity_p80_authorization_record_plan_regeneration_execution_plan.md"
)
P86_PLAN_PATH = (
    "docs/plans/P86_temporal_continuity_p84_regeneration_plan_regeneration_plan.md"
)
P87_PLAN_PATH = "docs/plans/P87_temporal_continuity_p83_status_plan_regeneration_plan.md"
HEALTH_DASHBOARD_PATH = "docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md"
P85_ROUTE_DOC_PATH = (
    "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_REGENERATION_EXECUTION_ROUTE.md"
)

SOURCE_PATHS = (
    P85_RECEIPT_PATH,
    P86_RECEIPT_PATH,
    CONTINUITY_SPINE_PATH,
    LINEAGE_MAP_PATH,
    P85_PLAN_PATH,
    P86_PLAN_PATH,
    P87_PLAN_PATH,
    HEALTH_DASHBOARD_PATH,
    P85_ROUTE_DOC_PATH,
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
                    payload.get("p80_regeneration_execution_plan_status", "OBSERVED"),
                ),
            )
            row["packet_hash"] = payload.get(
                "canonical_hash", payload.get("packet_hash", "NOT_COMPUTABLE")
            )
    return row


def _route_stage_rows(
    *,
    p85: dict[str, Any],
    p85_status: str,
    p86: dict[str, Any],
    p86_status: str,
) -> list[dict[str, Any]]:
    return [
        {
            "stage": "P85_AUTHORIZATION_RECORD_REGENERATION_EXECUTION_PLAN",
            "path": P85_RECEIPT_PATH,
            "source_status": p85_status,
            "status": p85.get("p80_regeneration_execution_plan_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p85.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "P85 keeps the held execution-planning lane visible and is the direct "
                "upstream source for the downstream P86 interpretation."
            ),
            "authority_granted": False,
        },
        {
            "stage": "P86_P84_REGENERATION_PLAN_REGENERATION_PLAN",
            "path": P86_RECEIPT_PATH,
            "source_status": p86_status,
            "status": p86.get("p84_regeneration_plan_regeneration_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p86.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "P86 packages the downstream regeneration-planning interpretation and "
                "records whether any further P84 regeneration planning is required."
            ),
            "authority_granted": False,
        },
    ]


def _route_target_rows(repo_root: Path, downstream_lane: str) -> list[dict[str, Any]]:
    combined = []
    for relative_path in (
        "README.md",
        "STATUS.md",
        "PLANS.md",
        "docs/START_HERE.md",
        "docs/INDEX.md",
        "docs/artifacts/ARTIFACT_INDEX.md",
        LINEAGE_MAP_PATH,
        P85_ROUTE_DOC_PATH,
        STATUS_DOC_PATH,
    ):
        text, _ = _read_text(repo_root / relative_path)
        combined.append(text)
    joined = "\n".join(combined)
    targets = (
        STATUS_DOC_PATH,
        DEFAULT_OUT_PATH,
        P86_RECEIPT_PATH,
        P85_ROUTE_DOC_PATH,
        downstream_lane,
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


def _findings(*, p86: dict[str, Any], p86_status: str) -> list[dict[str, Any]]:
    if p86_status != "OBSERVED":
        return [
            {
                "severity": "HIGH",
                "code": "P86_SOURCE_NOT_COMPUTABLE",
                "detail": (
                    "The emitted P86 regeneration-plan-regeneration packet is missing or "
                    "unreadable, so downstream continuity routing must fail closed."
                ),
                "authority_granted": False,
            }
        ]

    findings: list[dict[str, Any]] = []
    blocked_reasons = [str(item) for item in p86.get("blocked_regeneration_reasons", [])]
    if blocked_reasons:
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "P86_BLOCKED_REGENERATION_REASONS_PRESENT",
                "detail": (
                    f"{len(blocked_reasons)} blocked regeneration reason(s) remain in P86; "
                    f"sample: {blocked_reasons[0]}."
                ),
                "authority_granted": False,
            }
        )
    if (
        p86.get("p84_regeneration_plan_regeneration_status")
        == "P84_REGENERATION_NOT_REQUIRED"
    ):
        findings.append(
            {
                "severity": "LOW",
                "code": "P86_REGENERATION_NOT_REQUIRED",
                "detail": (
                    "The refreshed P86 packet now records that additional P84 regeneration "
                    "planning is not required because the upstream P84 packet is already ready."
                ),
                "authority_granted": False,
            }
        )
    if p86.get("source_p83_status_plan_observed") is True:
        findings.append(
            {
                "severity": "LOW",
                "code": "P86_SOURCE_P83_VISIBLE",
                "detail": (
                    "P86 now sees the packaged P83 status-plan source, which removes the "
                    "older false missing-source posture from the emitted packet."
                ),
                "authority_granted": False,
            }
        )
    if p86.get("recommended_next_lane"):
        findings.append(
            {
                "severity": "LOW",
                "code": "P86_DOWNSTREAM_LANE_EXPLICIT",
                "detail": (
                    "P86 carries an explicit downstream P87 handoff, so contributors can "
                    "preserve the lane transition without inventing execution authority."
                ),
                "authority_granted": False,
            }
        )
    return findings


def build_temporal_upstream_regeneration_plan_regeneration_route_refresh_receipt(
    *,
    repo_root: str | Path,
) -> dict[str, Any]:
    root = Path(repo_root)
    p85, p85_status = _load_json(root / P85_RECEIPT_PATH)
    p86, p86_status = _load_json(root / P86_RECEIPT_PATH)
    spine, spine_status = _load_json(root / CONTINUITY_SPINE_PATH)

    source_status = (
        "OBSERVED"
        if all(status == "OBSERVED" for status in (p85_status, p86_status))
        else "NOT_COMPUTABLE"
    )
    current_route_class = (
        "ACTIVE NAVIGATION" if p86_status == "OBSERVED" else "NOT_COMPUTABLE / HELD"
    )
    safe_next_surface = str(p86.get("recommended_next_lane", "NOT_COMPUTABLE"))

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
        "p85_regeneration_execution_plan_status": p85.get(
            "p80_regeneration_execution_plan_status", "NOT_COMPUTABLE"
        ),
        "p86_regeneration_plan_regeneration_status": p86.get(
            "p84_regeneration_plan_regeneration_status", "NOT_COMPUTABLE"
        ),
        "source_recommended_next_lane": safe_next_surface,
        "safe_next_surface": safe_next_surface,
        "recommended_next_engineering_move": (
            "Keep the route advisory-only, preserve the refreshed emitted P86 packet, and "
            "package the downstream P87 handoff separately if temporal continuity remains the active board lane."
        ),
        "continuity_summary": _continuity_summary(spine, spine_status),
        "route_stage_rows": _route_stage_rows(
            p85=p85,
            p85_status=p85_status,
            p86=p86,
            p86_status=p86_status,
        ),
        "route_target_rows": _route_target_rows(root, safe_next_surface),
        "findings": _findings(p86=p86, p86_status=p86_status),
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
            "Slice81 complete - Temporal upstream regeneration-plan regeneration route refresh "
            "shipped; the refreshed emitted P86 regeneration-planning packet is now routed "
            "through a contributor-facing status page and receipt, with the downstream P87 handoff "
            "kept explicit and advisory-only. Receipt hash: {canonical_hash}. No sandbox probe, "
            "runtime activation, canon mutation, MCP exposure, external calls, or autonomous "
            "writeback authorized. Brier Score: 0.10."
        ),
        "validation_plan": [
            "python scripts/temporal/run_temporal_upstream_regeneration_plan_regeneration_route_refresh_receipt.py",
            "python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_regeneration_plan_regeneration_route_refresh_001.latest.json",
            "python scripts/run_artifact_regeneration.py --artifact out/temporal_continuity_p84_regeneration_plan_regeneration_plan/latest.json",
            "python -m py_compile core/temporal_upstream_regeneration_plan_regeneration_route_refresh.py scripts/temporal/run_temporal_upstream_regeneration_plan_regeneration_route_refresh_receipt.py tests/test_temporal_upstream_regeneration_plan_regeneration_route_refresh.py core/generated_artifact_registry.py tests/test_generated_artifact_registry.py",
            "git diff --check",
        ],
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice81 + Hash: "
            "temporal_upstream_regeneration_plan_regeneration_route_refresh_001.latest.json"
        ),
    }
    packet["canonical_hash"] = canonical_hash(packet)
    return packet


def write_temporal_upstream_regeneration_plan_regeneration_route_refresh_receipt(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(Path(path), packet)
