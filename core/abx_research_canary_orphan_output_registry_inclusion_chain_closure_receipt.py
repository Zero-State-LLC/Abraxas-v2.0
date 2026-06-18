from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_research_canary_orphan_output_registry_inclusion_constants import ORPHAN_OUTPUT_JSON_PATHS
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxResearchCanaryOrphanOutputRegistryInclusionChainClosureReceipt.v1"
RECEIPT_ID = "ABX_RESEARCH_CANARY_ORPHAN_INCLUSION_CHAIN_CLOSURE_RECEIPT_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_chain_closure_receipt_001.latest.json"
)
RECEIPT_MD_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_chain_closure_receipt_001.latest.md"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"

CHAIN_STEPS: tuple[dict[str, Any], ...] = (
    {
        "step_order": 1,
        "lane_id": "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_OPERATOR_AUTHORIZATION_RECORD_001",
        "artifact_path": (
            "out/operator_review/"
            "abx_research_canary_orphan_output_registry_inclusion_operator_authorization_record_001.latest.json"
        ),
        "id_field": "artifact_id",
    },
    {
        "step_order": 2,
        "lane_id": "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_SPEC_PLAN_001",
        "artifact_path": (
            "out/operator_review/"
            "abx_research_canary_orphan_output_registry_inclusion_execution_spec_plan_001.latest.json"
        ),
        "id_field": "artifact_id",
    },
    {
        "step_order": 3,
        "lane_id": "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_AUTHORIZATION_GATE_001",
        "artifact_path": (
            "out/operator_review/"
            "abx_research_canary_orphan_output_registry_inclusion_execution_authorization_gate_001.latest.json"
        ),
        "id_field": "artifact_id",
    },
    {
        "step_order": 4,
        "lane_id": "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_AUTHORIZATION_RECORD_001",
        "artifact_path": (
            "out/operator_review/"
            "abx_research_canary_orphan_output_registry_inclusion_execution_authorization_record_001.latest.json"
        ),
        "id_field": "artifact_id",
    },
    {
        "step_order": 5,
        "lane_id": "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_SCOPED_EXECUTION_RECEIPT_001",
        "artifact_path": (
            "out/operator_review/"
            "abx_research_canary_orphan_output_registry_inclusion_scoped_execution_receipt_001.latest.json"
        ),
        "id_field": "artifact_id",
    },
    {
        "step_order": 6,
        "lane_id": "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_AUDIT_REGENERATION_RECEIPT_001",
        "artifact_path": (
            "out/operator_review/"
            "abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt_001.latest.json"
        ),
        "id_field": "artifact_id",
        "status_field": "downstream_status",
    },
)

BLOCKED_ACTIONS = [
    "MERGE_INCLUSION_INTO_EXCLUDE_POLICY_CLOSURE",
    "MERGE_INCLUSION_INTO_REPAIR_CHAIN_CLOSURE",
    "RESEARCH_CANARY_SPINE_REFRESH",
    "RESEARCH_CANARY_ARTIFACT_REGENERATION",
    "P130_ACTIVATION",
    "RUNTIME_MUTATION",
    "CANON_MUTATION",
    "QUEUE_MUTATION",
    "SCHEDULER_MUTATION",
    "LIVE_NOTION_WRITEBACK",
    "GITHUB_WRITEBACK_AUTOMATION",
    "UNSCOPED_REGISTRY_REPAIR_EXECUTION",
    "DIRECT_REGISTRY_REPAIR",
    "CHAIN_REOPEN_WITHOUT_OPERATOR_REVIEW",
]


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _observed_status(packet: Mapping[str, Any], *, status_field: str | None) -> str:
    if status_field and isinstance(packet.get(status_field), str):
        return str(packet[status_field])
    for field in ("status", "chain_closure_status", "receipt_status", "downstream_status"):
        value = packet.get(field)
        if isinstance(value, str):
            return value
    for key, value in sorted(packet.items()):
        if "status" in key and isinstance(value, str):
            return value
    return NOT_COMPUTABLE


def _step_record(root: Path, step: Mapping[str, Any]) -> dict[str, Any]:
    artifact_path = str(step["artifact_path"])
    path = root / artifact_path
    packet = _read_json(path) if path.is_file() else {}
    id_field = str(step["id_field"])
    lane_id = str(step["lane_id"])
    observed_id = str(packet.get(id_field, packet.get("artifact_id", NOT_COMPUTABLE)))
    content_hash = canonical_hash(packet) if packet else NOT_COMPUTABLE
    step_ready = path.is_file() and bool(packet) and observed_id == lane_id
    return {
        "step_order": int(step["step_order"]),
        "lane_id": lane_id,
        "artifact_path": artifact_path,
        "observed_status": _observed_status(packet, status_field=step.get("status_field")),
        "content_hash": content_hash,
        "step_ready": step_ready,
    }


