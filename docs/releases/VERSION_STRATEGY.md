# Version Strategy

**Decided 2026-10-10 (operator).** This file is the source of truth for version numbers in Abraxas-v2.0. It replaces the earlier "dual-track" model.

## What v2.0 versions

Abraxas-v2.0 is the **doctrine and reference** repository. It publishes **doctrine revisions**. It does not ship a product and must not claim a product version.

The supported Abraxas product lives in [`Zero-State-LLC/Abraxas`](https://github.com/Zero-State-LLC/Abraxas), and that repository owns product versions.

| Identifier | Meaning | Where it lives |
| --- | --- | --- |
| Doctrine revision `1.N.M` | A snapshot of `main`: doctrine, contracts and reference code | git tag `v1.N.M` and the GitHub release (semantic-release); mirrored in `VERSION` and the top entry of `CHANGELOG.md` |
| Reference build `0.0.0+reference` | The Python package label needed for editable installs. It is not a release. | `pyproject.toml` `[project].version`, `core/settings.py` `app_version` |
| "Product 2.5.0" (PR #710) | A **retired** historical milestone label ("Full Features"). It never identified a published artifact. | history only: `docs/releases/PRODUCT_2_5_0_*.md`, PLANS |
| Abraxas product version | A supported runtime release | `Zero-State-LLC/Abraxas` (outside this repository) |

The `v1.N.M` tags are kept unchanged. The 218 tags and GitHub releases carry no assets, so they are repository snapshots. From now on they are called doctrine revisions.

## How a doctrine revision is cut

1. A Conventional Commit lands on `main`.
2. semantic-release (`release.config.js`, `.github/workflows/release.yml`) creates the tag and the GitHub release notes. It does **not** commit `CHANGELOG.md`, because the bot cannot push to the protected `main`. See #1121 and `tests/test_dependency_ci_workflow_hygiene.py`.
3. An ordinary **sync PR** sets `VERSION` to the new tag and prepends that release's notes to `CHANGELOG.md`. The notes are copied verbatim from the GitHub release body (`gh release view vX.Y.Z --json body`); nothing is written by hand.

Entries 1.179.0 and 1.180.0 were backfilled this way on 2026-10-10 from their published release bodies.

## Validation (release-timing aware)

`python -m scripts.governance.validate_version_policy` runs in fast CI. It enforces these rules:

- `VERSION` names a `v*` tag that is an ancestor of `HEAD`. Development commits ahead of the latest tag pass.
- The top `CHANGELOG.md` entry equals `VERSION`.
- `pyproject.toml` keeps the reference label `0.0.0+reference`.
- When a newer tag exists than `VERSION` (the release ran and the sync PR is still open), the check **warns and passes**.
- When the checkout has no tags (shallow clone), the tag rules are `NOT_COMPUTABLE` and the check warns.
- The sync PR and any release lane run with `--strict`. There, a lagging `VERSION` or missing tags **fail**.

Hosted Actions are currently off for this repository (`HOSTED_ACTIONS_AVAILABLE=false`), so no new doctrine revision is cut until CI runs again. Commits since `v1.180.0` would produce `1.181.0`.
