# Operator Runtime Console — operator_runtime_console_001

**Patch:** `PATCH-P11-OPERATOR-RUNTIME-CONSOLE-001`
**Final Status:** `BLOCKED`
**Projection Only:** `True`
**Advisory Only:** `True`

## Authority Boundary
- authority_granted: `false`  mutation_allowed: `false`  promotion_allowed: `false`

## Artifact Health
- Total source artifacts: 6
- Present: 5
- **Missing (1):**
  - `out/audit/runtime_performance_profile_001.latest.json`

## Benchmark Summary
- Status: `PRESENT`
- Drift detected: `True`
- Drift signals: `variance_spike`

## Cache & Replay
- Cache safety: `SAFE`
- Replay equivalence held: `True`

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
- Escalations: `0`
- Top categories: `drift_review`, `missing_artifact_review`, `render_blocker_review`

## Temporal State Diff
- Status: `PASS`
- Total changes: `0`
- Topology changes: `0`
- Lineage shifts: `0`
- Drift acceleration: `NO_ACCELERATION`
- Replay equivalence changes: `NO_CHANGE`
- Queue deltas: `0`
- Transport deltas: `0`

## Operator Next Actions
- BLOCKED: Generate missing source artifact — out/audit/runtime_performance_profile_001.latest.json
- ADVISORY: Investigate benchmark drift signal — variance_spike

## Remaining Blockers
- `drift_signal:variance_spike`
- `missing_artifact:out/audit/runtime_performance_profile_001.latest.json`
