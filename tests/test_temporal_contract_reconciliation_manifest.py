import json
from dataclasses import replace, asdict
from pathlib import Path

from core.temporal_contract_reconciliation.manifest import *
from core.temporal_contract_reconciliation.validator import validate_temporal_contract_reconciliation_manifest


def _mk(tmp_path: Path):
    p1=tmp_path/"a.txt"; p1.write_text("alpha\n",encoding="utf-8")
    p2=tmp_path/"b.txt"; p2.write_text("beta\n",encoding="utf-8")
    return ["a.txt","b.txt"]


def test_all_present_reconciled_pass(tmp_path):
    m=derive_temporal_contract_reconciliation_manifest(tmp_path,_mk(tmp_path))
    assert m.manifest_status=="RECONCILED" and m.manifest_posture=="PASS"

def test_missing_path_blocked(tmp_path):
    m=derive_temporal_contract_reconciliation_manifest(tmp_path,["missing.txt"])
    assert m.manifest_status=="MISSING_ARTIFACTS" and m.manifest_posture=="BLOCKED"

def test_empty_artifact_detected(tmp_path):
    (tmp_path/"e.txt").write_text("",encoding="utf-8")
    m=derive_temporal_contract_reconciliation_manifest(tmp_path,["e.txt"])
    assert any(a.artifact_status=="EMPTY" for a in m.artifact_refs)

def test_no_diff_finding(tmp_path):
    m=derive_temporal_contract_reconciliation_manifest(tmp_path,_mk(tmp_path),True,True)
    assert any(f.finding_type=="NO_DIFF_CLEAN_TREE" for f in m.presence_findings)

def test_present_has_hash_size_linecount(tmp_path):
    m=derive_temporal_contract_reconciliation_manifest(tmp_path,_mk(tmp_path))
    assert all(a.sha256 and a.byte_size>0 and a.line_count>0 for a in m.artifact_refs)

def test_validation_policy_flags_blocked(tmp_path):
    m=derive_temporal_contract_reconciliation_manifest(tmp_path,_mk(tmp_path))
    for bad in [replace(m,audit_only=False),replace(m,manifest_authoritative=True),replace(m,execution_allowed=True),replace(m,mutation_allowed=True),replace(m,routing_change_allowed=True),replace(m,contract_semantics_change_allowed=True),replace(m,auto_apply_allowed=True)]:
        assert validate_temporal_contract_reconciliation_manifest(bad).status=="BLOCKED"

def test_nested_flags_blocked(tmp_path):
    m=derive_temporal_contract_reconciliation_manifest(tmp_path,_mk(tmp_path))
    assert validate_temporal_contract_reconciliation_manifest(replace(m, expected_surfaces=(replace(m.expected_surfaces[0], semantic_mutation_allowed=True),)+m.expected_surfaces[1:])).status=="BLOCKED"
    assert validate_temporal_contract_reconciliation_manifest(replace(m, artifact_refs=(replace(m.artifact_refs[0], mutation_allowed=True),)+m.artifact_refs[1:])).status=="BLOCKED"
    assert validate_temporal_contract_reconciliation_manifest(replace(m, artifact_refs=(replace(m.artifact_refs[0], sha256=""),)+m.artifact_refs[1:])).status=="BLOCKED"
    assert validate_temporal_contract_reconciliation_manifest(replace(m, recommendations=(replace(m.recommendations[0], auto_apply_allowed=True),))).status=="BLOCKED"

def test_hash_stability_and_canonical(tmp_path):
    m=derive_temporal_contract_reconciliation_manifest(tmp_path,_mk(tmp_path))
    assert temporal_contract_reconciliation_manifest_hash(replace(m, manifest_hash="x"))==m.manifest_hash
    assert canonical_temporal_contract_reconciliation_manifest_json(m)==canonical_temporal_contract_reconciliation_manifest_json(m)

def test_schema_required_fields_and_audit(tmp_path):
    m=derive_temporal_contract_reconciliation_manifest(tmp_path,_mk(tmp_path))
    schema=json.loads(Path("contracts/temporal_contract_reconciliation/temporal_contract_reconciliation_manifest.v1.schema.json").read_text(encoding="utf-8"))
    for k in schema["required"]: assert k in asdict(m)
    h=write_temporal_contract_reconciliation_manifest_audit(tmp_path)
    text=(tmp_path/"out/audit/temporal_contract_reconciliation_manifest.latest.json").read_text(encoding="utf-8")
    assert text.endswith("\n") and h
