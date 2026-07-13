# Loop Types & Controls

## Loop Types
- **Turn-based**: Short/one-off tasks. Stop on agent judgment, user context, or single verifiable step.
- **Goal-based**: Explicit machine-checkable goal (e.g., "all touched tests + Brier ≥0.9 + git clean + receipt emitted").
- **Time-based**: Scheduled (cron, night-shift sweeps, periodic ingest/audit).
- **Proactive**: Self-triggered on recurring signals (e.g., new commits, drift detection, oracle intake).

Auto-detect or let user specify. Default to goal-based for most Abraxas engineering.

## Controls
- Iteration caps (prevent infinite loops).
- No-progress detection (reset or escalate after N stagnant cycles).
- Generator/Evaluator split (mandatory).
- Token/effort management: choose model; prefer strong verification skills to reduce tokens.
- Partial outputs + escalation on cost overrun.
- Fail-closed on dangerous surfaces (canon mutation, git changes without grant, Research Canary, runtime authority).