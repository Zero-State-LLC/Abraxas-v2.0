from __future__ import annotations
import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping
from .models import ReliabilityScopeRef, ReliabilityMetricSnapshot, ReliabilityRecommendation, ReliabilityAdvisoryPolicy, AuthorityRef, SourceReliabilityAdvisory, ReliabilityValidationFinding, ReliabilityValidationReport
def _canonical_json(data: object) -> str: return json.dumps(data, sort_keys=True, separators=(",",":"), ensure_ascii=False)
def _sha256_text(text: str) -> str: return hashlib.sha256(text.encode("utf-8")).hexdigest()
def _to_advisory(a: SourceReliabilityAdvisory | Mapping[str, Any]) -> SourceReliabilityAdvisory:
    if isinstance(a, SourceReliabilityAdvisory):
        return a
    d=dict(a)
    return SourceReliabilityAdvisory(d["schema_version"],d["advisory_id"],d["input_calibration_ledger_id"],d["input_calibration_hash"],ReliabilityScopeRef(**d["scope_ref"]),ReliabilityMetricSnapshot(**d["metric_snapshot"]),tuple(ReliabilityRecommendation(**x) for x in d["recommendations"]),d["advisory_status"],ReliabilityAdvisoryPolicy(**d["advisory_policy"]),d["created_by_lane"],AuthorityRef(**d["authority_ref"]) if d.get("authority_ref") else None,d["mutation_allowed"],d["advisory_hash"])
def validate_source_reliability_advisory(advisory: SourceReliabilityAdvisory | Mapping[str, Any]) -> ReliabilityValidationReport:
    o=_to_advisory(advisory)
    findings=[]
    status="PASS"
    if o.schema_version!="SourceReliabilityAdvisory.v1":
        findings.append(ReliabilityValidationFinding("SCHEMA_VERSION_INVALID","not_computable","schema_version must be SourceReliabilityAdvisory.v1."))
        status="NOT_COMPUTABLE"
    if o.mutation_allowed:
        findings.append(ReliabilityValidationFinding("MUTATION_FORBIDDEN","error","mutation_allowed must be false."))
        status="BLOCKED"
    if o.advisory_policy.mutation_policy!="ADVISORY_ONLY_NO_MUTATION":
        findings.append(ReliabilityValidationFinding("MUTATION_POLICY_INVALID","error","advisory_policy.mutation_policy must be ADVISORY_ONLY_NO_MUTATION."))
        status="BLOCKED"
    if o.advisory_policy.routing_policy!="NO_ROUTING_CHANGE":
        findings.append(ReliabilityValidationFinding("ROUTING_POLICY_INVALID","error","advisory_policy.routing_policy must be NO_ROUTING_CHANGE."))
        status="BLOCKED"
    for r in o.recommendations:
        if r.actionability!="REVIEW_ONLY":
            findings.append(ReliabilityValidationFinding("ACTIONABILITY_INVALID","error","recommendation actionability must be REVIEW_ONLY."))
            status="BLOCKED"
        if r.mutation_allowed:
            findings.append(ReliabilityValidationFinding("RECOMMENDATION_MUTATION_FORBIDDEN","error","recommendation mutation_allowed must be false."))
            status="BLOCKED"
    for n,v in (("mean_brier_score",o.metric_snapshot.mean_brier_score),("expected_calibration_error",o.metric_snapshot.expected_calibration_error),("mean_probability",o.metric_snapshot.mean_probability),("mean_outcome",o.metric_snapshot.mean_outcome)):
        if v<0 or v>1:
            findings.append(ReliabilityValidationFinding("METRIC_RANGE_INVALID","error",f"{n} must be within [0,1]."))
            status="BLOCKED"
    if o.advisory_status=="ADVISORY_READY" and (not o.input_calibration_ledger_id or not o.input_calibration_hash):
        findings.append(ReliabilityValidationFinding("CALIBRATION_REF_REQUIRED","not_computable","ADVISORY_READY requires input calibration references."))
        status="NOT_COMPUTABLE" if status!="BLOCKED" else status
    if o.created_by_lane=="SHADOW" and o.advisory_status=="ADVISORY_READY":
        findings.append(ReliabilityValidationFinding("SHADOW_FINALIZE_BLOCKED","error","SHADOW may draft but cannot finalize ADVISORY_READY."))
        status="BLOCKED"
    if o.created_by_lane=="PROJECTION" and o.authority_ref is not None:
        findings.append(ReliabilityValidationFinding("PROJECTION_AUTHORITY_BLOCKED","error","PROJECTION cannot create advisory authority."))
        status="BLOCKED"
    if o.created_by_lane=="CANON" and o.advisory_status=="ADVISORY_READY":
        findings.append(ReliabilityValidationFinding("CANON_FINALIZE_BLOCKED","error","CANON may define schema/contracts only."))
        status="BLOCKED"
    if o.advisory_status=="ADVISORY_READY" and o.created_by_lane not in {"FORECAST","OPERATOR"}:
        findings.append(ReliabilityValidationFinding("ADVISORY_READY_LANE_INVALID","error","ADVISORY_READY must be FORECAST or OPERATOR lane."))
        status="BLOCKED"
    return ReliabilityValidationReport(status, tuple(findings), _sha256_text(_canonical_json({"status":status,"findings":[asdict(f) for f in findings],"advisory_id":o.advisory_id})))
