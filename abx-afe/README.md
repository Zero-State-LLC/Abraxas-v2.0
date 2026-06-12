# AFE v0.3

Angel Formation Environment (AFE) is an external-adjacent companion module for
Abraxas. It emits trace-only SHADOW packets for observation. It does not filter,
rewrite, suppress, align, govern, constrain, or authorize Abraxas output.

## Runtime

```bash
python scripts/run_afe_cycle.py --seed 42 --agents examples/agents.json --env examples/env.json
```

```bash
python scripts/run_hybrid_cycle.py --batch-id AFE-BATCH-001 --runs 10 --seed-start 42 --environment-set baseline,scarcity,high-noise --export notion
```

`--export notion` emits local Notion-ready payload rows only. It never performs
live Notion writeback.

## Authority

- Authority: `SHADOW_ONLY_TRACE`
- Bridge: `AFE -> Agent Trace Intake Layer -> SHADOW diagnostics`
- Denied: canon mutation, forecast weight mutation, response filtering, Oracle
  constraint behavior, live Notion writeback, auto-loop daemon behavior, and
  Abraxas output generation.
