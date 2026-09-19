"""Grounding composition for the Moses contract spine.

Composes already-produced evidence/calibration and SHADOW findings.
No specialist invocation, causal inference, truth assignment, or authority grant.
"""
from __future__ import annotations
from collections.abc import Mapping, Sequence
from typing import Any
from core.moses.contracts import GroundingDisposition, GroundingReceipt, MeaningPacket, MeaningStatus

_BLOCKING_SHADOW_CODES = frozenset({"MISSING_EVIDENCE","UNEXPECTED_TRANSITION","DIVERGENCE","CONTAMINATION","UNEXPLAINED_DECAY"})

def _finding(item: Mapping[str, Any]) -> dict[str, Any]:
    return {str(key): value for key, value in item.items()}

def compose_grounding_receipt(
    meaning: MeaningPacket, *, grounding_receipt_id: str,
    evidence_refs: Sequence[str] = (), calibration_evidence_refs: Sequence[str] = (),
    shadow_findings: Sequence[Mapping[str, Any]] = (),
    grounding_assertions: Sequence[Mapping[str, Any]] = (),
) -> GroundingReceipt:
    """Compose a fail-closed receipt from existing governed outputs."""
    findings = tuple(_finding(item) for item in shadow_findings)
    refs = tuple(sorted({str(ref) for ref in (*evidence_refs, *calibration_evidence_refs) if str(ref)}))
    assertions = tuple(_finding(item) for item in grounding_assertions)
    unresolved: list[str] = []
    if meaning.status == MeaningStatus.contradicted:
        disposition = GroundingDisposition.contradicted
        unresolved.extend(meaning.contradictions)
    elif meaning.status == MeaningStatus.not_computable:
        disposition = GroundingDisposition.not_computable
        unresolved.extend(meaning.uncertainty)
    else:
        blockers = [item for item in findings if str(item.get("code","")).upper() in _BLOCKING_SHADOW_CODES and str(item.get("severity","")).lower() == "anomaly"]
        unsupported = [item for item in assertions if str(item.get("status","")).upper() in {"CONTRADICTED","UNSUPPORTED"}]
        supported = [item for item in assertions if str(item.get("status","")).upper() == "SUPPORTED"]
        if unsupported:
            disposition = GroundingDisposition.contradicted
            unresolved.extend(f"grounding_assertion:{item.get('id','unknown')}:{item.get('status')}" for item in unsupported)
        elif blockers:
            disposition = GroundingDisposition.not_computable
            unresolved.extend(f"shadow:{item.get('code','UNKNOWN')}:{item.get('subject_id','unknown')}" for item in blockers)
        elif not refs:
            disposition = GroundingDisposition.not_computable
            unresolved.append("grounding:no_evidence_refs")
        elif supported:
            disposition = GroundingDisposition.resolved
        else:
            disposition = GroundingDisposition.provisional
            unresolved.append("grounding:no_explicit_supported_assertion")
    provenance = ({"source":"MosesGroundingComposer.v1","meaning_packet_hash":meaning.canonical_hash,"meaning_status":meaning.status.value,"calibration_evidence_refs":list(sorted(set(calibration_evidence_refs))),"grounding_assertions":list(assertions),"shadow_authority":"DETECTION_ONLY","resolution_policy":"EXPLICIT_SUPPORTED_ASSERTION_REQUIRED"},)
    return GroundingReceipt(grounding_receipt_id=grounding_receipt_id, meaning_id=meaning.meaning_id, meaning_packet_hash=meaning.canonical_hash or meaning.computed_canonical_hash(), evidence_refs=refs, shadow_findings=findings, grounding_disposition=disposition, unresolved=tuple(sorted(set(unresolved))), provenance=provenance)