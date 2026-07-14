from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "AbxResearchCanaryArtifactRegistryCoverageRepairChainClosureReceipt.v1"
RECEIPT_ID = "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_CHAIN_CLOSURE_RECEIPT_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt_001.latest.json"
)
RECEIPT_MD_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt_001.latest.md"
)

CHAIN_STEPS: tuple[dict[str, Any], ...] = (
    {
        "step_order": 1,
        "lane_id": "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_AUDIT_001",
        "artifact_path": "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_001.latest.json",
        "id_field": "audit_id",
    },
    {
        "step_order": 2,
        "lane_id": "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_SPEC_PLAN_001",
        "artifact_path": (
            "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_spec_plan_001.latest.json"
        ),
        "id_field": "artifact_id",
        "status_field": "spec_plan_status",
    },
    {
        "step_order": 3,
        "lane_id": "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_REQUEST_001",
        "artifact_path": (
            "out/operator_review/"
            "abx_research_canary_artifact_registry_coverage_repair_operator_decision_request_001.latest.json"
        ),
        "id_field": "artifact_id",
    },
    {
        "step_order": 4,
        "lane_id": "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_PHASE_EXECUTION_RECEIPT_001",
        "artifact_path": (
            "out/operator_review/"
            "abx_research_canary_artifact_registry_coverage_repair_phase_execution_receipt_001.latest.json"
        ),
        "id_field": "artifact_id",
        "status_field": "receipt_status",
    },
    {
        "step_order": 5,
        "lane_id": "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_RECORD_PLAN_001",
        "artifact_path": (
            "out/operator_review/"
            "abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_plan_001.latest.json"
        ),
        "id_field": "artifact_id",
    },
    {
        "step_order": 6,
        "lane_id": "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_RECORD_001",
        "artifact_path": (
            "out/operator_review/"
            "abx_research_canary_artifact_registry_coverage_repair_operator_decision_record_001.latest.json"
        ),
        "id_field": "artifact_id",
    },
    {
        "step_order": 7,
        "lane_id": "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_EXECUTION_SPEC_PLAN_001",
        "artifact_path": (
            "out/operator_review/"
            "abx_research_canary_artifact_registry_coverage_repair_execution_spec_plan_001.latest.json"
        ),
        "id_field": "artifact_id",
    },
    {
        "step_order": 8,
        "lane_id": "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_EXECUTION_AUTHORIZATION_GATE_001",
        "artifact_path": (
            "out/operator_review/"
            "abx_research_canary_artifact_registry_coverage_repair_execution_authorization_gate_001.latest.json"
        ),
        "id_field": "artifact_id",
    },
    {
        "step_order": 9,
        "lane_id": "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_EXECUTION_AUTHORIZATION_RECORD_001",
        "artifact_path": (
            "out/operator_review/"
            "abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record_001.latest.json"
        ),
        "id_field": "artifact_id",
    },
    {
        "step_order": 10,
        "lane_id": "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_SCOPED_EXECUTION_RECEIPT_001",
        "artifact_path": (
            "out/operator_review/"
            "abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt_001.latest.json"
        ),
        "id_field": "artifact_id",
    },
    {
        "step_order": 11,
        "lane_id": "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_AUDIT_REGENERATION_RECEIPT_001",
        "artifact_path": (
            "out/operator_review/"
            "abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt_001.latest.json"
        ),
        "id_field": "artifact_id",
    },
)

