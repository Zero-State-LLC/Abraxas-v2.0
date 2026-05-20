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

- Current implementation edge is **post-P35**.
- P40 and P42 planning-gate documents are present and remain non-authoritative roadmap surfaces.
- Next work must begin with an explicit planning/audit pass.
- Do not resume at P27 and do not redo P27–P35 unless audit/tests fail.

## Planning-gate surfaces (not canon yet)

- P40 AAL-Viz Climate + Motif Fusion Overlay: `PLANNING_GATE_PRESENT` for roadmap tracking.
- P42 Operator Narrative Report: `PLANNING_GATE_PRESENT` for roadmap tracking.

Any post-P35 work must be treated as non-canonical planning/exploration until explicitly sealed.

## Acceptance criteria for the next approved plan

The next approved lane must:

1. Consume sealed upstream artifacts and explicitly declare any additional dependencies.
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
