from __future__ import annotations
import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping
from .models import *

def _canonical_json(data: object) -> str: return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
def _sha256_text(text: str) -> str: return hashlib.sha256(text.encode("utf-8")).hexdigest()

def validate_temporal_contract_reconciliation_manifest(manifest: TemporalContractReconciliationManifest | Mapping[str, Any]) -> TemporalContractReconciliationValidationReport:
    m = manifest if isinstance(manifest, TemporalContractReconciliationManifest) else TemporalContractReconciliationManifest(**dict(manifest))
    findings=[]; status="PASS"
    if (not m.audit_only) or m.manifest_authoritative or m.execution_allowed or m.mutation_allowed or m.routing_change_allowed or m.contract_semantics_change_allowed or m.timeline_collapse_allowed or m.canonical_selection_allowed or m.adapter_activation_allowed or m.auto_apply_allowed: findings.append(TemporalContractReconciliationValidationFinding("FLAGS_FORBIDDEN","error","top-level flags violate audit-only policy.")); status="BLOCKED"
    if any((not s.required) or s.semantic_mutation_allowed for s in m.expected_surfaces): findings.append(TemporalContractReconciliationValidationFinding("EXPECTED_SURFACE_FLAGS_FORBIDDEN","error","expected surface flags invalid.")); status="BLOCKED"
    for a in m.artifact_refs:
        if a.mutation_allowed: findings.append(TemporalContractReconciliationValidationFinding("ARTIFACT_MUTATION_FORBIDDEN","error","artifact mutation_allowed must be false.")); status="BLOCKED"
        if a.exists and not a.sha256: findings.append(TemporalContractReconciliationValidationFinding("ARTIFACT_HASH_REQUIRED","error","existing artifact requires sha256.")); status="BLOCKED"
        if (not a.exists) and a.artifact_status not in {"MISSING","NOT_COMPUTABLE"}: findings.append(TemporalContractReconciliationValidationFinding("ARTIFACT_STATUS_INVALID","error","non-existing artifact must be MISSING/NOT_COMPUTABLE.")); status="BLOCKED"
    if any(f.auto_apply_allowed for f in m.presence_findings): findings.append(TemporalContractReconciliationValidationFinding("FINDING_AUTO_APPLY_FORBIDDEN","error","finding auto-apply forbidden.")); status="BLOCKED"
    if any(r.execution_allowed or r.mutation_allowed or r.routing_change_allowed or r.contract_semantics_change_allowed or r.auto_apply_allowed for r in m.recommendations): findings.append(TemporalContractReconciliationValidationFinding("RECOMMENDATION_FLAGS_FORBIDDEN","error","recommendation flags invalid.")); status="BLOCKED"
    s=m.summary
    if m.manifest_status=="RECONCILED" and (s.missing_count!=0 or s.present_count!=s.expected_surface_count): findings.append(TemporalContractReconciliationValidationFinding("STATUS_RECONCILED_INVARIANT","error","RECONCILED invariant failed.")); status="BLOCKED"
    if m.manifest_status=="MISSING_ARTIFACTS" and s.missing_count<=0: findings.append(TemporalContractReconciliationValidationFinding("STATUS_MISSING_INVARIANT","error","MISSING_ARTIFACTS invariant failed.")); status="BLOCKED"
    if m.manifest_status=="NO_DIFF_RECORDED" and not s.no_diff_recorded: findings.append(TemporalContractReconciliationValidationFinding("STATUS_NO_DIFF_INVARIANT","error","NO_DIFF_RECORDED invariant failed.")); status="BLOCKED"
    if m.manifest_status=="NOT_COMPUTABLE" and (s.not_computable_count<=0 and not any(f.finding_type=="NOT_COMPUTABLE" for f in m.presence_findings)): findings.append(TemporalContractReconciliationValidationFinding("STATUS_NOT_COMPUTABLE_INVARIANT","error","NOT_COMPUTABLE invariant failed.")); status="BLOCKED"
    receipt_hash=_sha256_text(_canonical_json({"status":status,"findings":[asdict(f) for f in findings],"manifest_id":m.manifest_id}))
    return TemporalContractReconciliationValidationReport(status, tuple(findings), receipt_hash)
