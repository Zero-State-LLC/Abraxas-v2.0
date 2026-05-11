from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import *


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_temporal_compression_digest_projection(digest: TemporalClimateCompressionDigestProjection | Mapping[str, Any]) -> TemporalDigestValidationReport:
    d = digest if isinstance(digest, TemporalClimateCompressionDigestProjection) else TemporalClimateCompressionDigestProjection(**dict(digest))
    findings=[]; status="PASS"
    if (not d.projection_only) or d.digest_authoritative or d.inference_authority_allowed or d.action_authorization_allowed or d.execution_allowed or d.mutation_allowed or d.rollback_allowed or d.promotion_allowed or d.routing_change_allowed or d.timeline_collapse_allowed or d.canonical_selection_allowed or d.replay_normalization_allowed or d.adapter_activation_allowed or d.auto_transition_allowed:
        findings.append(TemporalDigestValidationFinding("FLAGS_FORBIDDEN","error","digest must be projection-only, authority-null, execution/mutation/rollback/promotion/routing/collapse/selection/normalization/activation/transition false.")); status="BLOCKED"
    if any((not s.projection_only) or s.inference_authority_allowed for s in d.sections):
        findings.append(TemporalDigestValidationFinding("SECTION_FLAGS_FORBIDDEN","error","sections must be projection_only and inference_authority_allowed=false.")); status="BLOCKED"
    if any((not c.lineage_preserved) or c.replay_normalization_allowed or c.canonical_selection_allowed for c in d.signal_cards):
        findings.append(TemporalDigestValidationFinding("CARD_PRESERVATION_REQUIRED","error","cards must preserve lineage and disallow normalization/canonical selection.")); status="BLOCKED"
    if any((not p.included_in_digest) or (not p.provenance_required) for p in d.provenance_refs):
        findings.append(TemporalDigestValidationFinding("PROVENANCE_REQUIRED","error","provenance refs must be included and required.")); status="BLOCKED"
    if any(r.execution_allowed or r.mutation_allowed or r.routing_change_allowed or r.replay_normalization_allowed or r.canonical_selection_allowed for r in d.recommendations):
        findings.append(TemporalDigestValidationFinding("RECOMMENDATION_FLAGS_FORBIDDEN","error","recommendations cannot execute/mutate/route/normalize/select.")); status="BLOCKED"
    receipt_hash=_sha256_text(_canonical_json({"status":status,"findings":[asdict(f) for f in findings],"digest_id":d.digest_id}))
    return TemporalDigestValidationReport(status, tuple(findings), receipt_hash)
