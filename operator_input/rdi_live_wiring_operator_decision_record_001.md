# RDI Live Wiring — Operator Decision Record 001

Operator: **Daniel Meyer** (`daniel_meyer`), responding in the team Buzz channel on 2026-08-10.

Payload: [`rdi_live_wiring_operator_decision_record_001.json`](rdi_live_wiring_operator_decision_record_001.json)

Upstream request: [PR #1110](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/1110), [`OPERATOR_DECISION_REQUEST_RDI_LIVE_WIRING_001.md`](../docs/governance/OPERATOR_DECISION_REQUEST_RDI_LIVE_WIRING_001.md).

## Decision 1 — live shadow ingest

**Option B — SANDBOX only.** Live/real ingest evidence may be consumed by the SHADOW RDI detector only for dry runs producing artifacts under `out/`. This is detection-only: no console feed change, explanation, forecast, intervention, settlement, or canon touch. The authority block remains hard-false.

This is a bounded authorization record, not implementation authorization. Before wiring is implemented, the operator must specify which evidence registers/windows and which CFAR construct(s) real construct `H` should target.

## Decision 2 — legacy `binding_status` scoring path

**Option B — approved in principle, not yet executable.** The legacy `binding_status` outcome path in `build_brier_ledger` remains in place until resolver/settlement flows produce `SettlementVerdict.v1` verdicts for every scored outcome. The precondition is tracked by open issue [#1112](https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/issues/1112).

## Authority boundary

This record authorizes no runtime execution or mutation, console-feed change, queue/scheduler mutation, settlement, explanation/forecast/intervention, canon mutation, production activation, or authority grant. Downstream gates bind to payload SHA-256 `sha256:edd82736fb99f0ae009ec2229861a9751515a71e38b14a4332a4d7d659e20faa`, computed as `jq -S -c` canonical JSON with `binding.payload_sha256` set to `null`.
