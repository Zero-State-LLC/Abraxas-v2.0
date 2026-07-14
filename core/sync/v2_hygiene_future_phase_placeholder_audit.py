from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase2_module_skeleton_backlog_plan import (
    PLAN_JSON_PATH as SOURCE_PHASE2_BACKLOG_JSON,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygieneFuturePhasePlaceholderAudit.v1"
AUDIT_ID = "v2_hygiene_future_phase_placeholder_audit_001"
AUDIT_JSON_PATH = Path("out/sync/v2_hygiene_future_phase_placeholder_audit/latest.json")
AUDIT_MD_PATH = AUDIT_JSON_PATH.with_suffix(".md")

SOURCE_OPERATOR_GATE_JSON = (
    "out/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate_001.latest.json"
)
NOTION_FUTURE_PHASE_SOURCES: tuple[dict[str, str], ...] = (
    {
        "phase_id": "phase3",
        "page_id": "37e3e8ba-2f5c-8170-b132-d06f5c8f0acd",
        "title": "Phase 3: Output Surface Integration",
        "goal": (
            "Carefully roll out three-register discipline and loop awareness behind "
            "feature flags."
        ),
        "notion_status": "Placeholder",
        "source_observed_at": "2026-06-13T16:22:47Z",
    },
    {
        "phase_id": "phase4",
        "page_id": "37e3e8ba-2f5c-81a7-a55b-da585d0fe220",
        "title": "Phase 4: Full Integration & Promotion",
        "goal": (
            "Deep integration and promotion workflow for moving components out of "
            "advisory mode."
        ),
        "notion_status": "Placeholder",
        "source_observed_at": "2026-06-13T16:22:47Z",
    },
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _hash_source(path: Path) -> str:
    value = _read_json(path)
    return canonical_hash(value) if value else NOT_COMPUTABLE


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _notion_source_records() -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for source in NOTION_FUTURE_PHASE_SOURCES:
        record = dict(source)
        record["source_hash"] = canonical_hash(source)
        records.append(record)
    return records


def _phase_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for source in NOTION_FUTURE_PHASE_SOURCES:
        records.append(
            {
                "phase_id": source["phase_id"],
                "page_id": source["page_id"],
                "title": source["title"],
                "goal": source["goal"],
                "notion_status": source["notion_status"],
                "repo_audit_status": "PLACEHOLDER_CONFIRMED_HELD_FOR_NOTION_SPEC",
                "spec_detail_ready": False,
                "backlog_ready": False,
                "implementation_authorized": False,
                "execution_authority": False,
                "operator_authorization_required": True,
            }
        )
    return records


def _authority_locks() -> dict[str, bool]:
    return {
        "activation": False,
        "auto_continuation": False,
        "auto_patch_generation": False,
        "canon_mutation": False,
        "execution_authority": False,
        "feature_flag_rollout": False,
        "full_integration": False,
        "github_writeback": False,
        "implementation_authorization": False,
        "loop_awareness_activation": False,
        "module_promotion": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_authorization_record_creation": False,
        "phase3_output_surface_integration": False,
        "phase4_full_integration_promotion": False,
        "projection_surface_mutation": False,
        "promotion_workflow_activation": False,
        "queue_mutation": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_mutation": False,
        "strict_mode_enablement": False,
        "three_register_activation": False,
        "token_minting": False,
    }


def build_v2_hygiene_future_phase_placeholder_audit(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    source_paths = {
        "phase2_module_skeleton_backlog_plan": str(SOURCE_PHASE2_BACKLOG_JSON),
        "operator_authorization_gate": SOURCE_OPERATOR_GATE_JSON,
    }
    source_packets = {key: _read_json(root / path) for key, path in source_paths.items()}
    phase2 = source_packets["phase2_module_skeleton_backlog_plan"] or {}
    gate = source_packets["operator_authorization_gate"] or {}
    source_ready = (
        phase2.get("status")
        == "V2_HYGIENE_PHASE2_MODULE_SKELETON_BACKLOG_PLAN_READY"
        and phase2.get("phase3_status") == "PLACEHOLDER_HELD_FOR_FUTURE_DETAIL"
        and phase2.get("phase4_status") == "PLACEHOLDER_HELD_FOR_FUTURE_DETAIL"
        and gate.get("authorization_granted") is False
        and gate.get("valid_for_implementation") is False
    )
    phase_records = _phase_records()
    blocked_phase_count = sum(
        1 for phase in phase_records if phase["implementation_authorized"] is False
    )
    blockers = [] if source_ready else ["v2_hygiene_future_phase_sources_not_ready"]

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "V2_HYGIENE_FUTURE_PHASE_PLACEHOLDER_AUDIT_READY"
            if source_ready
            else "V2_HYGIENE_FUTURE_PHASE_PLACEHOLDER_AUDIT_BLOCKED"
        ),
        "audit_id": AUDIT_ID,
        "audit_hash": "",
        "source_paths": source_paths,
        "source_hashes": {
            key: _hash_source(root / path) for key, path in source_paths.items()
        },
        "source_ready": source_ready,
        "notion_future_phase_sources": _notion_source_records(),
        "phase_records": phase_records,
        "placeholder_summary": {
            "future_phase_count": len(phase_records),
            "placeholder_phase_count": sum(
                1 for phase in phase_records if phase["notion_status"] == "Placeholder"
            ),
            "blocked_phase_count": blocked_phase_count,
            "backlog_ready_count": sum(
                1 for phase in phase_records if phase["backlog_ready"] is True
            ),
            "spec_detail_ready_count": sum(
                1 for phase in phase_records if phase["spec_detail_ready"] is True
            ),
        },
        "acceptance_gate_summary": {
            "phase2_backlog_ready": source_ready,
            "operator_authorization_required": True,
            "operator_authorization_observed": False,
            "safe_to_prepare_phase3_backlog": False,
            "safe_to_prepare_phase4_backlog": False,
            "safe_to_integrate_output_surface": False,
            "safe_to_activate_feature_flags": False,
            "safe_to_promote_components": False,
        },
        "recommended_next_action": (
            "hold Phase 3 and Phase 4 as Notion placeholders until expanded specs "
            "and explicit external operator authorization permit separate backlog lanes"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "implementation_authorized": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_prepare_patch": False,
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "authority_locks": _authority_locks(),
        "blockers": blockers,
    }
    packet_without_hash = dict(packet)
    packet_without_hash.pop("audit_hash")
    packet["audit_hash"] = canonical_hash(packet_without_hash)
    return packet


def render_v2_hygiene_future_phase_placeholder_audit_markdown(
    packet: dict[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Future Phase Placeholder Audit",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `source_ready`: `{packet['source_ready']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        f"- `implementation_authorized`: `{packet['implementation_authorized']}`",
        f"- `valid_for_execution`: `{packet['valid_for_execution']}`",
        "",
        "## Placeholder Summary",
        "",
    ]
    for key, value in packet["placeholder_summary"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Future Phases", ""])
    for phase in packet["phase_records"]:
        lines.append(
            f"- `{phase['phase_id']}` {phase['title']}: "
            f"`{phase['repo_audit_status']}`"
        )
    lines.extend(["", "## Authority Locks", ""])
    for key, value in packet["authority_locks"].items():
        lines.append(f"- `{key}`: `{value}`")
    return lines


def write_v2_hygiene_future_phase_placeholder_audit(
    source_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    packet = build_v2_hygiene_future_phase_placeholder_audit(root)
    target_root = root if out_root is None else Path(out_root)
    json_path = target_root / AUDIT_JSON_PATH
    md_path = target_root / AUDIT_MD_PATH
    write_canonical_json(json_path, packet)
    _write_markdown(
        md_path,
        render_v2_hygiene_future_phase_placeholder_audit_markdown(packet),
    )
    return packet
