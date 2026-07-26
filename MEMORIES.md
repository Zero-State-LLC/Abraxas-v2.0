# Bug-finding automation memory

Tracked critical-bug reports only (open or rejected). No run history.

## Open

- `core/research_cross_drop_conflict_scan.py`: non-dict `stabilization_proof_records` satisfied proof-id checks via `str(record)` while the scanner dropped them, yielding a false-clean P99 PASS (`scanned_drop_count=2`) that advanced P100/P101 — https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/1010 — status: open — recorded: 2026-07-26
- `core/oracle/runtime.py`: multi-payload intake scanned all sources for conflicts but emitted only `source_payloads[0]`, silently dropping distinct `source_id`s while reporting `stable` — https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/1011 — status: open — recorded: 2026-07-26
- `core/forecast/runtime.py` + `scripts/research/run_forecast_candidates.py`: nested observability telemetry ignored with `"unknown"` fallback (hash collisions) and wrong input path `out/run_observability_pipeline/latest.json` — https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/1012 — status: open — recorded: 2026-07-26
- `core/sandbox/runtime.py` + `core/state/runtime.py`: nested observability / `telemetry_id` ignored with `"unknown"`/empty fallbacks, collapsing distinct telemetry into identical sandbox proposal and state hashes — https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/1013 — status: open — recorded: 2026-07-26
- `core/overlay_governance/runtime.py` + sole-writer: missing upstreams became `[{}]` and sentinel hashes (`canary`/`obs`/`sched`/`promo`), sealing overlay governance as passed with continuity 1.0 — https://github.com/scrimshawlife-ctrl/Abraxas-v2.0/pull/1014 — status: open — recorded: 2026-07-26

## Rejected

(none)
