# Dependency and CI Workflow Hygiene

Status: `DEPENDENCY_CI_HYGIENE_READY`
Issue: `#1121`

## Dependabot triage

`gh pr list --repo scrimshawlife-ctrl/Abraxas-v2.0 --state open --limit 100` showed no open Dependabot PRs on 2026-08-11. The only open PR at review time was Prabu's Track B overlap PR #1133, already commented with a coordination note.

## Release workflow repair

The Release workflow was failing because `@semantic-release/git` attempted to push a generated `CHANGELOG.md` commit back to protected `main`, which branch protection rejected with GH006. The release config now avoids branch-pushing prepare plugins and only publishes GitHub release artifacts/tags through semantic-release.

Hardening applied:

- removed `@semantic-release/changelog` and `@semantic-release/git` from `release.config.js`
- removed unused root dev dependencies from `package.json` / `package-lock.json`
- pinned `actions/checkout` and `actions/setup-node` in `.github/workflows/release.yml`
- set Release Node to `22.22.2`, matching the semantic-release engine floor
- added `cache-dependency-path: package-lock.json`

## Validation

```bash
python -m pytest tests/test_dependency_ci_workflow_hygiene.py -q
npm ci --package-lock-only
python scripts/run_fast_ci.py
```

## Authority

This is workflow hygiene only. It does not bypass branch protection, change required-check policy, merge Dependabot work, or grant release bypass authority.