def _terminal_invariants(root: Path) -> tuple[bool, list[str], dict[str, Any]]:
    blockers: list[str] = []
    audit_regen = _read_json(
        root
        / "out/operator_review/"
        "abx_research_canary_orphan_output_registry_inclusion_audit_regeneration_receipt_001.latest.json"
    )
    exclude_closure = _read_json(
        root
        / "out/operator_review/"
        "abx_research_canary_orphan_output_registry_policy_chain_closure_receipt_001.latest.json"
    )
    repair_closure = _read_json(
        root
        / "out/operator_review/"
        "abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt_001.latest.json"
    )

    inclusion_complete = audit_regen.get("downstream_status") == "ORPHAN_INCLUSION_CHAIN_COMPLETE"
    exclude_sealed = exclude_closure.get("chain_closure_status") == "ORPHAN_POLICY_GOVERNANCE_SEALED"
    repair_sealed = (
        repair_closure.get("chain_closure_status") == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_CHAIN_SEALED"
    )

    if not inclusion_complete:
        blockers.append("ORPHAN_INCLUSION_AUDIT_REGENERATION_NOT_COMPLETE")
    if not exclude_sealed:
        blockers.append("EXCLUDE_POLICY_CLOSURE_NOT_SEALED")
    if not repair_sealed:
        blockers.append("REPAIR_CHAIN_CLOSURE_NOT_SEALED")

    summary = {
        "inclusion_chain_complete": inclusion_complete,
        "exclude_policy_sealed": exclude_sealed,
        "repair_chain_sealed": repair_sealed,
        "included_orphan_path_count": len(ORPHAN_OUTPUT_JSON_PATHS),
        "audit_regeneration_hash": str(audit_regen.get("receipt_hash", NOT_COMPUTABLE)),
        "exclude_policy_closure_hash": str(exclude_closure.get("receipt_hash", NOT_COMPUTABLE)),
        "repair_chain_closure_hash": str(repair_closure.get("receipt_hash", NOT_COMPUTABLE)),
    }
    return inclusion_complete and exclude_sealed and repair_sealed, blockers, summary


def build_abx_research_canary_orphan_output_registry_inclusion_chain_closure_receipt(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    chain_step_records = sorted(
        [_step_record(root, step) for step in CHAIN_STEPS],
        key=lambda record: record["step_order"],
    )
    terminal_ready, terminal_blockers, terminal_summary = _terminal_invariants(root)
    missing_steps = [record["lane_id"] for record in chain_step_records if not record["step_ready"]]

    if not terminal_ready or missing_steps:
        chain_closure_status = NOT_COMPUTABLE
        status = "ABX_RESEARCH_CANARY_ORPHAN_INCLUSION_CHAIN_CLOSURE_RECEIPT_BLOCKED"
    else:
        chain_closure_status = "ORPHAN_INCLUSION_GOVERNANCE_SEALED"
        status = "ABX_RESEARCH_CANARY_ORPHAN_INCLUSION_CHAIN_CLOSURE_RECEIPT_EMITTED"

    blockers = sorted(
        {
            *terminal_blockers,
            *[f"CHAIN_STEP_MISSING:{lane_id}" for lane_id in missing_steps],
        }
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": RECEIPT_ID,
        "status": status,
        "receipt_id": "abx_research_canary_orphan_output_registry_inclusion_chain_closure_receipt_001",
        "command": "BUILD_ABX_RESEARCH_CANARY_ORPHAN_INCLUSION_CHAIN_CLOSURE_RECEIPT_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "registry_mutation_allowed": False,
        "registry_mutation_performed": False,
        "implementation_authorized": False,
        "safe_to_auto_continue": False,
        "chain_closure_status": chain_closure_status,
        "closure_posture": "SEALED" if chain_closure_status == "ORPHAN_INCLUSION_GOVERNANCE_SEALED" else NOT_COMPUTABLE,
        "included_orphan_path_count": len(ORPHAN_OUTPUT_JSON_PATHS),
        "chain_steps": chain_step_records,
        "chain_steps_ready_count": sum(1 for record in chain_step_records if record["step_ready"]),
        "chain_steps_total_count": len(chain_step_records),
        "terminal_summary": terminal_summary,
        "governance_preservation": {
            "p130_hold_preserved": True,
            "exclude_policy_remains_sealed": terminal_summary.get("exclude_policy_sealed", False),
            "repair_chain_remains_sealed": terminal_summary.get("repair_chain_sealed", False),
            "research_canary_spine_refresh_performed": False,
            "separate_from_exclude_policy_closure": True,
        },
        "blocked_actions": list(BLOCKED_ACTIONS),
        "blocked_reasons": blockers,
        "recommended_next_action": (
            "orphan inclusion governance is sealed separately from exclude policy; downstream remains NOT_COMPUTABLE"
            if chain_closure_status == "ORPHAN_INCLUSION_GOVERNANCE_SEALED"
            else "repair orphan inclusion chain prerequisites before chain closure"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "downstream_status": NOT_COMPUTABLE,
    }
    return {**packet, "receipt_hash": canonical_hash(packet)}


def render_markdown(packet: Mapping[str, Any]) -> list[str]:
    lines = [
        "# ABX Research Canary Orphan Output Registry Inclusion Chain Closure Receipt 001",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `chain_closure_status`: `{packet['chain_closure_status']}`",
        f"- `included_orphan_path_count`: `{packet['included_orphan_path_count']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        "",
        "## Chain Steps",
    ]
    for step in packet.get("chain_steps", []):
        if isinstance(step, dict):
            lines.append(
                f"- `{step.get('lane_id')}`: ready=`{step.get('step_ready')}` "
                f"status=`{step.get('observed_status')}`"
            )
    return lines


def write_abx_research_canary_orphan_output_registry_inclusion_chain_closure_receipt(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_orphan_output_registry_inclusion_chain_closure_receipt(root)
    write_canonical_json(target_root / RECEIPT_JSON_PATH, packet)
    _write_markdown(target_root / RECEIPT_MD_PATH, render_markdown(packet))
    return packet
