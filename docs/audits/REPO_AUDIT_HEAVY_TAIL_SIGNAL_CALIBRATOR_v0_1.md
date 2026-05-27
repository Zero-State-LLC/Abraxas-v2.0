# REPO_AUDIT_HEAVY_TAIL_SIGNAL_CALIBRATOR_v0_1

## Scope
- Add deterministic SHADOW-only diagnostic metadata surface for heavy-tail calibration intent/evidence declarations.

## Prior patch dependencies
- Geometric research/signal/operator/projection/route metadata and Oracle geometric attachment metadata surfaces.

## Repo inventory summary
- Geometric and Oracle metadata surfaces exist.
- No dedicated heavy-tail calibrator metadata contract existed.
- Existing canonical hash/serialization patterns reused.

## Selected patch
- Added schema/core/tests/audit for `HeavyTailSignalCalibrator.v1`.
- Metadata-only diagnostic declarations; no scoring/statistical/runtime execution.

## Contract fields
- `schema_version`, `calibrator_id`, `calibrator_type`, `source_attachment_refs`,
  `source_signal_packet_refs`, `source_metric_registry_refs`, `calibration_scope`,
  `tail_model_declarations`, `anomaly_observation_policy`, `threshold_declarations`,
  `output_contract`, `computation_status`, `governance_flags`, `provenance`,
  `created_at_utc`, `canonical_hash`.

## Diagnostic metadata guarantees
- Tail model declarations are metadata-only and evidence-gated.
- Observation policy is hard-locked to non-executing SHADOW-only semantics.
- Threshold declarations are non-executable and cannot affect routing/forecast/scheduler/runtime.
- Output contract emits context/notes only; emits no scores/forecast/runtime controls/authority tokens.

## No computation guarantees
- No heavy-tail score computation.
- No statistical estimation.
- No threshold execution.

## No Oracle/Forecast/Runtime mutation guarantees
- No Oracle score/routing mutation.
- No FORECAST influence.
- No runtime/scheduler/route mutation.

## Authority locks
- Governance flags hard-locked false.

## Files added/changed
- `contracts/canon/heavy_tail_signal_calibrator.v1.schema.json`
- `core/heavy_tail_signal_calibrator.py`
- `tests/test_heavy_tail_signal_calibrator.py`
- `docs/audits/REPO_AUDIT_HEAVY_TAIL_SIGNAL_CALIBRATOR_v0_1.md`

## Validation commands
- `python -m pip install -e '.[dev]'`
- `python -m pytest tests/test_geometric_research_item.py tests/test_geometric_signal_packet.py tests/test_metric_operator_registry.py tests/test_geometric_projection_spec.py tests/test_yggdrasil_geometric_route_metadata.py tests/test_oracle_geometric_signal_attachment.py tests/test_heavy_tail_signal_calibrator.py -q`
- `python scripts/run_fast_ci.py`
- `python -m pytest -q`
- `python -m pip_audit`
- governance scan command from patch prompt.

## Drift observations
- No authority drift.
- No Oracle/Forecast/runtime mutation introduced.
- Diagnostic metadata surface only.

## Next recommended patch
- `COUNTERFACTUAL_GEOMETRY_ENGINE_V1_OR_RESERVOIR_GEOMETRY_DIAGNOSTIC_V1`

## Final seal
- `HEAVY_TAIL_SIGNAL_CALIBRATOR_STATUS=ADDED`
- `PATCH_STATUS=SCHEMA_FIRST_DIAGNOSTIC_METADATA_ADDED_NO_COMPUTATION`
- `AUTHORITY_STATE=ADVISORY_ONLY`
- `NEXT_PATCH_TYPE=COUNTERFACTUAL_GEOMETRY_ENGINE_V1_OR_RESERVOIR_GEOMETRY_DIAGNOSTIC_V1`
- `VALIDATION_STATUS=PASS_OR_REPORTED_FAILURE`
