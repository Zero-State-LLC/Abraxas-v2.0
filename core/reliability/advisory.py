from __future__ import annotations
import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping
from .models import *
SCHEMA_VERSION="SourceReliabilityAdvisory.v1"
def _canonical_json(data: object) -> str: return json.dumps(data, sort_keys=True, separators=(",",":"), ensure_ascii=False)
def _sha256_text(text: str) -> str: return hashlib.sha256(text.encode("utf-8")).hexdigest()
def canonical_source_reliability_advisory_json(advisory: SourceReliabilityAdvisory|Mapping[str, Any]) -> str:
    p=asdict(advisory) if isinstance(advisory, SourceReliabilityAdvisory) else dict(advisory); p.pop("advisory_hash",None); return _canonical_json(p)
def source_reliability_advisory_hash(advisory: SourceReliabilityAdvisory|Mapping[str, Any]) -> str: return _sha256_text(canonical_source_reliability_advisory_json(advisory))
def _default_policy() -> ReliabilityAdvisoryPolicy:
    return ReliabilityAdvisoryPolicy("reliability-advisory-policy-v1",30,{"strong":{"mean_brier_score_lte":0.10,"expected_calibration_error_lte":0.05},"mixed":{"mean_brier_score_lte":0.25,"expected_calibration_error_lte":0.15}},"ADVISORY_ONLY_NO_MUTATION","NO_ROUTING_CHANGE")
def _derive_posture(n:int,b:float,e:float,p:ReliabilityAdvisoryPolicy)->str:
    if n<p.min_sample_size: return "INSUFFICIENT_SAMPLE"
    if b<=p.threshold_policy["strong"]["mean_brier_score_lte"] and e<=p.threshold_policy["strong"]["expected_calibration_error_lte"]: return "STRONG"
    if b<=p.threshold_policy["mixed"]["mean_brier_score_lte"] and e<=p.threshold_policy["mixed"]["expected_calibration_error_lte"]: return "MIXED"
    return "WEAK"
def build_source_reliability_advisory(advisory_id:str,input_calibration_ledger_id:str,input_calibration_hash:str,scope_ref:ReliabilityScopeRef,metric_snapshot:ReliabilityMetricSnapshot,recommendations:tuple[ReliabilityRecommendation,...],advisory_status:str,advisory_policy:ReliabilityAdvisoryPolicy,created_by_lane:str,authority_ref:AuthorityRef|None)->SourceReliabilityAdvisory:
    d=SourceReliabilityAdvisory(SCHEMA_VERSION,advisory_id,input_calibration_ledger_id,input_calibration_hash,scope_ref,metric_snapshot,recommendations,advisory_status,advisory_policy,created_by_lane,authority_ref,False,"PENDING")
    return replace(d, advisory_hash=source_reliability_advisory_hash(d))
def derive_reliability_advisory_from_calibration(ledger: Mapping[str, Any], scope_type:str="GLOBAL", scope_id:str="global") -> SourceReliabilityAdvisory:
    a=dict(ledger.get("aggregate",{})); p=_default_policy(); n=int(a.get("entry_count",0)); b=float(a.get("mean_brier_score",1.0)); e=float(a.get("expected_calibration_error",1.0)); posture=_derive_posture(n,b,e,p); s="INSUFFICIENT_SAMPLE" if posture=="INSUFFICIENT_SAMPLE" else "ADVISORY_READY"
    m=ReliabilityMetricSnapshot(n,b,e,float(a.get("mean_probability",0.0)),float(a.get("mean_outcome",0.0)),str(a.get("sample_policy","SAMPLE_MEAN_V1")),posture)
    rec=(ReliabilityRecommendation("rec-review-1","REVIEW_RELIABILITY_TREND",f"Posture={posture}; review source reliability trend before any policy changes.","REVIEW_ONLY",False,True),)
    return build_source_reliability_advisory(f"reliability-advisory:{ledger.get('calibration_ledger_id','unknown')}",str(ledger.get("calibration_ledger_id","")),str(ledger.get("calibration_hash","")),ReliabilityScopeRef(scope_type,scope_id),m,rec,s,p,"OPERATOR",AuthorityRef("MANUAL_RECEIPT","receipt://reliability/advisory","Operator reliability advisory receipt"))
def write_source_reliability_advisory_contract_audit(base_dir: Path|str=".") -> str:
    ledger={"calibration_ledger_id":"calibration-ledger-v1","calibration_hash":"abc123","aggregate":{"entry_count":40,"mean_brier_score":0.09,"mean_probability":0.55,"mean_outcome":0.5,"expected_calibration_error":0.04,"sample_policy":"SAMPLE_MEAN_V1"}}
    advisory=derive_reliability_advisory_from_calibration(ledger)
    from .validator import validate_source_reliability_advisory
    report=validate_source_reliability_advisory(advisory)
    payload={"status":report.status,"advisory_hash":advisory.advisory_hash,"receipt_hash":report.receipt_hash,"findings":[asdict(f) for f in report.findings],"schema_version":advisory.schema_version}
    text=_canonical_json(payload)+"\n"; out=Path(base_dir)/"out/audit/source_reliability_advisory_contract.latest.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(text,encoding="utf-8"); return _sha256_text(text)
