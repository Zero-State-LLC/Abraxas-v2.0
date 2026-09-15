# commercial_claims_blocked is a density gate

SHADOW / advisory. Does not grant authority.

## Two meanings that got fused

`core.signal.evidence_pack.commercial_claims_blocked(pack)` returns true when the pack lacks enough OBSERVED density for Neon/commercial language. False means density is high enough to speak commercially in advisory text.

SHADOW lane lock is a different object:

- `lane` must be `SHADOW`
- `advisory_only` must be true
- `authority.execution_authority` / `promotion_authorized` / `forecast_routing_authorized` / `canon_mutation_allowed` must be false

Execution repo Warden-pre (Abraxas #258, main `21f051d7`) treats `COMMERCIAL_UNBLOCKED` as a **warning**. It does not fail the lane.

## What this patch does not do

- Does not rename `commercial_claims_blocked`
- Does not add a new receipt key (that would change `receipt_hash`)
- Does not flip authority
- Does not copy execution IR into this remote

## Alias name for callers

Read `commercial_claims_blocked` as `commercial_density_gate`. Same function. Same boolean. Neon redaction keeps the old name.
