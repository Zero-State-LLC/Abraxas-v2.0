# Global Ingest Separate Implementation Spec Plan

- `status`: `GLOBAL_INGEST_SEPARATE_IMPLEMENTATION_SPEC_PLAN_CONSUMED_BY_IMPLEMENTATION_SPEC`
- `spec_authoring_allowed`: `True`
- `implementation_authorized`: `False`
- `execution_authority`: `False`
- `recommended_next_patch`: `NOT_COMPUTABLE`

## Planned Delivery Surfaces

- `contracts/operator_review/global_ingest_adapter_spine_implementation_spec.v1.schema.json`
- `core/global_ingest_adapter_spine_implementation_spec.py`
- `scripts/run_global_ingest_adapter_spine_implementation_spec.py`
- `tests/test_global_ingest_adapter_spine_implementation_spec.py`
- `out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.json`
- `out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.md`

## Blocked Delivery Surfaces

- `core/oracle_signal.py`
- `scripts/run_ingest_once.py behavior changes`
- `scripts/run_oracle_intake.py behavior changes`
- `contracts/pipelines runtime binding mutations`
- `contracts/yggdrasil route mutations`
