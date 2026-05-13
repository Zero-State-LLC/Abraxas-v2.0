# Temporal Governance Release Index Registry v1

Deterministic audit/projection-only registry for indexing `TemporalGovernanceReleaseBundle.v1` artifacts.

## Guarantees
- Audit-only and projection-only.
- Non-authoritative and non-executing.
- No mutation, rollback, promotion, routing change, replay normalization, timeline collapse, canonical selection, adapter activation, auto transition, or global runtime activation.

## Main API
- `derive_temporal_governance_release_index_registry(...)`
- `validate_temporal_governance_release_index_registry(...)`
- `canonical_temporal_governance_release_index_registry_json(...)`
- `temporal_governance_release_index_registry_hash(...)`
- `write_temporal_governance_release_index_registry_contract_audit(...)`
