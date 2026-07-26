# Operator-loop GitHub/CI evidence gatherer (projection-only)

**Status:** Approved design (brainstorming)  
**Date:** 2026-07-26  
**Companion:** `docs/architecture/ABRAXAS_MULTI_AGENT_OPERATOR_LOOP_001.md`  
**Approach:** Thin explicit gatherer (Approach A)  
**Authority:** Display / evidence snapshot only — no assign, approve, merge, or deploy

## 1. Problem

Operator-loop truth surfaces already exist (`core/operator_loop.build_truth_surfaces`, `collect_local_truth_surfaces`, live-console `OperatorLoopProjectionPanel`). GitHub evidence is limited to a **local git tip**; CI is often `NOT_COMPUTABLE` without hand-written files under `out/operator_loop/evidence/`.

Operators need a **status glance**: open PRs, main tip, and CI red/green — without granting any authority and without putting network calls in the projection builder or browser.

## 2. Goals

1. **Primary job:** Operator status glance (not deep CI babysit, not full audit trail).
2. **Gather path:** Explicit script using `gh` CLI when available; write evidence JSON under `out/`.
3. **Content:** Compact glance pack (capped open PRs + check summaries + main workflow conclusions).
4. **Reuse:** Existing projection builder and console panel remain the consumers; default offline path unchanged.
5. **Authority:** Projection-only everywhere; all `can_assign` / `can_approve` / `can_merge` / `can_deploy` stay false.

## 3. Non-goals (v1)

- Merge, approve, assign, or any write to GitHub
- Browser-side GitHub tokens or console → API fetch
- Per-check name matrices / full Actions log dump
- Work-packet ↔ PR join
- Scheduled GitHub Action as the primary gatherer
- Network calls inside `core/operator_loop.py` or on module import

## 4. Architecture

```text
[gh CLI] ──explicit──► scripts/viz/gather_operator_loop_github_ci_evidence.py
                              │
                              ▼
              out/operator_loop/evidence/
                github.v1.json
                ci.v1.json
                              │
                              ▼
              scripts/viz/build_aal_viz_operator_loop_projection.py
                (default: offline; reads evidence dir)
                              │
                              ▼
              OperatorLoopProjection.v1.truth_surfaces
                              │
                              ▼
              OperatorLoopProjectionPanel (display only)
```

### Unit responsibilities

| Unit | Does | Does not |
| --- | --- | --- |
| Gatherer script | Invoke `gh`, write evidence JSON | Merge, approve, assign, mutate GitHub |
| Evidence files | Durable snapshot for projection | Be “live” in the browser |
| Projection builder | Normalize into `truth_surfaces` | Call network |
| Console panel | Render status glance | Fetch GitHub or write files |

## 5. Evidence file schemas (compact glance pack)

Paths (repo-relative):

- `out/operator_loop/evidence/github.v1.json`
- `out/operator_loop/evidence/ci.v1.json`

Both share the envelope already implied by `build_truth_surfaces`:

- `status`: `PRESENT` | `NOT_COMPUTABLE`
- `source`: string (e.g. `gh_cli`)
- `items`: array of objects
- `notes`: array of strings
- Items carry `authority_implication: "none"` where applicable

### 5.1 `github.v1.json`

Additional top-level fields:

- `gathered_at`: ISO-8601 UTC
- `repo`: `owner/name`
- `cap`: integer (default **15**)

Item kinds:

1. **`git_tip`** — `sha`, `branch` (prefer `main` tip when available; otherwise current HEAD for fallback only, noted in `notes`)
2. **`open_pr`** — `number`, `title`, `is_draft`, `mergeable` (`MERGEABLE` | `CONFLICTING` | `UNKNOWN`), `head_branch`, `base_branch`, `url`

Open PRs: newest first, **max 15**.

### 5.2 `ci.v1.json`

Additional top-level fields:

- `gathered_at`: ISO-8601 UTC

Item kinds:

1. **`main_workflow`** — `workflow` (e.g. `ci`), `conclusion`, `status`, `head_sha`, `url` for recent runs on `main` (at least the primary `ci` workflow; optional cheap inclusion of `Release` if a single list query covers it)
2. **`pr_checks_summary`** — `pr_number`, `pass`, `fail`, `pending`, `primary` (`pass` | `fail` | `pending` | `mixed`)

No full check-name lists in v1.

## 6. Gatherer script

**Path:** `scripts/viz/gather_operator_loop_github_ci_evidence.py`

