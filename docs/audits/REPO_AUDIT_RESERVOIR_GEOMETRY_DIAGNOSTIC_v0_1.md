# REPO_AUDIT_RESERVOIR_GEOMETRY_DIAGNOSTIC_v0_1

## Scope
- Add deterministic SHADOW-only state-space diagnostic metadata surface for reservoir geometry declarations.

## Prior patch dependencies
- GeometricResearchItem/SignalPacket/MetricOperatorRegistry/ProjectionSpec.
- Yggdrasil route metadata, Oracle geometric attachment, HeavyTail calibrator, Counterfactual engine.

## Repo inventory summary
- Reservoir/state-space references exist in broader codebase but no dedicated schema-first metadata contract existed for this diagnostic lane.
- Reused existing deterministic canonical helper patterns.

## Selected patch
- Added schema/core/tests/audit for `ReservoirGeometryDiagnostic.v1`.
- Metadata-only declarations; no simulation, no spectral computation, no Krylov computation, no forecast generation.

## Contract fields
- `schema_version`, `diagnostic_id`, `diagnostic_type`, source refs, `diagnostic_scope`, `reservoir_declarations`, policies (`state_space`, `spectral`, `krylov`, `forecasting`), `output_contract`, `computation_status`, `governance_flags`, `provenance`, `created_at_utc`, `canonical_hash`.

## State-space diagnostic metadata guarantees
- Declarations/evidence are allowlisted and deterministic.
- Policy booleans hard-lock non-computing, non-mutating behavior.
- Output contract allows labels/notes only.

## No computation / no reservoir simulation guarantees
- No reservoir simulation.
- No spectral estimation.
- No Krylov-chain computation.
- No forecast generation/probability update.

## No Oracle/Forecast/YGGDRASIL/Runtime mutation guarantees
- No Oracle mutation.
- No FORECAST lane influence.
- No YGGDRASIL routing mutation.
- No runtime/scheduler mutation.

## Authority locks
- Governance flags hard-locked false.

## Files added/changed
- `contracts/canon/reservoir_geometry_diagnostic.v1.schema.json`
- `core/reservoir_geometry_diagnostic.py`
- `tests/test_reservoir_geometry_diagnostic.py`
- `docs/audits/REPO_AUDIT_RESERVOIR_GEOMETRY_DIAGNOSTIC_v0_1.md`

## Validation commands
- `python -m pip install -e '.[dev]'`
- `python -m pytest tests/test_geometric_research_item.py tests/test_geometric_signal_packet.py tests/test_metric_operator_registry.py tests/test_geometric_projection_spec.py tests/test_yggdrasil_geometric_route_metadata.py tests/test_oracle_geometric_signal_attachment.py tests/test_heavy_tail_signal_calibrator.py tests/test_counterfactual_geometry_engine.py tests/test_reservoir_geometry_diagnostic.py -q`
- `python scripts/run_fast_ci.py`
- `python -m pytest -q`
- `python -m pip_audit`
- governance scan command from patch prompt.

## Drift observations
- No authority drift.
- No Oracle/Forecast/YGGDRASIL/runtime mutation introduced.
- Diagnostic metadata surface only.

## Next recommended patch
- `GEOMETRIC_RUNTIME_CONSOLIDATION_RECEIPT_V1`

## Final seal
- `RESERVOIR_GEOMETRY_DIAGNOSTIC_STATUS=ADDED`
- `PATCH_STATUS=SCHEMA_FIRST_STATE_SPACE_DIAGNOSTIC_METADATA_ADDED_NO_COMPUTATION`
- `AUTHORITY_STATE=ADVISORY_ONLY`
- `NEXT_PATCH_TYPE=GEOMETRIC_RUNTIME_CONSOLIDATION_RECEIPT_V1`
- `VALIDATION_STATUS=PASS_OR_REPORTED_FAILURE`
