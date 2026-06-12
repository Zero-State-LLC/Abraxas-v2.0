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

```bash
python scripts/run_batch004_mapping.py --out out/afe_batch004_mapping.latest.json
```

Batch 004 is a spec-seeded real-world mapping surface. It classifies and
annotates scenario seeds, then emits `ABXMetricFrame.v1` as annotation-only
SHADOW evidence. It does not fetch live trends or filter outputs.

```bash
python scripts/run_oracle_annotation.py --out out/afe_oracle_annotation.latest.json
```

Oracle annotation integration emits an AFE / SHADOW observation panel beside an
Oracle output. The original output is copied intact and the annotation cannot
remove, suppress, rewrite, sanitize, soften, demote, or route Oracle text.

```bash
python scripts/run_aal_viz_overlay.py --out out/afe_aal_viz_overlay.latest.json
```

AAL-Viz overlay integration emits a projection-only overlay packet with the raw
layer always visible, overlays capped at 60% opacity, and required compliance
labels. It does not hide nodes, remove edges, collapse clusters invisibly, or
auto-filter high-risk data.

## Authority

- Authority: `SHADOW_ONLY_TRACE`
- Bridge: `AFE -> Agent Trace Intake Layer -> SHADOW diagnostics`
- Denied: canon mutation, forecast weight mutation, response filtering, Oracle
  constraint behavior, live Notion writeback, auto-loop daemon behavior, and
  Abraxas output generation.
