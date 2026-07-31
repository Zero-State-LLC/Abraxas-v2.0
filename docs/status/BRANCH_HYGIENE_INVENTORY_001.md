# Branch Hygiene Inventory 001

**Status:** ADVISORY · inventory + policy only  
**Date:** 2026-07-31  
**Authority:** no remote delete, no force-push, no history rewrite without explicit operator command  

## 0. Why

Remote head count on `origin` is **very large** (~800+). Most branches are agent/CI leftovers (`codex/`, `copilot/`, `cursor/`, old feature lanes). This document defines **classification and safe cleanup procedure** without performing deletes.

## 1. Observed prefix density (snapshot)

Approximate counts from `git ls-remote --heads origin` (2026-07-31):

| Prefix | ~Count | Default class |
|--------|--------|----------------|
| `codex/` | ~254 | `CANDIDATE_STALE` |
| `copilot/` | ~200 | `CANDIDATE_STALE` |
| `cursor/` | ~60 | `CANDIDATE_STALE` |
| `feat/` / `feature/` | ~78 | `REVIEW` (check open PRs) |
| `shadow/` | ~31 | `REVIEW` |
| `docs/` | ~15 | `REVIEW` |
| `main` | 1 | `KEEP` |
| other | remainder | `REVIEW` |

**Total remote heads:** ~817 (varies)

## 2. Classification

| Class | Meaning | Action |
|-------|---------|--------|
| `KEEP` | Default branch, release, protected | Never delete |
| `OPEN_PR` | Head of open PR | Keep until PR merges/closes |
| `MERGED_SAFE` | Fully merged into `main`, no open PR | Delete candidate after dry-run list |
| `CANDIDATE_STALE` | Agent prefix, no open PR, behind main | Delete candidate after human confirm |
| `UNKNOWN` | Ambiguous | Leave alone |

## 3. Safe procedure (operator-gated)

```text
1. python -m abraxas os branch-hygiene   # or scripts/tools inventory
2. Review JSON under out/audit/branch_hygiene_inventory.*.json
3. Operator confirms delete list (explicit command)
4. Only then: git push origin --delete <branch>  (one-by-one or batched with confirm)
```

**Never** in automation without confirm:

- `git push --delete` bulk
- force-push / `--force-with-lease` to rewrite shared history
- deleting `main` or open PR heads

## 4. Inventory generator

Pure builder: `core.engineering.branch_hygiene_inventory`

```bash
# Local classification against origin (read-only fetch assumed current)
python -m abraxas os branch-hygiene
```

Emits advisory inventory: counts by prefix/class, sample candidates. Does **not** delete.

## 5. Seal

Inventory and policy only. No remote mutation from this document or the inventory CLI.
