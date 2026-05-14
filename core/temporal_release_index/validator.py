from __future__ import annotations
import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping
from .models import *

def _canonical_json(d:object)->str:return json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _sha256_text(t:str)->str:return hashlib.sha256(t.encode()).hexdigest()

def validate_temporal_governance_release_index_registry(registry: TemporalGovernanceReleaseIndexRegistry|Mapping[str,Any])->TemporalReleaseIndexValidationReport:
    r=registry if isinstance(registry,TemporalGovernanceReleaseIndexRegistry) else TemporalGovernanceReleaseIndexRegistry(**dict(registry))
    f=[]; status="PASS"
    if (not r.audit_only) or (not r.projection_only) or r.registry_authoritative or r.release_activation_allowed or r.execution_allowed or r.mutation_allowed or r.rollback_allowed or r.promotion_allowed or r.routing_change_allowed or r.timeline_collapse_allowed or r.canonical_selection_allowed or r.replay_normalization_allowed or r.adapter_activation_allowed or r.auto_transition_allowed or r.global_runtime_activation_allowed:
        f.append(TemporalReleaseIndexValidationFinding("FLAGS_FORBIDDEN","error","top-level flags violate policy.")); status="BLOCKED"
    if any((not e.included_in_index) or e.activation_allowed or e.promotion_allowed or e.rollback_allowed for e in r.release_entries): f.append(TemporalReleaseIndexValidationFinding("ENTRY_FLAGS_FORBIDDEN","error","entry flags invalid.")); status="BLOCKED"
    if any((not l.lineage_preserved) or l.canonical_selection_allowed or l.timeline_collapse_allowed for l in r.lineage_refs): f.append(TemporalReleaseIndexValidationFinding("LINEAGE_FLAGS_FORBIDDEN","error","lineage flags invalid.")); status="BLOCKED"
    if any(x.execution_allowed for x in r.findings): f.append(TemporalReleaseIndexValidationFinding("FINDING_EXECUTION_FORBIDDEN","error","finding execution forbidden.")); status="BLOCKED"
    if any(x.action_authorization_allowed or x.execution_allowed or x.mutation_allowed or x.rollback_allowed or x.promotion_allowed or x.routing_change_allowed or x.timeline_collapse_allowed or x.canonical_selection_allowed or x.replay_normalization_allowed for x in r.recommendations): f.append(TemporalReleaseIndexValidationFinding("RECOMMENDATION_FLAGS_FORBIDDEN","error","recommendation flags invalid.")); status="BLOCKED"
    s=r.summary
    if r.registry_status=="INDEX_RECONCILED" and (s.blocked_count!=0 or s.warn_count!=0 or s.release_count<=0): f.append(TemporalReleaseIndexValidationFinding("STATUS_INVARIANT_INDEX_RECONCILED","error","INDEX_RECONCILED invariants violated.")); status="BLOCKED"
    if r.registry_status=="INDEX_RECONCILED_WITH_WARNINGS" and (s.warn_count<=0 or s.blocked_count!=0): f.append(TemporalReleaseIndexValidationFinding("STATUS_INVARIANT_INDEX_RECONCILED_WITH_WARNINGS","error","INDEX_RECONCILED_WITH_WARNINGS invariants violated.")); status="BLOCKED"
    if r.registry_status=="INDEX_BLOCKED" and s.blocked_count<=0: f.append(TemporalReleaseIndexValidationFinding("STATUS_INVARIANT_INDEX_BLOCKED","error","INDEX_BLOCKED invariants violated.")); status="BLOCKED"
    if r.registry_status=="INDEX_EMPTY" and s.release_count!=0: f.append(TemporalReleaseIndexValidationFinding("STATUS_INVARIANT_INDEX_EMPTY","error","INDEX_EMPTY invariants violated.")); status="BLOCKED"
    if r.registry_status=="INDEX_NO_DIFF_RECORDED" and s.no_diff_count<=0: f.append(TemporalReleaseIndexValidationFinding("STATUS_INVARIANT_INDEX_NO_DIFF_RECORDED","error","INDEX_NO_DIFF_RECORDED invariants violated.")); status="BLOCKED"
    if r.registry_status=="OPERATOR_REVIEW_REQUIRED" and (s.operator_review_required_count<=0 or not any(x.operator_review_required for x in r.recommendations)): f.append(TemporalReleaseIndexValidationFinding("STATUS_INVARIANT_OPERATOR_REVIEW_REQUIRED","error","OPERATOR_REVIEW_REQUIRED invariants violated.")); status="BLOCKED"
    if r.created_by_lane=="SHADOW" and r.registry_status!="DRAFT": f.append(TemporalReleaseIndexValidationFinding("LANE_SHADOW_DRAFT_ONLY","error","SHADOW lane may draft only.")); status="BLOCKED"
    if r.created_by_lane=="PROJECTION" and not r.projection_only: f.append(TemporalReleaseIndexValidationFinding("LANE_PROJECTION_ONLY","error","PROJECTION lane must stay projection-only.")); status="BLOCKED"
    receipt_hash=_sha256_text(_canonical_json({"status":status,"findings":[asdict(x) for x in f],"registry_id":r.registry_id}))
    return TemporalReleaseIndexValidationReport(status,tuple(f),receipt_hash)
