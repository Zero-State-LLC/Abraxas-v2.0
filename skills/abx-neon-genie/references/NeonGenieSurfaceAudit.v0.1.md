# Neon Genie Surface Audit & Repo–Notion Reconciliation (v0.1)

**Date of audit**: 2026-07-11 (via tools)
**Authority**: Advisory only. No fabrication of unobserved implementation.

## Repo State (OBSERVED)

- Pipeline: `neon_genie_ideation` (core/pipelines/registry.py)
  - Tier: 3
  - Lane: SHADOW_PRODUCT
  - Status: specified
  - Contract: MISSING_CONTRACT
  - Next action: "add idea novelty validation and operator packet"
- Global Pipeline Gap Backlog: DEFER_UNOBSERVED_SUBSYSTEM (explicit instruction: do not fabricate pipeline contract from inventory metadata alone).
- Subsystem Ownership Matrix: Neon Genie marked MISSING_CONTRACT.
- All concrete surfaces in `docs/ventures/`, `docs/runtime/`, `docs/oracle/`, `docs/visualization/`, `docs/receipts/`, `docs/index/CANON_INDEX_V2.md` are **documentation-only planning layers** (P4, P6, P8, P9, P11, P14, P17, etc.).
  - Explicit disclaimers: no runtime, no executable schemas, no telemetry, no product launch, no canon promotion, no governance expansion.
- AAL-Viz sample data references `system_id: 'neon_genie'` for projection purposes only.
- No core Python implementation of ideation stages.
- No existing `skills/abx-neon-genie/`.
- No registered `RUNE.NG.*` runes.
- Strong pattern of "planning only" and "autognome" / "venture factory" simulation vectors as review constructs.

## Notion State (per provided architecture)

- Richer operational definition: invention refinery / universal venture engine.
- Stages: intake, discovery, recombination, differentiation, scoring, shaping, simulation, pitching, cataloging.
- v0.4 venture packet, specific input modes (8), output classes (8).
- Duplicate prevention, cross-skill routing (Signal Forager, Noctis, Level 99, LeakForge, AAL-Viz, etc.).
- Evidence-gated claims, public packaging boundaries.

## Reconciliation

| Surface                  | Repo Classification          | Notion Classification     | Selected Authority | Action |
|--------------------------|------------------------------|---------------------------|--------------------|--------|
| neon_genie_ideation      | CURRENT_IMPLEMENTATION (declaration only) | CURRENT_CANON (full engine) | Repo for contract status; Notion for target architecture | Build umbrella + contracts + overlap gate (this skill) |
| Venture Factory docs     | CURRENT_REFERENCE (planning) | HISTORICAL / SUPERSEDED   | Repo | Preserve as provenance; do not execute |
| Autognome vectors        | CURRENT_REFERENCE (planning) | HISTORICAL                | Repo | Use as symbolic seed source only via Noctis |
| AAL-Viz neon_genie entry | CURRENT_IMPLEMENTATION (projection target) | CURRENT_CANON | Both | Projection-only binding |
| Runes / Routes           | MISSING | CURRENT_CANON (RUNE.NG.* list) | abx-runes-yggdrasil-manager | Register via manager skill |
| Evidence / Forager       | PARTIAL (existing skills) | CURRENT_CANON | Existing skills | Bind via cross-skill references |

**Key Divergence**: Repo treats as unobserved Tier 3 planning surface with explicit deferral. Notion treats as active invention engine. This skill bridges by creating the router + contracts + routing discipline while respecting "do not fabricate unobserved core" rule.

**Risk**: High risk of duplicate claims if overlap detection is weak. Overlap detector is therefore the first critical module.

## Rune Audit (to be completed via abx-runes-yggdrasil-manager)

Proposed (from user prompt + inventory):
- RUNE.NG.INTAKE
- RUNE.NG.DISCOVER
- RUNE.NG.RECOMBINE
- RUNE.NG.DIFFERENTIATE
- RUNE.NG.SCORE
- RUNE.NG.SHAPE
- RUNE.NG.SIMULATE
- RUNE.NG.PITCH
- RUNE.NG.CATALOG

These must be registered through the runes-yggdrasil-manager skill to avoid duplicate registries.

## Next Action

This umbrella skill + modular stages + targeted validation begins satisfying the "add idea novelty validation and operator packet" next action without violating the deferral rule.