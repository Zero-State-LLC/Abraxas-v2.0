# REPO AUDIT — ORACLE_GEOMETRIC_ATTACHMENT_STABILIZATION_WINDOW v0.1

## Scope
Stabilization-window declaration metadata for `OracleGeometricAttachmentStabilizationWindow.v1`.

## Source archive boundary
Anchored to `GEOMETRIC_INTELLIGENCE_RUNTIME_v0.1 FINAL ARCHIVE RECEIPT`.

## Prior batch dependency
- `AALVizGeometricRendererImplementationPlan.v1`
- `MetricOperatorImplementationSelectionPlan.v1`

## Repo inventory summary
Oracle geometric signal attachment and replay receipt metadata surfaces are present and validated. This patch adds declaration-only stabilization-window metadata with no execution semantics.

## Selected patch
Added stabilization-window schema, deterministic core builder/validator/hash/serializer, focused tests, and this audit receipt.

## Contract fields
Includes required top-level fields, strict scope/requirement enums, non-empty observation requirements, exact locked stability/constraint/effect/output booleans, governance false-locks, provenance token guards, and canonical hash contract.

## Stabilization-window guarantees
- Window is declaration-only metadata.
- Deterministic ordering and serialization behavior enforced.
- Canonical hash excludes `canonical_hash` preimage.

## No stabilization execution guarantees
- No stabilization execution introduced.
- No replay execution introduced.
- No Oracle score recomputation introduced.

## No Oracle/Forecast/YGGDRASIL/Runtime/Scheduler mutation guarantees
- No Oracle packet/runtime mutation.
- No forecast mutation or influence.
- No YGGDRASIL route mutation.
- No runtime/scheduler/canon mutation.

## Authority locks
All governance flags remain required and locked false:
`production_activation`, `canon_promotion`, `scheduler_mutation`, `runtime_authority`, `runtime_mutation`, `forecast_influence`, `execution_authority`, `token_minting_allowed`, `valid_for_execution`, `activation_approved`, `authorization_granted`.

## Files added/changed
- `contracts/canon/oracle_geometric_attachment_stabilization_window.v1.schema.json`
- `core/oracle_geometric_attachment_stabilization_window.py`
- `tests/test_oracle_geometric_attachment_stabilization_window.py`
- `docs/audits/REPO_AUDIT_ORACLE_GEOMETRIC_ATTACHMENT_STABILIZATION_WINDOW_v0_1.md`

## Validation commands
- `python -m pip install -e '.[dev]'`
- `python -m pytest tests/test_oracle_geometric_attachment_stabilization_window.py -q`
- `ABRAXAS_PYRIGHT_TIMEOUT_SECONDS=60 python scripts/run_fast_ci.py`
- `python -m pip_audit`
- governance `rg` scan for true authority flags

## Drift observations
No execution drift introduced; stabilization-window metadata only.

## Next recommended batch
`YGGDRASIL_GEOMETRIC_ROUTE_STABILIZATION_WINDOW_V1`

## Final seal
ORACLE_GEOMETRIC_ATTACHMENT_STABILIZATION_WINDOW_STATUS=ADDED
PATCH_STATUS=STABILIZATION_WINDOW_METADATA_ADDED_NO_EXECUTION
AUTHORITY_STATE=ADVISORY_ONLY
NEXT_BATCH=YGGDRASIL_GEOMETRIC_ROUTE_STABILIZATION_WINDOW_V1
VALIDATION_STATUS=PASS_OR_REPORTED_FAILURE
