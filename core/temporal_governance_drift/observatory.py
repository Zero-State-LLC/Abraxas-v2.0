from __future__ import annotations
import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping, Sequence
from .models import TemporalDriftInputRef, TemporalDriftZone, TemporalDriftVector, TemporalDriftPressureBand, TemporalDriftFinding, TemporalDriftRecommendation, TemporalGovernanceDriftObservatory
from .validator import validate_temporal_governance_drift_observatory
SCHEMA_VERSION="TemporalGovernanceDriftObservatory.v1"

def _canonical_json(d:object)->str:return json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _sha256_text(t:str)->str:return hashlib.sha256(t.encode()).hexdigest()

def canonical_temporal_governance_drift_observatory_json(observatory: TemporalGovernanceDriftObservatory | Mapping[str,Any])->str:
    p=asdict(observatory) if isinstance(observatory,TemporalGovernanceDriftObservatory) else dict(observatory)
    p.pop("observatory_hash",None)
    return _canonical_json(p)
def temporal_governance_drift_observatory_hash(observatory: TemporalGovernanceDriftObservatory | Mapping[str,Any])->str:return _sha256_text(canonical_temporal_governance_drift_observatory_json(observatory))

def build_temporal_governance_drift_observatory(**kwargs: Any)->TemporalGovernanceDriftObservatory:
    d=TemporalGovernanceDriftObservatory(observatory_hash="PENDING",**kwargs)
    return replace(d, observatory_hash=temporal_governance_drift_observatory_hash(d))

