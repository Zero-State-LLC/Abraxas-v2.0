from __future__ import annotations
import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping
from .models import *

def _canonical_json(d:object)->str:return json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _sha256_text(t:str)->str:return hashlib.sha256(t.encode()).hexdigest()
_REQUIRED_BADGES={"PROJECTION_ONLY","NON_AUTHORITATIVE","NO_INFERENCE_AUTHORITY","NO_ACTION_AUTHORIZATION","NO_EXECUTION","NO_MUTATION","NO_ROUTING","NO_TIMELINE_COLLAPSE","NO_CANONICAL_SELECTION","NO_REPLAY_NORMALIZATION"}

def validate_temporal_governance_operator_brief_bundle(brief: TemporalGovernanceOperatorBriefBundle | Mapping[str,Any])->TemporalOperatorBriefValidationReport:
    b=brief if isinstance(brief,TemporalGovernanceOperatorBriefBundle) else TemporalGovernanceOperatorBriefBundle(**dict(brief))
    f=[]; status="PASS"
    if (not b.projection_only) or b.brief_authoritative or b.inference_authority_allowed or b.action_authorization_allowed or b.execution_allowed or b.mutation_allowed or b.rollback_allowed or b.promotion_allowed or b.routing_change_allowed or b.timeline_collapse_allowed or b.canonical_selection_allowed or b.replay_normalization_allowed or b.adapter_activation_allowed or b.auto_transition_allowed: f.append(TemporalOperatorBriefValidationFinding("FLAGS_FORBIDDEN","error","top-level flags violate projection-only policy.")); status="BLOCKED"
    if not b.brief_header.projection_only: f.append(TemporalOperatorBriefValidationFinding("HEADER_PROJECTION_REQUIRED","error","header projection flag required.")); status="BLOCKED"
    if any((not s.projection_only) or s.inference_authority_allowed for s in b.sections): f.append(TemporalOperatorBriefValidationFinding("SECTION_FLAGS_FORBIDDEN","error","section flags invalid.")); status="BLOCKED"
    if any(c.action_authorization_allowed or c.execution_allowed or c.mutation_allowed or c.routing_change_allowed for c in b.action_cards): f.append(TemporalOperatorBriefValidationFinding("ACTION_CARD_FLAGS_FORBIDDEN","error","action cards must remain review-only.")); status="BLOCKED"
    if any((not p.included_in_brief) or (not p.provenance_required) or p.canonical_selection_allowed for p in b.provenance_refs): f.append(TemporalOperatorBriefValidationFinding("PROVENANCE_FLAGS_FORBIDDEN","error","provenance invariants failed.")); status="BLOCKED"
    badges={x.badge_type for x in b.constraint_badges if x.required}
    if not _REQUIRED_BADGES.issubset(badges): f.append(TemporalOperatorBriefValidationFinding("REQUIRED_BADGES_MISSING","error","required constraint badges missing.")); status="BLOCKED"
    receipt_hash=_sha256_text(_canonical_json({"status":status,"findings":[asdict(x) for x in f],"brief_id":b.brief_id}))
    return TemporalOperatorBriefValidationReport(status,tuple(f),receipt_hash)
