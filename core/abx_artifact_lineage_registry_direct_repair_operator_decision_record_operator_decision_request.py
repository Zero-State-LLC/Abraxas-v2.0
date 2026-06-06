from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

SCHEMA_VERSION = "AbxArtifactLineageRegistryDirectRepairOperatorDecisionRecordOperatorDecisionRequest.v1"
JSON_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_operator_decision_request_001.latest.json"
)
MD_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_operator_decision_request_001.latest.md"
)

COMPLETION_HOLD_PLAN_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan_001.latest.json"
)

DECISION_OPTIONS = [
    "HOLD",
    "AUTHORIZE_SEPARATE_DIRECT_REPAIR_EXECUTION_SPEC",
    "REQUEST_EXTERNAL_EVIDENCE",
    "REJECT_DIRECT_REPAIR_EXECUTION",
]


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_hash(data: Mapping[str, Any], field_name: str) -> str:
    payload = dict(data)
    payload.pop(field_name, None)
    return _sha256_text(_canonical_json(payload))


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json_and_markdown(
    json_path: Path,
    md_path: Path,
    packet: Mapping[str, Any],
    markdown_lines: list[str],
) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(_canonical_json(packet) + "\n", encoding="utf-8")
    md_path.write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")


def build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_operator_decision_request(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    completion_hold_plan = _read_json(root / COMPLETION_HOLD_PLAN_PATH)

    completion_hold_ready = (
        completion_hold_plan.get("schema_version")
        == "AbxArtifactLineageRegistryDirectRepairOperatorDecisionRecordCompletionHoldPlan.v1"
        and completion_hold_plan.get("completion_hold_plan_id")
        == "abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan_001"
        and completion_hold_plan.get("status")
        == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_COMPLETION_HOLD_PLAN_EMITTED"
    )
    validation_passed = bool(completion_hold_plan.get("validation_passed", False))

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_OPERATOR_DECISION_REQUEST_EMITTED",
        "request_id": "",
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_OPERATOR_DECISION_REQUEST_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "promotion_allowed": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "decision_scope": "DIRECT_REPAIR_EXECUTION_DECISION_REQUIRED",
        "decision_question": (
            "Should Abraxas authorize a separate governed execution spec for repo-local direct lineage repairs "
            "after the operator-decision-record subchain reached its explicit completion hold boundary?"
        ),
        "target_surface": "ABX Artifact Lineage Registry Direct Repair",
        "target_plan_id": completion_hold_plan.get("completion_hold_plan_id", "NOT_COMPUTABLE"),
        "source_completion_hold_path": COMPLETION_HOLD_PLAN_PATH.as_posix(),
        "priority": "P0",
        "queue_action": "HOLD_FOR_GOVERNED_OPERATOR_DECISION",
        "completion_hold_ready": completion_hold_ready,
        "validation_passed": validation_passed,
        "implementation_authorized": False,
        "spec_authoring_only_if_approved": True,
        "safe_to_auto_continue": False,
        "safe_to_prepare_planning_pr": False,
        "decision_options": DECISION_OPTIONS,
        "recommended_decision": "HOLD",
        "recommended_next_action": (
            "review the operator-decision-record completion hold plan, confirm the unresolved hold reasons, and collect explicit operator decision evidence before any separate direct-repair execution spec can exist"
            if completion_hold_ready and validation_passed
            else "repair the operator-decision-record completion-hold-plan prerequisites before any operator decision can be considered"
        ),
        "required_operator_actions": [
            "review_operator_decision_record_completion_hold_plan",
            "confirm_final_operator_decision_record_is_missing",
            "review_runner_casing_policy_hold",
            "review_notion_mapping_evidence_gap",
            "collect_operator_decision_record_chain_operator_decision",
            "record_operator_decision_record_chain_operator_decision",
        ],
        "required_evidence": list(completion_hold_plan.get("unresolved_hold_reasons", [])),
        "blocked_actions": list(completion_hold_plan.get("blocked_actions", [])),
        "acceptance_gates": [
            {
                "gate_id": "operator_decision_record_chain_operator_decision_required",
                "required_before": "any direct repair execution spec or repo-local repair mutation",
                "status": "PENDING_OPERATOR_DECISION",
            },
            {
                "gate_id": "runner_casing_policy_external_hold",
                "required_before": "any script casing normalization claim",
                "status": "OPERATOR_HELD",
            },
            {
                "gate_id": "notion_mapping_evidence_external_hold",
                "required_before": "any Notion completeness claim",
                "status": "NOT_COMPUTABLE",
            },
        ],
        "decision_record_plan_candidates": [
            "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan_001.latest.json",
            "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan_001.latest.md",
        ],
        "follow_on_actions_if_approved": [
            "AUTHOR_SEPARATE_DIRECT_REPAIR_EXECUTION_SPEC",
            "OPEN_SEPARATE_DIRECT_REPAIR_EXECUTION_PR",
        ],
        "follow_on_actions_if_held": [
            "MAINTAIN_COMPLETION_HOLD",
            "MAINTAIN_EXECUTION_DENIAL",
            "WAIT_FOR_EXPLICIT_OPERATOR_DECISION_EVIDENCE",
        ],
        "follow_on_actions_if_rejected": [
            "SEAL_DIRECT_REPAIR_CHAIN_AS_ADVISORY_ONLY",
            "DO_NOT_PREPARE_EXECUTION_SPEC",
        ],
        "follow_on_actions_if_external_evidence_requested": [
            "REQUEST_NOTION_MAPPING_EVIDENCE",
            "REQUEST_RUNNER_CASING_POLICY_DECISION",
        ],
        "blocked_reasons": list(completion_hold_plan.get("unresolved_hold_reasons", [])),
        "source_hashes": {
            "operator_decision_record_completion_hold_plan": completion_hold_plan.get(
                "completion_hold_plan_hash", ""
            ),
        },
    }
    packet["request_id"] = _canonical_hash(packet, "request_id")
    return packet


def render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_operator_decision_request_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    return [
        "# ABX Artifact Lineage Registry Direct Repair Operator Decision Record Operator Decision Request",
        "",
        f"- `request_id`: `{packet['request_id']}`",
        f"- `status`: `{packet['status']}`",
        f"- `decision_scope`: `{packet['decision_scope']}`",
        f"- `recommended_decision`: `{packet['recommended_decision']}`",
        f"- `recommended_next_action`: `{packet['recommended_next_action']}`",
        "",
        "## Blocked Reasons",
        *[f"- `{reason}`" for reason in packet["blocked_reasons"]],
    ]


def write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_operator_decision_request(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_operator_decision_request(
        source_root
    )
    markdown = render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_operator_decision_request_markdown(
        packet
    )
    _write_json_and_markdown(JSON_PATH, MD_PATH, packet, markdown)
    return packet
