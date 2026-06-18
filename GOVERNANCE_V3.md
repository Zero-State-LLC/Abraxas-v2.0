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

## Authority model

```yaml
status: ACTIVE
model: implementation_first
repo_authority: github_main
documentation_authority: notion
release_authority: validated_code
```

- **GitHub (`main`):** source of truth for code, tests, and reproducible artifacts.
- **Notion:** source of truth for product documentation, planning context, and operator-facing status pages.
- **Releases:** authorized only when validated code passes CI and merge gates on `main`.

## Historical governance artifacts

The P70–P130 continuity chain and related `out/operator_review/*` surfaces are **archived project history**. They are preserved for provenance and audit but are **not required** for routine development.

See [`GOVERNANCE_SIMPLIFICATION_001.md`](GOVERNANCE_SIMPLIFICATION_001.md) for the migration receipt and Notion alignment checklist.

## SHADOW and FORECAST separation

Keep SHADOW and FORECAST surfaces separated in code and documentation. Historical advisory/projection artifacts under `out/` retain their original locks; do not reinterpret them as live execution authorization.

## Brier provenance

Brier scoring remains telemetry-only. Do not resolve Brier outcomes or escalate authority locks from scoring surfaces.
