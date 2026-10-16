from core.moses.contracts import GroundingDisposition, MeaningPacket, MeaningStatus
from core.moses.grounding import compose_grounding_receipt

def _meaning(status=MeaningStatus.provisional, **kwargs):
    return MeaningPacket(meaning_id="meaning-001", status=status, **kwargs)

def test_grounding_requires_evidence():
    r=compose_grounding_receipt(_meaning(), grounding_receipt_id="g-1", grounding_assertions=({"id":"a-1","status":"SUPPORTED"},))
    assert r.grounding_disposition == GroundingDisposition.not_computable

def test_no_implicit_promotion():
    r=compose_grounding_receipt(_meaning(), grounding_receipt_id="g-1", evidence_refs=("e-1",))
    assert r.grounding_disposition == GroundingDisposition.provisional

def test_explicit_support_plus_evidence_resolves():
    r=compose_grounding_receipt(_meaning(), grounding_receipt_id="g-1", evidence_refs=("e-1",), calibration_evidence_refs=("brier-1",), grounding_assertions=({"id":"a-1","status":"SUPPORTED"},))
    assert r.grounding_disposition == GroundingDisposition.resolved

def test_shadow_anomaly_blocks_without_truth_authority():
    r=compose_grounding_receipt(_meaning(), grounding_receipt_id="g-1", evidence_refs=("e-1",), grounding_assertions=({"id":"a-1","status":"SUPPORTED"},), shadow_findings=({"code":"CONTAMINATION","severity":"anomaly","subject_id":"s-1"},))
    assert r.grounding_disposition == GroundingDisposition.not_computable
    assert r.provenance[0]["shadow_authority"] == "DETECTION_ONLY"

def test_upstream_contradiction_preserved():
    r=compose_grounding_receipt(_meaning(MeaningStatus.contradicted, contradictions=("conflict",)), grounding_receipt_id="g-1", evidence_refs=("e-1",), grounding_assertions=({"id":"a-1","status":"SUPPORTED"},))
    assert r.grounding_disposition == GroundingDisposition.contradicted