# Oracle Signal Physical Implementation Authorization Handoff

This packet is documentation only. It does not grant execution authority,
ingest runner mutation, runtime mutation, or canon promotion.

## Files

- Example template: `operator_input/templates/oracle_signal_physical_implementation_authorization_payload_001.example.json`
- Real payload path: `operator_input/oracle_signal_physical_implementation_authorization_payload_001.json`
- Preflight: `python3 scripts/preflight_oracle_signal_physical_implementation_authorization_payload.py`
- Intake gate: `python3 scripts/ingest/run_oracle_signal_physical_implementation_authorization_intake_gate.py`
- Authorization record: `python3 scripts/ingest/run_oracle_signal_physical_implementation_authorization_record.py`

## Required Attestation Groups

- `operator_identity`
- `operator_decision`
- `acknowledgements`

## Allowed `selected_decision` Values

| Value | Effect |
|-------|--------|
| `APPROVE_PHYSICAL_IMPLEMENTATION` | Advisory shadow implementation authorized; execution denied |
| `MAINTAIN_HOLD` | Physical implementation hold maintained |

## Critical Hash Binding

`operator_decision.source_review_hash` must match `source_review_hash` from:

`out/operator_review/oracle_signal_physical_implementation_authorization_record_plan_001.latest.json`

Refresh this hash if the physical implementation review artifact regenerates.

## Evidence Collection Steps

From `out/operator_review/oracle_signal_physical_implementation_authorization_evidence_collection_plan_001.latest.json`:

1. Collect explicit operator identity, role, timestamp, and selected decision.
2. Bind the operator decision to the held physical implementation review hash and record-plan hash.
3. Collect acknowledgment that execution, runtime, scheduler, route, queue, canon, forecast, writeback, and token authority remain denied unless separately authorized.
4. Collect rollback and fail-closed acknowledgments for any future physical implementation proposal.

## Fields Daniel Must Replace

- `operator_attestation_hash`
- `operator_reviewed_at_source_observed`
- `source_review_hash` (must match current record plan)

## Validation Workflow

```bash
python3 scripts/preflight_oracle_signal_physical_implementation_authorization_payload.py
python3 scripts/ingest/run_oracle_signal_physical_implementation_authorization_intake_gate.py
python3 scripts/ingest/run_oracle_signal_physical_implementation_authorization_record.py
python3 scripts/run_global_pipeline_gap_backlog.py
```

Passing intake validation still grants no execution authority.
