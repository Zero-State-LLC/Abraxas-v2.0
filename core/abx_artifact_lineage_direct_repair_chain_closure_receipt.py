from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_artifact_lineage_direct_repair_frontier_revalidation import (
    ARTIFACT_LINEAGE_DIRECT_REPAIR_CHAIN_COMPLETE,
    TRACEABILITY_REGEN_RECEIPT_PATH,
)
from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "AbxArtifactLineageDirectRepairChainClosureReceipt.v1"
RECEIPT_ID = "ABX_ARTIFACT_LINEAGE_DIRECT_REPAIR_CHAIN_CLOSURE_RECEIPT_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/abx_artifact_lineage_direct_repair_chain_closure_receipt_001.latest.json"
)
RECEIPT_MD_PATH = Path(
    "out/operator_review/abx_artifact_lineage_direct_repair_chain_closure_receipt_001.latest.md"
)
FRONTIER_REVALIDATION_PATH = (
    "out/operator_review/abx_artifact_lineage_direct_repair_frontier_revalidation_001.latest.json"
)

CHAIN_STEPS: tuple[dict[str, Any], ...] = (
    {
        "step_order": 1,
        "lane_id": "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SEPARATE_EXECUTION_SPEC_PLAN",
        "artifact_path": (
            "out/operator_review/"
            "abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan_001.latest.json"
        ),
        "id_field": "artifact_id",
    },
    {
        "step_order": 2,
        "lane_id": "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_GATE",
        "artifact_path": (
            "out/operator_review/"
            "abx_artifact_lineage_registry_direct_repair_execution_authorization_gate_001.latest.json"
        ),
        "id_field": "artifact_id",
    },
    {
        "step_order": 3,
        "lane_id": "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_RECORD",
        "artifact_path": (
            "out/operator_review/"
            "abx_artifact_lineage_registry_direct_repair_execution_authorization_record_001.latest.json"
        ),
        "id_field": "artifact_id",
    },
    {
        "step_order": 4,
        "lane_id": "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SCOPED_EXECUTION_RECEIPT",
        "artifact_path": (
            "out/operator_review/"
            "abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_001.latest.json"
        ),
        "id_field": "artifact_id",
    },
    {
        "step_order": 5,
        "lane_id": "ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_REGENERATION_001",
        "artifact_path": TRACEABILITY_REGEN_RECEIPT_PATH,
        "id_field": "artifact_id",
        "status_field": "downstream_status",
    },
    {
        "step_order": 6,
        "lane_id": "ABX_ARTIFACT_LINEAGE_DIRECT_REPAIR_FRONTIER_REVALIDATION_001",
        "artifact_path": FRONTIER_REVALIDATION_PATH,
        "id_field": "artifact_id",
        "status_field": "downstream_status",
    },
)

