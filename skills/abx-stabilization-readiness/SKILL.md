---
name: abx-stabilization-readiness
description: "Builds deterministic advisory evidence for stabilization readiness without freezing contracts, activating production, promoting runtime state, mutating canon, or writing externally."
version: 0.1.0
author: Abraxas Governed Operator
license: Proprietary
platforms: [macos, linux]
metadata:
  hermes:
    tags: [abraxas, stabilization, reproducibility, conformance, advisory]
    related_skills: [abx-hermes-skill-evolution]
---
# ABX Stabilization Readiness

## Boundary

This skill is `ADVISORY_ONLY` and `READ_ONLY_BY_DEFAULT`. It cannot freeze a
contract, activate production, mutate canon, promote runtime state, perform
external writeback, or start a stabilization campaign autonomously.

## Flow

1. Build a deterministic baseline state for an explicitly supplied commit.
2. Classify observed contract surfaces without inferring frozen status.
3. Record unavailable reproducibility evidence as `NOT_COMPUTABLE`.
4. Run deterministic conformance fixtures for observed Python behavior only.
5. Evaluate the independent fail-closed entry gate.
6. Publish advisory artifacts through `core.canonical.json.write_canonical_json`.

## Operator Boundary

Even a ready gate result is a recommendation. Operator action remains required,
and no approval or authority is issued by this package.
