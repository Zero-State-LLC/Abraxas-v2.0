# RDI Live Wiring — Operator Decision Record 002 Addendum

Operator: **Daniel Meyer** (`daniel_meyer`), responding in the team Buzz channel on 2026-08-10.

Payload: [`rdi_live_wiring_operator_decision_record_002.json`](rdi_live_wiring_operator_decision_record_002.json)

This addendum supplements [`rdi_live_wiring_operator_decision_record_001.json`](rdi_live_wiring_operator_decision_record_001.json)
and resolves only the open scoping preconditions for Decision 1.

## Decision 1 — authoritative SANDBOX scope

> Scoping for #1110 shadow live-wire: target EvidencePack.v0 claims with register=OBSERVED|INFERRED on the 8 InstantiationVector dims (symbolic_persistence..recursive_reinforcement). Windows: EvidencePack.time_horizon + EvidenceObject timestamps. Real construct H via CFAR ConstructPacket: construct='RDI instantiation vector H', status=EMERGENT, variable_class=HYBRID, dimensions=vector list, assumptions=per REPRESENTATION_DRIVEN_INSTANTIATION_001, route=EVIDENCE_RETRIEVAL.

The evidence-register/window and CFAR-construct preconditions in record 001 are
therefore satisfied. The bounded implementation remains SANDBOX-only,
detection-only, and dry-run-only; it writes classified artifacts under `out/`
and does not update the console feed.

## Decision 2 — unchanged and out of scope

This addendum makes no change to Decision 2. The legacy `binding_status` path
remains untouched pending `SettlementVerdict.v1` coverage in #1112.

## Authority boundary

The SHADOW authority block remains hard-false. This record grants no runtime or
production execution, mutation, explanation, forecast, intervention, settlement,
canon, queue/scheduler, console-feed, or authority-grant capability.

Downstream gates bind to payload SHA-256
`sha256:d8edfd3fb9a69a2a9b004fb3c5d8afbec74ca4297ef6ceed2fd59ce4569cb7ee`,
computed as `jq -S -c` canonical JSON with `binding.payload_sha256` set to
`null` and no trailing newline.
