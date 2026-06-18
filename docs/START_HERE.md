# Start Here — Abraxas v2.0

**Audience:** New contributor · **Goal:** Understand the repo in ~30 minutes · **Posture:** Advisory-only; fail-closed

## What is Abraxas?

Abraxas v2.0 is a **governed symbolic intelligence** repository: deterministic builders, observable artifacts, and explicit authority boundaries. Most surfaces are **advisory-only** — they project state without granting execution, canon mutation, or production activation.

Current product edge: **post-2.5.0** with research-canary advisory shadow **6/6 complete** and P130 production hold intact.

## What is active?

Read these in order:

1. [`docs/releases/POST_2_5_0_CONTINUATION_AUDIT.md`](releases/POST_2_5_0_CONTINUATION_AUDIT.md) — validation baseline
2. [`PLANS.md`](../PLANS.md) — implemented lanes (YAML block at top)
3. [`AGENTS.md`](../AGENTS.md) — mandatory agent rules

**Active implementation lanes (examples):** belief graph engine, operator narrative, runtime integration gate shadow wiring, research canary 6/6 advisory shadow, codegen attestation intake (VALIDATED), Notion stale-spec packet (manual sync pending).

**Active codegen chain (post-#741):**

- Intake gate: `INTAKE_VALIDATED` (`INTAKE_CLEARED_ONLY`)
- ODR review: `INTAKE_CLEARED_OBSERVED`
- Harness implementation: **denied** until separate authorization payload

## What is historical?

- **P70–P130** temporal continuity procedural chain — archived in AGENTS.md; not required for routine development under Governance V3
- **Chamfer / geometric v0.1** planning arc — archived audits under `docs/audits/REPO_*_v0_1`
- **Old POST_MERGE_720–724** plans — superseded by POST_2_5_0 and POST_MERGE_739

See [`docs/audits/AUDIT_INDEX.md`](audits/AUDIT_INDEX.md) and [`docs/releases/RELEASE_INDEX.md`](releases/RELEASE_INDEX.md).

## Where do I begin?

```text
START_HERE (this file)
  → POST_2_5_0_CONTINUATION_AUDIT
  → PLANS.md + AGENTS.md
  → docs/INDEX.md (navigation hub)
  → Subsystem-specific: docs/operators/contributor.md
```

Before any subsystem coding:

```bash
python scripts/run_canon_resume_state.py
python scripts/run_continuation_frontier_reconciliation.py
```

## How do I run tests?

```bash
python scripts/run_fast_ci.py
```

Targeted pytest first; full/canonical tests only when explicitly needed. See [`docs/testing/TEST_INDEX.md`](testing/TEST_INDEX.md).

## How do I create a PR?

1. Branch: `cursor/<descriptive-name>-1234`
2. Minimal diff; match existing conventions
3. Run `python scripts/run_fast_ci.py`
4. Open **draft** PR; document advisory-only posture
5. See [`CONTRIBUTING.md`](../CONTRIBUTING.md)

## How do I sync Notion?

**Manual copy-paste only** — no API writeback authorized.

1. Source: `out/sync/notion_p131_p133_stale_spec_reconciliation_packet_001.latest.json`
2. Checklist: [`docs/notion/GOVERNANCE_V3_NOTION_SYNC.md`](notion/GOVERNANCE_V3_NOTION_SYNC.md)
3. Copy `stale_lane_records` into Notion Canon Spine

## Do NOT (without governed operator lane)

- Regenerate `out/research_canary_*` artifacts
- Claim P130 production activation or runtime spine readiness
- Auto-create operator decision records or grant harness implementation
- Mutate canon, queue, scheduler, or Notion/GitHub writeback
- Delete historical evidence under `out/` or `docs/audits/`

## Quick links

| Need | Go to |
|------|-------|
| Full navigation | [`docs/INDEX.md`](INDEX.md) |
| Audits | [`docs/audits/AUDIT_INDEX.md`](audits/AUDIT_INDEX.md) |
| Artifacts | [`docs/artifacts/ARTIFACT_INDEX.md`](artifacts/ARTIFACT_INDEX.md) |
| Operator payloads | [`operator_input/README.md`](../operator_input/README.md) |
| CLI operators | [`docs/workflows/cli-operator-layer.md`](workflows/cli-operator-layer.md) |
