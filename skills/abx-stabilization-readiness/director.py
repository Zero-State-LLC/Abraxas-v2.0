"""Advisory orchestration for stabilization-readiness evidence packets."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.campaign_director.stabilization_campaign import StabilizationPhase

from .contract_inventory import build_contract_inventory
from .contracts import validate_stabilization_state
from .conformance_harness import run_conformance_cases
from .models import StabilizationState
from .reproducibility_auditor import audit_reproducibility
from .stabilization_gate import evaluate_stabilization_entry

ARTIFACT_NAMES = (
    "stabilization_contract_inventory.latest.json",
    "stabilization_reproducibility_baseline.latest.json",
    "stabilization_conformance_manifest.latest.json",
    "stabilization_entry_gate.latest.json",
    "stabilization_skill_foundation_receipt.latest.json",
)


def build_stabilization_state(
    baseline_commit: str,
    *,
    phase: str = StabilizationPhase.BASELINE_DISCOVERY.value,
) -> StabilizationState:
    state = StabilizationState(baseline_commit=baseline_commit, phase=phase)
    validate_stabilization_state(state)
    return state


def emit_foundation_artifacts(
    output_root: Path,
    *,
    baseline_commit: str,
    reproducibility_observations: Mapping[str, Mapping[str, Any]] | None = None,
    gate_evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Emit deterministic advisory artifacts through the canonical writer."""
    state = build_stabilization_state(baseline_commit)
    inventory = build_contract_inventory()
    reproducibility = audit_reproducibility(reproducibility_observations)
    conformance = run_conformance_cases()
    derived_evidence: dict[str, Any] = {
        "python_ready": reproducibility["ready"],
        "typescript_ready": False,
        "contract_inventory_complete": inventory["inventory_status"] == "COMPLETE",
        "conformance_corpus_ready": conformance["ready"],
        "reproducibility_ready": reproducibility["ready"],
        "canonical_artifact_safety_ready": conformance["ready"],
        "full_suite_confidence": "NOT_COMPUTABLE",
        "authority": {
            **state.authority.to_dict(),
            "autonomous_stabilization_entry": False,
            "feature_expansion_allowed": False,
        },
        "evidence_refs": [
            ARTIFACT_NAMES[0],
            ARTIFACT_NAMES[1],
            ARTIFACT_NAMES[2],
        ],
    }
    if gate_evidence is not None:
        derived_evidence.update(gate_evidence)
    gate = evaluate_stabilization_entry(derived_evidence).to_dict()
    payloads = {
        ARTIFACT_NAMES[0]: inventory,
        ARTIFACT_NAMES[1]: reproducibility,
        ARTIFACT_NAMES[2]: conformance,
        ARTIFACT_NAMES[3]: gate,
    }
    for name, payload in payloads.items():
        write_canonical_json(output_root / name, payload)
    receipt: dict[str, Any] = {
        "schema_version": "StabilizationSkillFoundationReceipt.v1",
        "work_order": "WO-ABX-STABILIZATION-SKILL-FOUNDATION-001",
        "state": state.to_dict(),
        "state_hash": state.deterministic_hash(),
        "artifacts": [
            {"path": name, "canonical_hash": canonical_hash(payloads[name])}
            for name in sorted(payloads)
        ],
        "decision": gate["decision"],
        "authority": state.authority.to_dict(),
        "feature_expansion_allowed": False,
        "recommended_next_packet": "WO-ABX-STABILIZATION-CONTRACT-INVENTORY-002",
    }
    receipt["canonical_hash"] = canonical_hash(receipt)
    write_canonical_json(output_root / ARTIFACT_NAMES[4], receipt)
    return {**payloads, ARTIFACT_NAMES[4]: receipt}
