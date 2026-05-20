# AGENTS OPERATING DOCTRINE

This repository is governed, deterministic, and fail-closed. Agents must preserve advisory/projection behavior and never escalate authority.

## Mandatory pre-change reads

Before proposing or making changes, coding agents must read:

1. `README.md`
2. `PLANS.md`
3. Latest relevant artifacts under `out/` for the target lane

## Current canonical edge

- Treat P27–P31 as sealed (`COMPLETE_AND_STABLE`) unless a fresh audit/test run proves breakage.
- Current coding edge is post-P35, with P40/P42 planning-gate surfaces present.
- Before new subsystem coding, run `scripts/run_canon_resume_state.py` and consult `out/canon_resume_state/latest.json` as the continuity pointer.
- If a user asks for audit/docs-only work, do not perform feature implementation.

## Test execution order

- Run targeted tests first for touched surfaces.
- Run broader/full tests only after targeted checks pass or when explicitly requested.
- If environment constraints block tests, record exact command failures without claiming success.

## Determinism and serialization rules

- Preserve deterministic serialization and hash behavior across packet/artifact writers.
- Never introduce wall-clock, UUID, filesystem-order, randomness, or network dependency into deterministic surfaces.
- Keep canonical ordering and stable field shapes intact.

## Governance and authority boundaries

- Keep SHADOW and FORECAST surfaces separated.
- Keep all advisory/projection surfaces non-authoritative.
- Preserve: advisory_only, projection_only, non_authoritative.
- Deny: mutation, execution, routing authority (unless explicitly advisory-only), forecast authority, canon/runtime/queue mutation.
- No auto-approval, no auto-execution, no adaptive learning unless future canon explicitly allows it.

## Failure and drift reporting

- Record broken surfaces explicitly; never hide or silently bypass them.
- Prefer fail-closed reporting with concrete blocker reasons.
- Do not fabricate artifact/test outcomes.
