from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalUpstreamAuthorizationGateRouteRefreshReceipt.v1"
STATUS = "TEMPORAL_UPSTREAM_AUTHORIZATION_GATE_ROUTE_REFRESH_READY_ADVISORY_ONLY"
BRIER_SCORE = "0.10"
SLICE_ID = "LOOP-805-SLICE-76"
NOTION_BOARD_URL = "https://app.notion.com/p/3843e8ba2f5c819480d0f2c5ffce6254"
DEFAULT_OUT_PATH = (
    "out/audit/temporal_upstream_authorization_gate_route_refresh_001.latest.json"
)
STATUS_DOC_PATH = "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_AUTHORIZATION_GATE_ROUTE.md"

P78_RECEIPT_PATH = "out/temporal_continuity_upstream_input_regeneration_execution_plan/latest.json"
P79_RECEIPT_PATH = (
    "out/temporal_continuity_upstream_input_regeneration_authorization_gate/latest.json"
)
CONTINUITY_SPINE_PATH = "docs/status/continuity-spine.json"
LINEAGE_MAP_PATH = "docs/lineage/CONTINUITY_LINEAGE_MAP_002.md"
P79_PLAN_PATH = "docs/plans/P79_temporal_continuity_upstream_input_regeneration_authorization_gate.md"
P80_PLAN_PATH = "docs/plans/P80_temporal_continuity_upstream_input_regeneration_authorization_record_plan.md"
HEALTH_DASHBOARD_PATH = "docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md"

SOURCE_PATHS = (
    P78_RECEIPT_PATH,
    P79_RECEIPT_PATH,
    CONTINUITY_SPINE_PATH,
    LINEAGE_MAP_PATH,
    P79_PLAN_PATH,
    P80_PLAN_PATH,
    HEALTH_DASHBOARD_PATH,
    STATUS_DOC_PATH,
    "core/generated_artifact_registry.py",
)

REQUIRED_ROUTE_TARGETS = (
    STATUS_DOC_PATH,
    DEFAULT_OUT_PATH,
    P79_RECEIPT_PATH,
    P79_PLAN_PATH,
    P80_PLAN_PATH,
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
                    payload.get("execution_plan_status", "OBSERVED"),
                ),
            )
            row["packet_hash"] = payload.get(
                "canonical_hash", payload.get("packet_hash", "NOT_COMPUTABLE")
            )
    return row