**Invocation:**

```bash
python3 scripts/viz/gather_operator_loop_github_ci_evidence.py
python3 scripts/viz/build_aal_viz_operator_loop_projection.py
```

**Behavior:**

1. Require `gh` on `PATH`. If missing: write both evidence files with `status: NOT_COMPUTABLE`, `source: none`, and a note that `gh` is required — fail-visible, not silent.
2. Resolve repo via `gh repo view --json nameWithOwner` (preferred) or parse `git remote get-url origin`.
3. Populate GitHub items: main tip + open PRs (`gh pr list --state open --limit 15` with JSON fields needed for the schema).
4. Populate CI items: recent runs on `main` for the primary CI workflow; for each open PR, derive a **summary** of check counts (e.g. `gh pr checks <n>` parsed into pass/fail/pending).
5. Stamp `gathered_at` (UTC). Never set any authority grant field true.
6. Create `out/operator_loop/evidence/` if needed. Write JSON with stable key ordering for readability (`sort_keys=True` acceptable for evidence snapshots).

**Flags (v1 minimum):**

- Default paths as above
- Optional `--max-prs N` (default 15) if cheap; otherwise hardcode 15
- No `--auto-merge` or similar

**Optional later (out of v1):** wrapper flag on the projection builder; scheduled Action gatherer.

## 7. Projection and console

- `collect_local_truth_surfaces` already loads `github.v1.json` / `ci.v1.json` when present. Prefer **no core API change** unless item shapes need mild normalization (unknown fields ignored; required display fields filled with safe defaults).
- Console: existing `OperatorLoopProjectionPanel` must remain fail-closed on authority escalation. **Light polish only** for `open_pr` and `pr_checks_summary` rows (title + primary status badge instead of raw `JSON.stringify` for those kinds). No auto-refresh against GitHub.
- Document the two-step glance in `apps/aal-viz-live-console/README.md` and/or `AGENTS.md` multi-agent / projection section.

## 8. Error handling

| Condition | Result |
| --- | --- |
| `gh` missing | Evidence files `NOT_COMPUTABLE`; projection still builds offline |
| `gh` auth failure / API error | Partial or empty items + notes; status `NOT_COMPUTABLE` if no usable items |
| Empty open PR list | Valid `PRESENT` GitHub surface with tip only (if tip known) |
| Malformed evidence file | Existing collector parse failure path (notes + empty items) |
| Console missing projection file | Existing “run builder” empty state |

## 9. Testing

| Layer | Cases |
| --- | --- |
| Gatherer unit | Fixture “gh JSON” → evidence shape; authority fields false; cap 15 |
| Gatherer unit | Missing `gh` → `NOT_COMPUTABLE` files (mock PATH / injection) |
| Projection | Existing tests still pass; optional fixture evidence file → item counts |
| Console (if polish) | `open_pr` row shows title + primary status; authority reject still works |

**CI must not call live GitHub.** Use fixtures and mocks only.

## 10. Acceptance criteria

- [ ] Explicit gatherer script exists under `scripts/viz/` and writes `github.v1.json` + `ci.v1.json`.
- [ ] With `gh` available, evidence includes main tip, up to 15 open PRs (draft/mergeable), and CI summaries for main + those PRs.
- [ ] Without `gh`, evidence is fail-visible `NOT_COMPUTABLE` and projection still works offline.
- [ ] Projection and panel never enable assign/approve/merge/deploy.
- [ ] No network on import of `core.operator_loop`.
- [ ] Docs describe the two-step operator glance.
- [ ] Tests cover happy path (fixtures) and missing-`gh` path.

## 11. Implementation sketch (for planning, not authorization)

1. Add gatherer script + fixtures under `tests/` or `scripts/viz/fixtures/`.
2. Wire/document evidence schemas (this doc is the contract; optional tiny schema JSON only if needed for validation tests).
3. Minimal console polish for `open_pr` / `pr_checks_summary`.
4. Docs: console README + short AGENTS/projection note.
5. Targeted tests; no production activation or CLEAR work.

## 12. Decisions log

| Decision | Choice |
| --- | --- |
| Primary job | Operator status glance |
| Gather mechanism | Explicit `gh` script → evidence files |
| Content pack | Compact glance (cap 15 open PRs) |
| Architecture | Approach A — thin gatherer, reuse builder/panel |
| Network in core/console | Forbidden |
| Work-packet join | Deferred |
| Scheduled Action | Deferred |
