# Esoteric Intelligence Surface Audit v0.1 (repo-grounded)

## Preliminary Audit Table (OBSERVED via tools + repo inspection)

| Surface | Observed Path | Status | Reuse Decision |
|---------|---------------|--------|----------------|
| Hermes Skill Layout (umbrella) | skills/*/SKILL.md + references/ (neon, noctis, hermes-skill-evolution) | PRESENT | PRESENT_REUSE |
| ABX-Runes / YGGDRASIL manager | docs/atlas/abx-runes.md, out/audit/yggdrasil_*, skills/abx-runes-yggdrasil-manager | PRESENT | PRESENT_EXTEND (new RUNE.ESOTERIC.* via manager) |
| Oracle Signal Layer + NOT_COMPUTABLE | core/, receipts, apps/api, atlas | PRESENT | PRESENT_REUSE (enrich, subordinate) |
| SHADOW / FORECAST separation | core/pipelines, many out/audit receipts, governance | PRESENT | PRESENT_REUSE (default SHADOW; FORECAST gated) |
| Noctis dream-symbol | skills/abx-noctis-dream-functions/, core/pipelines/registry | PRESENT | PRESENT_REUSE (motifs) |
| Symbolic / Archetype / Occult | docs/ventures/* (planning only), holler-sports slang/memetic, Neon Genie symbolic refs | PRESENT (planning/docs) | PRESENT_EXTEND (no core engine) |
| SoulDeck / Tarot / Astrology / Gematria full impl | None in core/skills (planning mentions only) | MISSING | MISSING_CREATE (thin adapter support) |
| Provenance / Evidence / Claim taxonomy | core/canonical, receipts, governance | PRESENT | PRESENT_REUSE |
| Skill registry / validation / determinism | scripts/, tests/test_abx_skill_evolution*, abx-hermes-skill-evolution | PRESENT | PRESENT_REUSE |
| Rune proposals / binding | docs, binding matrix | PRESENT | PRESENT_EXTEND |

## Key Decisions (OBSERVED)
- No duplicate corpus engine or oracle created.
- All new surfaces are adapters.
- Divination gated.
- Runes routed through existing manager.
- Targeted validation only (full pytest BLOCKED_BY_PRE_EXISTING_BASELINE as documented).

## Status
Implementation readiness: READY (thin candidate with schemas, laws, boundaries, runner, receipt). Deferred full corpus expansion and live rune binding.
