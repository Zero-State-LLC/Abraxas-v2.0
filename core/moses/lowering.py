"""Deterministic IR lowering verifier for the Moses contract spine."""
from __future__ import annotations
from collections.abc import Mapping, Sequence
from typing import Any
from core.moses.contracts import ArchitecturePacket, GroundingDisposition, GroundingReceipt, LoweringStep, MeaningPacket

_STAGES=("DOMAIN","REQUIREMENTS","JOURNEY","WORKFLOW","STATE_TRANSITION","CONTRACT","DATA_GOVERNANCE_ARCHITECTURE","ACCEPTANCE","IMPLEMENTATION")

def _ids(items: Sequence[Mapping[str, Any]], kind: str) -> tuple[str,...]:
    values=[]
    for item in items:
        value=str(item.get("id","")).strip()
        if not value: raise ValueError(f"{kind} item requires id")
        values.append(value)
    if len(values)!=len(set(values)): raise ValueError(f"{kind} ids must be unique")
    return tuple(values)

def _require_refs(items: Sequence[Mapping[str, Any]], field: str, allowed: set[str], kind: str) -> None:
    for item in items:
        refs=tuple(str(x) for x in item.get(field,()))
        if not refs: raise ValueError(f"{kind}:{item.get('id')} requires {field}")
        missing=set(refs)-allowed
        if missing: raise ValueError(f"{kind}:{item.get('id')} has unresolved {field}: {sorted(missing)}")

def build_architecture_packet(meaning: MeaningPacket, grounding: GroundingReceipt, *, architecture_id: str, domain: Mapping[str,Any], requirements: Sequence[Mapping[str,Any]], journeys: Sequence[Mapping[str,Any]], workflows: Sequence[Mapping[str,Any]], state_transitions: Sequence[Mapping[str,Any]], contracts: Sequence[Mapping[str,Any]], acceptance_tests: Sequence[Mapping[str,Any]], implementation_tasks: Sequence[Mapping[str,Any]]) -> ArchitecturePacket:
    """Validate the behavioral chain and emit an advisory ArchitecturePacket."""
    if grounding.meaning_id != meaning.meaning_id or grounding.meaning_packet_hash != meaning.canonical_hash:
        raise ValueError("grounding receipt does not bind supplied MeaningPacket")
    if grounding.grounding_disposition not in {GroundingDisposition.resolved, GroundingDisposition.provisional}:
        raise ValueError("grounding disposition does not permit architectural lowering")
    req_ids=set(_ids(requirements,"requirement")); journey_ids=set(_ids(journeys,"journey")); workflow_ids=set(_ids(workflows,"workflow")); state_ids=set(_ids(state_transitions,"state_transition")); contract_ids=set(_ids(contracts,"contract")); acceptance_ids=set(_ids(acceptance_tests,"acceptance_test")); task_ids=set(_ids(implementation_tasks,"implementation_task"))
    meaning_refs={str(x.get("claim_id")) for x in (*meaning.observations,*meaning.interpretations) if x.get("claim_id")}
    if not meaning_refs: raise ValueError("architectural lowering requires upstream claim references")
    _require_refs(requirements,"meaning_refs",meaning_refs,"requirement")
    _require_refs(journeys,"requirement_refs",req_ids,"journey")
    _require_refs(workflows,"journey_refs",journey_ids,"workflow")
    _require_refs(state_transitions,"workflow_refs",workflow_ids,"state_transition")
    _require_refs(contracts,"state_transition_refs",state_ids,"contract")
    _require_refs(acceptance_tests,"contract_refs",contract_ids,"acceptance_test")
    _require_refs(implementation_tasks,"acceptance_test_refs",acceptance_ids,"implementation_task")
    stages=[]
    refs=[tuple(sorted(meaning_refs)),tuple(sorted(req_ids)),tuple(sorted(journey_ids)),tuple(sorted(workflow_ids)),tuple(sorted(state_ids)),tuple(sorted(contract_ids)),("data-governance-architecture",),tuple(sorted(acceptance_ids)),tuple(sorted(task_ids))]
    for i,stage in enumerate(_STAGES):
        stages.append(LoweringStep(stage=stage,input_refs=refs[i-1] if i else tuple(sorted(meaning_refs)),output_refs=refs[i],preserved_invariants=meaning.semantic_invariants))
    return ArchitecturePacket(architecture_id=architecture_id,meaning_id=meaning.meaning_id,meaning_packet_hash=meaning.canonical_hash or meaning.computed_canonical_hash(),grounding_receipt_id=grounding.grounding_receipt_id,grounding_receipt_hash=grounding.canonical_hash or grounding.computed_canonical_hash(),grounding_disposition=grounding.grounding_disposition,semantic_invariants=meaning.semantic_invariants,lowering_trace=tuple(stages),domain=dict(domain),requirements=tuple(dict(x) for x in requirements),journeys=tuple(dict(x) for x in journeys),workflows=tuple(dict(x) for x in workflows),state_transitions=tuple(dict(x) for x in state_transitions),contracts=tuple(dict(x) for x in contracts),acceptance_tests=tuple(dict(x) for x in acceptance_tests),implementation_tasks=tuple(dict(x) for x in implementation_tasks),provenance=({"source":"MosesLoweringVerifier.v1","authority":"ADVISORY_ONLY"},))