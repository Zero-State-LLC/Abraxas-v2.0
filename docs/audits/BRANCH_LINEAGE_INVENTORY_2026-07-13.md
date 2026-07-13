# Branch Lineage Inventory - 2026-07-13

## Summary

- Source baseline: `origin/main` at `4f031e36` (`chore(release): update CHANGELOG.md for 1.133.2 [skip ci]`).
- Inventory scope: local branches visible in `/Users/appliedalchemylabs/Documents/Abraxas-v2.0`, with PR lineage sampled from the latest 120 GitHub PRs.
- This report is advisory only: no branches were deleted, modified, or rebased.
- Protected branches: `main`, `codex/preserve-local-main-a68ff94d`, and every branch currently attached to a worktree.

## Classification Totals

- `delete candidate`: 95
- `unknown`: 33
- `keep`: 9
- `active worktree`: 3
- `preserve/archive`: 1

## Classification Policy

- `delete candidate`: branch is ancestry-merged into `origin/main` or has merged PR lineage; delete only after a separate explicit cleanup command.
- `unknown`: branch lacks enough lineage evidence, or its PR was closed unmerged; retain until patch-equivalence or owner intent is inspected.
- `keep`: branch is `main` or has a live non-main upstream; retain pending owner or PR review.
- `active worktree`: branch is checked out in a worktree; do not delete without first removing or moving that worktree.
- `preserve/archive`: explicit archive branch; do not delete.

## Branch Inventory

