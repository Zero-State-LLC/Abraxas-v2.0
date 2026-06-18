# Product 2.5.0 — Release Readiness

Product version **2.5.0** merged via PR #710 (2026-06-18). Post-merge stabilization merged via PR #711; continuation work tracked on PR #712.

## Validation summary

| Check | Command | Result (2026-06-18) |
|-------|---------|------------------------|
| Fast CI | `python scripts/run_fast_ci.py` | **PASS** (post-#711 on `main`) |
| Full pytest | `pytest -q --maxfail=20` | **PASS** (after P102 doc handoff sync in #712) |
| AAL-Viz | `cd apps/aal-viz-live-console && npm ci && npm test && npm run build` | **PASS** (296+ tests, Node 20) |
| Canon-validation | GitHub Actions `workflow_dispatch` full mode | Optional; archive blockers remain historical |

## Merge record

| PR | Scope | Date |
|----|-------|------|
| #710 | Full Features Release Roadmap (product 2.5.0) | 2026-06-18 |
| #711 | Post-merge stabilization: artifacts, ingest handoff, YGGDRASIL bindings, AAL-Viz panels + CI | 2026-06-18 |
| #712 | Live-console bundle wiring, CI apps paths, P102 doc alignment, Belief Graph fixtures | draft |

## Completed continuation items (#711)

- v2 hygiene audit artifacts regenerated (14/14 Phase 1 tasks observed; loop-awareness audit READY)
- GeometricRenderer + P40 fusion overlay panels wired in live console
- Controlled handoff eligibility embedded in ingest scheduler manifest (shadow-only)
- Remaining YGGDRASIL catalog runes bound via drift_scan and canon_sync pipelines
- Ingest shadow chain artifacts regenerated for full-stack replay parity

## Completed continuation items (#712)

- Overlay panels consume live projection bundle geometry (deterministic fallback when empty)
- CI path filters include `apps/aal-viz-live-console/**`
- P102 temporal-continuity doc handoff strings synced in README/AGENTS/PLANS
- Belief Graph engine fixture tests for non-empty advisory graphs

## Authority posture

All surfaces remain **advisory-only**. No execution authority, canon mutation, forecast routing, or operator attestation escalation.

## Notion follow-up

Manual operator steps: [`docs/notion/GOVERNANCE_V3_NOTION_SYNC.md`](docs/notion/GOVERNANCE_V3_NOTION_SYNC.md)
