# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Policy Adoption Note**: Conventional Commits, the structured Keep a Changelog format, and `COMPATIBILITY.md` were adopted on 2026-06-09. Commits and changelog entries before this date follow previous conventions. Enforcement via GitHub Actions begins with PRs after this date.

## [2.0.1] — 2026-06

### Added
- `COMPATIBILITY.md` — defines public compatibility surface and SemVer policy for the governed system
- New GitHub workflow for Conventional Commits validation on PRs (`.github/workflows/conventional-commits.yml`)
- `.commitlintrc.json` configuration
- Version badge in `README.md` header
- `core/optimization/` module with Optuna Bayesian backend (`core/optimization/optuna_backend.py`)

### Changed
- Expanded Developer Workflow section in `README.md` with prominent CLI Operator Layer documentation
- Updated `CONTRIBUTING.md` with full Conventional Commits standards and examples
- Updated repository topology to document optimization module
- Restructured `CHANGELOG.md` to Keep a Changelog + explicit SemVer sections
- Aligned versioning across `VERSION` (fixed), `pyproject.toml`, `CHANGELOG.md`, and documentation

### Fixed
- Corrected broken placeholder content in root `VERSION` file

**Governance note**: All changes remain under `governance_status=FROZEN` and `canon_status=ADVISORY_ONLY`. No runtime, execution, or canon authority changes. These are documentation, signaling, and process improvements only.

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

Use this section for work in progress. Move items to a new versioned release when cutting a tag.

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
