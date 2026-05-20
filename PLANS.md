# PLANS — CURRENT CANONICAL ROADMAP

## Sealed baseline (current canonical chain)

Completed and stable:

- P27 Temporal Resonance Coherence
- P28 Coherence Field Operator Surface
- P29 Operator Attention Weather
- P30 Operator Review Routing Enhancer
- P31 Operator Attention Ledger

P31 canonical commit reference (Notion-provided): `06057d9` (`feat(p31): add operator attention ledger`).

## Current edge

- Current implementation edge is **post-P31**.
- Next work must begin with an explicit planning/audit pass.
- Do not resume at P27 and do not redo P27–P31 unless audit/tests fail.

## Candidate next lane (not canon yet)

### P32 Operator Fatigue Corridor Detection

Status: `CANDIDATE` / `NOT_CANON` for this roadmap unless explicitly approved as canonical in governing docs/process.

Any P32 or later work must be treated as non-canonical planning/exploration until explicitly sealed.

## Acceptance criteria for the next approved plan

The next approved lane must:

1. Consume P31 ledger output only, or explicitly declare any additional upstream artifacts.
2. Remain deterministic (stable ordering, serialization, and hash behavior).
3. Stay advisory/projection-only and non-authoritative.
4. Include all required delivery surfaces:
   - schema contract
   - runner script
   - tests
   - generated artifact registry entry
   - generated artifacts (`.latest.json` and `.latest.md`) where policy applies
5. Pass full tests and artifact drift checks:
   - `pytest -q`
   - `python scripts/run_artifact_regeneration.py --full --validation-only`
   - `python scripts/run_artifact_regeneration.py --check-drift`
