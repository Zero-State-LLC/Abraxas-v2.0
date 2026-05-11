from __future__ import annotations
import hashlib, json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping, Sequence
from .models import *
from .validator import validate_temporal_governance_operator_brief_bundle
SCHEMA_VERSION="TemporalGovernanceOperatorBriefBundle.v1"

def _canonical_json(d:object)->str:return json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _sha256_text(t:str)->str:return hashlib.sha256(t.encode()).hexdigest()

def canonical_temporal_governance_operator_brief_bundle_json(brief): p=asdict(brief) if isinstance(brief,TemporalGovernanceOperatorBriefBundle) else dict(brief); p.pop("brief_hash",None); return _canonical_json(p)
def temporal_governance_operator_brief_bundle_hash(brief)->str:return _sha256_text(canonical_temporal_governance_operator_brief_bundle_json(brief))
def build_temporal_governance_operator_brief_bundle(**kwargs): b=TemporalGovernanceOperatorBriefBundle(brief_hash="PENDING",**kwargs); return replace(b,brief_hash=temporal_governance_operator_brief_bundle_hash(b))
def compute_temporal_operator_brief_posture(status:str)->str:return {"BRIEF_CLEAR":"CLEAR","BRIEF_WATCH":"WATCH","BRIEF_DRIFT":"WATCH","BRIEF_FRACTURE":"WARN","BRIEF_BLOCKED_HISTORY":"BLOCKED","BRIEF_NONDETERMINISM":"BLOCKED","BRIEF_STALE_PROPAGATION":"WARN","BRIEF_OPERATOR_LOAD":"OVERLOADED","OPERATOR_REVIEW_REQUIRED":"OVERLOADED","INSUFFICIENT_WEATHER_INPUTS":"INSUFFICIENT_INPUTS","NOT_COMPUTABLE":"NOT_COMPUTABLE"}.get(status,"WATCH")

