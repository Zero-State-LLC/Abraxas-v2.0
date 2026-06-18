from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxResearchCanaryOrphanOutputRegistryPolicyChainClosureReceipt.v1"
RECEIPT_ID = "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_CHAIN_CLOSURE_RECEIPT_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_policy_chain_closure_receipt_001.latest.json"
)
RECEIPT_MD_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_policy_chain_closure_receipt_001.latest.md"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"
DEFAULT_DECISION = "MAINTAIN_EXCLUDE_FROM_CANONICAL_REPAIR"

CHAIN_STEPS: tuple[dict[str, Any], ...] = (
    {
        "step_order": 1,
        "lane_id": "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_REVIEW_001",
        "artifact_path": "out/operator_review/abx_research_canary_orphan_output_registry_policy_review_001.latest.json",
        "id_field": "artifact_id",
    },
    {
        "step_order": 2,
        "lane_id": "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_REQUEST_001",
        "artifact_path": (
            "out/operator_review/"
            "abx_research_canary_orphan_output_registry_policy_operator_decision_request_001.latest.json"
        ),
        "id_field": "artifact_id",
    },
    {
        "step_order": 3,
        "lane_id": "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_RECORD_PLAN_001",
        "artifact_path": (
            "out/operator_review/"
            "abx_research_canary_orphan_output_registry_policy_operator_decision_record_plan_001.latest.json"
        ),
        "id_field": "artifact_id",
    },
    {
        "step_order": 4,
        "lane_id": "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_RECORD_001",
        "artifact_path": (
            "out/operator_review/"
            "abx_research_canary_orphan_output_registry_policy_operator_decision_record_001.latest.json"
        ),
        "id_field": "artifact_id",
    },
)

BLOCKED_ACTIONS = [
    "ORPHAN_OUTPUT_REGISTRY_INCLUSION",
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
    "MERGE_ORPHAN_POLICY_INTO_REPAIR_CHAIN_CLOSURE",
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
    for field in ("status", "chain_closure_status", "receipt_status"):
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
    decision_record = _read_json(
        root
        / "out/operator_review/abx_research_canary_orphan_output_registry_policy_operator_decision_record_001.latest.json"
    )
    repair_chain_closure = _read_json(
        root
        / "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt_001.latest.json"
    )

    decision_ready = (
        decision_record.get("status")
        == "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_OPERATOR_DECISION_RECORD_EMITTED"
        and decision_record.get("selected_decision") == DEFAULT_DECISION
        and decision_record.get("registry_mutation_performed") is False
        and decision_record.get("orphan_count") == 10
    )
    repair_chain_sealed = (
        repair_chain_closure.get("chain_closure_status")
        == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_CHAIN_SEALED"
    )

    if not decision_ready:
        blockers.append("ORPHAN_POLICY_DECISION_RECORD_TERMINAL_STATE_NOT_READY")
    if not repair_chain_sealed:
        blockers.append("REPAIR_CHAIN_CLOSURE_NOT_SEALED")

    summary = {
        "decision_record_ready": decision_ready,
        "repair_chain_sealed": repair_chain_sealed,
        "decision_record_hash": str(decision_record.get("decision_record_hash", NOT_COMPUTABLE)),
        "repair_chain_closure_hash": str(repair_chain_closure.get("receipt_hash", NOT_COMPUTABLE)),
        "orphan_policy_operator_review_hold_reconciled": decision_ready,
    }
    return decision_ready and repair_chain_sealed, blockers, summary


def build_abx_research_canary_orphan_output_registry_policy_chain_closure_receipt(
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
        status = "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_CHAIN_CLOSURE_RECEIPT_BLOCKED"
    else:
        chain_closure_status = "ORPHAN_POLICY_GOVERNANCE_SEALED"
        status = "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_CHAIN_CLOSURE_RECEIPT_EMITTED"

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
        "receipt_id": "abx_research_canary_orphan_output_registry_policy_chain_closure_receipt_001",
        "command": "BUILD_ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_POLICY_CHAIN_CLOSURE_RECEIPT_001",
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
        "closure_posture": "SEALED" if chain_closure_status == "ORPHAN_POLICY_GOVERNANCE_SEALED" else NOT_COMPUTABLE,
        "selected_orphan_policy_decision": DEFAULT_DECISION if terminal_ready else NOT_COMPUTABLE,
        "orphan_count": 10,
        "chain_steps": chain_step_records,
        "chain_steps_ready_count": sum(1 for record in chain_step_records if record["step_ready"]),
        "chain_steps_total_count": len(chain_step_records),
        "terminal_summary": terminal_summary,
        "reconciled_gates": [
            {
                "gate_id": "orphan_policy_operator_review_hold",
                "prior_status": "OPERATOR_HELD",
                "reconciled_status": "SEALED_EXCLUDE_MAINTAINED" if terminal_ready else NOT_COMPUTABLE,
                "source_lane": (
                    "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_REQUEST_001"
                ),
            },
        ],
        "governance_preservation": {
            "p130_hold_preserved": True,
            "orphan_exclusion_preserved": True,
            "research_canary_spine_refresh_performed": False,
            "separate_orphan_registry_governance_required": True,
            "repair_chain_remains_sealed": terminal_summary.get("repair_chain_sealed", False),
        },
        "blocked_actions": list(BLOCKED_ACTIONS),
        "blocked_reasons": blockers,
        "recommended_next_action": (
            "orphan policy governance is sealed; downstream remains NOT_COMPUTABLE unless operator "
            "later authorizes inclusion or archive via separate governed lanes"
            if chain_closure_status == "ORPHAN_POLICY_GOVERNANCE_SEALED"
            else "repair orphan policy chain prerequisites before chain closure"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "downstream_status": NOT_COMPUTABLE,
    }
    return {**packet, "receipt_hash": canonical_hash(packet)}


def render_abx_research_canary_orphan_output_registry_policy_chain_closure_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Research Canary Orphan Output Registry Policy Chain Closure Receipt 001",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `chain_closure_status`: `{packet['chain_closure_status']}`",
        f"- `selected_orphan_policy_decision`: `{packet['selected_orphan_policy_decision']}`",
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
    lines.extend(["", "## Reconciled Gates"])
    for gate in packet.get("reconciled_gates", []):
        if isinstance(gate, dict):
            lines.append(f"- `{gate.get('gate_id')}`: `{gate.get('reconciled_status')}`")
    return lines


def write_abx_research_canary_orphan_output_registry_policy_chain_closure_receipt(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_orphan_output_registry_policy_chain_closure_receipt(root)
    write_canonical_json(target_root / RECEIPT_JSON_PATH, packet)
    _write_markdown(
        target_root / RECEIPT_MD_PATH,
        render_abx_research_canary_orphan_output_registry_policy_chain_closure_receipt_markdown(packet),
    )
    return packet
