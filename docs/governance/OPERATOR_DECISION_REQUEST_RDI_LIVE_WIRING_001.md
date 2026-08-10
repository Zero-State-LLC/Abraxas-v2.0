# Operator Decision Request — RDI Live Wiring 001

Status: **SCOPING ANSWERED — Decision 1 implementation precondition satisfied**

This request records the operator scoping required before implementing the
Decision 1 SANDBOX-only live shadow ingest lane from PR [#1110](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/1110)
and the operator decision recorded in PR [#1113](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/1113).

## Decision 1 scoping answer

The operator supplied the following exact scope:

> Scoping for #1110 shadow live-wire: target EvidencePack.v0 claims with register=OBSERVED|INFERRED on the 8 InstantiationVector dims (symbolic_persistence..recursive_reinforcement). Windows: EvidencePack.time_horizon + EvidenceObject timestamps. Real construct H via CFAR ConstructPacket: construct='RDI instantiation vector H', status=EMERGENT, variable_class=HYBRID, dimensions=vector list, assumptions=per REPRESENTATION_DRIVEN_INSTANTIATION_001, route=EVIDENCE_RETRIEVAL.

This answers the evidence-register, time-window, and CFAR-construct questions.
The binding precondition for Decision 1 is therefore satisfied. The resulting
implementation remains SANDBOX-only, detection-only, dry-run-only, and writes
artifacts under `out/`; it does not update the console feed or grant any
execution, activation, settlement, forecast, intervention, or canon authority.

The bindable addendum is
[`rdi_live_wiring_operator_decision_record_002.json`](../../operator_input/rdi_live_wiring_operator_decision_record_002.json)
and its paired human-readable companion. It supplements record 001 without
changing Decision 2.

The implementation binds a claim to a vector dimension only when the claim
explicitly carries the canonical `dimension` name; claim text is never parsed or
reinterpreted. It accepts the pack window only as a parseable ISO-8601
`start/end` interval, resolves claim `source_ids` through the pack source table,
and binds the resulting `EvidenceObject.v1` hashes and timestamps. Missing,
ambiguous, or wholly out-of-window evidence fails closed.

## Decision 2 boundary

Decision 2 remains blocked on complete `SettlementVerdict.v1` coverage. The
legacy `binding_status` path in `core/brier/runtime.py` is intentionally not
changed by this request or its implementation.