def derive_temporal_governance_operator_brief_bundle(inputs: Sequence[Mapping[str,Any]])->TemporalGovernanceOperatorBriefBundle:
    refs=tuple(TemporalOperatorBriefInputRef(f"in-{i}",str(x.get("type","NOT_COMPUTABLE")),str(x.get("path",f"ref-{i}")),str(x.get("hash",""))) for i,x in enumerate(inputs,1))
    if not refs: status="INSUFFICIENT_WEATHER_INPUTS"; flags={"none"}
    else:
        ws={str(x.get("weather_status","NOT_COMPUTABLE")) for x in inputs}; flags={k for x in inputs for k in ("drift","fracture","blocked","nondeterminism","stale","overload","operator_review_required") if x.get(k)}
        status="BRIEF_CLEAR" if ("WEATHER_CLEAR" in ws and len(ws)==1 and not flags) else "BRIEF_DRIFT"
        for k,v in [("fracture","BRIEF_FRACTURE"),("blocked","BRIEF_BLOCKED_HISTORY"),("nondeterminism","BRIEF_NONDETERMINISM"),("stale","BRIEF_STALE_PROPAGATION"),("overload","BRIEF_OPERATOR_LOAD"),("operator_review_required","OPERATOR_REVIEW_REQUIRED")]:
            if k in flags: status=v
    posture=compute_temporal_operator_brief_posture(status); ids=tuple(r.input_ref_id for r in refs)
    sections=[TemporalOperatorBriefSection("sec-exec","EXECUTIVE_BRIEF","Executive Brief",f"Status: {status}","PASS" if posture=="CLEAR" else "WATCH" if posture=="WATCH" else "WARN" if posture in {"WARN","OVERLOADED"} else "BLOCKED",ids,True,False),TemporalOperatorBriefSection("sec-weather","WEATHER_SUMMARY","Weather Summary","Projection-only weather compression.","WATCH" if posture!="CLEAR" else "PASS",ids,True,False),TemporalOperatorBriefSection("sec-prov","PROVENANCE_REVIEW","Provenance","All refs preserved.","PASS",ids,True,False)]
    cards=[]
    def add(tag,stype,ctype): sections.append(TemporalOperatorBriefSection(f"sec-{tag}",stype,stype.title(),f"{tag} visibility preserved.","WARN",ids,True,False)); cards.append(TemporalOperatorBriefActionCard(f"card-{tag}",ctype,f"Inspect {tag}","Review-only inspection.","WARN",True,False,False,False,False))
    if status in {"BRIEF_DRIFT","BRIEF_WATCH"}: add("drift","DRIFT_REVIEW","INSPECT_DRIFT")
    if "fracture" in flags: add("fracture","FRACTURE_REVIEW","INSPECT_FRACTURE")
    if "blocked" in flags: add("blocked_history","BLOCKED_HISTORY_REVIEW","INSPECT_BLOCKED_HISTORY")
    if "nondeterminism" in flags: add("nondeterminism","NONDETERMINISM_REVIEW","INSPECT_NONDETERMINISM")
    if "stale" in flags: add("stale_propagation","STALE_PROPAGATION_REVIEW","INSPECT_STALE_PROPAGATION")
    if "overload" in flags or status in {"BRIEF_OPERATOR_LOAD","OPERATOR_REVIEW_REQUIRED"}: add("operator_load","OPERATOR_LOAD_REVIEW","INSPECT_OPERATOR_LOAD")
    if not cards: cards=[TemporalOperatorBriefActionCard("card-review","REVIEW_ONLY","Review only","No action authorization.","PASS",False,False,False,False,False)]
    if status=="OPERATOR_REVIEW_REQUIRED": cards.append(TemporalOperatorBriefActionCard("card-context","REQUEST_MORE_CONTEXT","Request More Context","Operator review required.","WARN",True,False,False,False,False))
    prov=tuple(TemporalOperatorBriefProvenanceRef(f"prov-{i}",r.input_ref_id,r.input_ref_type,r.input_ref_hash,True,True,False) for i,r in enumerate(refs,1))
    req=["PROJECTION_ONLY","NON_AUTHORITATIVE","NO_INFERENCE_AUTHORITY","NO_ACTION_AUTHORIZATION","NO_EXECUTION","NO_MUTATION","NO_ROUTING","NO_TIMELINE_COLLAPSE","NO_CANONICAL_SELECTION","NO_REPLAY_NORMALIZATION"]
    badges=tuple(TemporalOperatorBriefConstraintBadge(f"badge-{i}",b,b.replace("_"," ").title(),True,"PASS") for i,b in enumerate(req,1))
    hdr_status={"BRIEF_CLEAR":"CLEAR","BRIEF_WATCH":"WATCH","BRIEF_DRIFT":"DRIFT","BRIEF_FRACTURE":"FRACTURE","BRIEF_BLOCKED_HISTORY":"BLOCKED_HISTORY","BRIEF_NONDETERMINISM":"NONDETERMINISM","BRIEF_STALE_PROPAGATION":"STALE_PROPAGATION","BRIEF_OPERATOR_LOAD":"OPERATOR_LOAD","OPERATOR_REVIEW_REQUIRED":"OPERATOR_LOAD","INSUFFICIENT_WEATHER_INPUTS":"NOT_COMPUTABLE"}[status]
    hdr_risk={"BRIEF_CLEAR":"NONE","BRIEF_WATCH":"DRIFT","BRIEF_DRIFT":"DRIFT","BRIEF_FRACTURE":"FRACTURE","BRIEF_BLOCKED_HISTORY":"BLOCKED_HISTORY","BRIEF_NONDETERMINISM":"NONDETERMINISM","BRIEF_STALE_PROPAGATION":"STALE_PROPAGATION","BRIEF_OPERATOR_LOAD":"OPERATOR_LOAD","OPERATOR_REVIEW_REQUIRED":"OPERATOR_LOAD","INSUFFICIENT_WEATHER_INPUTS":"NOT_COMPUTABLE"}[status]
    return build_temporal_governance_operator_brief_bundle(schema_version=SCHEMA_VERSION,brief_id="brief-1",input_refs=refs,brief_header=TemporalOperatorBriefHeader("header-1","Temporal Governance Operator Brief",hdr_status,hdr_risk,"Deterministic operator brief bundle.",status!="BRIEF_CLEAR",True),sections=tuple(sections),action_cards=tuple(cards),provenance_refs=prov,constraint_badges=badges,brief_status=status,brief_posture=posture,brief_policy="PROJECTION_ONLY",created_by_lane="PROJECTION",authority_ref=None,projection_only=True,brief_authoritative=False,inference_authority_allowed=False,action_authorization_allowed=False,execution_allowed=False,mutation_allowed=False,rollback_allowed=False,promotion_allowed=False,routing_change_allowed=False,timeline_collapse_allowed=False,canonical_selection_allowed=False,replay_normalization_allowed=False,adapter_activation_allowed=False,auto_transition_allowed=False)

def write_temporal_governance_operator_brief_bundle_contract_audit(base_dir: Path | str=".")->str:
    b=derive_temporal_governance_operator_brief_bundle([{"type":"TEMPORAL_GOVERNANCE_WEATHER_REPORT_PACKET","weather_status":"DRIFT_FRONT_PRESENT","drift":True,"hash":"abc"}]); vr=validate_temporal_governance_operator_brief_bundle(b)
    text=_canonical_json({"status":vr.status,"brief_hash":b.brief_hash,"receipt_hash":vr.receipt_hash,"findings":[asdict(x) for x in vr.findings],"schema_version":b.schema_version})+"\n"
    out=Path(base_dir)/"out/audit/temporal_governance_operator_brief_bundle_contract.latest.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(text,encoding="utf-8"); return _sha256_text(text)
