from __future__ import annotations
import hashlib, json
from dataclasses import asdict
from typing import Any, Mapping
from .models import *

def _canonical_json(d:object)->str:return json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _sha256_text(t:str)->str:return hashlib.sha256(t.encode()).hexdigest()
_REQ={"AUDIT_ONLY","PROJECTION_ONLY","NON_AUTHORITATIVE","NO_EXECUTION","NO_MUTATION","NO_ROLLBACK","NO_PROMOTION","NO_ROUTING","NO_TIMELINE_COLLAPSE","NO_CANONICAL_SELECTION","NO_REPLAY_NORMALIZATION","NO_GLOBAL_RUNTIME_ACTIVATION"}

def validate_temporal_governance_release_bundle(bundle: TemporalGovernanceReleaseBundle | Mapping[str,Any])->TemporalReleaseValidationReport:
    b=bundle if isinstance(bundle,TemporalGovernanceReleaseBundle) else TemporalGovernanceReleaseBundle(**dict(bundle))
    f=[]; status="PASS"
    if (not b.audit_only) or (not b.projection_only) or b.bundle_authoritative or b.inference_authority_allowed or b.action_authorization_allowed or b.execution_allowed or b.mutation_allowed or b.rollback_allowed or b.promotion_allowed or b.routing_change_allowed or b.timeline_collapse_allowed or b.canonical_selection_allowed or b.replay_normalization_allowed or b.adapter_activation_allowed or b.auto_transition_allowed or b.global_runtime_activation_allowed: f.append(TemporalReleaseValidationFinding("FLAGS_FORBIDDEN","error","top-level flags violate policy.")); status="BLOCKED"
    if any(a.mutation_allowed for a in b.artifact_refs): f.append(TemporalReleaseValidationFinding("ARTIFACT_MUTATION_FORBIDDEN","error","artifact mutation forbidden.")); status="BLOCKED"
    if any((not c.included_in_release) or c.promotion_allowed or c.rollback_allowed for c in b.commit_refs): f.append(TemporalReleaseValidationFinding("COMMIT_FLAGS_FORBIDDEN","error","commit flags invalid.")); status="BLOCKED"
    if any(not t.required for t in b.test_refs): f.append(TemporalReleaseValidationFinding("TEST_REQUIRED_FLAG","error","all tests must be required.")); status="BLOCKED"
    if any(s.canonical_selection_allowed for s in b.schema_refs): f.append(TemporalReleaseValidationFinding("SCHEMA_CANONICAL_FORBIDDEN","error","schema canonical selection forbidden.")); status="BLOCKED"
    badges={x.badge_type for x in b.constraint_badges if x.required}
    if not _REQ.issubset(badges): f.append(TemporalReleaseValidationFinding("REQUIRED_BADGES_MISSING","error","required badges missing.")); status="BLOCKED"
    if any(r.action_authorization_allowed or r.execution_allowed or r.mutation_allowed or r.rollback_allowed or r.promotion_allowed or r.routing_change_allowed or r.timeline_collapse_allowed or r.canonical_selection_allowed or r.replay_normalization_allowed for r in b.recommendations): f.append(TemporalReleaseValidationFinding("RECOMMENDATION_FLAGS_FORBIDDEN","error","recommendations must remain non-authorizing.")); status="BLOCKED"
    receipt_hash=_sha256_text(_canonical_json({"status":status,"findings":[asdict(x) for x in f],"bundle_id":b.bundle_id}))
    return TemporalReleaseValidationReport(status,tuple(f),receipt_hash)
