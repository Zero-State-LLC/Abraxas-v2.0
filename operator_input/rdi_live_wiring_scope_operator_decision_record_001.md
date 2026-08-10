# RDI Live Wiring — Scope Resolution Operator Decision Record 001

Operator-supplied scope resolution for Decision 1 from PR #1113, answering the
open precondition carried by the Decision 1 record from PR #1110.

Payload: [`rdi_live_wiring_scope_operator_decision_record_001.json`](rdi_live_wiring_scope_operator_decision_record_001.json)

## Binding precondition

**Satisfied.** The exact operator scope is:

> Scoping for #1110 shadow live-wire: target EvidencePack.v0 claims with register=OBSERVED|INFERRED on the 8 InstantiationVector dims (symbolic_persistence..recursive_reinforcement). Windows: EvidencePack.time_horizon + EvidenceObject timestamps. Real construct H via CFAR ConstructPacket: construct='RDI instantiation vector H', status=EMERGENT, variable_class=HYBRID, dimensions=vector list, assumptions=per REPRESENTATION_DRIVEN_INSTANTIATION_001, route=EVIDENCE_RETRIEVAL.

This record resolves the evidence registers, window sources, target vector, and
CFAR construct required before implementation. It does not itself authorize
execution or production activation.
