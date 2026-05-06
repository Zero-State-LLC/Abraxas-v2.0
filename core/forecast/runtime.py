from __future__ import annotations

import hashlib
from pathlib import Path

from core.canonical.json import write_canonical_json
from core.forecast.calibration import ForecastCalibrationPacket
from core.forecast.candidates import ForecastCandidatePacket
from core.forecast.lineage import ForecastLineageNode, ForecastLineagePacket
from core.forecast.operator_review import OperatorForecastReviewPacket
from core.forecast.outcomes import ForecastOutcomeBindingPacket
from core.forecast.probabilities import ForecastProbabilityPacket
from core.forecast.replay import ForecastReplayPacket
from core.forecast.stabilization import ForecastStabilizationPacket


def run_forecast_candidates(oracle_intakes: dict, sandbox_packets: dict, observability_packets: dict) -> dict:
    source_hash = oracle_intakes["intake"]["source_hash"]
    sandbox_hash = sandbox_packets["branch"]["sandbox_state_hash"]
    candidate_hash = hashlib.sha256(f"{source_hash}|{sandbox_hash}|{observability_packets.get('telemetry_hash','unknown')}".encode()).hexdigest()
    candidate = ForecastCandidatePacket(forecast_id=f"forecast:{candidate_hash[:10]}", source_intake_hash=source_hash, sandbox_branch_hash=sandbox_hash, candidate_type="sandbox", candidate_hash=candidate_hash, deterministic_candidate_hash=ForecastCandidatePacket.compute_hash(source_hash, sandbox_hash, "sandbox", candidate_hash), forecast_status="candidate")
    calibration = ForecastCalibrationPacket(calibration_id=f"cal:{candidate_hash[:10]}", forecast_hash=candidate_hash, calibration_method="replay_consistency", calibration_score=0.8, deterministic_calibration_hash=ForecastCalibrationPacket.compute_hash(candidate_hash, "replay_consistency", 0.8))
    probability = ForecastProbabilityPacket(probability_id=f"prob:{candidate_hash[:10]}", forecast_hash=candidate_hash, probability=0.6, calibration_score=calibration.calibration_score, deterministic_probability_hash=ForecastProbabilityPacket.compute_hash(candidate_hash, 0.6, calibration.calibration_score))
    replay = ForecastReplayPacket(replay_id=f"replay:{candidate_hash[:10]}", forecast_hash=candidate_hash, deterministic_match=True, replayed_probabilities=[probability.probability_id], mismatched_probabilities=[])
    binding = ForecastOutcomeBindingPacket(binding_id=f"bind:{candidate_hash[:10]}", forecast_hash=candidate_hash, expected_outcome_hash=hashlib.sha256(candidate_hash.encode()).hexdigest(), binding_status="unresolved")
    nodes = [ForecastLineageNode(forecast_hash=source_hash, generation=0), ForecastLineageNode(forecast_hash=candidate_hash, parent_hash=source_hash, generation=1, calibration_hash=calibration.deterministic_calibration_hash)]
    lineage = ForecastLineagePacket(lineage_id=f"lineage:{candidate_hash[:10]}", lineage_depth=2, lineage_nodes=nodes, deterministic_lineage_hash=ForecastLineagePacket.compute_hash(nodes))
    stabilization = ForecastStabilizationPacket(stabilization_id=f"stab:{candidate_hash[:10]}", forecast_hash=candidate_hash, replay_match_count=1, replay_failure_count=0, calibration_score=calibration.calibration_score, unresolved_bindings=1, stabilization_window=3, stabilization_state="stabilizing")
    review = OperatorForecastReviewPacket(review_id=f"review:{candidate_hash[:10]}", forecast_hash=candidate_hash, stabilization_state=stabilization.stabilization_state, calibration_score=calibration.calibration_score, unresolved_bindings=1, pending_actions=["operator_review_required"])
    out = {"candidate": candidate.model_dump(), "probability": probability.model_dump(), "replay": replay.model_dump(), "calibration": calibration.model_dump(), "outcome_binding": binding.model_dump(), "lineage": lineage.model_dump(), "stabilization": stabilization.model_dump(), "review": review.model_dump()}
    write_canonical_json(Path("out/forecast/latest.json"), out)
    write_canonical_json(Path("out/forecast_lineage/latest.json"), lineage.model_dump())
    write_canonical_json(Path("out/forecast_calibration/latest.json"), calibration.model_dump())
    write_canonical_json(Path("out/forecast_replay/latest.json"), replay.model_dump())
    return out
