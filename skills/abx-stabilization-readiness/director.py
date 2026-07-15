"""Stabilization director — sequences bounded work packets (advisory only)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .contracts import (
    BOUNDARY,
    CAMPAIGN_CLASS_STABILIZATION_READINESS,
    DEFAULT_CAMPAIGN_ID,
    SELECTION_PRIORITY,
    STABILIZATION_PHASES,
    TERMINAL_DECISIONS,
    WORK_ORDER_ID,
)
from .models import (
    StabilizationCampaignState,
    StabilizationDirectorReceipt,
    StabilizationScope,
    StabilizationWorkPacket,
)

RUNE_STABILIZATION_DIRECT = "RUNE.STABILIZATION_DIRECT"


def default_campaign_state(phase: Optional[str] = None) -> StabilizationCampaignState:
    p = phase or STABILIZATION_PHASES[0]
    state = StabilizationCampaignState(
        campaign_id=DEFAULT_CAMPAIGN_ID,
        campaign_class=CAMPAIGN_CLASS_STABILIZATION_READINESS,
        phase=p,
        scope=StabilizationScope(),
        feature_expansion_allowed=False,
        terminal_decisions=list(TERMINAL_DECISIONS),
        work_order_id=WORK_ORDER_ID,
    )
    return StabilizationCampaignState(
        campaign_id=state.campaign_id,
        campaign_class=state.campaign_class,
        phase=state.phase,
        scope=state.scope,
        feature_expansion_allowed=state.feature_expansion_allowed,
        terminal_decisions=state.terminal_decisions,
        work_order_id=state.work_order_id,
        state_hash=state.compute_hash(),
    )


def _packets_for_phase(phase: str) -> List[StabilizationWorkPacket]:
    catalog: Dict[str, List[StabilizationWorkPacket]] = {
        "PHASE.0_BASELINE_DISCOVERY": [
            StabilizationWorkPacket(
                packet_id="PKT-STAB-000-REPO-INTEL",
                phase=phase,
                priority_rank=1,
                title="Repo intel and dependency graph snapshot",
                bounded_scope=["abraxas-repo-intel", "codebase-memory"],
                entry_criteria=["clean worktree evidence requested"],
                exit_criteria=["inventory receipt emitted"],
            ),
        ],
        "PHASE.1_REPRODUCIBILITY": [
            StabilizationWorkPacket(
                packet_id="PKT-STAB-001-TOOLCHAIN",
                phase=phase,
                priority_rank=1,
                title="Python and TypeScript toolchain reproducibility audit",
                bounded_scope=["uv.lock", "package-lock", "pnpm-lock", "node version"],
                entry_criteria=["lock files present or NOT_COMPUTABLE recorded"],
                exit_criteria=["reproducibility classification emitted"],
            ),
        ],
        "PHASE.2_CONTRACT_FREEZE": [
            StabilizationWorkPacket(
                packet_id="PKT-STAB-002-INVENTORY",
                phase=phase,
                priority_rank=1,
                title="Cross-language contract inventory (classify only)",
                bounded_scope=["contracts/", "schemas", "public exports"],
                entry_criteria=["no freeze without operator decision"],
                exit_criteria=["contract records with classification"],
            ),
        ],
        "PHASE.3_CONFORMANCE": [
            StabilizationWorkPacket(
                packet_id="PKT-STAB-003-CORPUS",
                phase=phase,
                priority_rank=1,
                title="Seed conformance corpus for shared surfaces",
                bounded_scope=["statuses", "canonical JSON", "artifact envelopes"],
                entry_criteria=["fixture cases versioned"],
                exit_criteria=["harness can load and validate case shape"],
            ),
        ],
        "PHASE.4_STRESS_AND_REPLAY": [
            StabilizationWorkPacket(
                packet_id="PKT-STAB-004-OBSERVE",
                phase=phase,
                priority_rank=1,
                title="Stability regression observation window",
                bounded_scope=["extended canary", "flake rate", "skip drift"],
                entry_criteria=["baseline validation receipt"],
                exit_criteria=["observation metrics recorded"],
            ),
        ],
        "PHASE.5_ENTRY_DECISION": [
            StabilizationWorkPacket(
                packet_id="PKT-STAB-005-GATE",
                phase=phase,
                priority_rank=1,
                title="Independent stabilization entry gate",
                bounded_scope=["stabilization_gate only"],
                entry_criteria=["all prior phase receipts linked"],
                exit_criteria=["terminal decision with operator_action_required"],
            ),
        ],
    }
    return catalog.get(phase, [])


def _rank_residual_risks(
    repo_state: Dict[str, Any],
    residual_risks: List[str],
) -> List[str]:
    ordered: List[str] = []
    risk_text = " ".join(residual_risks).lower()
    for key in SELECTION_PRIORITY:
        if key.replace("_", " ") in risk_text or key in risk_text:
            ordered.append(key)
    for r in residual_risks:
        if r not in ordered:
            ordered.append(r)
    if repo_state.get("dirty_worktree"):
        if "repository_corruption_risk" not in ordered:
            ordered.insert(0, "repository_corruption_risk")
    return ordered


def stabilization_direct(
    repo_state: Optional[Dict[str, Any]] = None,
    contract_inventory: Optional[Dict[str, Any]] = None,
    validation_evidence: Optional[Dict[str, Any]] = None,
    residual_risks: Optional[List[str]] = None,
    phase: Optional[str] = None,
) -> StabilizationDirectorReceipt:
    """RUNE.STABILIZATION_DIRECT — advisory packet selection."""
    repo_state = repo_state or {}
    contract_inventory = contract_inventory or {}
    validation_evidence = validation_evidence or {}
    risks = list(residual_risks or [])

    if validation_evidence.get("flake_rate", 0) > 0:
        risks.append("nondeterminism")
    if not contract_inventory.get("contracts"):
        risks.append("public_contract_ambiguity")

    state = default_campaign_state(phase=phase)
    packets = _packets_for_phase(state.phase)
    ranked = _rank_residual_risks(repo_state, risks)

    phase_index = STABILIZATION_PHASES.index(state.phase)
    next_phase = (
        STABILIZATION_PHASES[phase_index + 1]
        if phase_index + 1 < len(STABILIZATION_PHASES)
        else state.phase
    )

    receipt = StabilizationDirectorReceipt(
        rune=RUNE_STABILIZATION_DIRECT,
        campaign_state_hash=state.state_hash,
        phase=state.phase,
        selected_packets=[p.packet_id for p in packets],
        residual_risks=ranked,
        next_phase=next_phase,
        boundary=BOUNDARY,
    )
    h = receipt.compute_hash()
    return StabilizationDirectorReceipt(
        rune=receipt.rune,
        campaign_state_hash=receipt.campaign_state_hash,
        phase=receipt.phase,
        selected_packets=receipt.selected_packets,
        residual_risks=receipt.residual_risks,
        next_phase=receipt.next_phase,
        boundary=receipt.boundary,
        receipt_hash=h,
    )


def packets_detail(phase: Optional[str] = None) -> List[Dict[str, Any]]:
    p = phase or STABILIZATION_PHASES[0]
    return [x.to_dict() for x in _packets_for_phase(p)]


def load_fixture_campaign_state(fixtures_dir: Path) -> StabilizationCampaignState:
    import json

    path = fixtures_dir / "sample_campaign_state.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    scope = StabilizationScope(**data["scope"])
    state = StabilizationCampaignState(
        campaign_id=data["campaign_id"],
        campaign_class=data["campaign_class"],
        phase=data["phase"],
        scope=scope,
        feature_expansion_allowed=data["feature_expansion_allowed"],
        terminal_decisions=data["terminal_decisions"],
        state_hash="",
    )
    return StabilizationCampaignState(
        campaign_id=state.campaign_id,
        campaign_class=state.campaign_class,
        phase=state.phase,
        scope=state.scope,
        feature_expansion_allowed=state.feature_expansion_allowed,
        terminal_decisions=state.terminal_decisions,
        state_hash=state.compute_hash(),
    )