BLOCKED_ACTIONS = [
    "RESEARCH_CANARY_SPINE_REFRESH",
    "RESEARCH_CANARY_ARTIFACT_REGENERATION",
    "P130_ACTIVATION",
    "ORPHAN_OUTPUT_REGISTRY_INCLUSION",
    "SCOPE_PREFIX_MUTATION_WITHOUT_OPERATOR_DECISION",
    "RUNTIME_MUTATION",
    "CANON_MUTATION",
    "QUEUE_MUTATION",
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
    for field in ("status", "audit_status", "receipt_status", "spec_plan_status", "chain_closure_status"):
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
    regen = _read_json(
        root
        / "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt_001.latest.json"
    )
    scoped = _read_json(
        root
        / "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt_001.latest.json"
    )
    audit = _read_json(
        root / "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_001.latest.json"
    )
    coverage = audit.get("coverage_summary", {})
    if not isinstance(coverage, dict):
        coverage = {}

    regen_ready = (
        regen.get("status") == "RESEARCH_CANARY_REGISTRY_COVERAGE_AUDIT_REGENERATION_RECEIPT_EMITTED"
        and regen.get("downstream_status") == "COVERAGE_REPAIR_CHAIN_COMPLETE"
        and regen.get("audit_regeneration_performed") is True
    )
    scoped_ready = (
        scoped.get("status") == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_SCOPED_EXECUTION_RECEIPT_EMITTED"
        and scoped.get("repair_execution_performed") is True
        and scoped.get("registry_mutation_performed") is True
    )
    audit_ready = (
        audit.get("audit_id") == "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_AUDIT_001"
        and audit.get("audit_status") == NOT_COMPUTABLE
        and coverage.get("direct_registry_lane_id_coverage") is True
        and coverage.get("lane_id_gap_count") == 0
        and coverage.get("output_path_gap_count") == 0
        and coverage.get("orphan_research_output_count") == 0
    )

    if not regen_ready:
        blockers.append("REGENERATION_RECEIPT_TERMINAL_STATE_NOT_READY")
    if not scoped_ready:
        blockers.append("SCOPED_EXECUTION_RECEIPT_TERMINAL_STATE_NOT_READY")
    if not audit_ready:
        blockers.append("POST_REPAIR_AUDIT_TERMINAL_STATE_NOT_READY")

    summary = {
        "regeneration_receipt_ready": regen_ready,
        "scoped_execution_receipt_ready": scoped_ready,
        "post_repair_audit_ready": audit_ready,
        "regeneration_receipt_hash": str(regen.get("receipt_hash", NOT_COMPUTABLE)),
        "scoped_execution_receipt_hash": str(scoped.get("receipt_hash", NOT_COMPUTABLE)),
        "post_repair_audit_hash": str(audit.get("audit_hash", NOT_COMPUTABLE)),
    }
    return regen_ready and scoped_ready and audit_ready, blockers, summary


def build_abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    chain_step_records = [_step_record(root, step) for step in CHAIN_STEPS]
    chain_step_records = sorted(chain_step_records, key=lambda record: record["step_order"])
    terminal_ready, terminal_blockers, terminal_summary = _terminal_invariants(root)
    missing_steps = [record["lane_id"] for record in chain_step_records if not record["step_ready"]]
    degraded_steps = [
        record["lane_id"]
        for record in chain_step_records
        if record["step_ready"] and record["observed_status"] == NOT_COMPUTABLE
    ]

    if not terminal_ready or missing_steps:
        closure_posture = NOT_COMPUTABLE
        chain_closure_status = NOT_COMPUTABLE
        status = "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_CHAIN_CLOSURE_RECEIPT_BLOCKED"
    elif degraded_steps:
        closure_posture = "SEALED_WITH_OBSERVED_BLOCKERS"
        chain_closure_status = "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_CHAIN_SEALED"
        status = "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_CHAIN_CLOSURE_RECEIPT_EMITTED"
    else:
        closure_posture = "SEALED"
        chain_closure_status = "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_CHAIN_SEALED"
        status = "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_CHAIN_CLOSURE_RECEIPT_EMITTED"

    blockers = sorted(
        {
            *terminal_blockers,
            *[f"CHAIN_STEP_MISSING:{lane_id}" for lane_id in missing_steps],
        }
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": RECEIPT_ID,
        "receipt_id": "abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt_001",
        "status": status,
        "receipt_hash": "",
        "command": "BUILD_ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_CHAIN_CLOSURE_RECEIPT_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "closure_receipt_only": True,
        "chain_closure_status": chain_closure_status,
        "closure_posture": closure_posture,
        "chain_step_count": len(CHAIN_STEPS),
        "chain_step_records": chain_step_records,
        "terminal_validation_summary": terminal_summary,
        "blockers": blockers,
        "governance_preservation": {
            "p130_hold_preserved": True,
            "orphan_exclusion_preserved": True,
            "research_canary_spine_refresh_performed": False,
            "p102g_temporal_continuity_spine_edge_preserved": True,
        },
        "provenance": {
            "deterministic": True,
            "closure_receipt_only": True,
            "read_only": True,
            "non_authoritative": True,
            "source_linked": True,
            "fail_closed": True,
        },
        "authorization_scope": "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_CHAIN_CLOSURE_ONLY",
        "execution_allowed": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "github_writeback_allowed": False,
        "notion_writeback_allowed": False,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "downstream_status": NOT_COMPUTABLE,
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_action": (
            "registry coverage repair chain is sealed; do not reopen without separate operator review"
            if chain_closure_status == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_CHAIN_SEALED"
            else "complete registry coverage repair chain prerequisites before chain closure"
        ),
    }
    packet["receipt_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "receipt_hash"})
    return packet


def render_abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Research Canary Artifact Registry Coverage Repair Chain Closure Receipt 001",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `artifact_id`: `{packet['artifact_id']}`",
        f"- `chain_closure_status`: `{packet['chain_closure_status']}`",
        f"- `closure_posture`: `{packet['closure_posture']}`",
        f"- `downstream_status`: `{packet['downstream_status']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        "",
        "## Chain Step Records",
        "",
    ]
    for record in packet.get("chain_step_records", []):
        if not isinstance(record, dict):
            continue
        lines.append(
            f"- step `{record.get('step_order')}` `{record.get('lane_id')}`: "
            f"`{record.get('observed_status')}` ready=`{record.get('step_ready')}`"
        )
    lines.extend(
        [
            "",
            "## Preserved Holds",
            "",
            "- `P130_ACTIVATION` remains blocked",
            "- `ORPHAN_OUTPUT_REGISTRY_INCLUSION` remains blocked",
            "- `RESEARCH_CANARY_SPINE_REFRESH` remains blocked",
        ]
    )
    return lines


def write_abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt(root)
    write_canonical_json(target_root / RECEIPT_JSON_PATH, packet)
    _write_markdown(
        target_root / RECEIPT_MD_PATH,
        render_abx_research_canary_artifact_registry_coverage_repair_chain_closure_receipt_markdown(packet),
    )
    return packet
