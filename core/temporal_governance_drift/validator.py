from __future__ import annotations
import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping
from .models import *

def _canonical_json(d:object)->str:return json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _sha256_text(t:str)->str:return hashlib.sha256(t.encode()).hexdigest()

def validate_temporal_governance_drift_observatory(observatory: TemporalGovernanceDriftObservatory | Mapping[str,Any])->TemporalDriftValidationReport:
    o = observatory if isinstance(observatory, TemporalGovernanceDriftObservatory) else TemporalGovernanceDriftObservatory(**dict(observatory))
    findings=[]; status="PASS"
    if (not o.projection_only) or o.observatory_authoritative or o.inference_authority_allowed or o.execution_allowed or o.mutation_allowed or o.rollback_allowed or o.promotion_allowed or o.routing_change_allowed or o.timeline_collapse_allowed or o.canonical_selection_allowed or o.replay_normalization_allowed or o.adapter_activation_allowed or o.auto_transition_allowed: findings.append(TemporalDriftValidationFinding("FLAGS_FORBIDDEN","error","top-level flags violate projection-only policy.")); status="BLOCKED"
    if any((not z.lineage_preserved) or z.replay_normalization_allowed or z.canonical_selection_allowed for z in o.drift_zones): findings.append(TemporalDriftValidationFinding("ZONE_FLAGS_FORBIDDEN","error","zone lineage/normalization/selection constraints failed.")); status="BLOCKED"
    if any(v.routing_change_allowed for v in o.drift_vectors): findings.append(TemporalDriftValidationFinding("VECTOR_ROUTING_FORBIDDEN","error","vector routing change forbidden.")); status="BLOCKED"
    if any((not p.blocked_visibility_preserved) or (not p.nondeterminism_visibility_preserved) for p in o.pressure_bands): findings.append(TemporalDriftValidationFinding("VISIBILITY_PRESERVATION_REQUIRED","error","blocked/nondeterminism visibility must be preserved.")); status="BLOCKED"
    if any(f.execution_allowed for f in o.findings): findings.append(TemporalDriftValidationFinding("FINDING_EXECUTION_FORBIDDEN","error","findings execution not allowed.")); status="BLOCKED"
    if any(r.execution_allowed or r.mutation_allowed or r.rollback_allowed or r.promotion_allowed or r.routing_change_allowed or r.timeline_collapse_allowed or r.canonical_selection_allowed or r.replay_normalization_allowed for r in o.recommendations): findings.append(TemporalDriftValidationFinding("RECOMMENDATION_FLAGS_FORBIDDEN","error","recommendation flags invalid.")); status="BLOCKED"
    receipt_hash=_sha256_text(_canonical_json({"status":status,"findings":[asdict(f) for f in findings],"observatory_id":o.observatory_id}))
    return TemporalDriftValidationReport(status,tuple(findings),receipt_hash)
