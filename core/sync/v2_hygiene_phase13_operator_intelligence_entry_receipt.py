from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.scoring.brier import compute_brier_score
from core.sync.v2_hygiene_phase6_execution_surface_promotion_gate import (
    RECEIPT_JSON_PATH as SOURCE_PHASE12_GATE_JSON_PATH,
)

SCHEMA_VERSION = "V2HygienePhase13OperatorIntelligenceEntryReceipt.v1"
RECEIPT_ID = "v2_hygiene_phase13_operator_intelligence_entry_receipt_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_phase13_operator_intelligence_entry_receipt_001.latest.json"
)
RECEIPT_MD_PATH = RECEIPT_JSON_PATH.with_suffix(".md")
READY_STATUS = "V2_HYGIENE_PHASE13_OPERATOR_INTELLIGENCE_ENTRY_RECEIPT_READY"
BLOCKED_STATUS = "V2_HYGIENE_PHASE13_OPERATOR_INTELLIGENCE_ENTRY_RECEIPT_BLOCKED"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
EXPECTED_PHASE12_STATUS = "V2_HYGIENE_PHASE6_EXECUTION_SURFACE_PROMOTION_GATE_READY"
EXPECTED_PHASE12_HASH = "47528b2cc5acad1ac94ac8df8fa57eed0af9ad1741480463237935651ef9e306"
EXPECTED_PHASE12_RECOMMENDED_LANE = "NOT_COMPUTABLE"
CONTINUITY_SPINE_PATH = Path("docs/status/continuity-spine.json")
PHASE_NUMBER = 13

AUTHORITY_EXPANDING_FIELDS = (
    "notion_writeback_allowed",
    "github_writeback_allowed",
    "canon_promotion_authorized",
    "runtime_activation_authorized",
    "runtime_mutation",
    "queue_mutation",
    "scheduler_mutation",
    "canon_mutation",
    "execution_authority",
    "forecast_routing_authorized",
    "adaptive_learning_authorized",
    "promotion_authorized",
    "activation_authorized",
    "brier_resolution_authorized",
    "package_lock_mutation_authorized",
    "v2_module_registration_authorized",
    "rune_registration_authorized",
    "implementation_authorized",
    "valid_for_writeback",
    "valid_for_promotion",
    "valid_for_activation",
    "valid_for_execution",
    "valid_for_implementation",
    "safe_to_auto_continue",
    "dependency_mutation_authorized",
    "toolchain_provisioning_authorized",
    "uncontrolled_writeback_authorized",
    "execution_surface_promotion_authorized",
    "mcp_auto_writeback_authorized",
)