| Branch | Commit | Upstream | Worktree | PR lineage | Classification | Recommended action |
|---|---:|---|---|---|---|---|
| `codex-aal-viz-scoring-binding-frame` | `a7128214` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex-runtime-integration-gate-receipt` | `c3c93f07` | `origin/codex-runtime-integration-gate-receipt` | `-` | - | `keep` | Remote-backed branch still exists; keep pending owner or PR review. |
| `codex-v2-duplicate-frontier-repair` | `2e31f4aa` | `origin/codex-v2-duplicate-frontier-repair` | `-` | - | `keep` | Remote-backed branch still exists; keep pending owner or PR review. |
| `codex/abx-artifact-lineage-direct-repair-batch` | `ce5117fc` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-completion-hold-plan` | `9583afca` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-final-approval-validation-dry-run` | `3c9563bc` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-final-approval-validation-plan` | `69b3c7c8` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-implementation-dry-run` | `56be47d7` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-implementation-plan` | `214b1711` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-approval-dry-run` | `cdb61fc5` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-approval-dry-run-post531` | `18afa58f` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-approval-dry-run-post542` | `a0c4dfd2` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-approval-plan` | `01ad307d` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-approval-plan-post530` | `07130805` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-approval-plan-post530-stacked` | `ca359a49` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-approval-plan-post541` | `a9f6c41a` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-approval-validation-dry-run` | `a2a0e4f7` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-approval-validation-plan` | `a854f9e3` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-completion-hold-plan` | `da62fc2a` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-completion-hold-post535` | `eda05a14` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-dry-run` | `d9f68bfd` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-dry-run-post528` | `fa2500c6` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-dry-run-post538` | `bc65cd5a` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-final-approval-dry-run` | `6289c312` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-final-approval-plan` | `4c39203a` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-final-approval-plan-post533` | `5c859058` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-final-approval-validation-dry-run-forward-port` | `fa8ebba2` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-final-approval-validation-dry-run-main` | `073257f6` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-final-approval-validation-plan` | `d897c8cf` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-final-approval-validation-plan-main` | `b2c0ded6` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-final-approval-validation-post534` | `d5db08dc` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-operator-decision-request` | `ffe46726` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-operator-decision-request-forward-port` | `56256ebe` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-plan` | `a56582e2` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-plan-post527` | `968cc67d` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-plan-post537` | `9adb6855` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-request-post536` | `1eb07d05` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-validation-dry-run` | `226a4f0f` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-validation-dry-run-post529` | `cfec4617` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-validation-dry-run-post540` | `e9703b20` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-validation-plan` | `cbb8737c` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-validation-plan-post529` | `698fed6d` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-record-validation-plan-post539` | `7e08737a` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/abx-artifact-lineage-direct-repair-operator-decision-request` | `0799b7ea` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-direct-repair-validation-dry-run` | `ec26df1c` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/abx-artifact-lineage-direct-repair-validation-plan` | `c8ff1fbb` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-repair-execution-plan` | `67f97f06` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-repair-plan` | `4b4d40e4` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/abx-artifact-lineage-traceability-audit` | `f5b6c6f8` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/audit-main-current` | `ad24a44b` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/auto-ingest-002` | `cfe06e76` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/auto-ingest-003` | `f852cd5d` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/auto-ingest-004` | `56b21c68` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/auto-ingest-005` | `d205df10` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/auto-ingest-006` | `a0179e27` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/branch-lineage-inventory` | `4f031e36` | `-` | `/private/tmp/abraxas-green-main` | - | `active worktree` | Keep; checked out at /private/tmp/abraxas-green-main |
| `codex/campaign-director-repair` | `93059fd3` | `-` | `-` | #942 merged | `delete candidate` | Merged PR lineage observed; eligible only after operator approval. |
| `codex/campaign-director-repair-before-squash` | `93059fd3` | `-` | `-` | #942 merged | `delete candidate` | Merged PR lineage observed; eligible only after operator approval. |
| `codex/campaign-director-repair-squashed` | `5b131b30` | `-` | `-` | #942 merged | `delete candidate` | Merged PR lineage observed; eligible only after operator approval. |
| `codex/controlled-ingest-governance-audit` | `6cf6c83c` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/dashboard-doctrine-sync` | `d99540ae` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/docs-ingest-state-sync` | `66dfb489` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/doctrine-review-sync` | `8ae2661d` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/fast-ci-baseline-repair` | `ec3ac042` | `-` | `-` | #934 merged | `delete candidate` | Merged PR lineage observed; eligible only after operator approval. |
| `codex/fix-canon-validation-main` | `2c9e1c9b` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/fix-main-canon-validation-2` | `848c1ad0` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/global-ingest-adapter-spine-alignment-plan` | `f7772ddc` | `origin/main` | `/Users/appliedalchemylabs/Documents/Abraxas-v2.0-global-ingest-plan` | - | `active worktree` | Keep; checked out at /Users/appliedalchemylabs/Documents/Abraxas-v2.0-global-ingest-plan |
| `codex/global-ingest-operator-decision-request` | `4a08999a` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/global-operator-review-queue` | `25616486` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/global-pipeline-aal-viz-dashboard` | `0cadb355` | `origin/codex/global-pipeline-aal-viz-dashboard` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/global-pipeline-doctrine-validation` | `b76bbaf9` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/global-pipeline-drift-scan` | `c774a1a9` | `origin/codex/global-pipeline-drift-scan` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/global-pipeline-gap-backlog` | `b78c693e` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/global-pipeline-operator-review-queue-contract` | `f48267b4` | `origin/codex/global-pipeline-operator-review-queue-contract` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/global-pipeline-registry` | `0652edc4` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/global-pipeline-repo-exec-prep` | `63403d18` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/global-pipeline-repo-execution-prep` | `5d661ae6` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/global-pipeline-repo-prep-packet` | `3e3dda5f` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/heavy-tail-baseline-promotion-review` | `0bb163ad` | `origin/codex/heavy-tail-baseline-promotion-review` | `-` | - | `keep` | Remote-backed branch still exists; keep pending owner or PR review. |
| `codex/heavy-tail-computation-receipt` | `e5f8fe33` | `origin/codex/heavy-tail-computation-receipt` | `-` | - | `keep` | Remote-backed branch still exists; keep pending owner or PR review. |
| `codex/merge-runtime-observability` | `0bd9b006` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/next-governed-lane` | `4aa62f73` | `origin/codex/next-governed-lane` | `-` | - | `keep` | Remote-backed branch still exists; keep pending owner or PR review. |
| `codex/next-governed-lane2` | `6795a4f6` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/next-governed-lane3` | `ce0e45a8` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/next-governed-lane4` | `3268f00b` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/next-governed-lane5` | `c7daaf5f` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/next-governed-lane6` | `9705a794` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/next-governed-lane7` | `62f34486` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/notion-operator-decision-backlog` | `8b19b19c` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/notion-queue-refresh` | `887816a5` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/notion-spec-completion-queue` | `533da804` | `origin/main` | `/Users/appliedalchemylabs/Documents/Abraxas-v2.0-notion-spec-queue` | - | `active worktree` | Keep; checked out at /Users/appliedalchemylabs/Documents/Abraxas-v2.0-notion-spec-queue |
| `codex/notion-writeback-dry-run` | `a088c585` | `origin/main` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/operator-review-coherence-refresh` | `24c0d786` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/operator-review-queue-decision-request` | `4259d1a1` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/oracle-calibration-contract-plan-coherence` | `3bb9cb76` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/oracle-confidence-calibration-contract-dry-run` | `93f7c6bf` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/oracle-confidence-calibration-contract-plan` | `faf3948d` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/oracle-confidence-calibration-contract-validation-plan` | `e7c76cfe` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/oracle-signal-decision-evidence-approval-plan` | `beac055f` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/oracle-signal-decision-evidence-dry-run` | `1e14b7d7` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/oracle-signal-decision-evidence-plan` | `e360b609` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/oracle-signal-decision-evidence-validation-dry-run` | `bc0df219` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/oracle-signal-decision-evidence-validation-plan` | `fc2a27c9` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/oracle-signal-intake-boundary-audit` | `a04f8b3f` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/oracle-signal-intake-boundary-implementation-plan` | `73b6eaf9` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/oracle-signal-review-coherence-refresh` | `0221cff0` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/p71-temporal-continuity-spine-binder-contract` | `d4a97288` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/p81-frontier` | `c92f50a6` | `origin/main` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/p81-temporal-continuity-source-status-audit` | `c2e607aa` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/p87-frontier` | `887816a5` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/p95-operator-authorization-seal-review` | `debc813f` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/pr-179-refresh` | `84721aa8` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/pr-179-sync` | `9049df85` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/pr-19-refresh` | `87442462` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/pr-269-sync` | `d21f7bec` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/pr-3-forward` | `f4969e58` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/pr-3-refresh` | `282af460` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/pr-33-refresh` | `b1cfe6b7` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/pr-33-refresh2` | `92688851` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/pr-4-forward` | `9ea6dcac` | `-` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/preserve-local-main-a68ff94d` | `a68ff94d` | `-` | `-` | - | `preserve/archive` | Safety archive for old divergent local main; do not delete. |
| `codex/priority2-live-console-migration-preflight-projection` | `e36b45ee` | `-` | `-` | #936 merged | `delete candidate` | Merged PR lineage observed; eligible only after operator approval. |
| `codex/priority2-migration-preflight-scaffold` | `e76ea717` | `-` | `-` | #935 merged | `delete candidate` | Merged PR lineage observed; eligible only after operator approval. |
| `codex/readme-state-sync` | `cc5af4a1` | `origin/codex/readme-state-sync` | `-` | - | `keep` | Remote-backed branch still exists; keep pending owner or PR review. |
| `codex/repo-exec-prep-refresh` | `f958eddd` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `codex/repo-notion-advisory-refresh` | `d62b024a` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `codex/scripts-import-shim` | `34b806ac` | `origin/codex/scripts-import-shim` | `-` | - | `keep` | Remote-backed branch still exists; keep pending owner or PR review. |
| `docs/cli-operator-layer` | `e94e218c` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `docs/cli-operator-layer-refresh` | `d2217613` | `origin/main` | `-` | - | `delete candidate` | Merged into origin/main by ancestry; eligible only after operator approval. |
| `feat/aer-v1-autonomous-gap-closure-campaign` | `4cfc3b9a` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `main` | `4f031e36` | `origin/main` | `/Users/appliedalchemylabs/Documents/Abraxas-v2.0` | - | `keep` | Current production baseline; do not delete. |
| `pr-179` | `9049df85` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `pr-19` | `87442462` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `pr-255` | `c4c478e5` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `pr-269` | `d21f7bec` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `pr-3` | `282af460` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `pr-30` | `9df8190e` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `pr-33` | `b1cfe6b7` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `pr-4` | `570ce1d8` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `pr-6` | `907e007d` | `-` | `-` | - | `unknown` | No sufficient lineage evidence; retain until inspected. |
| `replit/cockpit-closure-2026-05-28` | `d21f7bec` | `origin/replit/cockpit-closure-2026-05-28` | `-` | - | `keep` | Remote-backed branch still exists; keep pending owner or PR review. |

## Verification Checklist

- Before deletion, re-run `git fetch --prune origin` and refresh `gh pr list --state all`.
- Confirm `git status --short --branch` is clean on `main`.
- Confirm `git log --oneline --left-right main...origin/main` is empty.
- Confirm `gh pr list --state open` is empty or intentionally scoped.
- Confirm `/private/tmp/abraxas-green-main` remains clean and detached at `origin/main`.
- Confirm `codex/preserve-local-main-a68ff94d` is still present after any cleanup pass.
