from __future__ import annotations
import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping, Sequence
from .models import TemporalReleaseIndexInputRef, TemporalReleaseIndexEntry, TemporalReleaseLineageRef, TemporalReleaseIndexSummary, TemporalReleaseIndexFinding, TemporalReleaseIndexRecommendation, TemporalGovernanceReleaseIndexRegistry
from .validator import validate_temporal_governance_release_index_registry
SCHEMA_VERSION="TemporalGovernanceReleaseIndexRegistry.v1"

def _canonical_json(d:object)->str:return json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _sha256_text(t:str)->str:return hashlib.sha256(t.encode()).hexdigest()
def _version_key(v:str):
    p=[]
    for x in str(v).replace("v","").split("."):
        try:
            p.append(int(x))
        except ValueError:
            p.append(x)
    return tuple(p)

def canonical_temporal_governance_release_index_registry_json(registry):
    p=asdict(registry) if isinstance(registry,TemporalGovernanceReleaseIndexRegistry) else dict(registry)
    p.pop("registry_hash",None)
    return _canonical_json(p)
def temporal_governance_release_index_registry_hash(registry)->str:return _sha256_text(canonical_temporal_governance_release_index_registry_json(registry))
def build_temporal_governance_release_index_registry(**kwargs):
    r=TemporalGovernanceReleaseIndexRegistry(registry_hash="PENDING",**kwargs)
    return replace(r,registry_hash=temporal_governance_release_index_registry_hash(r))

def compute_temporal_release_index_registry_posture(status:str)->str:return {"INDEX_RECONCILED":"PASS","INDEX_RECONCILED_WITH_WARNINGS":"WARN","INDEX_BLOCKED":"BLOCKED","INDEX_EMPTY":"EMPTY","INDEX_NO_DIFF_RECORDED":"NO_DIFF","NOT_COMPUTABLE":"NOT_COMPUTABLE","INDEX_INCOMPLETE":"WARN","OPERATOR_REVIEW_REQUIRED":"WARN"}.get(status,"WARN")

