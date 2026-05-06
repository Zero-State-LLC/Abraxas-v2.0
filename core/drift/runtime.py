from __future__ import annotations

from pathlib import Path

from core.canonical.json import write_canonical_json
from core.drift.calibration import DriftCalibrationPacket
from core.drift.lineage import DriftLineageNode, DriftLineagePacket
from core.drift.operator_review import OperatorDriftReviewPacket
from core.drift.overlays import WeightOverlayPacket
from core.drift.proposals import WeightDriftProposalPacket
from core.drift.reliability import DriftReliabilityPacket
from core.drift.replay import DriftReplayPacket
from core.drift.stabilization import DriftStabilizationPacket


def run_weight_drift_simulation(reliability_packets: dict, brier_packets: dict, forecast_packets: dict) -> dict:
    source_reliability_hash = reliability_packets["deterministic_reliability_hash"]
    source_brier_hash = brier_packets["ledger"]["deterministic_ledger_hash"]
    bounded_weight = min(1.0, max(0.0, forecast_packets["probability"]["probability"] + 0.05))
    proposal = WeightDriftProposalPacket(proposal_id=f"drift:{source_brier_hash[:10]}", source_reliability_hash=source_reliability_hash, source_brier_hash=source_brier_hash, proposed_weight_delta=0.05, bounded_weight=bounded_weight, deterministic_proposal_hash=WeightDriftProposalPacket.compute_hash(source_reliability_hash, source_brier_hash, 0.05, bounded_weight), proposal_status="simulated")
    overlay = WeightOverlayPacket(overlay_id=f"overlay:{proposal.deterministic_proposal_hash[:10]}", proposal_hash=proposal.deterministic_proposal_hash, overlay_generation=1, overlay_weight=bounded_weight, deterministic_overlay_hash=WeightOverlayPacket.compute_hash(proposal.deterministic_proposal_hash, 1, bounded_weight))
    calibration = DriftCalibrationPacket(calibration_id=f"cal:{overlay.deterministic_overlay_hash[:10]}", overlay_hash=overlay.deterministic_overlay_hash, replay_consistency=1.0, reliability_consistency=0.9, stabilization_consistency=0.9, calibration_score=0.933333, deterministic_calibration_hash=DriftCalibrationPacket.compute_hash(overlay.deterministic_overlay_hash, 1.0, 0.9, 0.9, 0.933333))
    reliability = DriftReliabilityPacket(reliability_id=f"rel:{overlay.deterministic_overlay_hash[:10]}", overlay_hashes=[overlay.deterministic_overlay_hash], average_reliability=reliability_packets["reliability_score"], average_brier=brier_packets["reliability"]["average_brier"], drift_confidence=0.9, deterministic_reliability_hash=DriftReliabilityPacket.compute_hash([overlay.deterministic_overlay_hash], reliability_packets["reliability_score"], brier_packets["reliability"]["average_brier"], 0.9))
    replay = DriftReplayPacket(replay_id=f"replay:{overlay.deterministic_overlay_hash[:10]}", overlay_hash=overlay.deterministic_overlay_hash, deterministic_match=True, replayed_overlays=[overlay.overlay_id], mismatched_overlays=[])
    nodes = [DriftLineageNode(overlay_hash=overlay.deterministic_overlay_hash, generation=0, calibration_hash=calibration.deterministic_calibration_hash)]
    lineage = DriftLineagePacket(lineage_id=f"lineage:{overlay.deterministic_overlay_hash[:10]}", lineage_depth=1, lineage_nodes=nodes, deterministic_lineage_hash=DriftLineagePacket.compute_hash(nodes))
    stabilization = DriftStabilizationPacket(stabilization_id=f"stab:{overlay.deterministic_overlay_hash[:10]}", overlay_hash=overlay.deterministic_overlay_hash, replay_match_count=1, replay_failure_count=0, calibration_score=calibration.calibration_score, drift_confidence=reliability.drift_confidence, stabilization_window=3, stabilization_state="stable")
    review = OperatorDriftReviewPacket(review_id=f"review:{overlay.deterministic_overlay_hash[:10]}", overlay_hash=overlay.deterministic_overlay_hash, calibration_score=calibration.calibration_score, drift_confidence=reliability.drift_confidence, replay_failures=0, pending_actions=["operator_review_required"])
    out = {"proposal": proposal.model_dump(), "overlay": overlay.model_dump(), "calibration": calibration.model_dump(), "reliability": reliability.model_dump(), "replay": replay.model_dump(), "lineage": lineage.model_dump(), "stabilization": stabilization.model_dump(), "review": review.model_dump()}
    write_canonical_json(Path("out/drift/latest.json"), out)
    write_canonical_json(Path("out/drift_lineage/latest.json"), lineage.model_dump())
    write_canonical_json(Path("out/drift_reliability/latest.json"), reliability.model_dump())
    write_canonical_json(Path("out/drift_replay/latest.json"), replay.model_dump())
    return out
