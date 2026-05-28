# REPO AUDIT — CHAMFER EXPECTED DISTANCE VALUES ACTUAL PR v0.1

## 1. Scope
This patch adds deterministic static `expected_distance` values to eligible valid CHAMFER fixtures and updates manifest metadata to record expected-distance presence.

The patch remains advisory-only. It does not add tolerance values, CHAMFER runtime math, metric emission, runtime fixture loading, scoring, scheduler/cache/runtime mutation, forecast influence, canon promotion, activation, authorization, or execution authority.

## 2. Operator authorization path
- Selected operator: `CHAMFER_DISTANCE`
- Boundary: `CHAMFER_EXPECTED_DISTANCE_VALUES_ACTUAL_PR_V1`
- Posture: `ADVISORY_ONLY`
- Prior gate dependency: `CHAMFER_EXPECTED_DISTANCE_VALUES_ACTUAL_PR_GATE_V1`
- Next boundary: `CHAMFER_EXPECTED_DISTANCE_VALUES_ARCHIVE_RECEIPT_V1_OR_CHAMFER_DISTANCE_IMPLEMENTATION_PLAN_V1`

## 3. Expected distance policy
Expected distances are static fixture metadata only. The stored values follow the symmetric Chamfer mean-distance convention using squared Euclidean nearest-neighbor distances:

1. Compute the mean nearest-neighbor squared distance from point set A to point set B.
2. Compute the mean nearest-neighbor squared distance from point set B to point set A.
3. Store `expected_distance` as the average of those two directional means.

No reusable runtime metric operator is introduced by this patch.

## 4. Valid fixture value summary
The valid fixtures now carry expected-distance values and `expected_status=VALID_INPUT_WITH_EXPECTED_DISTANCE`:

| Fixture ID | expected_distance |
| --- | ---: |
| `chamfer.valid.identical_point_sets.v1` | `0.0` |
| `chamfer.valid.offset_point_sets.v1` | `1.0` |
| `chamfer.valid.partial_overlap_point_sets.v1` | `0.5` |
| `chamfer.valid.duplicate_points.v1` | `0.0` |
| `chamfer.valid.multidimensional_points.v1` | `3.0` |

## 5. Null-locked fixture summary
Invalid fixtures remain null-locked with `expected_distance=null` and `expected_status=INVALID_INPUT_NO_EXPECTED_DISTANCE`.

NOT_COMPUTABLE fixtures remain null-locked with `expected_distance=null` and `expected_status=NOT_COMPUTABLE_NO_EXPECTED_DISTANCE`.

## 6. Manifest update summary
The CHAMFER fixture manifest now records:

- `expected_distances_added=true`
- `tolerance_values_added=false`
- `chamfer_math_added=false`
- `metric_values_emitted=false`
- `runtime_loading_enabled=false`
- sorted `expected_distance_fixture_ids`
- sorted `null_locked_fixture_ids`
- static expected-distance policy metadata

Existing `fixture_ids` and `fixture_paths` deterministic ordering is preserved.

## 7. Hash and canonicalization summary
For each modified fixture and the manifest:

- JSON is serialized with sorted keys.
- Compact separators are used.
- `ensure_ascii=false` behavior is preserved.
- A final newline is present.
- `canonical_hash` is excluded from its own preimage.
- `canonical_hash` is recomputed after metadata updates.

## 8. Governance locks
All governance flags remain false:

- `production_activation=false`
- `canon_promotion=false`
- `scheduler_mutation=false`
- `runtime_authority=false`
- `runtime_mutation=false`
- `forecast_influence=false`
- `execution_authority=false`
- `token_minting_allowed=false`
- `valid_for_execution=false`
- `activation_approved=false`
- `authorization_granted=false`

## 9. Out-of-scope locks preserved
- No tolerance values added.
- No CHAMFER math added.
- No metric values emitted.
- No runtime loading enabled.
- No Oracle mutation added.
- No YGGDRASIL mutation added.
- No AAL-Viz mutation added.
- No scheduler/cache/runtime mutation added.
- No forecast influence added.
- No canon promotion added.
- No execution authority added.
- No scoring added.

## 10. Validation surfaces
Validation coverage is added in `tests/test_chamfer_expected_distance_values.py` and existing CHAMFER fixture-file validation is updated for the new valid-fixture expected-distance state.

## 11. Final seal
- `CHAMFER_EXPECTED_DISTANCE_VALUES_ACTUAL_PR_STATUS=ADDED`
- `PATCH_STATUS=EXPECTED_DISTANCE_VALUES_ADDED_NO_TOLERANCE_NO_MATH`
- `SELECTED_OPERATOR=CHAMFER_DISTANCE`
- `EXPECTED_DISTANCES_ADDED=true`
- `TOLERANCE_VALUES_ADDED=false`
- `CHAMFER_MATH_ADDED=false`
- `METRIC_VALUES_EMITTED=false`
- `RUNTIME_LOADING_ENABLED=false`
- `AUTHORITY_STATE=ADVISORY_ONLY`
- `NEXT_BOUNDARY=CHAMFER_EXPECTED_DISTANCE_VALUES_ARCHIVE_RECEIPT_V1_OR_CHAMFER_DISTANCE_IMPLEMENTATION_PLAN_V1`
- `VALIDATION_STATUS=PASS_OR_REPORTED_FAILURE`
