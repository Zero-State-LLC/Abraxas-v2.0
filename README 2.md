# ABRAXAS

Abraxas — A governed symbolic intelligence architecture.

Status surfaces below are generated deterministically from the repository. Observational, not authoritative.

## CI and Operators

This project includes:

- A CI workflow that runs a counts script, uploads `artifacts/badges.json`, can optionally commit it, and can publish it as a Shields.io JSON endpoint via GitHub Pages.
- Minimal operator docs under `docs/operators/` to make Operator Paths actionable.
- A small Swift generator to produce a temporal continuity spine SVG from a continuity index file.

### CI Usage
- Workflow file: `.github/workflows/counts.yml`
- `repo-status.yml` is deprecated; `counts.yml` is the single source of truth for status generation and optional Pages deployment.
- Triggers: push to `main`, PRs, and manual dispatch
- Manual inputs:
  - `commit_badges`: set to `true` to commit `artifacts/badges.json` back to the repo
  - `publish_shields_endpoint`: set to `true` to publish `badges.json` for shields.io via Pages

The workflow expects a counts script that writes `artifacts/badges.json`. It will try, in order:
- `Scripts/counts.js` (Node)
- `Scripts/counts.swift` (Swift)
- `Scripts/counts` (executable)

If none are present, it emits a placeholder badge JSON.

Shields usage example (after Pages deploy):

Use the exact repo path `scrimshawlife-ctrl/Abraxas-v2.0`.
- Whole-surface JSON:

https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges.json
https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/schemas.json
https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/contracts.json
https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/tests.json
https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/continuity.json
https://scrimshawlife-ctrl.github.io/Abraxas-v2.0/badges/governance.json

These endpoints are observational repository surfaces generated from local scans. They are not authority grants, forecast outputs, or canon promotion signals.

