# Version Strategy

Abraxas uses a dual-track version model under Governance V3.

## Semantic release (1.x)

- Automated via [`release.config.js`](../../release.config.js) on merge to `main`
- Conventional Commits drive patch/minor bumps
- Updates [`CHANGELOG.md`](../../CHANGELOG.md) only

## Product version (2.x)

- Declared in [`pyproject.toml`](../../pyproject.toml), [`VERSION`](../../VERSION), and README badge
- Bumped at product milestones (v2.2 hygiene, v2.3 ingest, v2.4 intelligence, v2.5 full features)
- Documented in [`STATUS.md`](../../STATUS.md)

Current product version target: **2.5.0** (Full Features Release Roadmap)
