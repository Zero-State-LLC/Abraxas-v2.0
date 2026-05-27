# REPO_AUDIT_COUNTERFACTUAL_GEOMETRY_ENGINE_v0_1

## Scope
- Add deterministic SHADOW-only branch metadata surface for counterfactual geometry declarations.

## Prior patch dependencies
- Geometric research/signal/operator/projection surfaces.
- YGGDRASIL geometric route metadata.
- Oracle geometric attachment and heavy-tail calibrator metadata surfaces.

## Repo inventory summary
- Branch/counterfactual references exist in broader repo surfaces, but no dedicated schema-first counterfactual geometry metadata contract existed.
- Existing deterministic canonical helper patterns reused.

## Selected patch
- Added schema/core/tests/audit for `CounterfactualGeometryEngine.v1`.
- Metadata-only counterfactual branch declarations, no computation or scenario generation.

## Contract fields
- `schema_version`, `engine_id`, `engine_type`, `source_attachment_refs`,
  `source_signal_packet_refs`, `source_metric_registry_refs`, `source_projection_refs`,
  `source_route_metadata_refs`, `counterfactual_scope`, `branch_declarations`,
  `geometry_policy`, `diffusion_policy`, `comparison_policy`, `output_contract`,
  `computation_status`, `governance_flags`, `provenance`, `created_at_utc`, `canonical_hash`.

## Branch metadata guarantees
- Branch declarations are metadata-only, evidence-gated, and deterministic.
- Scope constrains intended lane and branch family via allowlists.
- Output contract emits labels/notes only; no scores/scenarios/probability/runtime controls.

## No computation / no scenario generation guarantees
- No counterfactual scenario generation.
- No branch scoring.
- No diffusion/smoothing computation.
- No probability updates.

## No Oracle/Forecast/P27/P28/YGGDRASIL/Runtime mutation guarantees
- No Oracle signal mutation.
- No Forecast influence.
- No P27/P28 continuity mutation.
- No YGGDRASIL routing mutation.
- No runtime/scheduler mutation.

## Authority locks
- Governance flags hard-locked false.

## Files added/changed
- `contracts/canon/counterfactual_geometry_engine.v1.schema.json`
- `core/counterfactual_geometry_engine.py`
- `tests/test_counterfactual_geometry_engine.py`
- `docs/audits/REPO_AUDIT_COUNTERFACTUAL_GEOMETRY_ENGINE_v0_1.md`

## Validation commands
- `python -m pip install -e '.[dev]'`
- `python -m pytest tests/test_geometric_research_item.py tests/test_geometric_signal_packet.py tests/test_metric_operator_registry.py tests/test_geometric_projection_spec.py tests/test_yggdrasil_geometric_route_metadata.py tests/test_oracle_geometric_signal_attachment.py tests/test_heavy_tail_signal_calibrator.py tests/test_counterfactual_geometry_engine.py -q`
- `python scripts/run_fast_ci.py`
- `python -m pytest -q`
- `python -m pip_audit`
- governance scan command from patch prompt.

## Drift observations
- No authority drift.
- No Oracle/Forecast/P27/P28/YGGDRASIL/runtime mutation introduced.
- Branch metadata surface only.

## Next recommended patch
- `RESERVOIR_GEOMETRY_DIAGNOSTIC_V1`

## Final seal
- `COUNTERFACTUAL_GEOMETRY_ENGINE_STATUS=ADDED`
- `PATCH_STATUS=SCHEMA_FIRST_BRANCH_METADATA_ADDED_NO_COMPUTATION`
- `AUTHORITY_STATE=ADVISORY_ONLY`
- `NEXT_PATCH_TYPE=RESERVOIR_GEOMETRY_DIAGNOSTIC_V1`
- `VALIDATION_STATUS=PASS_OR_REPORTED_FAILURE`