def _resolve(root: Path, path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return NOT_COMPUTABLE


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _locks_all_false(value: Any) -> bool:
    return isinstance(value, Mapping) and bool(value) and all(
        item is False for item in value.values()
    )


def _copied_authority_locks(source: Mapping[str, Any]) -> dict[str, bool]:
    locks = source.get("authority_locks")
    if _locks_all_false(locks):
        copied = {str(key): False for key in sorted(locks)}
    else:
        copied = {}
    for key in (
        "activation",
        "adaptive_learning",
        "auto_continuation",
        "brier_resolution",
        "canon_mutation",
        "controlled_writeback",
        "dependency_mutation",
        "execution_authority",
        "execution_surface_promotion",
        "forecast_routing",
        "github_writeback",
        "mcp_auto_writeback",
        "notion_writeback",
        "package_lock_mutation",
        "promotion",
        "queue_mutation",
        "rune_registration",
        "runtime_mutation",
        "scheduler_mutation",
        "toolchain_provisioning",
        "uncontrolled_writeback",
        "v2_module_registration",
        "writeback",
    ):
        copied.setdefault(key, False)
    return copied


def _authority_expansion_blockers(source_id: str, packet: Mapping[str, Any]) -> list[str]:
    blockers = [
        f"{source_id}_authority_expanding_field:{field}"
        for field in AUTHORITY_EXPANDING_FIELDS
        if packet.get(field) is True
    ]
    locks = packet.get("authority_locks")
    if isinstance(locks, Mapping):
        blockers.extend(
            f"{source_id}_authority_lock_true:{field}"
            for field, value in sorted(locks.items())
            if value is True
        )
    return blockers


def _source_record(source_id: str, path: Path, packet: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "path": path.as_posix(),
        "observed": bool(packet),
        "file_hash": _sha256(path),
        "packet_hash": str(packet.get("execution_surface_promotion_gate_hash", NOT_COMPUTABLE)),
        "expected_packet_hash": EXPECTED_PHASE12_HASH,
        "status": str(packet.get("status", NOT_COMPUTABLE)),
        "expected_status": EXPECTED_PHASE12_STATUS,
        "authority_locks_all_false": _locks_all_false(packet.get("authority_locks")),
        "operator_review_posture": packet.get("operator_review_posture", NOT_COMPUTABLE),
        "recommended_next_lane": packet.get("recommended_next_lane", NOT_COMPUTABLE),
        "downstream": packet.get("downstream", NOT_COMPUTABLE),
    }


def _phase12_blockers(packet: Mapping[str, Any]) -> list[str]:
    blockers = []
    if packet.get("status") != EXPECTED_PHASE12_STATUS:
        blockers.append("phase12_execution_surface_promotion_gate_not_ready")
    if packet.get("source_readiness") != "SOURCE_ARTIFACTS_READY":
        blockers.append("phase12_source_not_ready")
    if packet.get("source_blockers") != []:
        blockers.append("phase12_source_blockers_not_empty")
    if packet.get("execution_surface_promotion_gate_ready") is not True:
        blockers.append("phase12_execution_surface_promotion_gate_ready_not_true")
    if packet.get("execution_surface_promotion_gate_hash") != EXPECTED_PHASE12_HASH:
        blockers.append("phase12_execution_surface_promotion_gate_hash_mismatch")
    without_hash = dict(packet)
    observed_hash = without_hash.pop("execution_surface_promotion_gate_hash", NOT_COMPUTABLE)
    if canonical_hash(without_hash) != observed_hash:
        blockers.append("phase12_execution_surface_promotion_gate_self_hash_mismatch")
    if packet.get("recommended_next_lane") != EXPECTED_PHASE12_RECOMMENDED_LANE:
        blockers.append("phase12_recommended_lane_mismatch")
    if packet.get("downstream") != NOT_COMPUTABLE:
        blockers.append("phase12_downstream_not_closed")
    if packet.get("operator_review_posture") != "ACTIVE":
        blockers.append("phase12_operator_review_posture_not_active")
    if not _locks_all_false(packet.get("authority_locks")):
        blockers.append("phase12_authority_locks_not_false")
    blockers.extend(_authority_expansion_blockers("phase12_execution_surface_promotion_gate", packet))
    return blockers


def _spine_hash(repo_root: Path) -> str:
    spine_path = repo_root / CONTINUITY_SPINE_PATH
    try:
        return _sha256(spine_path)
    except OSError:
        return NOT_COMPUTABLE


def _phase_transition_receipt_contract(
    repo_root: Path,
    *,
    phase12_hash: str,
    ready: bool,
) -> dict[str, Any]:
    spine_hash = _spine_hash(repo_root)
    return {
        "contract_id": "v2_hygiene_phase13_phase_transition_receipt_contract_001",
        "phase": PHASE_NUMBER,
        "timestamp_utc": NOT_COMPUTABLE,
        "authority_state": "read/controlled-write",
        "operator_review_posture": "ACTIVE",
        "spine_path": CONTINUITY_SPINE_PATH.as_posix(),
        "spine_hash": spine_hash,
        "phase12_gate_hash": phase12_hash if ready else NOT_COMPUTABLE,
        "claims": [
            {
                "field": "phase12_gate_verified",
                "classification": "OBSERVED" if ready else "INFERRED",
                "provenance": "phase12_execution_surface_promotion_gate_hash_verified",
                "value": ready,
            },
            {
                "field": "continuity_spine_observed",
                "classification": "OBSERVED" if spine_hash != NOT_COMPUTABLE else "SPECULATIVE",
                "provenance": CONTINUITY_SPINE_PATH.as_posix(),
                "value": spine_hash != NOT_COMPUTABLE,
            },
            {
                "field": "mcp_graph_artifact_optional",
                "classification": "INFERRED",
                "provenance": ".codebase-memory/graph.db.zst",
                "value": (repo_root / ".codebase-memory/graph.db.zst").exists(),
            },
            {
                "field": "brier_resolution_held",
                "classification": "OBSERVED",
                "provenance": "phase12_brier_scoring_contract",
                "value": True,
            },
            {
                "field": "notion_auto_sync_denied",
                "classification": "OBSERVED",
                "provenance": "canon_writeback_denial",
                "value": True,
            },
        ],
    }


def _mcp_integration_contract(repo_root: Path) -> dict[str, Any]:
    mcp_example = repo_root / ".cursor/mcp.json.example"
    mcp_rules = repo_root / ".cursor/rules/codebase-memory-mcp.mdc"
    graph_artifact = repo_root / ".codebase-memory/graph.db.zst"
    return {
        "contract_id": "v2_hygiene_phase13_mcp_integration_contract_001",
        "mcp_json_example_observed": mcp_example.exists(),
        "mcp_rules_observed": mcp_rules.exists(),
        "graph_artifact_observed": graph_artifact.exists(),
        "auto_index_configured": NOT_COMPUTABLE,
        "mcp_auto_writeback_authorized": False,
        "operator_local_install_required": True,
    }


def _brier_scoring_contract() -> dict[str, Any]:
    return {
        "contract_id": "v2_hygiene_phase13_operator_intelligence_brier_telemetry_contract_001",
        "telemetry_only": True,
        "brier_score_formula": "(forecast_probability - binary_outcome)^2",
        "telemetry_hooks": [
            {
                "claim_id": "phase13_entry_receipt_ready",
                "forecast_probability": 0.8,
                "binary_outcome": NOT_COMPUTABLE,
                "brier_score": NOT_COMPUTABLE,
                "resolution_source": NOT_COMPUTABLE,
                "resolution_allowed": False,
            },
            {
                "claim_id": "mcp_graph_improves_governance_trace_efficiency",
                "forecast_probability": 0.7,
                "binary_outcome": NOT_COMPUTABLE,
                "brier_score": NOT_COMPUTABLE,
                "resolution_source": NOT_COMPUTABLE,
                "resolution_allowed": False,
            },
            {
                "claim_id": "brier_provenance_module_wired",
                "forecast_probability": compute_brier_score(0.75, 0.0),
                "binary_outcome": NOT_COMPUTABLE,
                "brier_score": NOT_COMPUTABLE,
                "resolution_source": "core/governance/brier_provenance.py",
                "resolution_allowed": False,
            },
        ],
        "resolution_allowed": False,
        "adaptive_learning_authorized": False,
        "forecast_routing_authorized": False,
        "promotion_authorized": False,
        "execution_authority": False,
        "brier_resolution_authorized": False,
    }


def _rune_governance_mapping() -> list[dict[str, Any]]:
    return [
        {
            "rune": "Observe",
            "governance_mapping": "Phase 12 gate and Phase 13 operator intelligence entry observation",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Bind",
            "governance_mapping": "Phase 12 hash, continuity spine hash, and MCP template binding",
            "authority_granted": False,
            "risk_level": "MEDIUM",
        },
        {
            "rune": "Hold",
            "governance_mapping": "Notion auto-sync, Brier resolution, and authority escalation held",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
        {
            "rune": "Weigh",
            "governance_mapping": "telemetry-only Brier posture for operator intelligence entry",
            "authority_granted": False,
            "risk_level": "LOW",
        },
        {
            "rune": "Seal",
            "governance_mapping": "Phase 13 entry receipt only; operator review posture remains active",
            "authority_granted": False,
            "risk_level": "HIGH",
        },
    ]


def build_v2_hygiene_phase13_operator_intelligence_entry_receipt(
    repo_root: str | Path = ".",
    *,
    source_phase12_gate_path: str | Path = SOURCE_PHASE12_GATE_JSON_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_phase12_gate_path)
    phase12 = _read_json(_resolve(root, source_path)) or {}
    blockers = []
    if not phase12:
        blockers.append("required_phase12_execution_surface_promotion_gate_missing")
    else:
        blockers.extend(_phase12_blockers(phase12))
    blockers = sorted(set(blockers))
    ready = bool(phase12) and not blockers
    phase12_hash = str(phase12.get("execution_surface_promotion_gate_hash", NOT_COMPUTABLE))
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": READY_STATUS if ready else BLOCKED_STATUS,
        "sources_observed": bool(phase12),
        "source_records": [_source_record("phase12_execution_surface_promotion_gate", source_path, phase12)],
        "source_blockers": blockers,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "SOURCE_ARTIFACTS_NOT_READY",
        "operator_intelligence_entry_receipt_ready": ready,
        "phase12_execution_surface_promotion_gate_hash_verified": ready,
        "phase_transition_receipt_contract": _phase_transition_receipt_contract(
            root,
            phase12_hash=phase12_hash,
            ready=ready,
        ),
        "mcp_integration_contract": _mcp_integration_contract(root),
        "brier_scoring_contract": _brier_scoring_contract(),
        "rune_governance_mapping": _rune_governance_mapping(),
        "recommended_next_action": (
            "use MCP graph tools and manual Notion sync packet for operator review; "
            "hold Brier resolution and authority escalation fail-closed"
            if ready
            else "restore the Phase 12 execution surface promotion gate before Phase 13 entry"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "downstream": NOT_COMPUTABLE,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "canon_promotion_authorized": False,
        "runtime_activation_authorized": False,
        "promotion_authorized": False,
        "activation_authorized": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "canon_mutation": False,
        "schema_mutation": False,
        "execution_authority": False,
        "execution_surface_promotion_authorized": False,
        "forecast_routing_authorized": False,
        "adaptive_learning_authorized": False,
        "brier_resolution_authorized": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "implementation_authorized": False,
        "valid_for_writeback": False,
        "valid_for_controlled_writeback": ready,
        "valid_for_promotion": False,
        "valid_for_activation": False,
        "valid_for_execution": False,
        "uncontrolled_writeback_authorized": False,
        "mcp_auto_writeback_authorized": False,
        "safe_to_auto_continue": False,
        "operator_review_posture": "ACTIVE",
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authority_locks": _copied_authority_locks(phase12),
        "operator_intelligence_entry_receipt_hash": "",
    }
    packet["operator_intelligence_entry_receipt_hash"] = canonical_hash(
        {
            key: value
            for key, value in packet.items()
            if key != "operator_intelligence_entry_receipt_hash"
        }
    )
    return packet


def render_v2_hygiene_phase13_operator_intelligence_entry_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    transition = packet["phase_transition_receipt_contract"]
    mcp = packet["mcp_integration_contract"]
    brier = packet["brier_scoring_contract"]
    lines = [
        "# v2.0 Hygiene Phase 13 Operator Intelligence Entry Receipt",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- status: {packet['status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- operator_intelligence_entry_receipt_ready: {packet['operator_intelligence_entry_receipt_ready']}",
        f"- phase12_execution_surface_promotion_gate_hash_verified: {packet['phase12_execution_surface_promotion_gate_hash_verified']}",
        f"- operator_review_posture: {packet['operator_review_posture']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- downstream: {packet['downstream']}",
        "",
        "## Phase Transition Contract",
        f"- phase: {transition['phase']}",
        f"- authority_state: {transition['authority_state']}",
        f"- spine_hash: {transition['spine_hash']}",
        f"- phase12_gate_hash: {transition['phase12_gate_hash']}",
        "",
        "## MCP Integration Contract",
        f"- mcp_json_example_observed: {mcp['mcp_json_example_observed']}",
        f"- mcp_rules_observed: {mcp['mcp_rules_observed']}",
        f"- graph_artifact_observed: {mcp['graph_artifact_observed']}",
        f"- mcp_auto_writeback_authorized: {mcp['mcp_auto_writeback_authorized']}",
        "",
        "## Brier Scoring Contract",
        f"- telemetry_only: {brier['telemetry_only']}",
        f"- resolution_allowed: {brier['resolution_allowed']}",
        f"- brier_resolution_authorized: {brier['brier_resolution_authorized']}",
        "",
        "## Source Blockers",
    ]
    if packet["source_blockers"]:
        lines.extend(f"- {blocker}" for blocker in packet["source_blockers"])
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_phase13_operator_intelligence_entry_receipt(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase13_operator_intelligence_entry_receipt(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / RECEIPT_JSON_PATH, packet)
    md_path = root / RECEIPT_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase13_operator_intelligence_entry_receipt_markdown(packet)
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
