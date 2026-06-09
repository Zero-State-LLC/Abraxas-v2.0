# Compatibility Policy

Abraxas follows [Semantic Versioning 2.0.0](https://semver.org/).

## Public Compatibility Surface

The following surfaces constitute the governed public interface. Changes that break replayability, governance invariants, or these surfaces require a **MAJOR** version bump.

- Rune catalog and semantics (`contracts/runes/catalog.v1.json` and related contracts)
- YGGDRASIL route graphs and rune/route binding rules (`contracts/yggdrasil/`)
- Pipeline contracts and governance promotion gates (`contracts/pipelines/`)
- CLI Operator Layer commands, evidence packet formats, and drift-watch rules (`docs/workflows/cli-operator-layer.md`)
- Core evidence schemas (continuity-spine, badges.json, governance receipts, temporal continuity artifacts)
- Optimization module public interfaces (once stabilized in `core/optimization/`)

## Versioning Rules

| Change Type | Version Impact | Notes |
|-------------|----------------|-------|
| Breaking change to runes, routes, pipelines, or governance invariants | **MAJOR** | Incompatible with prior replay or governance expectations |
| Additive new surfaces or capabilities (new operators, new evidence types, new optimization backends) | **MINOR** | Backward-compatible addition |
| Bug fixes, internal improvements, documentation, and non-surface changes | **PATCH** | No compatibility impact |
| Deprecations | Announced in **MINOR**, removed in subsequent **MAJOR** | Must include migration guidance |

Pre-release versions use suffixes (`-alpha`, `-beta`, `-rc`).

See `CHANGELOG.md` for release history and `README.md` for current version badge and policy summary.

**Governance note**: All compatibility decisions remain under the established `FROZEN` / `ADVISORY_ONLY` posture. Version bumps are documentation and signaling only; they do not grant execution authority.