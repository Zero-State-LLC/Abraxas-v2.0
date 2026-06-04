# CLI Operator Layer — Token Conservation Workflow

## Status

- OBSERVED: Repo uses AI-assisted development across Codex, GitHub, and Notion.
- INFERRED: Token usage is reduced when terminal evidence is scoped before asking an AI agent to inspect or modify the repo.
- BOUNDARY: ADVISORY_ONLY. No runtime/schema/artifact/governance/lane/execution effect.

## Governance Boundary

| Surface | Value |
| --- | --- |
| `governance_status` | `FROZEN` |
| `canon_status` | `ADVISORY_ONLY` |
| `downstream` | `NOT_COMPUTABLE` |
| `execution_authority` | `NONE` |
| `runtime_effect` | `NONE` |

## Primary Rule

"Send AI the smallest complete evidence packet, not a full repo dump."

## Operator Map

| Operator | Tooling | Use |
| --- | --- | --- |
| `OP.SEARCH_SIGNAL` | `rg` / `ripgrep` | Search for exact repo signals before broader inspection. |
| `OP.FIND_PATH` | `fd` | Find candidate files and directories quickly. |
| `OP.JSON_EXTRACT` | `jq` | Extract deterministic JSON evidence for prompts and reviews. |
| `OP.YAML_EXTRACT` | `yq` | Pull targeted workflow or config fields without pasting whole files. |
| `OP.FUZZY_SELECT` | `fzf` | Interactively narrow candidate files, commands, or results. |
| `OP.DIFF_COMPRESS` | `git diff` / `git-delta` | Compress change context into reviewable diffs. |
| `OP.REPO_PACK` | `repomix` | Package a scoped repo subset after local evidence gathering. |
| `OP.STRUCTURAL_SEARCH` | `ast-grep` | Search syntax structure instead of raw text when code shape matters. |
| `OP.STATIC_SCAN` | `semgrep` | Run lightweight static scanning on touched surfaces. |
| `OP.LOC_METRIC` | `tokei` / `cloc` | Measure code volume without asking AI to count files manually. |
| `OP.PERF_CHECK` | `hyperfine` | Compare command latency for repeatable developer workflows. |
| `OP.PR_CONTROL` | `gh` / `gh-dash` | Inspect PR state, checks, reviews, and mergeability. |
| `OP.GIT_VISUAL` | `lazygit` | Review branch and staging state interactively when needed. |
| `OP.DOC_SHORTCUT` | `tldr` | Look up concise command usage during workflow execution. |
| `OP.SYSTEM_PRESSURE` | `bottom` / `btm` | Inspect CPU, memory, and process pressure while running local checks. |
| `OP.DISK_PRESSURE` | `dust` | Inspect disk usage and growth in working directories. |

## Install Commands

```bash
brew install gh lazygit ripgrep fd jq yq fzf bat tree tokei cloc hyperfine ast-grep git-delta bottom dust tldr semgrep
npm install -g repomix @openai/codex
gh extension install dlvhdr/gh-dash
```

## Recommended Invocation Order

1. `OP.PR_CONTROL`
2. `OP.SEARCH_SIGNAL`
3. `OP.JSON_EXTRACT` / `OP.YAML_EXTRACT`
4. `OP.DIFF_COMPRESS`
5. `OP.REPO_PACK`
6. Codex implementation
7. `OP.STATIC_SCAN` and targeted tests
8. `OP.PR_CONTROL` confirmation
9. Notion advisory status update

## Abraxas-Specific Command Recipes

Search continuity and governance signals:

```bash
rg "recommended_next_lane|governance_status|canon_status|NOT_COMPUTABLE|P102G"
```

Extract continuity status:

```bash
jq '{lane_count, highest_lane, highest_observed_lane, governance_status, canon_status, recommended_next_lane}' docs/status/continuity-spine.json
```

Inspect a pull request:

```bash
gh pr view <PR_NUMBER> --json number,title,mergeable,headRefName,baseRefName,statusCheckRollup
```

Watch CI:

```bash
gh run list --limit 10
gh run watch
```

Inspect workflow jobs:

```bash
yq '.jobs | keys' .github/workflows/*.yml
```

Package repo for AI after scoping:

```bash
repomix --ignore "node_modules,.git,.venv,out/**/archive/**"
```

Count code:

```bash
tokei .
cloc .
```

## Codex Evidence Packet Template

```text
BOUNDARY
- Docs-only, advisory-only, projection-only, non-authoritative.

EVIDENCE PACKET
- Branch, PR, targeted files, extracted artifact fields, scoped diffs, and check status.

TASK
- Concrete repo change or analysis request tied to the evidence packet.

OUTPUT
- Requested deliverable, files changed, and exact validation expectation.

VALIDATION
- Targeted commands, tests, and drift checks actually run.

RESIDUAL RISKS
- Known blockers, stale evidence, dirty worktree, or missing authority.

RECOMMENDED NEXT ADVISORY ACTION
- Smallest safe next move based on observed state.
```

## Drift Watch

SHADOW flags:

- Full repo dumps before targeted search.
- Screenshots instead of `gh` or JSON output when terminal access exists.
- AI asked to count LOC without `tokei` or `cloc`.
- AI asked to inspect full workflow files without `yq` extraction.
- Codex prompted without branch, PR, or check evidence.
- Notion updated as canon when source state is advisory-only.

## Seal

"This document is an advisory developer workflow layer. It is not runtime canon."
