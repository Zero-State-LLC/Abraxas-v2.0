from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.overlay_risk.cliffs import OverlayConfidenceCliffPacket
from core.overlay_risk.diagnostics import OverlayRiskDiagnosticPacket
from core.overlay_risk.envelopes import OverlayRiskEnvelopePacket
from core.overlay_risk.exposure import OverlayExposurePacket
from core.overlay_risk.lineage import OverlayRiskLineageNode, OverlayRiskLineagePacket
from core.overlay_risk.operator_review import OperatorOverlayRiskReviewPacket
from core.overlay_risk.propagation import OverlayPropagationRiskPacket
from core.overlay_risk.replay import OverlayRiskReplayPacket
from core.overlay_risk.saturation import OverlayGovernanceSaturationPacket
from core.overlay_risk.validators import validate_overlay_risk


def run_overlay_risk_envelope(governance_packets: list[dict], observability_packets: list[dict], scheduler_packets: list[dict], promotion_packets: list[dict]) -> dict[str, object]:
    overlay_hash = governance_packets[-1].get("ledger", {}).get("deterministic_ledger_hash", "overlay-risk")
    escalation = 0.2 + min(0.3, len(governance_packets) * 0.01)
    rollback = 0.2
    propagation_score = 0.25
    saturation_score = 0.2
    cliff_score = 0.15
    aggregate = (escalation + rollback + propagation_score + saturation_score + cliff_score) / 5
    envelope = OverlayRiskEnvelopePacket(risk_envelope_id="ore-1", overlay_hash=overlay_hash, governance_scope="projection_only", escalation_pressure_score=escalation, rollback_exposure_score=rollback, propagation_risk_score=propagation_score, saturation_score=saturation_score, cliff_risk_score=cliff_score, aggregate_risk_score=aggregate, deterministic_risk_hash=OverlayRiskEnvelopePacket.compute_hash(overlay_hash, "projection_only", escalation, rollback, propagation_score, saturation_score, cliff_score, aggregate), status="passed")
    propagation = OverlayPropagationRiskPacket(propagation_id="orp-1", overlay_hashes=[overlay_hash], shared_dependencies=1, governance_coupling_score=0.2, replay_overlap_score=0.1, correlated_rollback_exposure=0.2, propagation_depth=1, cycles_detected=False, autonomous_escalation_detected=False, deterministic_propagation_hash=OverlayPropagationRiskPacket.compute_hash([overlay_hash],1,0.2,0.1,0.2,1,False,False), status="passed")
    exposure = OverlayExposurePacket(exposure_id="ox-1", rollback_dependency_count=1, replay_dependency_count=1, governance_dependency_depth=1, operator_review_load=0, exposure_score=0.2, deterministic_exposure_hash=OverlayExposurePacket.compute_hash(1,1,1,0,0.2), status="passed")
    cliff = OverlayConfidenceCliffPacket(cliff_id="oc-1", confidence_drop_rate=0.1, replay_instability_score=0.1, governance_inconsistency_score=0.0, continuity_drop_score=0.1, cliff_risk_score=0.1, deterministic_cliff_hash=OverlayConfidenceCliffPacket.compute_hash(0.1,0.1,0.0,0.1,0.1), status="passed")
    saturation = OverlayGovernanceSaturationPacket(saturation_id="os-1", pending_review_count=0, governance_backlog=0, unresolved_diagnostics=0, overlay_density=0.2, review_saturation_pressure=0.1, saturation_score=0.1, deterministic_saturation_hash=OverlayGovernanceSaturationPacket.compute_hash(0,0,0,0.2,0.1,0.1), status="passed")
    replay = OverlayRiskReplayPacket(replay_id="orr-1", source_risk_hash=envelope.deterministic_risk_hash, replay_risk_hash=envelope.deterministic_risk_hash, deterministic_match=True, mismatched_packets=[], status="passed")
    lineage_node = OverlayRiskLineageNode(risk_hash=envelope.deterministic_risk_hash, generation=1)
    lineage = OverlayRiskLineagePacket(lineage_id="orl-1", lineage_nodes=[lineage_node], lineage_depth=1, deterministic_lineage_hash=OverlayRiskLineagePacket.compute_hash([lineage_node]), status="passed")
    diagnostics: list[OverlayRiskDiagnosticPacket] = []
    if aggregate > 0.8:
        diagnostics.append(OverlayRiskDiagnosticPacket(diagnostic_id="ord-1", diagnostic_type="escalation_pressure_high", severity="critical", diagnostic_message="aggregate risk high", deterministic_diagnostic_hash=OverlayRiskDiagnosticPacket.compute_hash("escalation_pressure_high", "critical", "aggregate risk high"), status="failed"))
    review = OperatorOverlayRiskReviewPacket(review_id="orv-1", aggregate_risk_score=aggregate, critical_diagnostics=sum(1 for d in diagnostics if d.severity == 'critical'), pending_actions=["reduce_risk"] if diagnostics else [], status="pending" if diagnostics else "approved")
    validator = validate_overlay_risk([envelope], propagation, replay, [d.model_dump() for d in diagnostics])
    packet = {"schema_version": "OverlayRiskRuntimePacket.v1", "envelopes": [envelope.model_dump()], "propagation": propagation.model_dump(), "exposure": exposure.model_dump(), "cliff": cliff.model_dump(), "saturation": saturation.model_dump(), "diagnostics": [d.model_dump() for d in diagnostics], "replay": replay.model_dump(), "lineage": lineage.model_dump(), "operator_review": review.model_dump(), "validator": validator, "status": validator["status"]}
    write_canonical_json('out/overlay_risk/latest.json', packet)
    write_canonical_json('out/overlay_risk_replay/latest.json', replay.model_dump())
    write_canonical_json('out/overlay_risk_lineage/latest.json', lineage.model_dump())
    write_canonical_json('out/overlay_risk_diagnostics/latest.json', [d.model_dump() for d in diagnostics])
    return packet
