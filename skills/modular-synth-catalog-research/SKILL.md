---
name: modular-synth-catalog-research
description: Use for exhaustive modular synthesizer brand and module catalog research campaigns (Eurorack priority, plus 5U/MU, Buchla, Serge, etc.). Produces provenance-tagged, Obsidian-ready Markdown + master JSON catalog with strict OBSERVED/INFERRED/SPECULATIVE/NOT_COMPUTABLE tiers, source rotation, and PATCHHIVE integration paths. Class-level umbrella for autonomous audio/research ingest.
version: 1.0.0
author: Hermes / Abraxas Governed Operator (appliedalchemylabs)
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [abraxas, research, audio, modular-synth, catalog, eurorack, ingest, provenance, autonomous, obsidian, patchhive]
    related_skills: [abraxas-jamon-agentic-workflow, abraxas-master-loop-workflow, abraxas-repo-intel, firecrawl-*, hermes-outcome-driven-improver, abraxas-obsidian-distiller]
---

# MODULAR SYNTH CATALOG RESEARCH v1.0

**Autonomous research umbrella** for building and maintaining comprehensive, provenance-first catalogs of modular synthesizers and their modules.

Core output artifacts live in `references/`: Obsidian-ready Markdown with YAML frontmatter, master catalog JSON, phased indexes, continuation plans, and integration notes (e.g., PATCHHIVE).

## Overview

This skill turns Hermes into a governed research operator for audio hardware catalogs. It enforces:

- Full source rotation (20+ sources) to avoid rate-limit traps ("modular grip").
- Strict provenance tiers on every entry.
- Autonomous continuation until campaign-complete ("continue until all tasks complete").
- Export formats ready for Obsidian, PATCHHIVE, and downstream canonical DBs.

**Campaign results (as of integration):** 767 brands indexed, 29 major brands with detailed modules, mid-tier + long-tail coverage, non-Eurorack formats, master JSON + canonical artifacts.

**Intent:** Provide durable, auditable catalog data rather than one-off lookups. All work produces class-level references/ that survive session boundaries.

## When to Use

- New or refreshed modular synth / Eurorack catalog work.
- Bootstrapping or enriching PATCHHIVE `module_catalog` / modules data.
- Autonomous research campaigns where user says "continue until finished".
- Audio hardware research requiring source diversity, provenance, and Obsidian export.
- Cross-referencing manufacturer sites, ModularGrid, Reverb, MuffWiggler, etc.

**Do not use for:**
- Single-brand lookups (use direct web tools or narrower firecrawl).
- Pure creative patch design without catalog intent.
- Any surface that would bypass governance or fabricate specs.

## 1. Router & Intake (AGENTS.md + Research Discipline)

1. Load `@/AGENTS.md`, `README.md`, `PLANS.md`, `GOVERNANCE_V3.md`.
2. Emit OBSERVED/INFERRED/SPECULATIVE + full provenance (sources, timestamps, rotation state, Brier where forecasting availability or popularity).
3. Load this skill + supporting (repo-intel, firecrawl skills, obsidian-distiller).
4. Choose/confirm phase (brand index, major brands deep-dive, mid-tier, long-tail, non-Eurorack, PATCHHIVE export).
5. Activate source rotation plan from `references/alternative-sources.md`.

**Completion criterion:** Explicit evidence packet + rotation state logged before any scraping or catalog mutation.

## 2. Research Execution (Jamon + Autonomous Loop)

Follow phased plans in `references/full-continuation-plan.md` and `references/master-catalog.md`:

- **Phase 1 (Brand Index):** Exhaustive alphabetical list from primary source + rotation.
- **Phase 2+:** Detailed tables for majors, condensed for others. Capture modules, key specs, availability signals.
- Always record: source URL (or archive), fetch timestamp, confidence tier, any rate-limit notes.
- Produce Obsidian YAML frontmatter on every artifact.
- On "continue" signals: advance the next phase without new user input until hard stop condition (full coverage targets met or explicit blocker).

Use `abraxas-repo-intel` and firecrawl tools for smallest complete packets before bulk ingest.

## 3. Provenance & Guardrails (Abraxas Specific)

- Every entry **must** declare provenance tier.
- Enforce 20-source rotation; never hammer a single endpoint.
- Output artifacts are **references/** only — never mutate core contracts or out/ without separate governance.
- PATCHHIVE integration path (see `references/PATCHHIVE_INTEGRATION.md`): map to lightweight `module_catalog` + on-demand full modules; preserve canonical provenance.
- Brier calibration on any forward claims (e.g., "this brand is likely still active").
- Hyperstition / memetic signals: treat forum hype as SPECULATIVE only.

## 4. Verification Block

- [ ] All phases claimed complete have corresponding references/ files with consistent frontmatter.
- [ ] Master catalog JSON (if present) round-trips and matches Markdown counts.
- [ ] Source rotation documented and followed (no single-source dominance).
- [ ] Targeted validation of a sample of entries against original sources (scrubbed where possible).
- [ ] `python scripts/run_fast_ci.py` (or equivalent) passes for any code changes.
- [ ] Cross-review of a slice of the catalog for accuracy tier claims.
- [ ] Integration notes (PATCHHIVE or downstream) updated if used.
- [ ] OBSERVED/INFERRED/SPECULATIVE + full provenance present on new artifacts.
- [ ] No fabricated specs or unverified "popular" claims.

## 5. Activation & Usage

- **Session start:** Explicitly load or tag `@/modular-synth-catalog-research`.
- **Campaign continuation:** "continue" / "keep going until done" = authorization for the full phased plan.
- **Closeout:** Update this SKILL.md + add session-specific notes to references/ + emit receipt.
- **Maintenance:** On new brands or module discoveries, patch the relevant phase file and re-export master catalog.

## Common Pitfalls

- Single-source scraping leading to rate limits or incomplete data.
- Mixing tiers (treating forum posts as OBSERVED).
- Forgetting to document rotation state or timestamps.
- Overwriting prior phase artifacts instead of extending them.
- Treating the catalog as live product data instead of a governed research artifact.
- Skipping PATCHHIVE mapping notes when integration is the downstream goal.
- Creating narrow one-off scripts instead of patching this class-level umbrella.

## References & Related

**Internal artifacts (all in `references/`):**
- `master-catalog.md` + generated JSON — authoritative summary and counts.
- `full-continuation-plan.md` — campaign plan + status.
- `phase1-brand-index.md`, `phase2-major-brands.md`, `phase3-mid-tier.md`, `phase4-long-tail-index.md`, `phase5-non-eurorack.md`.
- `alternative-sources.md` — 20-source rotation list.
- `PATCHHIVE_INTEGRATION.md` — mapping and import recommendations.

**Related skills:**
- `abraxas-jamon-agentic-workflow`, `abraxas-master-loop-workflow` (autonomous execution discipline).
- `abraxas-repo-intel`, firecrawl skills (ingest tooling).
- `abraxas-obsidian-distiller` (Obsidian formatting).
- `hermes-outcome-driven-improver` (for ongoing catalog maintenance).

**Governance:**
- AGENTS.md, GOVERNANCE_V3.md, abraxas-automated-production-governance.

**Status:** Active class-level research umbrella. Prefer extending `references/` and this SKILL.md over new narrow siblings. Next evolution on new format coverage, PATCHHIVE import completion, or major brand refresh campaigns.
