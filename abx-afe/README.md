# AFE v0.2

Angel Formation Environment (AFE) is an external-adjacent companion module for
Abraxas. It emits trace-only SHADOW packets for observation. It does not filter,
rewrite, suppress, align, govern, constrain, or authorize Abraxas output.

## Runtime

```bash
python scripts/run_afe_cycle.py --seed 42 --agents examples/agents.json --env examples/env.json
```

## Authority

- Authority: `SHADOW_ONLY_TRACE`
- Bridge: `AFE -> Agent Trace Intake Layer -> SHADOW diagnostics`
- Denied: canon mutation, forecast weight mutation, response filtering, Oracle
  constraint behavior, and Abraxas output generation.

