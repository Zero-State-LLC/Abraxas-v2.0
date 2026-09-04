# PR automerge (docs only)

Fail-closed. Candidate posture unchanged. EXTERNAL_PRODUCTION remains held.

## What it does

Workflow `.github/workflows/pr-automerge-docs.yml` enables GitHub **squash auto-merge** when:

- PR targets `main`
- not a draft, not a fork
- labels `docs` and `automerge`
- every path is on the allowlist
- repo Settings allow auto-merge

Required checks still must pass.

## Allowlist

`docs/**`, `README.md`, `CHANGELOG.md`, `LICENSE`, `MEMORIES.md`, `PLANS.md`, `STATUS.md`, `QUICKSTART.md`, `ARCHITECTURE.md`.

`GOVERNANCE_V3.md`, `AGENTS.md`, `SKILLS.md`, `core/`, `contracts/`, `scripts/`, `.github/` are blocked.

## Operator setup

Settings → General → Pull Requests → Allow auto-merge. Create labels `docs` and `automerge`.
