# Branch Lineage Cleanup Receipt - 2026-07-13

## Summary

- Cleanup branch: `codex/branch-lineage-cleanup-receipt` at `7aa96ebd`.
- Baseline: `origin/main` at `7aa96ebd`.
- Source inventory: `docs/audits/BRANCH_LINEAGE_INVENTORY_2026-07-13.md`.
- Scope: local branch cleanup only; no remote refs were deleted.
- Deletion method: `git branch -d` only; force deletion was not used.
- GitHub open PR queue: empty via GitHub connector immediately before receipt generation.

## Cleanup Totals

- Inventory rows reviewed: 141
- Inventory delete candidates: 92
- Local branches deleted: 89
- Delete candidates retained after safe-delete refusal: 3
- Non-delete-candidate local branches retained: 49
- Protected branches confirmed present: 5

## Deleted Local Branches

- `codex-aal-viz-scoring-binding-frame` at `a7128214`
- `codex/abx-artifact-lineage-direct-repair-batch` at `ce5117fc`
- `codex/abx-artifact-lineage-direct-repair-completion-hold-plan` at `9583afca`
- `codex/abx-artifact-lineage-direct-repair-final-approval-validation-dry-run` at `3c9563bc`
- `codex/abx-artifact-lineage-direct-repair-final-approval-validation-plan` at `69b3c7c8`
- `codex/abx-artifact-lineage-direct-repair-implementation-dry-run` at `56be47d7`
- `codex/abx-artifact-lineage-direct-repair-implementation-plan` at `214b1711`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-approval-dry-run` at `cdb61fc5`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-approval-dry-run-post531` at `18afa58f`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-approval-plan` at `01ad307d`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-approval-plan-post530` at `07130805`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-approval-plan-post530-stacked` at `ca359a49`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-approval-validation-dry-run` at `a2a0e4f7`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-approval-validation-plan` at `a854f9e3`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-completion-hold-plan` at `da62fc2a`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-dry-run` at `d9f68bfd`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-dry-run-post528` at `fa2500c6`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-final-approval-dry-run` at `6289c312`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-final-approval-plan` at `4c39203a`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-final-approval-plan-post533` at `5c859058`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-final-approval-validation-dry-run-forward-port` at `fa8ebba2`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-final-approval-validation-plan-main` at `b2c0ded6`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-operator-decision-request-forward-port` at `56256ebe`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-plan` at `a56582e2`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-plan-post527` at `968cc67d`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-validation-dry-run` at `226a4f0f`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-validation-dry-run-post529` at `cfec4617`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-validation-plan` at `cbb8737c`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-record-validation-plan-post529` at `698fed6d`
- `codex/abx-artifact-lineage-direct-repair-operator-decision-request` at `0799b7ea`
- `codex/abx-artifact-lineage-direct-repair-validation-plan` at `c8ff1fbb`
- `codex/abx-artifact-lineage-repair-execution-plan` at `67f97f06`
- `codex/abx-artifact-lineage-repair-plan` at `4b4d40e4`
- `codex/abx-artifact-lineage-traceability-audit` at `f5b6c6f8`
- `codex/audit-main-current` at `ad24a44b`
- `codex/auto-ingest-002` at `cfe06e76`
- `codex/auto-ingest-003` at `f852cd5d`
- `codex/auto-ingest-004` at `56b21c68`
- `codex/auto-ingest-005` at `d205df10`
- `codex/auto-ingest-006` at `a0179e27`
- `codex/controlled-ingest-governance-audit` at `6cf6c83c`
- `codex/dashboard-doctrine-sync` at `d99540ae`
- `codex/docs-ingest-state-sync` at `66dfb489`
- `codex/doctrine-review-sync` at `8ae2661d`
- `codex/fast-ci-baseline-repair` at `ec3ac042`
- `codex/fix-canon-validation-main` at `2c9e1c9b`
- `codex/fix-main-canon-validation-2` at `848c1ad0`
- `codex/global-ingest-operator-decision-request` at `4a08999a`
- `codex/global-operator-review-queue` at `25616486`
- `codex/global-pipeline-doctrine-validation` at `b76bbaf9`
- `codex/global-pipeline-gap-backlog` at `b78c693e`
- `codex/global-pipeline-registry` at `0652edc4`
- `codex/global-pipeline-repo-exec-prep` at `63403d18`
- `codex/global-pipeline-repo-execution-prep` at `5d661ae6`
- `codex/global-pipeline-repo-prep-packet` at `3e3dda5f`
- `codex/merge-runtime-observability` at `0bd9b006`
- `codex/next-governed-lane2` at `6795a4f6`
- `codex/next-governed-lane3` at `ce0e45a8`
- `codex/next-governed-lane4` at `3268f00b`
- `codex/next-governed-lane5` at `c7daaf5f`
- `codex/next-governed-lane6` at `9705a794`
- `codex/next-governed-lane7` at `62f34486`
- `codex/notion-queue-refresh` at `887816a5`
- `codex/operator-review-coherence-refresh` at `24c0d786`
- `codex/operator-review-queue-decision-request` at `4259d1a1`
- `codex/oracle-calibration-contract-plan-coherence` at `3bb9cb76`
- `codex/oracle-confidence-calibration-contract-dry-run` at `93f7c6bf`
- `codex/oracle-confidence-calibration-contract-plan` at `faf3948d`
- `codex/oracle-confidence-calibration-contract-validation-plan` at `e7c76cfe`
- `codex/oracle-signal-decision-evidence-approval-plan` at `beac055f`
- `codex/oracle-signal-decision-evidence-dry-run` at `1e14b7d7`
- `codex/oracle-signal-decision-evidence-plan` at `e360b609`
- `codex/oracle-signal-decision-evidence-validation-dry-run` at `bc0df219`
- `codex/oracle-signal-decision-evidence-validation-plan` at `fc2a27c9`
- `codex/oracle-signal-intake-boundary-audit` at `a04f8b3f`
- `codex/oracle-signal-intake-boundary-implementation-plan` at `73b6eaf9`
- `codex/oracle-signal-review-coherence-refresh` at `0221cff0`
- `codex/p71-temporal-continuity-spine-binder-contract` at `d4a97288`
- `codex/p81-temporal-continuity-source-status-audit` at `c2e607aa`
- `codex/p87-frontier` at `887816a5`
- `codex/p95-operator-authorization-seal-review` at `debc813f`
- `codex/pr-179-refresh` at `84721aa8`
- `codex/pr-3-forward` at `f4969e58`
- `codex/pr-33-refresh2` at `92688851`
- `codex/pr-4-forward` at `9ea6dcac`
- `codex/priority2-live-console-migration-preflight-projection` at `e36b45ee`
- `codex/priority2-migration-preflight-scaffold` at `e76ea717`
- `codex/repo-exec-prep-refresh` at `f958eddd`
- `docs/cli-operator-layer-refresh` at `d2217613`

