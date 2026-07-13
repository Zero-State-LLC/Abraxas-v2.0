# Campaign Branch Equivalence Receipt - 2026-07-13

## Summary

- Receipt branch: `codex/campaign-branch-equivalence-receipt` at `0fdffed7`.
- Baseline: `origin/main` at `0fdffed7`.
- Scope: local-only inspection of the three retained campaign branches from `BRANCH_LINEAGE_CLEANUP_RECEIPT_2026-07-13.md`.
- GitHub evidence: PR #942 is merged; head SHA `5b131b30`; merge commit `0bf30b54`; changed files `430`.
- Deletion policy: `git branch -d` only; no force deletion and no remote deletion.
- Result: no branches deleted in this lane.

## Branch Decisions

| Branch | Head | Evidence | Decision |
|---|---:|---|---|
| `codex/campaign-director-repair` | `93059fd3` | cherry `15	7`; origin diff `17 files changed, 89 insertions(+), 1116 deletions(-)`; vs merge `1 file changed, 15 insertions(+), 65 deletions(-)`; vs PR head `1 file changed, 15 insertions(+), 65 deletions(-)` | `retain`; not tree-equivalent to merged PR #942 because `scripts/abx_loop.py` differs. |
| `codex/campaign-director-repair-before-squash` | `93059fd3` | cherry `15	7`; origin diff `17 files changed, 89 insertions(+), 1116 deletions(-)`; vs merge `1 file changed, 15 insertions(+), 65 deletions(-)`; vs PR head `1 file changed, 15 insertions(+), 65 deletions(-)` | `retain`; not tree-equivalent to merged PR #942 because `scripts/abx_loop.py` differs. |
| `codex/campaign-director-repair-squashed` | `5b131b30` | cherry `14	0`; origin diff `16 files changed, 74 insertions(+), 1051 deletions(-)`; vs merge `(empty)`; vs PR head `(empty)` | `force-delete candidate`; tree-identical to PR #942 merge/head, but `git branch -d` refused due missing ancestry. |

## Delta Notes

- `codex/campaign-director-repair` and `codex/campaign-director-repair-before-squash` both point at `93059fd3`.
- Compared with PR #942 head `5b131b30`, the two `93059fd3` branches differ only in `scripts/abx_loop.py`: `1 file changed, 15 insertions(+), 65 deletions(-)`.
- `codex/campaign-director-repair-squashed` points at PR #942 head `5b131b30`; `git diff --quiet 0bf30b54 5b131b30` succeeds, so its tree is equivalent to the merged PR #942 tree.
- Safe deletion still refused `codex/campaign-director-repair-squashed`; no `git branch -D` was run.

## Verification

`git status --short --branch`:

```text
## codex/campaign-branch-equivalence-receipt
```

`git log --oneline --left-right main...origin/main`:

```text
(empty)
```

`git worktree list`:

```text
/Users/appliedalchemylabs/Documents/Abraxas-v2.0                    0fdffed7 [main]
/private/tmp/abraxas-green-main                                     0fdffed7 [codex/campaign-branch-equivalence-receipt]
/Users/appliedalchemylabs/Documents/Abraxas-v2.0-global-ingest-plan f7772ddc [codex/global-ingest-adapter-spine-alignment-plan]
/Users/appliedalchemylabs/Documents/Abraxas-v2.0-notion-spec-queue  533da804 [codex/notion-spec-completion-queue]
```

Protected/campaign branch presence:

```text
codex/campaign-director-repair
  codex/campaign-director-repair-before-squash
  codex/campaign-director-repair-squashed
  codex/preserve-local-main-a68ff94d
+ main
```

## Follow-Up

- A future explicit force-delete plan may delete only `codex/campaign-director-repair-squashed`, based on tree equivalence to PR #942.
- The two `93059fd3` branches should remain until `scripts/abx_loop.py` is patch-reviewed against current `main`.
- Remote branch cleanup remains out of scope.
