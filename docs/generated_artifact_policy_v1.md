# GENERATED_ARTIFACT_POLICY_V1

## Purpose
Stabilize generated artifact handling by treating generators, schemas, and deterministic inputs as canonical truth and treating emitted artifacts as derived surfaces.

## Rules
- Canonical truth is the generator plus schema plus deterministic inputs.
- Generated artifacts are advisory derived outputs.
- CI must regenerate managed artifacts before tests.
- CI must fail closed when generators or schemas are missing.
- CI must detect stale artifact drift explicitly.
- Unrelated artifact churn is prohibited.
- Mixed feature and artifact governance changes are prohibited.
- Giant regeneration-only pull requests are prohibited.

## Invariants
- advisory_only = true
- mutation_allowed = false
- authority_granted = false
- auto_execute = false
- auto_approve = false

## Regeneration posture
- Regenerate only known managed artifacts.
- Preserve deterministic ordering.
- Normalize canonical JSON and newlines.
- Never fabricate artifacts.
- Treat missing generators or schemas as blocking failures.
