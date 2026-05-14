from __future__ import annotations
import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping, Sequence
from .models import *
from .validator import validate_temporal_contract_reconciliation_manifest

SCHEMA_VERSION="TemporalContractReconciliationManifest.v1"
DEFAULT_EXPECTED_PATHS=[
"contracts/temporal_climate_dashboard/temporal_climate_dashboard_packet.v1.schema.json","contracts/temporal_climate_viz/temporal_climate_aal_viz_projection_binding.v1.schema.json","contracts/temporal_compression_digest/temporal_climate_compression_digest_projection.v1.schema.json","contracts/temporal_continuity/temporal_continuity_index.v1.schema.json","contracts/temporal_operator_review/temporal_climate_operator_review_projection_queue.v1.schema.json","contracts/temporal_pressure_forecast/temporal_pressure_forecast_surface.v1.schema.json","contracts/temporal_regime_detector/temporal_regime_transition_detector.v1.schema.json","contracts/temporal_signal_compression/temporal_climate_signal_compression_ledger.v1.schema.json","contracts/temporal_topology/temporal_governance_topology_index.v1.schema.json","tests/test_temporal_climate_dashboard_packet_contract.py","tests/test_temporal_climate_aal_viz_projection_binding_contract.py","tests/test_temporal_climate_compression_digest_projection_contract.py","tests/test_temporal_continuity_index_contract.py","tests/test_temporal_climate_operator_review_projection_queue_contract.py","tests/test_temporal_pressure_forecast_surface_contract.py","tests/test_temporal_regime_transition_detector_contract.py","tests/test_temporal_climate_signal_compression_ledger_contract.py","tests/test_temporal_governance_topology_index_contract.py"]

def _canonical_json(d: object)->str:return json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _sha256_text(t:str)->str:return hashlib.sha256(t.encode()).hexdigest()

def canonical_temporal_contract_reconciliation_manifest_json(manifest: TemporalContractReconciliationManifest | Mapping[str, Any])->str:
    p=asdict(manifest) if isinstance(manifest, TemporalContractReconciliationManifest) else dict(manifest); p.pop("manifest_hash",None); return _canonical_json(p)
def temporal_contract_reconciliation_manifest_hash(manifest: TemporalContractReconciliationManifest | Mapping[str, Any])->str:return _sha256_text(canonical_temporal_contract_reconciliation_manifest_json(manifest))

def build_temporal_contract_reconciliation_manifest(**kwargs: Any)->TemporalContractReconciliationManifest:
    draft=TemporalContractReconciliationManifest(manifest_hash="PENDING",**kwargs); return replace(draft, manifest_hash=temporal_contract_reconciliation_manifest_hash(draft))

def derive_temporal_contract_reconciliation_manifest(base_dir: Path | str=".", expected_paths: Sequence[str] | None=None, clean_tree_observed: bool=False, no_diff_recorded: bool=False)->TemporalContractReconciliationManifest:
    base=Path(base_dir); exp=expected_paths or DEFAULT_EXPECTED_PATHS
    surfaces=[]; artifacts=[]; findings=[]; present=missing=empty=0
    for i,p in enumerate(exp,1):
        stype="SCHEMA" if p.endswith("schema.json") else "TEST" if "/tests/" in f"/{p}" or p.startswith("tests/") else "MODULE"
        sid=f"surface-{i}"; surfaces.append(TemporalContractExpectedSurface(sid,Path(p).name,stype,p,True,False))
        fp=base/p; exists=fp.exists(); content=fp.read_text(encoding="utf-8") if exists else ""; b=len(content.encode()) if exists else 0; lc=content.count("\n")+(1 if content and not content.endswith("\n") else 0)
        ast="MISSING" if not exists else "EMPTY" if b==0 else "PRESENT"; present += 1 if ast=="PRESENT" else 0; missing += 1 if ast=="MISSING" else 0; empty += 1 if ast=="EMPTY" else 0
        artifacts.append(TemporalContractArtifactRef(f"artifact-{i}",sid,p,exists,_sha256_text(content) if exists and b>0 else "",b,lc,ast,exists,False))
    if missing>0: findings.append(TemporalContractPresenceFinding("finding-missing","MISSING_REQUIRED_SURFACE","BLOCKED",tuple(s.surface_id for s,a in zip(surfaces,artifacts) if a.artifact_status=="MISSING"),"Missing required surfaces.",False))
    if empty>0: findings.append(TemporalContractPresenceFinding("finding-empty","EMPTY_ARTIFACT","WARN",tuple(s.surface_id for s,a in zip(surfaces,artifacts) if a.artifact_status=="EMPTY"),"Empty required artifacts detected.",False))
    if present==len(exp): findings.append(TemporalContractPresenceFinding("finding-all","ALL_PRESENT","INFO",tuple(s.surface_id for s in surfaces),"All expected surfaces present.",False))
    if clean_tree_observed and no_diff_recorded: findings.append(TemporalContractPresenceFinding("finding-no-diff","NO_DIFF_CLEAN_TREE","INFO",tuple(),"Clean tree and no diff recorded.",False))
    posture="BLOCKED" if missing>0 else "WARN" if empty>0 else "NO_DIFF" if (clean_tree_observed and no_diff_recorded) else "PASS"
    status="MISSING_ARTIFACTS" if missing>0 else "STALE_ARTIFACTS" if empty>0 else "NO_DIFF_RECORDED" if (clean_tree_observed and no_diff_recorded) else "RECONCILED"
    summary=TemporalContractReconciliationSummary("summary-1",len(exp),present,missing,empty,0,empty,0,clean_tree_observed,no_diff_recorded,posture)
    rec_type="REGENERATE_MISSING_ARTIFACTS" if missing>0 else "INSPECT_STALE_ARTIFACTS" if empty>0 else "RECORD_NO_DIFF_RESULT" if no_diff_recorded else "REVIEW_ONLY"
    rec=(TemporalContractReconciliationRecommendation("rec-1",rec_type,"Audit-only reconciliation recommendation.",False,False,False,False,False),)
    return build_temporal_contract_reconciliation_manifest(schema_version=SCHEMA_VERSION,manifest_id="reconciliation-1",expected_surfaces=tuple(surfaces),artifact_refs=tuple(artifacts),presence_findings=tuple(findings),summary=summary,recommendations=rec,manifest_status=status,manifest_posture=posture,manifest_policy="AUDIT_ONLY",created_by_lane="PROJECTION",authority_ref=None,audit_only=True,manifest_authoritative=False,execution_allowed=False,mutation_allowed=False,routing_change_allowed=False,contract_semantics_change_allowed=False,timeline_collapse_allowed=False,canonical_selection_allowed=False,adapter_activation_allowed=False,auto_apply_allowed=False)

def write_temporal_contract_reconciliation_manifest_audit(base_dir: Path | str=".")->str:
    m=derive_temporal_contract_reconciliation_manifest(base_dir=base_dir, clean_tree_observed=True, no_diff_recorded=True); r=validate_temporal_contract_reconciliation_manifest(m)
    payload={"status":r.status,"manifest_hash":m.manifest_hash,"receipt_hash":r.receipt_hash,"findings":[asdict(f) for f in r.findings],"schema_version":m.schema_version}
    text=_canonical_json(payload)+"\n"; out=Path(base_dir)/"out/audit/temporal_contract_reconciliation_manifest.latest.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(text,encoding="utf-8"); return _sha256_text(text)
