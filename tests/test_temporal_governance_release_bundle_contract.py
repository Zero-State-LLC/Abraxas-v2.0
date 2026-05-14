import json
from dataclasses import replace, asdict
from pathlib import Path
from core.temporal_release_bundle.bundle import canonical_temporal_governance_release_bundle_json, temporal_governance_release_bundle_hash, derive_temporal_governance_release_bundle, write_temporal_governance_release_bundle_contract_audit
from core.temporal_release_bundle.validator import validate_temporal_governance_release_bundle

def test_release_bundle_contract(tmp_path):
    assert derive_temporal_governance_release_bundle([]).bundle_status in {"NOT_COMPUTABLE","INSUFFICIENT_RELEASE_INPUTS"}
    assert derive_temporal_governance_release_bundle([{"type":"TEMPORAL_OPERATOR_BRIEF_BUNDLE"}]).bundle_status=="RELEASE_RECONCILED"
    assert derive_temporal_governance_release_bundle([{"warning":True}]).bundle_status=="RELEASE_RECONCILED_WITH_WARNINGS"
    assert derive_temporal_governance_release_bundle([{"missing_artifact":True}]).bundle_status in {"RELEASE_INCOMPLETE","RELEASE_BLOCKED"}
    assert derive_temporal_governance_release_bundle([{"test_failed":True}]).bundle_status=="RELEASE_BLOCKED"
    assert derive_temporal_governance_release_bundle([{"no_diff":True}]).bundle_status in {"RELEASE_NO_DIFF_RECORDED","RELEASE_RECONCILED_WITH_WARNINGS"}
    assert derive_temporal_governance_release_bundle([{"operator_review_required":True}]).bundle_status=="OPERATOR_REVIEW_REQUIRED"
    b=derive_temporal_governance_release_bundle([{"missing_artifact":True,"test_failed":True,"type":"NOT_COMPUTABLE"}])
    assert any((not a.exists) for a in b.artifact_refs)
    assert any(t.test_status=="FAIL" for t in b.test_refs)
    assert any(r.input_ref_type=="NOT_COMPUTABLE" for r in b.input_refs)
    req={"AUDIT_ONLY","PROJECTION_ONLY","NON_AUTHORITATIVE","NO_EXECUTION","NO_MUTATION","NO_ROLLBACK","NO_PROMOTION","NO_ROUTING","NO_TIMELINE_COLLAPSE","NO_CANONICAL_SELECTION","NO_REPLAY_NORMALIZATION","NO_GLOBAL_RUNTIME_ACTIVATION"}
    assert req.issubset({x.badge_type for x in b.constraint_badges})
    for bad in [replace(b,audit_only=False),replace(b,projection_only=False),replace(b,bundle_authoritative=True),replace(b,inference_authority_allowed=True),replace(b,action_authorization_allowed=True),replace(b,execution_allowed=True),replace(b,mutation_allowed=True),replace(b,rollback_allowed=True),replace(b,promotion_allowed=True),replace(b,routing_change_allowed=True),replace(b,replay_normalization_allowed=True),replace(b,canonical_selection_allowed=True),replace(b,global_runtime_activation_allowed=True),replace(b,artifact_refs=(replace(b.artifact_refs[0],mutation_allowed=True),)),replace(b,commit_refs=(replace(b.commit_refs[0],promotion_allowed=True),)),replace(b,commit_refs=(replace(b.commit_refs[0],rollback_allowed=True),)),replace(b,recommendations=(replace(b.recommendations[0],execution_allowed=True),)),replace(b,recommendations=(replace(b.recommendations[0],routing_change_allowed=True),)),replace(b,recommendations=(replace(b.recommendations[0],promotion_allowed=True),)),replace(b,recommendations=(replace(b.recommendations[0],rollback_allowed=True),))]:
        assert validate_temporal_governance_release_bundle(bad).status=="BLOCKED"
    assert temporal_governance_release_bundle_hash(replace(b,bundle_hash="x"))==b.bundle_hash
    assert canonical_temporal_governance_release_bundle_json(b)==canonical_temporal_governance_release_bundle_json(b)
    schema=json.loads(Path("contracts/temporal_release_bundle/temporal_governance_release_bundle.v1.schema.json").read_text())
    for k in schema["required"]:
        assert k in asdict(b)
    h=write_temporal_governance_release_bundle_contract_audit(tmp_path)
    text=(tmp_path/"out/audit/temporal_governance_release_bundle_contract.latest.json").read_text()
    assert text.endswith("\n") and h