def derive_temporal_governance_release_index_registry(release_bundles: Sequence[Mapping[str,Any]], created_by_lane:str="PROJECTION", authority_ref:dict|None=None)->TemporalGovernanceReleaseIndexRegistry:
    refs=tuple(TemporalReleaseIndexInputRef(f"in-{i}",str(x.get("input_ref_type","TEMPORAL_GOVERNANCE_RELEASE_BUNDLE")),str(x.get("input_ref_path",f"bundle-{i}")),str(x.get("input_ref_hash",x.get("release_hash","")))) for i,x in enumerate(release_bundles,1))
    entries=[]
    for i,b in enumerate(release_bundles,1):
        rid=str(b.get("release_bundle_id",""))
        rh=str(b.get("release_hash",""))
        rv=str(b.get("release_version",f"0.0.{i}"))
        rs=str(b.get("release_status","NOT_COMPUTABLE"))
        rp=str(b.get("release_posture","NOT_COMPUTABLE"))
        entries.append(TemporalReleaseIndexEntry(f"e-{i}",rid,rv,rh,rs,rp,tuple(b.get("commit_hashes",())),tuple(b.get("artifact_hashes",())),tuple(b.get("test_statuses",())),tuple(b.get("schema_hashes",())),bool(b.get("operator_review_required",False)),True,False,False,False))
    entries=tuple(sorted(entries,key=lambda e: (_version_key(e.release_version),e.release_bundle_id)))
    lineages=[]
    for i in range(len(entries)-1):
        a,b=entries[i],entries[i+1]
        lt="NEXT_RELEASE"
        if b.release_status=="RELEASE_NO_DIFF_RECORDED":
            lt="NO_DIFF_SUCCESSOR"
        elif b.release_status=="RELEASE_RECONCILED_WITH_WARNINGS":
            lt="WARNING_SUCCESSOR"
        elif b.release_status=="RELEASE_BLOCKED":
            lt="BLOCKED_SUCCESSOR"
        elif b.release_status=="NOT_COMPUTABLE":
            lt="NOT_COMPUTABLE"
        lh=_sha256_text(_canonical_json({"from":a.release_bundle_id,"to":b.release_bundle_id,"type":lt}))
        lineages.append(TemporalReleaseLineageRef(f"l-{i+1}",a.release_bundle_id,b.release_bundle_id,lt,lh,True,False,False))
    lineages=tuple(lineages)
    rc=len(entries)
    blocked=sum(e.release_status=="RELEASE_BLOCKED" for e in entries)
    warn=sum(e.release_status in {"RELEASE_RECONCILED_WITH_WARNINGS","RELEASE_INCOMPLETE"} for e in entries)
    nd=sum(e.release_status=="RELEASE_NO_DIFF_RECORDED" for e in entries)
    nc=sum(e.release_status=="NOT_COMPUTABLE" for e in entries)
    opr=sum(e.operator_review_required or e.release_status=="OPERATOR_REVIEW_REQUIRED" for e in entries)
    pc=sum(e.release_posture=="PASS" for e in entries)
    missing=any((not e.release_bundle_id) or (not e.release_hash) for e in entries)
    if rc==0:
        status="INDEX_EMPTY"
    elif opr>0:
        status="OPERATOR_REVIEW_REQUIRED"
    elif blocked>0:
        status="INDEX_BLOCKED"
    elif missing:
        status="INDEX_INCOMPLETE"
    elif nd>0:
        status="INDEX_NO_DIFF_RECORDED"
    elif warn>0:
        status="INDEX_RECONCILED_WITH_WARNINGS"
    elif nc>0:
        status="NOT_COMPUTABLE"
    else:
        status="INDEX_RECONCILED"
    findings=[]
    if rc==0:
        findings.append(TemporalReleaseIndexFinding("f-1","INDEX_EMPTY","WARN",tuple(),"No release bundles indexed.",False))
    if blocked>0:
        findings.append(TemporalReleaseIndexFinding("f-b","BLOCKED_RELEASE_PRESENT","BLOCKED",tuple(e.release_bundle_id for e in entries if e.release_status=="RELEASE_BLOCKED"),"Blocked release present.",False))
    if warn>0:
        findings.append(TemporalReleaseIndexFinding("f-w","WARNING_RELEASE_PRESENT","WARN",tuple(e.release_bundle_id for e in entries if e.release_status=="RELEASE_RECONCILED_WITH_WARNINGS"),"Warning release present.",False))
    if nd>0:
        findings.append(TemporalReleaseIndexFinding("f-n","NO_DIFF_RELEASE_PRESENT","INFO",tuple(e.release_bundle_id for e in entries if e.release_status=="RELEASE_NO_DIFF_RECORDED"),"No diff release present.",False))
    if nc>0:
        findings.append(TemporalReleaseIndexFinding("f-c","NOT_COMPUTABLE","NOT_COMPUTABLE",tuple(e.release_bundle_id for e in entries if e.release_status=="NOT_COMPUTABLE"),"Not computable release present.",False))
    rec_type="REQUEST_OPERATOR_REVIEW" if opr>0 else "INSPECT_BLOCKED_RELEASE" if blocked>0 else "INSPECT_WARNING_RELEASE" if warn>0 else "REVIEW_ONLY"
    rec=(TemporalReleaseIndexRecommendation("r-1",rec_type,"Index is audit-only and projection-only.",opr>0,False,False,False,False,False,False,False,False,False),)
    latest=entries[-1] if entries else None
    summary=TemporalReleaseIndexSummary("sum-1",rc,pc,warn,blocked,nd,nc,opr,latest.release_bundle_id if latest else "",latest.release_hash if latest else "",compute_temporal_release_index_registry_posture(status))
    return build_temporal_governance_release_index_registry(schema_version=SCHEMA_VERSION,registry_id="rir-1",input_refs=refs,release_entries=entries,lineage_refs=lineages,summary=summary,findings=tuple(findings),recommendations=rec,registry_status=status,registry_posture=compute_temporal_release_index_registry_posture(status),registry_policy="AUDIT_PROJECTION_ONLY",created_by_lane=created_by_lane,authority_ref=authority_ref,audit_only=True,projection_only=True,registry_authoritative=False,release_activation_allowed=False,execution_allowed=False,mutation_allowed=False,rollback_allowed=False,promotion_allowed=False,routing_change_allowed=False,timeline_collapse_allowed=False,canonical_selection_allowed=False,replay_normalization_allowed=False,adapter_activation_allowed=False,auto_transition_allowed=False,global_runtime_activation_allowed=False)

def write_temporal_governance_release_index_registry_contract_audit(base_dir: Path | str=".")->str:
    r=derive_temporal_governance_release_index_registry([{"release_bundle_id":"rb-1","release_version":"1.0.0","release_hash":"abc","release_status":"RELEASE_RECONCILED","release_posture":"PASS"}])
    vr=validate_temporal_governance_release_index_registry(r)
    text=_canonical_json({"status":vr.status,"registry_hash":r.registry_hash,"receipt_hash":vr.receipt_hash,"findings":[asdict(x) for x in vr.findings],"schema_version":r.schema_version})+"\n"
    out=Path(base_dir)/"out/audit/temporal_governance_release_index_registry_contract.latest.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(text,encoding="utf-8")
    return _sha256_text(text)