def derive_temporal_governance_drift_observatory(inputs: Sequence[Mapping[str,Any]])->TemporalGovernanceDriftObservatory:
    if not inputs:
        z=(TemporalDriftZone("zone-0","NOT_COMPUTABLE","No Inputs","NOT_COMPUTABLE",tuple(),True,False,False),)
        v=(TemporalDriftVector("vec-0","NOT_COMPUTABLE",0.0,"UNKNOWN",tuple(),False),)
        p=(TemporalDriftPressureBand("band-0","NOT_COMPUTABLE",0.0,"Insufficient inputs.",True,True),)
        f=(TemporalDriftFinding("f-0","NOT_COMPUTABLE","NOT_COMPUTABLE",tuple(),"No observatory inputs.",False),)
        r=(TemporalDriftRecommendation("r-0","NOT_COMPUTABLE","Insufficient observatory inputs.",False,False,False,False,False,False,False,False),)
        return build_temporal_governance_drift_observatory(schema_version=SCHEMA_VERSION,observatory_id="obs-1",input_refs=tuple(),drift_zones=z,drift_vectors=v,pressure_bands=p,findings=f,recommendations=r,observatory_status="INSUFFICIENT_OBSERVATORY_INPUTS",observatory_posture="NOT_COMPUTABLE",observatory_policy="PROJECTION_ONLY",created_by_lane="PROJECTION",authority_ref=None,projection_only=True,observatory_authoritative=False,inference_authority_allowed=False,execution_allowed=False,mutation_allowed=False,rollback_allowed=False,promotion_allowed=False,routing_change_allowed=False,timeline_collapse_allowed=False,canonical_selection_allowed=False,replay_normalization_allowed=False,adapter_activation_allowed=False,auto_transition_allowed=False)
    refs=[]
    score=0.0
    flags=set()
    for i,x in enumerate(inputs,1):
        t=str(x.get("type","NOT_COMPUTABLE"))
        s=float(x.get("pressure",0.0))
        score+=s
        refs.append(TemporalDriftInputRef(f"in-{i}",t,str(x.get("path",f"ref-{i}")),str(x.get("hash",""))))
        for k in ("fracture","blocked","nondeterminism","stale","overload"): 
            if x.get(k):
                flags.add(k)
    avg=score/len(inputs)
    status,posture=("STABLE","PASS") if avg<0.25 and not flags else ("DRIFT_OBSERVED","WATCH")
    if "fracture" in flags:
        status,posture="FRACTURE_CONCENTRATION","WARN"
    if "blocked" in flags:
        status,posture="BLOCKED_HISTORY_ACCUMULATION","BLOCKED"
    if "nondeterminism" in flags:
        status,posture="NONDETERMINISM_CLUSTER","BLOCKED"
    if "stale" in flags:
        status,posture="STALE_PROPAGATION","WARN"
    if "overload" in flags:
        status,posture="SIGNAL_OVERLOAD","OVERLOADED"
    zones=[TemporalDriftZone("zone-pressure","PRESSURE_ZONE","Pressure Drift",posture if posture in {"PASS","WATCH","WARN","BLOCKED"} else "WARN",tuple(r.input_ref_id for r in refs),True,False,False)]
    if "fracture" in flags:
        zones.append(TemporalDriftZone("zone-fracture","FRACTURE_ZONE","Fracture Concentration","WARN",tuple(r.input_ref_id for r in refs),True,False,False))
    vectors=[TemporalDriftVector("vec-1","PRESSURE_ACCELERATION",avg,"INCREASING" if avg>=0.25 else "STABLE",tuple(r.input_ref_id for r in refs),False)]
    if "nondeterminism" in flags:
        vectors.append(TemporalDriftVector("vec-2","NONDETERMINISM_ESCALATION",0.9,"INCREASING",tuple(r.input_ref_id for r in refs),False))
    bands=[TemporalDriftPressureBand("band-1","LOW" if avg<0.25 else "MODERATE" if avg<0.5 else "HIGH" if avg<0.75 else "EXTREME",avg,"Composite governance drift pressure.",True,True)]
    ftype="DRIFT_CLUSTER_DETECTED" if status=="DRIFT_OBSERVED" else "FRACTURE_PROPAGATION_DETECTED" if status=="FRACTURE_CONCENTRATION" else "BLOCKED_HISTORY_ACCUMULATION_DETECTED" if status=="BLOCKED_HISTORY_ACCUMULATION" else "NONDETERMINISM_CLUSTER_DETECTED" if status=="NONDETERMINISM_CLUSTER" else "STALE_PROPAGATION_DETECTED" if status=="STALE_PROPAGATION" else "SIGNAL_OVERLOAD_DETECTED" if status=="SIGNAL_OVERLOAD" else "DRIFT_CLUSTER_DETECTED"
    findings=(TemporalDriftFinding("f-1",ftype,"INFO" if posture=="PASS" else "WATCH" if posture=="WATCH" else "WARN" if posture=="WARN" else "BLOCKED",tuple(r.input_ref_id for r in refs),"Deterministic governance drift observatory finding.",False),)
    rec_type="REVIEW_ONLY" if status=="STABLE" else "REQUEST_OPERATOR_REVIEW" if status in {"SIGNAL_OVERLOAD","BLOCKED_HISTORY_ACCUMULATION","NONDETERMINISM_CLUSTER"} else "INSPECT_DRIFT_ZONE"
    rec=(TemporalDriftRecommendation("r-1",rec_type,"Audit-only observatory recommendation.",False,False,False,False,False,False,False,False),)
    return build_temporal_governance_drift_observatory(schema_version=SCHEMA_VERSION,observatory_id="obs-1",input_refs=tuple(refs),drift_zones=tuple(zones),drift_vectors=tuple(vectors),pressure_bands=tuple(bands),findings=findings,recommendations=rec,observatory_status=status,observatory_posture=posture,observatory_policy="PROJECTION_ONLY",created_by_lane="PROJECTION",authority_ref=None,projection_only=True,observatory_authoritative=False,inference_authority_allowed=False,execution_allowed=False,mutation_allowed=False,rollback_allowed=False,promotion_allowed=False,routing_change_allowed=False,timeline_collapse_allowed=False,canonical_selection_allowed=False,replay_normalization_allowed=False,adapter_activation_allowed=False,auto_transition_allowed=False)

def write_temporal_governance_drift_observatory_contract_audit(base_dir: Path | str=".")->str:
    o=derive_temporal_governance_drift_observatory([{"type":"TEMPORAL_CONTRACT_RECONCILIATION_MANIFEST","pressure":0.4,"path":"out/audit/temporal_contract_reconciliation_manifest.latest.json"}])
    r=validate_temporal_governance_drift_observatory(o)
    payload={"status":r.status,"observatory_hash":o.observatory_hash,"receipt_hash":r.receipt_hash,"findings":[asdict(f) for f in r.findings],"schema_version":o.schema_version}
    text=_canonical_json(payload)+"\n"
    out=Path(base_dir)/"out/audit/temporal_governance_drift_observatory_contract.latest.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(text,encoding="utf-8")
    return _sha256_text(text)
