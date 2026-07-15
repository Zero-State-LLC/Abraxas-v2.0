"""Campaign Director — stabilization readiness routing (advisory)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

CAMPAIGN_CLASS_STABILIZATION = "STABILIZATION_READINESS"
STABILIZATION_CAMPAIGN_ID = "ABRAXAS_STABILIZATION_READINESS_CAMPAIGN_001"
STABILIZATION_SKILL_RUNNER = "skills/abx-stabilization-readiness/run_advisory.py"


def is_stabilization_campaign(campaign_id: Optional[str] = None, campaign_class: Optional[str] = None) -> bool:
    if campaign_class == CAMPAIGN_CLASS_STABILIZATION:
        return True
    if campaign_id == STABILIZATION_CAMPAIGN_ID:
        return True
    return False


def stabilization_routing_packet(repo_root: Optional[Path] = None) -> Dict[str, Any]:
    """Emit routing metadata for Campaign Director — does not execute structural campaign modes."""
    root = repo_root or Path(".")
    return {
        "campaign_class": CAMPAIGN_CLASS_STABILIZATION,
        "campaign_id": STABILIZATION_CAMPAIGN_ID,
        "feature_expansion_allowed": False,
        "runtime_activation": False,
        "delegated_skill": "abx-stabilization-readiness",
        "runner": STABILIZATION_SKILL_RUNNER,
        "terminal_decisions": [
            "STABILIZATION_ENTRY_READY",
            "STABILIZATION_ENTRY_READY_WITH_BOUNDED_EXCEPTIONS",
            "STABILIZATION_ENTRY_HELD",
        ],
        "evidence_dir": str(root / "out" / "stabilization_readiness"),
        "boundary": "ADVISORY_ONLY | ROUTED_UNDER_CAMPAIGN_DIRECTOR",
    }


def load_stabilization_gate_decision(repo_root: Path) -> Dict[str, Any]:
    path = repo_root / "out" / "stabilization_readiness" / "stabilization_gate_decision.latest.json"
    if not path.exists():
        return {"decision": "NOT_COMPUTABLE", "operator_action_required": True}
    return json.loads(path.read_text(encoding="utf-8"))


def campaign_should_stop_on_terminal(repo_root: Path) -> bool:
    gate = load_stabilization_gate_decision(repo_root)
    decision = gate.get("decision", "")
    return decision in (
        "STABILIZATION_ENTRY_READY",
        "STABILIZATION_ENTRY_READY_WITH_BOUNDED_EXCEPTIONS",
        "STABILIZATION_ENTRY_HELD",
    )