def _route_stage_rows(
    *,
    p78: dict[str, Any],
    p78_status: str,
    p79: dict[str, Any],
    p79_status: str,
) -> list[dict[str, Any]]:
    return [
        {
            "stage": "P78_UPSTREAM_INPUT_REGENERATION_EXECUTION_PLAN",
            "path": P78_RECEIPT_PATH,
            "source_status": p78_status,
            "status": p78.get("execution_plan_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p78.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "P78 keeps the execution-planning lane deterministic while holding every "
                "execution step behind a future authorization surface."
            ),
            "authority_granted": False,
        },
        {
            "stage": "P79_UPSTREAM_INPUT_REGENERATION_AUTHORIZATION_GATE",
            "path": P79_RECEIPT_PATH,
            "source_status": p79_status,
            "status": p79.get("authorization_gate_status", "NOT_COMPUTABLE"),
            "recommended_next_lane": p79.get("recommended_next_lane", "NOT_COMPUTABLE"),
            "why_this_matters": (
                "P79 converts the execution-planning lane into an explicit authorization "
                "review packet without granting authorization, execution, or mutation authority."
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
        "docs/status/TEMPORAL_CONTINUITY_UPSTREAM_EXECUTION_ROUTE.md",
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


def _findings(*, p79: dict[str, Any], p79_status: str) -> list[dict[str, Any]]:
    if p79_status != "OBSERVED":
        return [
            {
                "severity": "HIGH",
                "code": "P79_SOURCE_NOT_COMPUTABLE",
                "detail": (
                    "The authorization-gate packet is missing or unreadable, so downstream "
                    "continuity routing must fail closed."
                ),
                "authority_granted": False,
            }
        ]

    findings: list[dict[str, Any]] = []
    gate_status = p79.get("authorization_gate_status", "NOT_COMPUTABLE")
    if gate_status == "AUTHORIZATION_ELIGIBLE":
        findings.append(
            {
                "severity": "MEDIUM",
                "code": "AUTHORIZATION_ELIGIBLE_BUT_HELD",
                "detail": (
                    "P79 is authorization-eligible, but all authorization, execution, and "
                    "record-creation authority remains false until a future P80+ lane is reviewed."
                ),
                "authority_granted": False,
            }
        )
    eligible_steps = [
        item for item in p79.get("eligible_execution_steps", []) if isinstance(item, dict)
    ]
    if eligible_steps:
        findings.append(
            {
                "severity": "LOW",
                "code": "ELIGIBLE_STEPS_REMAIN_PLANNING_ONLY",
                "detail": (
                    f"P79 carries {len(eligible_steps)} eligible execution-step row(s), all "
                    "tracked as advisory planning evidence only."
                ),
                "authority_granted": False,
            }
        )
    degraded_inputs = [str(item) for item in p79.get("degraded_evidence_inputs", [])]
    if degraded_inputs:
        findings.append(
            {
                "severity": "LOW",
                "code": "DEGRADED_EVIDENCE_INHERITED",
                "detail": (
                    f"P79 inherits {len(degraded_inputs)} degraded evidence input(s); "
                    f"sample: {degraded_inputs[0]}."
                ),
                "authority_granted": False,
            }
        )
    return findings


def build_temporal_upstream_authorization_gate_route_refresh_receipt(
    *,
    repo_root: str | Path,
) -> dict[str, Any]:
    root = Path(repo_root)
    p78, p78_status = _load_json(root / P78_RECEIPT_PATH)
    p79, p79_status = _load_json(root / P79_RECEIPT_PATH)
    spine, spine_status = _load_json(root / CONTINUITY_SPINE_PATH)

    source_status = (
        "OBSERVED"
        if all(status == "OBSERVED" for status in (p78_status, p79_status))
        else "NOT_COMPUTABLE"
    )
    current_route_class = (
        "ACTIVE NAVIGATION" if source_status == "OBSERVED" else "NOT_COMPUTABLE / HELD"
    )
    required_record = p79.get("authorization_required_record", {})
    authorization_required = bool(required_record.get("required", False))
    eligible_steps = [
        item for item in p79.get("eligible_execution_steps", []) if isinstance(item, dict)
    ]
    eligible_commands = [
        item for item in p79.get("eligible_commands", []) if isinstance(item, dict)
    ]
    blocked_actions = list(p79.get("denied_authority", []))

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
        "execution_plan_status": p78.get("execution_plan_status", "NOT_COMPUTABLE"),
        "authorization_gate_status": p79.get(
            "authorization_gate_status", "NOT_COMPUTABLE"
        ),
        "authorization_eligible": bool(p79.get("authorization_eligible", False)),
        "authorization_required_record": authorization_required,
        "source_recommended_next_lane": p79.get(
            "source_recommended_next_lane",
            p78.get("recommended_next_lane", "NOT_COMPUTABLE"),
        ),
        "safe_next_surface": p79.get("recommended_next_lane", "NOT_COMPUTABLE"),
        "recommended_next_engineering_move": (
            "Keep the route advisory-only, preserve the tracked P79 authorization-gate "
            "packet, and use the P80 authorization-record-plan surface as routing only."
        ),
        "eligible_execution_step_count": len(eligible_steps),
        "eligible_command_count": len(eligible_commands),
        "blocked_action_count": len(blocked_actions),
        "blocked_action_sample": blocked_actions[:5],
        "required_record_path": required_record.get(
            "required_record_path", "NOT_COMPUTABLE"
        ),
        "required_record_type": required_record.get(
            "required_record_type", "NOT_COMPUTABLE"
        ),
        "continuity_summary": _continuity_summary(spine, spine_status),
        "route_stage_rows": _route_stage_rows(
            p78=p78,
            p78_status=p78_status,
            p79=p79,
            p79_status=p79_status,
        ),
        "route_target_rows": _route_target_rows(root),
        "findings": _findings(p79=p79, p79_status=p79_status),
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
            "Slice76 complete - Temporal upstream authorization-gate route refresh shipped; "
            "the existing P79 upstream input regeneration authorization gate is now routed "
            "through a contributor-facing status page and receipt, with P80 kept as the next "
            "advisory-only authorization-record-planning surface; no sandbox probe, runtime "
            "activation, canon mutation, MCP exposure, external calls, or autonomous writeback "
            "authorized. Brier Score: 0.10."
        ),
        "validation_plan": [
            "python scripts/temporal/run_temporal_upstream_authorization_gate_route_refresh_receipt.py",
            "python scripts/run_artifact_regeneration.py --artifact out/audit/temporal_upstream_authorization_gate_route_refresh_001.latest.json",
            "python -m py_compile core/temporal_upstream_authorization_gate_route_refresh.py scripts/temporal/run_temporal_upstream_authorization_gate_route_refresh_receipt.py tests/test_temporal_upstream_authorization_gate_route_refresh.py",
            "git diff --check",
        ],
        "provenance": (
            "Notion Sprint 001 Hub + Loop 805 Slice76 + "
            "Hash: temporal_upstream_authorization_gate_route_refresh_001.latest.json"
        ),
    }
    packet["canonical_hash"] = canonical_hash(packet)
    return packet


def write_temporal_upstream_authorization_gate_route_refresh_receipt(
    path: str | Path,
    packet: dict[str, Any],
) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    write_canonical_json(target, packet)
    return target
