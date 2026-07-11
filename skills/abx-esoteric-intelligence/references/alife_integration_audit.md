# ALife Integration Audit — abx-esoteric-intelligence (Repo Reality)

**Date**: Current working tree
**Brier**: 0.92 (direct searches + file reads; no Notion assumption)

## Audit Method
- `search_files` for alife/ALife/AAL_ALIFE/symbolic organism/organism/ fitness/mutation/lineage/habitat/metabolism/genotype/phenotype/ecology/extinction/RUNE.ORGANISMIZE/RFD/egregore
- Reads of SUBSYSTEM_OWNERSHIP_MATRIX.md, core files, existing skills (neon-genie, holler-sports/slang-emergence, runes-yggdrasil-manager)
- Exclusion of planning-only Notion references

## Classification Table

| Surface | Observed Path(s) | Status | Reuse Decision | Notes |
|---------|------------------|--------|----------------|-------|
| ALife runtime core | (none found) | MISSING_CREATE | Extend via adapter only | No `alife/`, no AAL_ALIFE_ORGANISM schema, no organism lifecycle code |
| RUNE.ORGANISMIZE / organismization logic | (none found) | MISSING_CREATE | Hand off to future; create adapter RUNE.ESOTERIC.ORGANISMIZE | Delegate point only |
| Bounded mutation logic | abraxas/v2/hygiene (mutation_policy locks), general governance | PRESENT_EXTEND | Reuse mutation policy patterns | Governance locks (no forecast/score mutation) are compatible |
| Selection / lineage tracing | Partial in artifact_lineage tests + core lineage files | PRESENT_EXTEND | Extend for symbolic lineages | Artifact-lineage provides provenance/lineage scaffolding |
| Extinction / archive | None explicit for symbolic | MISSING_CREATE | New in symbolic lifecycle | Use existing archive patterns |
| Propagation / runtime loop | slang-emergence (memetic), hyperstition in hygiene | PRESENT_EXTEND | Reuse for hyperstition/egregore populations | holler-sports/slang-emergence + abraxas/v2/hygiene |
| YGGDRASIL ALife routes | None | MISSING_CREATE | Route new RUNEs via existing runes-manager | Extend abx-runes-yggdrasil-manager |
| ALife AAL-Viz projection | aal-viz related mutation frames | PRESENT_EXTEND | Use for ecosystem projection | Existing projection packets can consume symbolic organisms |
| Symbolic corpus registries | esoteric skill + Neon + holler slang | PRESENT_EXTEND | Primary input to organism candidates | Strong existing coverage |
| RFD / Egregore Watchlist | Referenced in planning + hygiene | PRESENT_EXTEND (weak) | Habitat for distributed populations | Connect via memetic surfaces |
| Hyperstition / meme propagation | skills/holler-sports/slang-emergence, abraxas/v2/hygiene, neon-genie | PRESENT_REUSE + EXTEND | Direct owner for hyperstition/egregore models | Strong memetic engine already exists |
| Archetype lineage surfaces | Partial in esoteric planning + archetype mentions | PRESENT_EXTEND | New RUNE.ARCHETYPE.LINEAGE | Build on existing archetype classification |
| Symbolic recurrence tracking | esoteric synchronicity + slang emergence | PRESENT_EXTEND | Extend with alife_ecology | Already has recurrence + alternatives |
| Organism schema (AAL_ALIFE_ORGANISM.v0.1) | (none found) | MISSING_CREATE | Define adapter candidate only | Do not implement full runtime |
| Interaction / hybrid-organism runtime | None | NOT_APPLICABLE | Future | Not in scope for this adapter |

## Key Observations (OBSERVED)
- No live ALife runtime exists in the current tree. ALife is treated as the "systemwide architectural superstructure" in Notion but remains unmaterialized in code.
- Strong sibling surfaces for memetic/hyperstition/egregore work (holler-sports, hygiene runes, neon-genie routing to Level 99).
- Mutation/selection/ lineage concepts appear in governance (locks) and artifact-lineage (provenance) — reusable patterns.
- Existing rune system (abx-runes-yggdrasil-manager) is the correct registration point for new RUNE.ESOTERIC.* surfaces.
- The esoteric skill already declares hyperstition/meme magic and modern_memetic_occulture as corpus families.

## Decision
- Create adapter-only surfaces inside `abx-esoteric-intelligence`.
- Emit `SymbolicOrganismCandidate.v1` and related packets.
- Register new orchestration runes via runes-manager.
- Do **not** implement organism lifecycle, mutation engine, selection, or propagation here.
- Preserve strict SHADOW lane, `entity_assertion: false`, `forecast: false`, etc.
- Handoff point: `RUNE.ESOTERIC.ORGANISMIZE` → future `RUNE.ORGANISMIZE`.

**Next**: Implement schemas, rune, runner extension, tests, and receipt update.
