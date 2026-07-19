# Motion principles — Abraxas Visual OS

Motion **communicates information**. It never exists for decoration.

## Rules

1. **State first** — animate only when system state, focus, or relationship changes.
2. **Causal order** — node activation → edge propagation → receipt settle.
3. **Short** — prefer 80–220 ms; 520 ms only for deliberate receipt emission.
4. **Reduced motion** — honor `prefers-reduced-motion` (tokens collapse durations).
5. **No loops** for success/celebration; telemetry may pulse gently with domain color.
6. **Authority stillness** — DENIED / NO_GO surfaces do not pulse green; use static chips.

## Pattern → meaning

| Pattern | Meaning |
|---------|---------|
| Panel fade/slide | Navigation / operator focus shift |
| Graph node stroke brighten | Entity selected or activated |
| Edge dash draw | Signal / dependency propagation |
| Timeline scrub | Temporal continuity navigation |
| Pipeline step fill | Execution progress |
| Receipt rise + settle | Artifact emission (once) |
| Forecast path extend | Projection growth (advisory styling) |

## Durations

See `tokens/motion.tokens.json`.
