from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_operator_authorization_evidence_request_plan import (
    PLAN_JSON_PATH as SOURCE_EVIDENCE_REQUEST_PLAN_JSON,
)

SCHEMA_VERSION = "V2HygieneOperatorAuthorizationEvidenceDryRun.v1"
DRY_RUN_ID = "v2_hygiene_operator_authorization_evidence_dry_run_001"
DRY_RUN_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_operator_authorization_evidence_dry_run_001.latest.json"
)
DRY_RUN_MD_PATH = DRY_RUN_JSON_PATH.with_suffix(".md")
NOT_COMPUTABLE = "NOT_COMPUTABLE"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _authority_locks() -> dict[str, bool]:
    return {
        "activation": False,
        "authorization_record_creation": False,
        "auto_approval": False,
        "auto_continuation": False,
        "auto_patch_generation": False,
        "canon_mutation": False,
        "decision_record_creation": False,
        "evidence_bundle_creation": False,
        "execution_authority": False,
        "forecast_routing": False,
        "github_writeback": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_evidence_collection": False,
        "projection_surface_mutation": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_mutation": False,
        "strict_mode_enablement": False,
        "token_minting": False,
        "v2_module_registration": False,
    }


def _simulated_evidence_bundle(
    evidence_groups: list[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    bundle: list[dict[str, Any]] = []
    for group in evidence_groups:
        required_fields = [
            str(item) for item in group.get("required_fields", []) if isinstance(item, str)
        ]
        bundle.append(
            {
                "group_id": str(group.get("group_id", NOT_COMPUTABLE)),
                "attested": False,
                "field_count": len(required_fields),
                "missing_fields": required_fields,
            }
        )
    return bundle


def _evaluation_blockers(groups: list[Mapping[str, Any]]) -> list[str]:
    group_ids = [str(group.get("group_id", "")) for group in groups]
    blocker_map = {
        "operator_identity": "operator_identity_not_attested",
        "review_acknowledgements": "review_acknowledgements_not_attested",
        "provenance_evidence": "operator_provenance_evidence_not_attested",
        "workstream_disposition": "workstream_disposition_not_attested",
        "evidence_request_outputs": "operator_evidence_outputs_not_attested",
    }
    return [blocker_map[group_id] for group_id in group_ids if group_id in blocker_map]


def build_v2_hygiene_operator_authorization_evidence_dry_run(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    plan = _read_json(root / SOURCE_EVIDENCE_REQUEST_PLAN_JSON)
    plan_observed = plan is not None
    plan = plan or {}
    source_ready = (
        plan.get("schema_version")
        == "V2HygieneOperatorAuthorizationEvidenceRequestPlan.v1"
        and plan.get("status")
        == "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_REQUEST_PLAN_READY"
        and plan.get("evidence_request_only") is True
        and plan.get("operator_input_required") is True
        and plan.get("authorization_record_created") is False
        and plan.get("authorization_record_creation_authorized") is False
        and plan.get("implementation_authorized") is False
        and plan.get("valid_for_execution") is False
        and plan.get("valid_for_implementation") is False
        and plan.get("safe_to_auto_continue") is False
    )
    evidence_groups = [
        group
        for group in plan.get("evidence_bundle_groups", [])
        if isinstance(group, Mapping)
    ]
    simulated_bundle = _simulated_evidence_bundle(evidence_groups)
    evaluation_blockers = (
        _evaluation_blockers(evidence_groups)
        if source_ready
        else [
            "source_v2_hygiene_operator_authorization_evidence_request_plan_not_ready",
            f"source_path:{SOURCE_EVIDENCE_REQUEST_PLAN_JSON}",
        ]
    )
    groups_total = len(simulated_bundle)

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_DRY_RUN_READY"
            if source_ready
            else "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_DRY_RUN_BLOCKED"
        ),
        "dry_run_id": DRY_RUN_ID,
        "dry_run_hash": "",
        "source_evidence_request_plan_path": str(SOURCE_EVIDENCE_REQUEST_PLAN_JSON),
        "source_evidence_request_plan_observed": plan_observed,
        "source_evidence_request_plan_ready": source_ready,
        "source_evidence_request_plan_hash": str(plan.get("plan_hash", NOT_COMPUTABLE)),
        "source_gate_path": str(plan.get("source_gate_path", NOT_COMPUTABLE)),
        "source_gate_hash": str(plan.get("source_gate_hash", NOT_COMPUTABLE)),
        "source_review_artifacts": [
            str(item) for item in plan.get("required_review_artifacts", [])
        ],
        "simulated_only": True,
        "operator_input_required": True,
        "operator_attestations_present": False,
        "operator_evidence_bundle_created": False,
        "authorization_record_created": False,
        "authorization_record_creation_authorized": False,
        "implementation_authorized": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "projection_surface_mutation_authorized": False,
        "schema_mutation_authorized": False,
        "execution_authority": False,
        "valid_for_authorization_record": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_prepare_patch": False,
        "safe_to_auto_continue": False,
        "recommended_next_action": (
            "preserve the v2 hygiene operator authorization hold and use this "
            "simulated evidence bundle to guide external operator evidence collection; "
            "do not create evidence, attestations, authorization records, module/rune "
            "registrations, implementation patches, writeback, or execution"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_state": "hold",
        "simulated_evidence_bundle": simulated_bundle,
        "readiness_summary": {
            "simulated_only": True,
            "operator_input_required": True,
            "groups_ready": 0,
            "groups_total": groups_total,
            "evidence_bundle_complete": False,
            "valid_for_authorization_record": False,
            "evaluation_blockers": evaluation_blockers,
        },
        "evaluation_blockers": evaluation_blockers,
        "disallowed_follow_on_actions": [
            "OPERATOR_ATTESTATION_CREATION",
            "OPERATOR_EVIDENCE_BUNDLE_CREATION",
            "AUTHORIZATION_RECORD_CREATION",
            "V2_MODULE_REGISTRATION",
            "RUNE_REGISTRATION",
            "PROJECTION_SURFACE_MUTATION",
            "SCHEMA_MUTATION",
            "AUTO_APPROVAL",
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
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "authority_locks": _authority_locks(),
    }
    packet_without_hash = dict(packet)
    packet_without_hash.pop("dry_run_hash")
    packet["dry_run_hash"] = canonical_hash(packet_without_hash)
    return packet


def render_v2_hygiene_operator_authorization_evidence_dry_run_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Operator Authorization Evidence Dry Run",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `source_evidence_request_plan_ready`: `{packet['source_evidence_request_plan_ready']}`",
        f"- `recommended_next_state`: `{packet['recommended_next_state']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        f"- `operator_attestations_present`: `{packet['operator_attestations_present']}`",
        f"- `valid_for_authorization_record`: `{packet['valid_for_authorization_record']}`",
        f"- `valid_for_execution`: `{packet['valid_for_execution']}`",
        "",
        "## Evaluation Blockers",
        "",
    ]
    for item in packet["evaluation_blockers"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Simulated Evidence Bundle", ""])
    for item in packet["simulated_evidence_bundle"]:
        lines.append(f"- `{item['group_id']}`: `{item['field_count']}` missing fields")
    return lines


def write_v2_hygiene_operator_authorization_evidence_dry_run(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = root if out_root is None else Path(out_root)
    packet = build_v2_hygiene_operator_authorization_evidence_dry_run(root)
    write_canonical_json(target_root / DRY_RUN_JSON_PATH, packet)
    _write_markdown(
        target_root / DRY_RUN_MD_PATH,
        render_v2_hygiene_operator_authorization_evidence_dry_run_markdown(packet),
    )
    return packet
