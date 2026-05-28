# REPO AUDIT — CHAMFER EXPECTED DISTANCE VALUE PLAN v0.1

## Scope
- Added deterministic planning-only metadata surface for CHAMFER expected-distance values.
- No expected distance values were introduced.
- No tolerance values were introduced.
- No CHAMFER math, metric emission, or runtime loading was introduced.

## Added Surfaces
1. `contracts/canon/chamfer_expected_distance_value_plan.v1.schema.json`
2. `core/chamfer_expected_distance_value_plan.py`
3. `tests/test_chamfer_expected_distance_value_plan.py`

## Governance and Authority
- Advisory-only posture preserved.
- Governance flags remain locked false.
- No activation, authorization, execution, or canon-promotion tokens emitted.

## Determinism
- Stable canonical serialization with trailing newline.
- Canonical hash computed from preimage that excludes `canonical_hash`.
- Group and mapping collections sorted by deterministic IDs in builder.

## Validation Coverage
- Required top-level field presence.
- Non-empty required source refs and mapping groups.
- Duplicate ID rejection (group and mapping IDs).
- Locked-map mutation rejection.
- Governance truthy flag rejection.
- Expected-distance/tolerance/math/metric/runtime enablement rejection via locked constraints.
- Schema validation via `jsonschema` (`importorskip`).

## Out-of-Scope Guarantee
This patch does not add any expected distance values, tolerance values, or runtime/math behavior.
