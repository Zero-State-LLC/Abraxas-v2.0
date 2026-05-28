---
name: P103 replay observations path
description: How to unblock P103 from CONTINUE loop (replay_run_count: 0)
---
P103 (`run_research_shadow_replay_audit.py`) reads per-candidate `replay_run_hashes` from an optional `--replay-observations-path` argument. Without it, all six candidates show replay_run_count=0 → status=SHADOW_REPLAY_AUDIT_EMITTED with recommended_next_lane=P103 (CONTINUE loop), blocking P104–P130.

**Fix:** `python scripts/run_research_shadow_replay_audit.py --replay-observations-path input/research_shadow_replay_observations.json`

**Why:** The pre-existing file at `input/research_shadow_replay_observations.json` contains 12 replay_run_hashes per candidate (all six DROP006A/B/C, DROP007A/B/C). Without this argument, the module defaults to empty hashes.

**How to apply:** Whenever a session refresh/spine-refresh overwrites `out/research_shadow_replay_audit/latest.json`, always supply the observations path when re-running P103.
