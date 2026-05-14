import json
from dataclasses import asdict, replace
from pathlib import Path
from core.temporal_release_index.registry import canonical_temporal_governance_release_index_registry_json, temporal_governance_release_index_registry_hash, derive_temporal_governance_release_index_registry, write_temporal_governance_release_index_registry_contract_audit
from core.temporal_release_index.validator import validate_temporal_governance_release_index_registry
from core.temporal_release_index.models import TemporalReleaseIndexFinding

def _bundle(i,status="RELEASE_RECONCILED",posture="PASS",**kw):
    x={"release_bundle_id":f"rb-{i}","release_version":f"1.0.{i}","release_hash":f"h{i}","release_status":status,"release_posture":posture}
    x.update(kw)
    return x

def test_release_index_registry_contract(tmp_path):
    assert derive_temporal_governance_release_index_registry([]).registry_status in {"INDEX_EMPTY","NOT_COMPUTABLE"}
    assert derive_temporal_governance_release_index_registry([_bundle(1)]).registry_status=="INDEX_RECONCILED"
    assert derive_temporal_governance_release_index_registry([_bundle(1,"RELEASE_RECONCILED_WITH_WARNINGS","WARN")]).registry_status=="INDEX_RECONCILED_WITH_WARNINGS"
    assert derive_temporal_governance_release_index_registry([_bundle(1,"RELEASE_BLOCKED","BLOCKED")]).registry_status=="INDEX_BLOCKED"
    assert derive_temporal_governance_release_index_registry([_bundle(1,release_hash="")]).registry_status in {"INDEX_INCOMPLETE","NOT_COMPUTABLE"}
    assert derive_temporal_governance_release_index_registry([_bundle(1,"RELEASE_NO_DIFF_RECORDED","NO_DIFF")]).registry_status in {"INDEX_NO_DIFF_RECORDED","INDEX_RECONCILED_WITH_WARNINGS"}
    assert derive_temporal_governance_release_index_registry([_bundle(1,"OPERATOR_REVIEW_REQUIRED","WARN",operator_review_required=True)]).registry_status=="OPERATOR_REVIEW_REQUIRED"
    r=derive_temporal_governance_release_index_registry([_bundle(2,release_version="1.0.2"),_bundle(1,release_version="1.0.1")])
    assert [e.release_bundle_id for e in r.release_entries]==["rb-1","rb-2"]
    assert len(r.lineage_refs)==1
    assert all((not ledger_entry.timeline_collapse_allowed) and (not ledger_entry.canonical_selection_allowed) and ledger_entry.lineage_preserved for ledger_entry in r.lineage_refs)
    for bad in [replace(r,audit_only=False),replace(r,projection_only=False),replace(r,registry_authoritative=True),replace(r,execution_allowed=True),replace(r,release_entries=(replace(r.release_entries[0],activation_allowed=True),)),replace(r.release_entries[0],promotion_allowed=True) if False else None]:
        if bad is not None:
            assert validate_temporal_governance_release_index_registry(bad).status=="BLOCKED"
    assert validate_temporal_governance_release_index_registry(replace(r,release_entries=(replace(r.release_entries[0],promotion_allowed=True),)+r.release_entries[1:])).status=="BLOCKED"
    assert validate_temporal_governance_release_index_registry(replace(r,release_entries=(replace(r.release_entries[0],rollback_allowed=True),)+r.release_entries[1:])).status=="BLOCKED"
    assert validate_temporal_governance_release_index_registry(replace(r,lineage_refs=(replace(r.lineage_refs[0],canonical_selection_allowed=True),))).status=="BLOCKED"
    assert validate_temporal_governance_release_index_registry(replace(r,lineage_refs=(replace(r.lineage_refs[0],timeline_collapse_allowed=True),))).status=="BLOCKED"
    assert validate_temporal_governance_release_index_registry(replace(r,findings=(replace((r.findings or (TemporalReleaseIndexFinding('f','INDEX_EMPTY','WARN',tuple(),'x',False),))[0],execution_allowed=True),))).status=="BLOCKED"
    assert validate_temporal_governance_release_index_registry(replace(r,recommendations=(replace(r.recommendations[0],execution_allowed=True),))).status=="BLOCKED"
    assert temporal_governance_release_index_registry_hash(replace(r,registry_hash="x"))==r.registry_hash
    assert canonical_temporal_governance_release_index_registry_json(r)==canonical_temporal_governance_release_index_registry_json(r)
    schema=json.loads(Path("contracts/temporal_release_index/temporal_governance_release_index_registry.v1.schema.json").read_text())
    for k in schema["required"]:
        assert k in asdict(r)
    h=write_temporal_governance_release_index_registry_contract_audit(tmp_path)
    text=(tmp_path/"out/audit/temporal_governance_release_index_registry_contract.latest.json").read_text()
    assert text.endswith("\n") and h