BLOCKED_ACTIONS = [
    "DIRECT_REGISTRY_REPAIR_EXECUTION",
    "OUTPUT_PAIRING_REPAIR_EXECUTION",
    "DOCS_REFERENCE_REPAIR_EXECUTION",
    "RUNNER_CASING_POLICY_OVERRIDE",
    "NOTION_MAPPING_COMPLETENESS_CLAIM",
    "RUNTIME_MUTATION",
    "CANON_MUTATION",
    "QUEUE_MUTATION",
    "SCHEDULER_MUTATION",
    "NOTION_WRITEBACK",
    "GITHUB_WRITEBACK",
    "UNSCOPED_REPAIR_EXECUTION",
    "RESEARCH_CANARY_ARTIFACT_REGENERATION",
    "RESEARCH_CANARY_SPINE_REFRESH",
    "P130_ACTIVATION",
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
    for field in ("status", "chain_closure_status", "receipt_status", "downstream_status", "revalidation_status"):
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
    traceability_regen = _read_json(root / TRACEABILITY_REGEN_RECEIPT_PATH)
    frontier_revalidation = _read_json(root / FRONTIER_REVALIDATION_PATH)
    scoped_receipt = _read_json(
        root
        / "out/operator_review/"
        "abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_001.latest.json"
    )

    traceability_complete = (
        traceability_regen.get("downstream_status") == "TRACEABILITY_AUDIT_REGENERATION_COMPLETE"
        and traceability_regen.get("audit_regeneration_performed") is True
    )
    frontier_complete = (
        frontier_revalidation.get("downstream_status") == ARTIFACT_LINEAGE_DIRECT_REPAIR_CHAIN_COMPLETE
        and frontier_revalidation.get("traceability_regeneration_receipt", {}).get("regeneration_complete")
        is True
    )
    scoped_emitted = (
        scoped_receipt.get("status")
        == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SCOPED_EXECUTION_RECEIPT_EMITTED"
    )

    if not traceability_complete:
        blockers.append("TRACEABILITY_AUDIT_REGENERATION_NOT_COMPLETE")
    if not frontier_complete:
        blockers.append("FRONTIER_REVALIDATION_NOT_COMPLETE")
    if not scoped_emitted:
        blockers.append("SCOPED_EXECUTION_RECEIPT_NOT_EMITTED")

    summary = {
        "traceability_regeneration_complete": traceability_complete,
        "frontier_revalidation_complete": frontier_complete,
        "scoped_execution_emitted": scoped_emitted,
        "traceability_regen_hash": str(traceability_regen.get("receipt_hash", NOT_COMPUTABLE)),
        "frontier_revalidation_hash": str(frontier_revalidation.get("revalidation_hash", NOT_COMPUTABLE)),
        "scoped_execution_hash": str(scoped_receipt.get("receipt_hash", NOT_COMPUTABLE)),
    }
    return traceability_complete and frontier_complete and scoped_emitted, blockers, summary


def build_abx_artifact_lineage_direct_repair_chain_closure_receipt(
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
        status = "ABX_ARTIFACT_LINEAGE_DIRECT_REPAIR_CHAIN_CLOSURE_RECEIPT_BLOCKED"
    else:
        chain_closure_status = "ARTIFACT_LINEAGE_DIRECT_REPAIR_CHAIN_SEALED"
        status = "ABX_ARTIFACT_LINEAGE_DIRECT_REPAIR_CHAIN_CLOSURE_RECEIPT_EMITTED"

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
        "receipt_id": "abx_artifact_lineage_direct_repair_chain_closure_receipt_001",
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_DIRECT_REPAIR_CHAIN_CLOSURE_RECEIPT_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "implementation_authorized": False,
        "safe_to_auto_continue": False,
        "chain_closure_status": chain_closure_status,
        "closure_posture": (
            "SEALED" if chain_closure_status == "ARTIFACT_LINEAGE_DIRECT_REPAIR_CHAIN_SEALED" else NOT_COMPUTABLE
        ),
        "chain_steps": chain_step_records,
        "chain_steps_ready_count": sum(1 for record in chain_step_records if record["step_ready"]),
        "chain_steps_total_count": len(chain_step_records),
        "terminal_summary": terminal_summary,
        "governance_preservation": {
            "p130_hold_preserved": True,
            "research_canary_spine_refresh_performed": False,
            "notion_completeness_claim_allowed": False,
            "runner_casing_policy_override_allowed": False,
        },
        "blocked_actions": list(BLOCKED_ACTIONS),
        "blocked_reasons": blockers,
        "recommended_next_action": (
            "artifact-lineage direct repair chain is sealed; downstream remains NOT_COMPUTABLE"
            if chain_closure_status == "ARTIFACT_LINEAGE_DIRECT_REPAIR_CHAIN_SEALED"
            else "repair artifact-lineage direct repair chain prerequisites before chain closure"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "downstream_status": NOT_COMPUTABLE,
    }
    return {**packet, "receipt_hash": canonical_hash(packet)}


def render_markdown(packet: Mapping[str, Any]) -> list[str]:
    lines = [
        "# ABX Artifact Lineage Direct Repair Chain Closure Receipt 001",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `chain_closure_status`: `{packet['chain_closure_status']}`",
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


def write_abx_artifact_lineage_direct_repair_chain_closure_receipt(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_artifact_lineage_direct_repair_chain_closure_receipt(root)
    write_canonical_json(target_root / RECEIPT_JSON_PATH, packet)
    _write_markdown(target_root / RECEIPT_MD_PATH, render_markdown(packet))
    return packet
