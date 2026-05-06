from __future__ import annotations

from core.brier.reliability import ReliabilityAggregatePacket
from core.brier.replay import BrierReplayPacket


def validate_brier_ledger(ledger: dict, replay_packet: BrierReplayPacket, reliability_packet: ReliabilityAggregatePacket) -> dict[str, object]:
    gates = [
        {"gate": "brier_replay_gate", "passed": replay_packet.deterministic_match, "reason": "replay mismatch invalidates stabilization"},
        {"gate": "brier_score_gate", "passed": 0 <= ledger.get("expected_probability", 0.0) <= 1, "reason": "invalid probabilities fail closed"},
        {"gate": "brier_reliability_gate", "passed": reliability_packet.reliability_score >= 0.0, "reason": "reliability present"},
        {"gate": "brier_stabilization_gate", "passed": not replay_packet.mismatched_scores, "reason": "unresolved mismatches block stable promotion"},
    ]
    return {"status": "doctrine_compliant" if all(g["passed"] for g in gates) else "repair_required", "gate_results": gates}
