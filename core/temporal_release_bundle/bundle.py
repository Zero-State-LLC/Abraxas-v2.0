from __future__ import annotations
import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping, Sequence
from .models import *
from .validator import validate_temporal_governance_release_bundle
SCHEMA_VERSION="TemporalGovernanceReleaseBundle.v1"

def _canonical_json(d:object)->str:return json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _sha256_text(t:str)->str:return hashlib.sha256(t.encode()).hexdigest()
def canonical_temporal_governance_release_bundle_json(bundle): p=asdict(bundle) if isinstance(bundle,TemporalGovernanceReleaseBundle) else dict(bundle); p.pop("bundle_hash",None); return _canonical_json(p)
def temporal_governance_release_bundle_hash(bundle)->str:return _sha256_text(canonical_temporal_governance_release_bundle_json(bundle))
def build_temporal_governance_release_bundle(**kwargs): b=TemporalGovernanceReleaseBundle(bundle_hash="PENDING",**kwargs); return replace(b,bundle_hash=temporal_governance_release_bundle_hash(b))
def compute_temporal_release_bundle_posture(status:str)->str:return {"RELEASE_RECONCILED":"PASS","RELEASE_RECONCILED_WITH_WARNINGS":"WARN","RELEASE_INCOMPLETE":"WARN","RELEASE_BLOCKED":"BLOCKED","RELEASE_NO_DIFF_RECORDED":"NO_DIFF","OPERATOR_REVIEW_REQUIRED":"WARN","INSUFFICIENT_RELEASE_INPUTS":"INSUFFICIENT_INPUTS","NOT_COMPUTABLE":"NOT_COMPUTABLE"}.get(status,"WARN")

def derive_temporal_governance_release_bundle(inputs: Sequence[Mapping[str,Any]])->TemporalGovernanceReleaseBundle:
    refs=tuple(TemporalReleaseInputRef(f"in-{i}",str(x.get("type","NOT_COMPUTABLE")),str(x.get("path",f"ref-{i}")),str(x.get("hash",""))) for i,x in enumerate(inputs,1))
    if not refs: status="INSUFFICIENT_RELEASE_INPUTS"
    else:
        miss=any(x.get("missing_artifact") or x.get("missing_schema") or x.get("missing_test") for x in inputs)
        fail=any(x.get("test_failed") for x in inputs)
        warn=any(x.get("warning") for x in inputs)
        nd=any(x.get("no_diff") for x in inputs)
        review=any(x.get("operator_review_required") for x in inputs)
        if review: status="OPERATOR_REVIEW_REQUIRED"
        elif fail: status="RELEASE_BLOCKED"
        elif miss: status="RELEASE_INCOMPLETE"
        elif nd: status="RELEASE_NO_DIFF_RECORDED"
        elif warn: status="RELEASE_RECONCILED_WITH_WARNINGS"
        else: status="RELEASE_RECONCILED"
    tuple(r.input_ref_id for r in refs)
    artifacts=(TemporalReleaseArtifactRef("art-1","AUDIT_ARTIFACT","out/audit/temporal_governance_release_bundle_contract.latest.json","",True,True,"PASS",False),)
    if status in {"RELEASE_INCOMPLETE","RELEASE_BLOCKED"}: artifacts+=(TemporalReleaseArtifactRef("art-missing","MODULE","missing/module.py","",False,True,"BLOCKED",False),)
    tests=(TemporalReleaseTestRef("t-1","pytest -q tests/test_temporal_governance_release_bundle_contract.py","FAIL" if status=="RELEASE_BLOCKED" else "PASS","Deterministic contract checks.",True),)
    schemas=(TemporalReleaseSchemaRef("s-1","contracts/temporal_release_bundle/temporal_governance_release_bundle.v1.schema.json",SCHEMA_VERSION,"","PRESENT",False),)
    commits=(TemporalReleaseCommitRef("c-1","local","abx: add temporal governance release bundle v1 contract",True,False,False),)
    req=["AUDIT_ONLY","PROJECTION_ONLY","NON_AUTHORITATIVE","NO_INFERENCE_AUTHORITY","NO_ACTION_AUTHORIZATION","NO_EXECUTION","NO_MUTATION","NO_ROLLBACK","NO_PROMOTION","NO_ROUTING","NO_TIMELINE_COLLAPSE","NO_CANONICAL_SELECTION","NO_REPLAY_NORMALIZATION","NO_GLOBAL_RUNTIME_ACTIVATION"]
    badges=tuple(TemporalReleaseConstraintBadge(f"b-{i}",x,x.replace("_"," ").title(),True,"PASS") for i,x in enumerate(req,1))
    rec_type="REQUEST_OPERATOR_REVIEW" if status=="OPERATOR_REVIEW_REQUIRED" else "INSPECT_FAILED_TESTS" if status=="RELEASE_BLOCKED" else "INSPECT_MISSING_ARTIFACTS" if status=="RELEASE_INCOMPLETE" else "INSPECT_RELEASE_ARTIFACTS"
    rec=(TemporalReleaseRecommendation("r-1",rec_type,"Audit-only release recommendation.",status=="OPERATOR_REVIEW_REQUIRED",False,False,False,False,False,False,False,False,False),)
    blocked=1 if status=="RELEASE_BLOCKED" else 0; warn=1 if status in {"RELEASE_RECONCILED_WITH_WARNINGS","RELEASE_INCOMPLETE","OPERATOR_REVIEW_REQUIRED"} else 0; nc=1 if status=="INSUFFICIENT_RELEASE_INPUTS" else 0
    summary=TemporalReleaseSummary("sum-1",len(refs),len(artifacts),len(commits),len(tests),len(schemas),1 if status=="RELEASE_RECONCILED" else 0,warn,blocked,nc,status=="RELEASE_RECONCILED",status=="OPERATOR_REVIEW_REQUIRED",compute_temporal_release_bundle_posture(status))
    return build_temporal_governance_release_bundle(schema_version=SCHEMA_VERSION,bundle_id="rb-1",input_refs=refs,artifact_refs=artifacts,commit_refs=commits,test_refs=tests,schema_refs=schemas,release_summary=summary,constraint_badges=badges,recommendations=rec,bundle_status=status,bundle_posture=compute_temporal_release_bundle_posture(status),bundle_policy="AUDIT_PROJECTION_ONLY",created_by_lane="PROJECTION",authority_ref=None,audit_only=True,projection_only=True,bundle_authoritative=False,inference_authority_allowed=False,action_authorization_allowed=False,execution_allowed=False,mutation_allowed=False,rollback_allowed=False,promotion_allowed=False,routing_change_allowed=False,timeline_collapse_allowed=False,canonical_selection_allowed=False,replay_normalization_allowed=False,adapter_activation_allowed=False,auto_transition_allowed=False,global_runtime_activation_allowed=False)

def write_temporal_governance_release_bundle_contract_audit(base_dir: Path | str=".")->str:
    b=derive_temporal_governance_release_bundle([{"type":"TEMPORAL_OPERATOR_BRIEF_BUNDLE","hash":"abc"}]); vr=validate_temporal_governance_release_bundle(b)
    text=_canonical_json({"status":vr.status,"bundle_hash":b.bundle_hash,"receipt_hash":vr.receipt_hash,"findings":[asdict(x) for x in vr.findings],"schema_version":b.schema_version})+"\n"
    out=Path(base_dir)/"out/audit/temporal_governance_release_bundle_contract.latest.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(text,encoding="utf-8"); return _sha256_text(text)
