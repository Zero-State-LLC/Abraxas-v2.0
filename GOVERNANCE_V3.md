# Governance V3

```yaml
governance_version: 3
philosophy:
  build_first_validate_second
development:
  direct_implementation_allowed: true
experimentation:
  enabled: true
runtime_changes:
  allowed: true
schema_changes:
  allowed: true
refactors:
  allowed: true
activation:
  local_dev: allowed
  sandbox: allowed
  internal_canary: conditional
  external_production: operator_gated
requirements:
  tests_pass
  artifacts_reproducible
  docs_updated
forbidden:
  fake_data
  fabricated_evidence
  unverifiable_claims
```

## Development workflow

Routine engineering work follows this path:

```text
Feature Request → Code → Test → Commit → PR → Merge → Notion Update
```

Do **not** generate new authorization, approval, review, eligibility, or seal packets for ordinary development work.

## Preserved invariants

These controls remain mandatory regardless of governance mode:

- **Determinism:** preserve `canonical_hash` provenance and deterministic serialization across artifact writers.
- **Schema validation:** all contract-bound surfaces must pass schema checks.
- **Artifact lineage:** maintain traceability between generators, outputs, and registry entries.
- **Testing:** targeted tests for touched surfaces; run `python scripts/run_fast_ci.py` before opening or updating a PR.
- **Changelog:** semantic-release updates `CHANGELOG.md` on merge to `main` following Conventional Commits.

## Bounded product activation

Product activation is lane-based rather than a single blanket deny.

- `LOCAL_DEV`: allowed for local runners, fixtures, adapters, migrations, UI work, deterministic replay, and integration testing.
- `SANDBOX`: allowed for isolated, reversible activation using non-production data and bounded configuration.
- `INTERNAL_CANARY`: conditionally allowed when the candidate commit is validated, observable, reversible, and credential scope is bounded.
- `EXTERNAL_PRODUCTION`: remains operator-gated for public deployment, persistent external automation, user/customer data, irreversible mutation, billing, or broad network authority.

Routine engineering does not require production-readiness packets merely to activate local or sandbox paths. Classify by actual blast radius, not by the word `runtime` or the subsystem name.

See [`docs/governance/BOUNDED_PRODUCT_ACTIVATION_001.md`](docs/governance/BOUNDED_PRODUCT_ACTIVATION_001.md).

## Governance Stratification (v1)

See [`GOVERNANCE_STRATIFICATION_001.md`](GOVERNANCE_STRATIFICATION_001.md).

Routine engineering (Layer 0 — Internal Engineering) and advisory architecture (Layer 1) proceed under existing operator engineering approval via Continuous Engineering Mode.

Escalation to Layer 2 (Canon) or Layer 3 (Runtime) requires objective evidence of crossing a trust boundary and explicit authorization. Local development and isolated sandbox execution do not become Layer 3 solely because code runs.

Default rule: every engineering task begins at Layer 0 unless evidence demonstrates otherwise.

## Authority model

```yaml
status: ACTIVE
model: implementation_first
repo_authority: github_main
documentation_authority: notion
release_authority: validated_code
external_production_authority: operator
```

- **GitHub (`main`):** source of truth for code, tests, and reproducible artifacts.
- **Notion:** source of truth for product documentation, planning context, and operator-facing status pages.
- **Releases:** authorized when validated code passes CI and merge gates on `main`.
- **Activation:** local development and sandbox activation are allowed within bounded scope; external production remains a separate operator gate.

## Historical governance artifacts

The P70–P130 continuity chain and related `out/operator_review/*` surfaces are **archived project history**. They are preserved for provenance and audit but are **not required** for routine development.

See [`GOVERNANCE_SIMPLIFICATION_001.md`](GOVERNANCE_SIMPLIFICATION_001.md) for the migration receipt and Notion alignment checklist.

## SHADOW and FORECAST separation

Keep SHADOW and FORECAST surfaces separated in code and documentation. Historical advisory/projection artifacts under `out/` retain their original locks; do not reinterpret them as live execution authorization.

## Brier provenance

Brier scoring remains telemetry-only. Do not resolve Brier outcomes or escalate authority locks from scoring surfaces.
