from __future__ import annotations
import hashlib, json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping, Sequence
from .models import *
from .validator import validate_temporal_governance_weather_report_packet
SCHEMA_VERSION="TemporalGovernanceWeatherReportPacket.v1"

def _canonical_json(d:object)->str:return json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _sha256_text(t:str)->str:return hashlib.sha256(t.encode()).hexdigest()
def canonical_temporal_governance_weather_report_packet_json(report): p=asdict(report) if isinstance(report,TemporalGovernanceWeatherReportPacket) else dict(report); p.pop("report_hash",None); return _canonical_json(p)
def temporal_governance_weather_report_packet_hash(report)->str:return _sha256_text(canonical_temporal_governance_weather_report_packet_json(report))
def build_temporal_governance_weather_report_packet(**kwargs): r=TemporalGovernanceWeatherReportPacket(report_hash="PENDING",**kwargs); return replace(r,report_hash=temporal_governance_weather_report_packet_hash(r))
def compute_temporal_weather_report_posture(status:str)->str:return {"WEATHER_CLEAR":"CLEAR","DRIFT_FRONT_PRESENT":"WATCH","FRACTURE_STORM_PRESENT":"STORM","BLOCKED_HISTORY_FRONT_PRESENT":"BLOCKED","NONDETERMINISM_FRONT_PRESENT":"BLOCKED","STALE_PROPAGATION_PRESENT":"WARN","OPERATOR_LOAD_HIGH":"OVERLOADED","OPERATOR_REVIEW_REQUIRED":"OVERLOADED","INSUFFICIENT_OBSERVATORY_INPUTS":"INSUFFICIENT_INPUTS","NOT_COMPUTABLE":"NOT_COMPUTABLE"}.get(status,"WATCH")

