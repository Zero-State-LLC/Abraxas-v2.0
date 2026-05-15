# Operator Runtime Console — operator_runtime_console_001

**Patch:** `PATCH-P11-OPERATOR-RUNTIME-CONSOLE-001`
**Final Status:** `BLOCKED`
**Projection Only:** `True`
**Advisory Only:** `True`

## Authority Boundary
- authority_granted: `false`  mutation_allowed: `false`  promotion_allowed: `false`

## Artifact Health
- Total source artifacts: 5
- Present: 3
- **Missing (2):**
  - `out/audit/runtime_benchmark_001.latest.json`
  - `out/audit/runtime_performance_profile_001.latest.json`

## Benchmark Summary
- Status: `NOT_COMPUTABLE`

## Cache & Replay
- Cache safety: `NOT_COMPUTABLE`
- Replay equivalence held: `NOT_COMPUTABLE`

## Replay Scaling
- Status: `PRESENT`
- Invalidated nodes: `2`
- Skipped surfaces: `4`
- Replay chunks: `1`
- Equivalence verified: `True`
- Incremental replay health: `HEALTHY`
- Invalidation posture: `INCREMENTAL`

## Operator Action Queue
- Status: `ADVISORY_ONLY`
- Queue items: `4`
- Pending approvals: `4`
- Escalations: `1`
- Top categories: `missing_artifact_review`, `render_blocker_review`

## Temporal State Diff
- Status: `NOT_COMPUTABLE`
- Total changes: `0`
- Topology changes: `0`
- Lineage shifts: `0`
- Drift acceleration: `NO_ACCELERATION`
- Replay equivalence changes: `NO_CHANGE`
- Queue deltas: `0`
- Transport deltas: `0`

## Operator Next Actions
- BLOCKED: Generate missing source artifact — out/audit/runtime_benchmark_001.latest.json
- BLOCKED: Generate missing source artifact — out/audit/runtime_performance_profile_001.latest.json

## Remaining Blockers
- `missing_artifact:out/audit/runtime_benchmark_001.latest.json`
- `missing_artifact:out/audit/runtime_performance_profile_001.latest.json`
