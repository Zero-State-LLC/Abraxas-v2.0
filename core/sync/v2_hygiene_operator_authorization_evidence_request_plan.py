from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_loop_awareness_operator_authorization_gate import (
    OUT_JSON as SOURCE_OPERATOR_GATE_JSON,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygieneOperatorAuthorizationEvidenceRequestPlan.v1"
PLAN_ID = "v2_hygiene_operator_authorization_evidence_request_plan_001"
PLAN_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_operator_authorization_evidence_request_plan_001.latest.json"
)
PLAN_MD_PATH = PLAN_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = "V2_HYGIENE_LOOP_AWARENESS_OPERATOR_AUTHORIZATION_GATE_HELD_FOR_OPERATOR"

NOTION_V2_SOURCES: tuple[dict[str, str], ...] = (
    {
        "page_id": "37e3e8ba-2f5c-811a-96f9-cdd0cc09bf7f",
        "title": "v2.0 Implementation Surfaces",
        "status": "HUB_NAVIGATION_SURFACE",
        "source_observed_at": "2026-06-13T16:43:43Z",
    },
    {
        "page_id": "37e3e8ba-2f5c-811e-93f1-c45ad28f5057",
        "title": "Abraxas v2.0 Core Directive",
        "status": "CANON_ACTIVE_V2_EVOLUTION",
        "source_observed_at": "2026-06-13T04:41:16Z",
    },
    {
        "page_id": "37e3e8ba-2f5c-81b0-8bd9-fe40510f2af3",
        "title": "Phase 1: Foundations & Hygiene Layer",
        "status": "READY_FOR_WORK",
        "source_observed_at": "2026-06-13T16:41:00Z",
    },
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _field_plan(group_id: str, fields: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "step_id": f"{group_id}_{idx:03d}",
            "field": field,
            "required": True,
        }
        for idx, field in enumerate(fields, start=1)
    ]


def _source_records() -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for source in NOTION_V2_SOURCES:
        record = dict(source)
        record["source_hash"] = canonical_hash(source)
        records.append(record)
    return records


def _authority_locks() -> dict[str, bool]:
    return {
        "auto_continuation": False,
        "auto_patch_generation": False,
        "authorization_record_creation": False,
        "canon_mutation": False,
        "execution_authority": False,
        "forecast_routing": False,
        "github_writeback": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_authorization_record_creation": False,
        "projection_surface_mutation": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_mutation": False,
        "token_minting": False,
        "v2_module_registration": False,
    }