def derive_temporal_governance_weather_report_packet(inputs: Sequence[Mapping[str,Any]])->TemporalGovernanceWeatherReportPacket:
    refs=tuple(TemporalWeatherInputRef(f"in-{i}",str(x.get("type","NOT_COMPUTABLE")),str(x.get("path",f"ref-{i}")),str(x.get("hash",""))) for i,x in enumerate(inputs,1))
    if not refs: flags={"none"}; status="INSUFFICIENT_OBSERVATORY_INPUTS"; avg=0.0
    else:
        avg=sum(float(x.get("pressure",0.0)) for x in inputs)/len(inputs); flags={k for x in inputs for k in ("drift","fracture","blocked","nondeterminism","stale","overload","operator_review_required") if x.get(k)}; status="WEATHER_CLEAR" if avg<0.25 and not flags else "DRIFT_FRONT_PRESENT"
        for k,v in [("fracture","FRACTURE_STORM_PRESENT"),("blocked","BLOCKED_HISTORY_FRONT_PRESENT"),("nondeterminism","NONDETERMINISM_FRONT_PRESENT"),("stale","STALE_PROPAGATION_PRESENT"),("overload","OPERATOR_LOAD_HIGH"),("operator_review_required","OPERATOR_REVIEW_REQUIRED")]:
            if k in flags: status=v
    posture=compute_temporal_weather_report_posture(status); ids=tuple(r.input_ref_id for r in refs)
    sec=[TemporalWeatherSection("sec-exec","EXECUTIVE_WEATHER","Executive Weather",f"Status: {status}","PASS" if posture=="CLEAR" else "WATCH" if posture=="WATCH" else "WARN" if posture in {"WARN","STORM","OVERLOADED"} else "BLOCKED",ids,True,False)]
    alerts=[]; fronts=[]
    def add(tag,stype,atype,ftype,sev="WARN"): sec.append(TemporalWeatherSection(f"sec-{tag}",stype,stype.title(),f"{tag} visibility preserved.","WARN",ids,True,False)); alerts.append(TemporalWeatherAlert(f"al-{tag}",atype,sev,f"{tag} detected.",ids,True,False)); fronts.append(TemporalWeatherPressureFront(f"fr-{tag}",ftype,max(avg,0.5),"INCREASING",ids,True,False,False))
    if status in {"DRIFT_FRONT_PRESENT"}: add("drift","DRIFT_ZONES","DRIFT_FRONT","DRIFT_FRONT","WATCH")
    if "fracture" in flags: add("fracture","FRACTURE_STORMS","FRACTURE_STORM","FRACTURE_FRONT")
    if "blocked" in flags: add("blocked","BLOCKED_HISTORY","BLOCKED_HISTORY_FRONT","BLOCKED_FRONT","BLOCKED")
    if "nondeterminism" in flags: add("nondeterminism","NONDETERMINISM","NONDETERMINISM_FRONT","NONDETERMINISM_FRONT","BLOCKED")
    if "stale" in flags: add("stale","STALE_PROPAGATION","STALE_PROPAGATION","STALE_FRONT")
    if "overload" in flags or "operator_review_required" in flags: add("operator_load","OPERATOR_LOAD","OPERATOR_LOAD","OVERLOAD_FRONT")
    if not alerts: alerts=[TemporalWeatherAlert("al-clear","DRIFT_FRONT","INFO","No significant fronts.",ids,False,False)]; fronts=[TemporalWeatherPressureFront("fr-clear","DRIFT_FRONT",avg,"STABLE",ids,True,False,False)]
    prompts=(TemporalWeatherReviewPrompt("pr-1","REVIEW_ONLY","Operator review only; no action authorization.",status!="WEATHER_CLEAR",False,False,False,False),)
    domw={"WEATHER_CLEAR":"CLEAR","DRIFT_FRONT_PRESENT":"DRIFT_FRONT","FRACTURE_STORM_PRESENT":"FRACTURE_STORM","BLOCKED_HISTORY_FRONT_PRESENT":"BLOCKED_FRONT","NONDETERMINISM_FRONT_PRESENT":"NONDETERMINISM_FRONT","STALE_PROPAGATION_PRESENT":"STALE_FRONT","OPERATOR_LOAD_HIGH":"OVERLOAD","OPERATOR_REVIEW_REQUIRED":"OVERLOAD","INSUFFICIENT_OBSERVATORY_INPUTS":"NOT_COMPUTABLE"}[status]
    domr={"WEATHER_CLEAR":"NONE","DRIFT_FRONT_PRESENT":"DRIFT","FRACTURE_STORM_PRESENT":"FRACTURE","BLOCKED_HISTORY_FRONT_PRESENT":"BLOCKED_HISTORY","NONDETERMINISM_FRONT_PRESENT":"NONDETERMINISM","STALE_PROPAGATION_PRESENT":"STALE_PROPAGATION","OPERATOR_LOAD_HIGH":"OPERATOR_LOAD","OPERATOR_REVIEW_REQUIRED":"OPERATOR_LOAD","INSUFFICIENT_OBSERVATORY_INPUTS":"NOT_COMPUTABLE"}[status]
    return build_temporal_governance_weather_report_packet(schema_version=SCHEMA_VERSION,report_id="wr-1",input_refs=refs,weather_summary=TemporalWeatherSummary("sum-1",domw,domr,"Deterministic weather report projection.",1.0 if status=="WEATHER_CLEAR" else 0.8,status!="WEATHER_CLEAR",True),sections=tuple(sec),alerts=tuple(alerts),pressure_fronts=tuple(fronts),review_prompts=prompts,report_status=status,report_posture=posture,report_policy="PROJECTION_ONLY",created_by_lane="PROJECTION",authority_ref=None,projection_only=True,report_authoritative=False,inference_authority_allowed=False,action_authorization_allowed=False,execution_allowed=False,mutation_allowed=False,rollback_allowed=False,promotion_allowed=False,routing_change_allowed=False,timeline_collapse_allowed=False,canonical_selection_allowed=False,replay_normalization_allowed=False,adapter_activation_allowed=False,auto_transition_allowed=False)

def write_temporal_governance_weather_report_packet_contract_audit(base_dir: Path | str=".")->str:
    r=derive_temporal_governance_weather_report_packet([{"type":"TEMPORAL_GOVERNANCE_DRIFT_OBSERVATORY","pressure":0.6,"drift":True}]); vr=validate_temporal_governance_weather_report_packet(r)
    text=_canonical_json({"status":vr.status,"report_hash":r.report_hash,"receipt_hash":vr.receipt_hash,"findings":[asdict(f) for f in vr.findings],"schema_version":r.schema_version})+"\n"
    out=Path(base_dir)/"out/audit/temporal_governance_weather_report_packet_contract.latest.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(text,encoding="utf-8"); return _sha256_text(text)