## Retained Delete Candidates

- `codex/campaign-director-repair` at `93059fd3`: git branch -d refused; branch remains local and was not force-deleted; inventory PR lineage `#942 merged`.
- `codex/campaign-director-repair-before-squash` at `93059fd3`: git branch -d refused; branch remains local and was not force-deleted; inventory PR lineage `#942 merged`.
- `codex/campaign-director-repair-squashed` at `5b131b30`: git branch -d refused; branch remains local and was not force-deleted; inventory PR lineage `#942 merged`.

## Protected And Retained Branches

Protected branches confirmed present:
- `codex/branch-lineage-cleanup-receipt`
- `codex/global-ingest-adapter-spine-alignment-plan`
- `codex/notion-spec-completion-queue`
- `codex/preserve-local-main-a68ff94d`
- `main`

Retained non-delete-candidate branches by classification:
- `active worktree`: 3
- `keep`: 12
- `preserve/archive`: 1
- `unknown`: 33

## Verification

`git status --short --branch`:

```text
## codex/branch-lineage-cleanup-receipt
```

`git log --oneline --left-right main...origin/main`:

```text
(empty)
```

`git worktree list`:

```text
/Users/appliedalchemylabs/Documents/Abraxas-v2.0                    7aa96ebd [main]
/private/tmp/abraxas-green-main                                     7aa96ebd [codex/branch-lineage-cleanup-receipt]
/Users/appliedalchemylabs/Documents/Abraxas-v2.0-global-ingest-plan f7772ddc [codex/global-ingest-adapter-spine-alignment-plan]
/Users/appliedalchemylabs/Documents/Abraxas-v2.0-notion-spec-queue  533da804 [codex/notion-spec-completion-queue]
```

## Follow-Up

- The three retained campaign branches require separate patch-equivalence review before any forced or manual deletion decision.
- Remote branch cleanup is out of scope and requires a separate explicit plan.
