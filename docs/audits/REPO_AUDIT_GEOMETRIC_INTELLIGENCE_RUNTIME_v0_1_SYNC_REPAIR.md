# REPO_AUDIT_GEOMETRIC_INTELLIGENCE_RUNTIME_v0_1_SYNC_REPAIR

## Scope
- Branch-state sync repair restoring missing `GeometricResearchItem.v1` surfaces.

## Drift observed
- `geometric_signal_packet` existed while `geometric_research_item` schema/core/tests were absent in the current branch checkout.

## Repair action
- Re-added `GeometricResearchItem.v1` schema, core deterministic helpers, and focused tests.
- Left `GeometricSignalPacket.v1` semantics unchanged.

## Files restored/added
- `contracts/canon/geometric_research_item.v1.schema.json`
- `core/geometric_research_item.py`
- `tests/test_geometric_research_item.py`

## Compatibility with GeometricSignalPacket.v1
- `GeometricSignalPacket.v1` remains decoupled and references research item IDs as plain strings.
- No object import coupling introduced between the two packet types.

## Validation
- `python -m pip install -e '.[dev]'`
- `python -m pytest tests/test_geometric_research_item.py tests/test_geometric_signal_packet.py -q`
- `python scripts/run_fast_ci.py`
- `python -m pytest -q`
- `python -m pip_audit`

## Governance scan
- Forbidden authority booleans set to `true` were scanned across core/scripts/tests/contracts/docs/README/PLANS/AGENTS/input/out.

## Next recommended patch
- `METRIC_OPERATOR_REGISTRY_V1`

## Final seal
- `GEOMETRIC_RESEARCH_ITEM_STATUS=RESTORED_OR_ADDED`
- `GEOMETRIC_SIGNAL_PACKET_COMPATIBILITY=PASS`
- `BRANCH_SYNC_STATUS=REPAIRED`
- `AUTHORITY_STATE=ADVISORY_ONLY`
- `NEXT_PATCH_TYPE=METRIC_OPERATOR_REGISTRY_V1`
- `VALIDATION_STATUS=PASS_OR_REPORTED_FAILURE`
