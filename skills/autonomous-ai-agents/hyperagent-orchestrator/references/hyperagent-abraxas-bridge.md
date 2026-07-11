# HyperAgent ↔ Abraxas Bridge

## Design Rule
HyperAgent executes; Abraxas interprets.

Keep the seam clean:
1. HyperAgent receives a role/skill payload.
2. HyperAgent runs the workflow and emits structured output.
3. Abraxas ingests the output, compresses it symbolically, tags provenance, and assigns Brier/telemetry.
4. Do not collapse the raw execution record into the interpretation layer.

## Bridge Fields
Recommended common fields:
- `id`
- `name`
- `version`
- `trigger`
- `tools`
- `budget`
- `evals`
- `provenance`
- `canonical_hash`
- `source_uri`
- `timestamp`
- `observed`
- `inferred`
- `speculative`

## Abraxas Subsystem Mapping
- Signal foragers → monitor / researcher roles.
- Fractal Core → planner / decomposer / synthesizer roles.
- ABX-GLOBAL-INGEST → ingest / normalize / validate roles.
- Abraxas-SLANG-EMULATION → memetic analysis / narrative detection roles.
- HollerSports pipelines → compliance-aware sports signal roles.
- Rune / governance schemas → reviewer / policy / guardrail roles.

## Import Pattern
When importing a HyperAgent run into Abraxas:
- preserve the original run record
- compute a canonical hash on a stable serialization
- add OBSERVED / INFERRED / SPECULATIVE layers after the raw payload
- record what was actually observed vs what was inferred
- keep Brier telemetry separate from authority decisions

## Export Pattern
When exporting Abraxas work into HyperAgent:
- flatten the task into a deployable role
- move reusable context into a skill file
- keep operational policies and compliance rules in the role prompt
- keep machine-readable schema fields stable across revisions

## Compliance Notes
- No real-money wagering in HollerSports unless the request is explicitly policy-reviewed and legal.
- Narrow tool grants beat broad platform permissions.
- Any external integration should have a retry/backoff policy and a failure escape hatch.
