# Abraxas Spec Stack Ingest Schema Audit 001

- id: abraxas_spec_stack_ingest_schema_audit_001
- domain: ingest
- status: ABRAXAS_SPEC_STACK_INGEST_SCHEMA_AUDIT_EMITTED_ADVISORY_ONLY
- recommended_next_lane: NOT_COMPUTABLE

## Contract Summary
- expected_contract_count: 5
- repo_observed_count: 5
- missing_contract_count: 0

## Contract Records
- scheduled_ingest_run_manifest: REPO_CONTRACT_OBSERVED_ADVISORY_ONLY (repo_observed=True)
- oracle_signal_intake_receipt: REPO_CONTRACT_OBSERVED_ADVISORY_ONLY (repo_observed=True)
- oracle_signal_pipeline: REPO_CONTRACT_OBSERVED_ADVISORY_ONLY (repo_observed=True)
- global_ingest_adapter_spine_alignment_plan: REPO_CONTRACT_OBSERVED_ADVISORY_ONLY (repo_observed=True)
- oracle_intake_queue: REPO_CONTRACT_OBSERVED_ADVISORY_ONLY (repo_observed=True)

## Findings
- global_ingest_adapter_spine_shadow_binding_gap: MISSING

## Shadow Binding Refs
- GLOBAL_INGEST_ADAPTER_SPINE_001: REPO_CONTRACT_OBSERVED_ADVISORY_ONLY
- GLOBAL_INGEST_ADAPTER_SPINE_001: REPO_CONTRACT_OBSERVED_ADVISORY_ONLY
