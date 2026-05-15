# Operator Action Queue — operator_action_queue_001

**Patch:** `PATCH-P18-OPERATOR-ACTION-QUEUE-AND-REVIEW-SPINE-001`
**Final Status:** `ADVISORY_ONLY`
**Queue Item Count:** `3`
**Pending Approvals:** `3`
**Escalation Count:** `1`

## Severity Counts
- `HIGH`: `3`

## Blocked Sources
- `out/audit/operator_runtime_console_001.latest.json`
- `out/audit/runtime_benchmark_001.latest.json`
- `out/audit/runtime_performance_profile_001.latest.json`

## Recommended Operator Next Actions
- BLOCKED: Generate missing source artifact — out/audit/runtime_benchmark_001.latest.json
- BLOCKED: Generate missing source artifact — out/audit/runtime_performance_profile_001.latest.json
- Review missing artifact evidence and rerun upstream generation for out/audit/runtime_benchmark_001.latest.json.
- Review missing artifact evidence and rerun upstream generation for out/audit/runtime_performance_profile_001.latest.json.
- Review render blocker evidence before treating graph render surfaces as reliable.
