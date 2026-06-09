# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Versioning Note**: The project uses `2.x.y` versioning. Given the substantial maturity of the system (362 contracts, 342 schemas, 58 continuity lanes, 750+ tests, 561 artifacts), version numbers are chosen to reflect both SemVer compliance and the overall scope of the governed architecture.

## [2.1.0] — 2026-06

### Added
- `COMPATIBILITY.md` — defines public compatibility surface and SemVer policy
- New GitHub workflow + configuration for Conventional Commits validation
- Dependabot configuration with grouping (`.github/dependabot.yml`)
- PR and Issue templates (`.github/PULL_REQUEST_TEMPLATE.md`, `.github/ISSUE_TEMPLATE/`)
- Caching improvements in CI workflows
- `core/optimization/` module with Optuna Bayesian backend

### Changed
- Expanded and formalized Developer Workflow + CLI Operator Layer in `README.md`
- Major updates to `CONTRIBUTING.md` (Conventional Commits standards)
- Restructured `CHANGELOG.md` to Keep a Changelog format
- Updated repository topology and documentation alignment
- Version bumped from 2.0.1 to 2.1.0 to better reflect project maturity and scope of recent work

### Fixed
- Corrected broken placeholder in root `VERSION` file

**Governance note**: All changes remain under `governance_status=FROZEN` and `canon_status=ADVISORY_ONLY`. These are documentation, process, and capability improvements with no runtime or canon impact.

## [2.0.0] — 2026-06-01

### Added
- Technical atlas README and canonical Atlas document
- Governance receipts and continuity artifacts structure
- YGGDRASIL routing invariants
- ABX-Runes contracts and determinism test guidance
- Initial Research Surface and Operator Paths

See `docs/atlas/ABRAXAS_ATLAS.md` for architecture and roadmap details.

---

## Unreleased

Use this section for work in progress.

### Breaking Changes
- (none)

### Added
- (none)

### Changed
- (none)

### Deprecated
- (none)

### Fixed
- (none)

### Security
- (none)
