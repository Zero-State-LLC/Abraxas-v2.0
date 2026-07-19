from __future__ import annotations

import hashlib

from core.brier.calibration_history import CalibrationHistoryPacket
from core.brier.ledger import BrierLedgerEntry
from core.brier.lineage import BrierLineageNode, BrierLineagePacket
from core.brier.operator_review import OperatorBrierReviewPacket
from core.brier.reliability import ReliabilityAggregatePacket
from core.brier.replay import BrierReplayPacket
from core.brier.scores import BrierScorePacket
from core.brier.stabilization import BrierStabilizationPacket


def build_brier_ledger(forecast_packets: dict, outcome_packets: dict) -> dict:
    """Pure builder: returns brier ledger packet. Does not write to disk.

    Publication belongs in scripts/belief/run_brier_ledger.py (sole-writer).
    """
    forecast_hash = forecast_packets["candidate"]["candidate_hash"]
    p = forecast_packets["probability"]["probability"]
    outcome = 1 if outcome_packets.get("binding_status") == "matched" else 0
    score = BrierScorePacket.compute_score(p, outcome)
    score_packet = BrierScorePacket(
        score_id=f"score:{forecast_hash[:10]}",
        forecast_hash=forecast_hash,
        expected_probability=p,
        observed_outcome=outcome,
        brier_score=score,
        deterministic_score_hash=BrierScorePacket.compute_hash(
            forecast_hash, p, outcome, score
        ),
    )
    ledger_hash = hashlib.sha256(
        f"{forecast_hash}|{score_packet.deterministic_score_hash}".encode()
    ).hexdigest()
    ledger = BrierLedgerEntry(
        ledger_entry_id=f"ledger:{ledger_hash[:10]}",
        forecast_hash=forecast_hash,
        score_hash=score_packet.deterministic_score_hash,
        calibration_hash=forecast_packets["calibration"]["deterministic_calibration_hash"],
        ledger_generation=1,
        deterministic_ledger_hash=BrierLedgerEntry.compute_hash(
            forecast_hash,
            score_packet.deterministic_score_hash,
            forecast_packets["calibration"]["deterministic_calibration_hash"],
            1,
        ),
    )
    history = CalibrationHistoryPacket(
        calibration_history_id=f"hist:{forecast_hash[:10]}",
        forecast_hash=forecast_hash,
        calibration_scores=[forecast_packets["calibration"]["calibration_score"]],
        moving_average=CalibrationHistoryPacket.compute_average(
            [forecast_packets["calibration"]["calibration_score"]]
        ),
        deterministic_history_hash=CalibrationHistoryPacket.compute_hash(
            forecast_hash,
            [forecast_packets["calibration"]["calibration_score"]],
            CalibrationHistoryPacket.compute_average(
                [forecast_packets["calibration"]["calibration_score"]]
            ),
        ),
    )
    rel_score = round(max(0.0, 1.0 - score), 6)
    reliability = ReliabilityAggregatePacket(
        reliability_id=f"rel:{forecast_hash[:10]}",
        forecast_hashes=[forecast_hash],
        average_brier=score,
        calibration_average=history.moving_average,
        reliability_score=rel_score,
        deterministic_reliability_hash=ReliabilityAggregatePacket.compute_hash(
            [forecast_hash], score, history.moving_average, rel_score
        ),
    )
    replay = BrierReplayPacket(
        replay_id=f"replay:{ledger_hash[:10]}",
        ledger_hash=ledger_hash,
        deterministic_match=True,
        replayed_scores=[score_packet.score_id],
        mismatched_scores=[],
    )
    nodes = [
        BrierLineageNode(
            score_hash=score_packet.deterministic_score_hash,
            generation=0,
            calibration_hash=ledger.calibration_hash,
        )
    ]
    lineage = BrierLineagePacket(
        lineage_id=f"lineage:{ledger_hash[:10]}",
        lineage_depth=1,
        lineage_nodes=nodes,
        deterministic_lineage_hash=BrierLineagePacket.compute_hash(nodes),
    )
    stabilization = BrierStabilizationPacket(
        stabilization_id=f"stab:{ledger_hash[:10]}",
        ledger_hash=ledger_hash,
        replay_match_count=1,
        replay_failure_count=0,
        reliability_score=reliability.reliability_score,
        stabilization_window=3,
        stabilization_state="stable",
    )
    review = OperatorBrierReviewPacket(
        review_id=f"review:{ledger_hash[:10]}",
        ledger_hash=ledger_hash,
        reliability_score=reliability.reliability_score,
        replay_failures=0,
        pending_actions=["operator_review_required"],
    )
    return {
        "score": score_packet.model_dump(),
        "ledger": ledger.model_dump(),
        "calibration_history": history.model_dump(),
        "reliability": reliability.model_dump(),
        "replay": replay.model_dump(),
        "lineage": lineage.model_dump(),
        "stabilization": stabilization.model_dump(),
        "review": review.model_dump(),
    }


def run_brier_ledger(forecast_packets: dict, outcome_packets: dict) -> dict:
    """Compatibility alias for build_brier_ledger (no disk I/O as of WP-D)."""
    return build_brier_ledger(forecast_packets, outcome_packets)
