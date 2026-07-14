from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "AbxResearchCanaryOrphanOutputRegistryInclusionExecutionAuthorizationRecord.v1"
RECORD_ID = "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_AUTHORIZATION_RECORD_001"
GATE_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_execution_authorization_gate_001.latest.json"
)
RECORD_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_execution_authorization_record_001.latest.json"
)
RECORD_MD_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_execution_authorization_record_001.latest.md"
)
SCOPED_RECEIPT_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_orphan_output_registry_inclusion_scoped_execution_receipt_001.latest.json"
)
SCOPED_RECEIPT_LANE = "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_SCOPED_EXECUTION_RECEIPT_001"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_abx_research_canary_orphan_output_registry_inclusion_execution_authorization_record(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    gate = _read_json(root / GATE_JSON_PATH)
    scoped_receipt = _read_json(root / SCOPED_RECEIPT_JSON_PATH)

    gate_ready = (
        gate.get("schema_version") == "AbxResearchCanaryOrphanOutputRegistryInclusionExecutionAuthorizationGate.v1"
        and gate.get("status")
        == "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR"
        and gate.get("operator_authorization_required") is True
        and gate.get("authorization_granted") is False
    )
    scoped_observed = (
        scoped_receipt.get("schema_version")
        == "AbxResearchCanaryOrphanOutputRegistryInclusionScopedExecutionReceipt.v1"
        and scoped_receipt.get("status")
        == "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_SCOPED_EXECUTION_RECEIPT_EMITTED"
        and scoped_receipt.get("registry_mutation_performed") is True
    )
    consumed_by_scoped = gate_ready and scoped_observed

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": RECORD_ID,
        "status": (
            "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_AUTHORIZATION_RECORD_CONSUMED_BY_SCOPED_EXECUTION_RECEIPT"
            if consumed_by_scoped
            else "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_AUTHORIZATION_RECORD_GRANTED_FOR_SCOPED_EXECUTION_PR"
            if gate_ready
            else "ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_AUTHORIZATION_RECORD_BLOCKED"
        ),
        "authorization_record_id": RECORD_ID,
        "command": "BUILD_ABX_RESEARCH_CANARY_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_AUTHORIZATION_RECORD_001",
        "authorization_record_only": True,
        "source_authorization_gate": {
            "path": str(GATE_JSON_PATH),
            "hash": str(gate.get("authorization_gate_hash", NOT_COMPUTABLE)),
            "status": str(gate.get("status", NOT_COMPUTABLE)),
            "observed": gate_ready,
        },
        "operator_authorization": {
            "operator_id": "thread_operator",
            "operator_name": "appliedalchemylabs",
            "operator_role": "governed_operator",
            "operator_instruction_observed": "authorize",
            "authorization_timestamp_utc": "2026-06-18T00:00:00Z",
            "p130_hold_preservation_acknowledged": True,
            "separate_orphan_registry_governance_acknowledged": True,
        },
        "authorization_scope": "SCOPED_ORPHAN_OUTPUT_REGISTRY_INCLUSION_EXECUTION_PR_ONLY",
        "authorization_granted": gate_ready,
        "execution_authority": gate_ready,
        "registry_mutation_performed": consumed_by_scoped,
        "implementation_authorized": gate_ready,
        "safe_to_prepare_execution_pr": gate_ready and not consumed_by_scoped,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "scoped_execution_receipt": {
            "path": str(SCOPED_RECEIPT_JSON_PATH),
            "status": str(scoped_receipt.get("status", NOT_COMPUTABLE)),
            "observed": scoped_observed,
        },
        "downstream_status": (
            "SCOPED_EXECUTION_RECEIPT_OBSERVED"
            if consumed_by_scoped
            else "READY_FOR_SCOPED_EXECUTION_PR_PREPARATION"
            if gate_ready
            else NOT_COMPUTABLE
        ),
        "recommended_next_lane": NOT_COMPUTABLE if consumed_by_scoped else SCOPED_RECEIPT_LANE if gate_ready else NOT_COMPUTABLE,
    }
    return {**packet, "authorization_record_hash": canonical_hash(packet)}


def render_markdown(packet: Mapping[str, Any]) -> list[str]:
    return [
        "# ABX Research Canary Orphan Output Registry Inclusion Execution Authorization Record 001",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `authorization_granted`: `{packet['authorization_granted']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
    ]


def write_abx_research_canary_orphan_output_registry_inclusion_execution_authorization_record(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_orphan_output_registry_inclusion_execution_authorization_record(root)
    write_canonical_json(target_root / RECORD_JSON_PATH, packet)
    _write_markdown(target_root / RECORD_MD_PATH, render_markdown(packet))
    return packet