def build_v2_hygiene_operator_authorization_evidence_request_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    gate = _read_json(root / SOURCE_OPERATOR_GATE_JSON)
    gate_observed = gate is not None
    gate = gate or {}
    required_fields = [
        str(field)
        for field in gate.get("required_operator_authorization_fields", [])
        if isinstance(field, str)
    ]
    allowed_decisions = [
        str(decision)
        for decision in gate.get("allowed_operator_decisions", [])
        if isinstance(decision, str)
    ]

    source_ready = (
        gate.get("artifact_type") == "V2HygieneLoopAwarenessOperatorAuthorizationGate.v1"
        and gate.get("gate_status") == EXPECTED_SOURCE_STATUS
        and gate.get("authorization_eligible") is True
        and gate.get("requires_operator_decision") is True
        and gate.get("selected_operator_decision") == "HOLD"
        and gate.get("recommended_next_lane") == NOT_COMPUTABLE
        and gate.get("recommended_next_patch") == NOT_COMPUTABLE
        and gate.get("authorization_granted") is False
        and gate.get("operator_authorization_record_created") is False
        and gate.get("valid_for_execution") is False
        and gate.get("valid_for_implementation") is False
        and gate.get("safe_to_prepare_patch") is False
        and gate.get("safe_to_auto_continue") is False
        and bool(required_fields)
    )

    blockers = [] if source_ready else ["source_v2_operator_authorization_gate_not_ready"]
    if not gate_observed:
        blockers = [
            "source_v2_operator_authorization_gate_missing_or_unreadable",
            f"source_path:{SOURCE_OPERATOR_GATE_JSON}",
        ]

    operator_identity_fields = [
        field
        for field in required_fields
        if field in {"operator_id", "operator_name", "operator_role", "authorization_timestamp_utc"}
    ]
    review_acknowledgement_fields = [
        field
        for field in required_fields
        if field
        in {
            "authorization_scope_acknowledged",
            "authority_boundary_acknowledged",
            "no_auto_continuation_acknowledged",
        }
    ]
    provenance_fields = [
        field for field in required_fields if field == "reviewed_alignment_plan_hash"
    ]
    workstream_fields = [
        field
        for field in required_fields
        if field in {"approved_workstreams", "denied_workstreams"}
    ]
    output_fields = [
        "operator_authorization_evidence_request_id",
        "operator_authorization_evidence_request_hash",
        "terminal_authority_summary",
    ]

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_REQUEST_PLAN_READY"
            if source_ready
            else "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_REQUEST_PLAN_BLOCKED"
        ),
        "plan_id": PLAN_ID,
        "plan_hash": "",
        "source_gate_path": str(SOURCE_OPERATOR_GATE_JSON),
        "source_gate_hash": str(gate.get("gate_hash", NOT_COMPUTABLE)),
        "source_gate_ready": source_ready,
        "notion_v2_sources": _source_records(),
        "evidence_request_only": True,
        "operator_input_required": True,
        "recommended_default_decision": "HOLD",
        "allowed_operator_decisions": allowed_decisions,
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_action": (
            "collect explicit external operator authorization evidence for the v2 hygiene "
            "operator gate; do not register modules or runes, mutate schemas or projections, "
            "create authorization records, write back to Notion/GitHub, or execute runtime work"
        ),
        "safe_to_auto_continue": False,
        "safe_to_prepare_patch": False,
        "authorization_record_created": False,
        "authorization_record_creation_authorized": False,
        "implementation_authorized": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "projection_surface_mutation_authorized": False,
        "schema_mutation_authorized": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "evidence_bundle_groups": [
            {
                "group_id": "operator_identity",
                "required_fields": operator_identity_fields,
                "collection_steps": _field_plan("operator_identity", operator_identity_fields),
            },
            {
                "group_id": "review_acknowledgements",
                "required_fields": review_acknowledgement_fields,
                "collection_steps": _field_plan(
                    "review_acknowledgement",
                    review_acknowledgement_fields,
                ),
            },
            {
                "group_id": "provenance_evidence",
                "required_fields": provenance_fields,
                "collection_steps": _field_plan("provenance", provenance_fields),
            },
            {
                "group_id": "workstream_disposition",
                "required_fields": workstream_fields,
                "collection_steps": _field_plan("workstream", workstream_fields),
            },
            {
                "group_id": "evidence_request_outputs",
                "required_fields": output_fields,
                "collection_steps": _field_plan("output", output_fields),
            },
        ],
        "required_review_artifacts": [
            str(SOURCE_OPERATOR_GATE_JSON),
            "out/sync/v2_hygiene_loop_awareness_alignment_plan/latest.json",
            "out/sync/v2_hygiene_registration_readiness_audit/latest.json",
            "out/sync/v2_upgrade_completion_reconciliation/latest.json",
        ],
        "future_evidence_output_candidates": [
            "out/operator_review/v2_hygiene_operator_authorization_evidence_bundle_001.latest.json",
            "out/operator_review/v2_hygiene_operator_authorization_evidence_bundle_001.latest.md",
        ],
        "future_record_output_candidates": [
            "out/operator_review/v2_hygiene_operator_authorization_record_001.latest.json",
            "out/operator_review/v2_hygiene_operator_authorization_record_001.latest.md",
        ],
        "disallowed_follow_on_actions": [
            "AUTHORIZATION_RECORD_CREATION",
            "OPERATOR_ATTESTATION_CREATION",
            "OPERATOR_EVIDENCE_BUNDLE_CREATION",
            "V2_MODULE_REGISTRATION",
            "RUNE_REGISTRATION",
            "PROJECTION_SURFACE_MUTATION",
            "SCHEMA_MUTATION",
            "AUTO_PATCH_GENERATION",
            "AUTO_CONTINUATION",
            "NOTION_WRITEBACK",
            "GITHUB_WRITEBACK",
            "RUNTIME_MUTATION",
            "CANON_MUTATION",
            "QUEUE_MUTATION",
            "SCHEDULER_MUTATION",
            "FORECAST_ROUTING",
            "TOKEN_MINTING",
            "ACTIVATION",
            "EXECUTION",
        ],
        "evidence_readiness_summary": {
            "source_gate_observed": gate_observed,
            "source_gate_ready": source_ready,
            "required_group_count": 5,
            "required_operator_field_count": len(required_fields),
            "blocker_count": len(blockers),
        },
        "blockers": blockers,
        "authority_locks": _authority_locks(),
    }
    packet["plan_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "plan_hash"}
    )
    return packet


def render_v2_hygiene_operator_authorization_evidence_request_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Operator Authorization Evidence Request Plan",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `source_gate_ready`: `{packet['source_gate_ready']}`",
        f"- `recommended_default_decision`: `{packet['recommended_default_decision']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        f"- `authorization_record_created`: `{packet['authorization_record_created']}`",
        f"- `implementation_authorized`: `{packet['implementation_authorized']}`",
        "",
        "## Required Review Artifacts",
        "",
    ]
    for item in packet["required_review_artifacts"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Evidence Bundle Groups", ""])
    for group in packet["evidence_bundle_groups"]:
        lines.append(f"- `{group['group_id']}`")
        for field in group["required_fields"]:
            lines.append(f"  - `{field}`")
    lines.extend(["", "## Disallowed Follow-On Actions", ""])
    for action in packet["disallowed_follow_on_actions"]:
        lines.append(f"- `{action}`")
    if packet["blockers"]:
        lines.extend(["", "## Blockers", ""])
        for blocker in packet["blockers"]:
            lines.append(f"- `{blocker}`")
    return lines


def write_v2_hygiene_operator_authorization_evidence_request_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_v2_hygiene_operator_authorization_evidence_request_plan(root)
    write_canonical_json(target_root / PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / PLAN_MD_PATH,
        render_v2_hygiene_operator_authorization_evidence_request_plan_markdown(packet),
    )
    return packet
