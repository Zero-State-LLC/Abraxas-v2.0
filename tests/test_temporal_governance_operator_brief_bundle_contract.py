import json
from dataclasses import replace, asdict
from pathlib import Path
from core.temporal_operator_brief.brief import *
from core.temporal_operator_brief.validator import validate_temporal_governance_operator_brief_bundle

def test_operator_brief_bundle_contract(tmp_path):
    assert derive_temporal_governance_operator_brief_bundle([]).brief_status in {"NOT_COMPUTABLE","INSUFFICIENT_WEATHER_INPUTS"}
    assert derive_temporal_governance_operator_brief_bundle([{"type":"TEMPORAL_GOVERNANCE_WEATHER_REPORT_PACKET","weather_status":"WEATHER_CLEAR"}]).brief_status=="BRIEF_CLEAR"
    assert derive_temporal_governance_operator_brief_bundle([{"type":"TEMPORAL_GOVERNANCE_WEATHER_REPORT_PACKET","weather_status":"DRIFT_FRONT_PRESENT","drift":True}]).brief_status in {"BRIEF_DRIFT","BRIEF_WATCH"}
    assert derive_temporal_governance_operator_brief_bundle([{"weather_status":"FRACTURE_STORM_PRESENT","fracture":True}]).brief_status=="BRIEF_FRACTURE"
    assert derive_temporal_governance_operator_brief_bundle([{"weather_status":"BLOCKED_HISTORY_FRONT_PRESENT","blocked":True}]).brief_status=="BRIEF_BLOCKED_HISTORY"
    assert derive_temporal_governance_operator_brief_bundle([{"weather_status":"NONDETERMINISM_FRONT_PRESENT","nondeterminism":True}]).brief_status=="BRIEF_NONDETERMINISM"
    assert derive_temporal_governance_operator_brief_bundle([{"weather_status":"STALE_PROPAGATION_PRESENT","stale":True}]).brief_status=="BRIEF_STALE_PROPAGATION"
    assert derive_temporal_governance_operator_brief_bundle([{"weather_status":"OPERATOR_LOAD_HIGH","overload":True}]).brief_status in {"BRIEF_OPERATOR_LOAD","OPERATOR_REVIEW_REQUIRED"}
    b=derive_temporal_governance_operator_brief_bundle([{"weather_status":"BLOCKED_HISTORY_FRONT_PRESENT","blocked":True,"nondeterminism":True,"fracture":True,"hash":"hx"}])
    assert any("BLOCKED_HISTORY" in s.section_type for s in b.sections) and any("BLOCKED_HISTORY" in c.card_type for c in b.action_cards)
    assert any("NONDETERMINISM" in s.section_type for s in b.sections) and any("NONDETERMINISM" in c.card_type for c in b.action_cards)
    assert any("FRACTURE" in s.section_type for s in b.sections) and any("FRACTURE" in c.card_type for c in b.action_cards)
    assert b.provenance_refs and all(p.included_in_brief and p.provenance_required for p in b.provenance_refs)
    req={"PROJECTION_ONLY","NON_AUTHORITATIVE","NO_INFERENCE_AUTHORITY","NO_ACTION_AUTHORIZATION","NO_EXECUTION","NO_MUTATION","NO_ROUTING","NO_TIMELINE_COLLAPSE","NO_CANONICAL_SELECTION","NO_REPLAY_NORMALIZATION"}
    assert req.issubset({x.badge_type for x in b.constraint_badges})
    for bad in [replace(b,projection_only=False),replace(b,brief_authoritative=True),replace(b,inference_authority_allowed=True),replace(b,action_authorization_allowed=True),replace(b,execution_allowed=True),replace(b,mutation_allowed=True),replace(b,rollback_allowed=True),replace(b,promotion_allowed=True),replace(b,routing_change_allowed=True),replace(b,replay_normalization_allowed=True),replace(b,canonical_selection_allowed=True),replace(b,action_cards=(replace(b.action_cards[0],execution_allowed=True),)),replace(b,action_cards=(replace(b.action_cards[0],routing_change_allowed=True),)),replace(b,provenance_refs=(replace(b.provenance_refs[0],canonical_selection_allowed=True),))]:
        assert validate_temporal_governance_operator_brief_bundle(bad).status=="BLOCKED"
    assert temporal_governance_operator_brief_bundle_hash(replace(b,brief_hash="x"))==b.brief_hash
    assert canonical_temporal_governance_operator_brief_bundle_json(b)==canonical_temporal_governance_operator_brief_bundle_json(b)
    schema=json.loads(Path("contracts/temporal_operator_brief/temporal_governance_operator_brief_bundle.v1.schema.json").read_text())
    for k in schema["required"]: assert k in asdict(b)
    h=write_temporal_governance_operator_brief_bundle_contract_audit(tmp_path)
    text=(tmp_path/"out/audit/temporal_governance_operator_brief_bundle_contract.latest.json").read_text()
    assert text.endswith("\n") and h
