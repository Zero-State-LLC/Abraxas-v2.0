# Global Ingest Adapter Spine Implementation Spec

- `status`: `GLOBAL_INGEST_ADAPTER_SPINE_IMPLEMENTATION_SPEC_READY`
- `patch_id`: `PATCH-ABX-GLOBAL-INGEST-SEPARATE-IMPLEMENTATION-SPEC-001`
- `spec_authoring_allowed`: `True`
- `implementation_authorized`: `False`
- `execution_authority`: `False`
- `recommended_next_patch`: `PATCH-ABX-GLOBAL-INGEST-ADDITIVE-SHADOW-CONTRACTS-001`

## Future Additive Contracts

- `contracts/oracle/oracle_candidate_signal_packet.v1.schema.json`
- `contracts/oracle/oracle_signal_input_envelope_ref.v1.schema.json`
- `contracts/oracle/oracle_signal_intake_receipt.v1.schema.json`

## Preserved Surfaces

- core/oracle_signal.py must remain absent unless a later governed implementation lane authorizes creation
- scripts/run_ingest_once.py behavior remains unchanged
- scripts/run_oracle_intake.py behavior remains unchanged
- contracts/pipelines runtime bindings remain unchanged
- contracts/yggdrasil route bindings remain unchanged

## Blocked Actions

- `CORE_ORACLE_SIGNAL_IMPLEMENTATION`
- `INGEST_RUNNER_BEHAVIOR_MUTATION`
- `PIPELINE_OR_ROUTE_MUTATION`
- `RUNTIME_OR_SCHEDULER_MUTATION`
- `QUEUE_MUTATION`
- `FORECAST_WEIGHTING`
- `CANON_PROMOTION`
- `EXECUTION_AUTHORITY_GRANT`
- `LIVE_NOTION_WRITEBACK`
- `GITHUB_WRITEBACK_AUTOMATION`
- `TOKEN_MINTING`

## Spec Sections

- `GI-SPEC-001` `operator_decision_evidence_binding`: SPECIFIED_ADVISORY_ONLY
- `GI-SPEC-002` `oracle_signal_contract_boundary`: SPECIFIED_ADVISORY_ONLY
- `GI-SPEC-003` `ingest_runner_non_mutation_boundary`: AUTHORITY_DENIED
- `GI-SPEC-004` `pipeline_route_non_mutation_boundary`: AUTHORITY_DENIED
- `GI-SPEC-005` `deterministic_serialization_contract`: SPECIFIED_ADVISORY_ONLY
- `GI-SPEC-006` `shadow_only_validation_plan`: SPECIFIED_ADVISORY_ONLY
- `GI-SPEC-007` `authority_lock_validation_matrix`: SPECIFIED_ADVISORY_ONLY
- `GI-SPEC-008` `rollback_and_fail_closed_plan`: SPECIFIED_ADVISORY_ONLY
