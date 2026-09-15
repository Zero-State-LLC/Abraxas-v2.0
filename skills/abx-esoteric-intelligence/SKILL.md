---
name: abx-esoteric-intelligence
description: "Governed symbolic-intelligence adapter for occult, esoteric, mythological, ritual, divinatory, archetypal, numerical, geometric, temporal, dream-symbol, and correspondence-based analysis within Abraxas. Umbrella orchestrator; reuses existing surfaces (Noctis, runes-manager, Oracle Signal, SHADOW). Does not create parallel ontology, forecast engine, or execution authority. Default lane: SHADOW. Runtime disabled by default. Divination explicit only."
version: 0.1.0
author: Abraxas Governed Operator
license: Proprietary
platforms: [macos, linux]
metadata:
  hermes:
    tags: [abraxas, esoteric, symbolic, occult, archetype, tarot, astrology, gematria, ritual, dream, synchronicity, runes, shadow-symbolic, validation-routing]
    related_skills: [abx-runes-yggdrasil-manager, abx-noctis-dream-functions, abx-neon-genie, abraxas-validation-routing, abraxas-repo-intel, abx-familiar-signal-forager, abraxas-ingest]
    authority: SHADOW_SYMBOLIC_ADVISORY_ONLY
    runtime_authority: false
    canon_authority: false
    promotion_authority: false
    forecast_authority: false
    divination_default: "OFF_UNLESS_EXPLICIT"
    memory_write_authority: false
---

Supported mode: **full checkout**. Read repository-root `skills/OPERATING.md`
for Python 3.12 bootstrap, canonical source/version, explicit output paths,
unshipped sibling fallback and fail-closed verification before using this skill.

# ABX-ESOTERIC-INTELLIGENCE (Umbrella)

## Purpose (OBSERVED)

Governed adapter that lets Hermes retrieve, normalize, analyze, and emit typed symbolic material from esoteric, mythological, ritual, divinatory, archetypal, and correspondence-based sources for use by Abraxas subsystems.

**Core contract:**
- Intake and normalize source material or operator requests.
- Classify claims with provenance and claim_class (OBSERVED / TRADITION_ATTESTED / INFERRED / SYMBOLIC_INTERPRETATION / NOT_COMPUTABLE etc.).
- Perform bounded operations: correspondence, archetype, ritual grammar, transformation, tarot/deck, astrology/temporal, gematria, geometry, sigil, dream motif, synchronicity.
- Preserve source traditions; functional mappings only (no identity collapse).
- Emit EsotericAnalysisPacket and specialized packets with SHADOW lane, authority blocks, and NOT_COMPUTABLE where data/evidence missing.
- Route to existing owners (Noctis for dreams, runes-manager for contracts, Oracle for enrichment, SHADOW for anomalies, Neon for mythic framing).
- Explicit mode for divinatory_render only on direct request.

It is **not**:
- An occult truth oracle or autonomous agent.
- Replacement for Oracle Signal Layer, SHADOW, or FORECAST.
- A new canonical ontology or execution authority.
- A license to invent traditions, correspondences, or claims.
- Automatic divination engine (divinatory_render gated).

## Canonical Laws (OBSERVED from prompt + repo patterns)

### Symbolic Data Law
Every symbolic system is admissible as data. No symbolic system is automatically truth, proof, forecast, healing, ontology, or execution authority.

### Tradition Preservation Law
Every interpretation preserves source tradition, period, text/artifact, traditional vs modern interpretation, transformation history, uncertainty, disputed attribution, and provenance. Do not collapse traditions into a universal system.

### Functional Mapping Law
Cross-tradition mappings use functional role, motif overlap, ritual position, polarity, transformation behavior, narrative/temporal role, or graph structure. Not visual resemblance, name similarity, "vibe", or unsourced association. Similarity ≠ identity.

### Divination Mode Law
Default: analytical_symbolic. divinatory_render activates only on explicit operator request or typed upstream selection. Results remain interpretive frames unless separate calibrated evidence supplied.

### No Phantom Correspondence Law
Never fabricate historical correspondence, quotation, attribution, deity/planetary/tarot link, gematria, lineage, calculation, or citation. Use NOT_COMPUTABLE or UNSOURCED_OPERATOR_ASSOCIATION.

### Dual-Lane Law
SHADOW preserves motifs, anomalies, recurrences, collisions, conflicts, drift. FORECAST only from calibrated evidence. Symbolic resonance ≠ forecast weight.

### Oracle Subordination Law
Enriches Oracle inputs with typed symbolic material. Does not replace Oracle intake, mutate state, or create independent oracle authority.

## Supported Corpus Families (OBSERVED)

See references/corpus-families.md for full definitions, aliases, admissible sources, lanes, operations, restrictions, provenance requirements, and NOT_COMPUTABLE conditions.

Key families (non-exhaustive):
- hermetic_alchemical
- qabalah_tree_of_life
- gematria_numeric_encoding
- sacred_symbolic_geometry
- runic_sigil
- tarot_archetype
- astrology_planetary_timing
- enochian_magical_language
- goetia_spirit_catalog
- mythology_comparative_religion
- ritual_initiation
- sound_frequency_music_symbolism
- color_element_direction
- dream_unconscious_symbol
- modern_memetic_occulture
- folk_magic_divination
- operator_defined_symbolic_system

## Operational Modes (OBSERVED)

See references/divination-modes.md and integration-map.md.

Supported operations (adapter layer):
- Source Extraction
- Correspondence Analysis (historically_attested, tradition_internal, comparative_functional, etc.)
- Archetype Analysis (creation, preservation, destruction, threshold, trickster, etc.; identity_equivalence default false)
- Ritual Grammar Analysis (opening, invocation, ordeal, transformation, integration, closure, etc.)
- Transformation Analysis (alchemical stages + general; prima materia → rubedo, nigredo etc. with alternatives)
- Tarot / Symbolic Deck Analysis (deterministic with seed; spreads; upright/reversed; narrative; archetype mapping)
- Astrology / Temporal Alignment (planets, signs, houses, aspects, lunar, retrogrades, electional; distinguish astronomical vs interpretive; NOT_COMPUTABLE on missing data)
- Gematria / Numeric-Symbolic (named systems only: Hebrew, Greek isopsephy, English ordinal/reduction; with normalization, collisions, bias warnings)
- Sacred / Symbolic Geometry (circle, vesica, pentagram, etc.; observed vs constructed vs attributed)
- Sigil / Rune Analysis (historical vs ABX-Runes; ABX distinct)
- Dream / Unconscious Symbol (motif, recurrence, threshold, shadow candidates; personal associations precedence)
- Synchronicity / Occult Pattern (temporal/numeric/symbolic recurrence; selection/algorithmic alternatives; symbolic value preserved without causal proof)

All emit with claim_class, evidence_class, derivation_path, provenance, confidence (capped), drift_risk, authority blocks.

## Claim Taxonomy (OBSERVED)

See references/claim-taxonomy.md.

claim_classes: OBSERVED, COMPUTED, TRADITION_ATTESTED, HISTORICALLY_REPORTED, OPERATOR_REPORTED, INFERRED, COMPARATIVE, SYMBOLIC_INTERPRETATION, DIVINATORY_RENDER, SPECULATIVE, CONTRADICTED, NOT_COMPUTABLE.

evidence_classes: primary_source, secondary_source, scholarly_source, traditional_commentary, modern_practitioner, operator_input, repository_canon, computed_result, unsourced.

No claim omits classification.

## Output Protocol

Default structured packets (see schemas):
- EsotericAnalysisPacket.v1 (core envelope with observed/computed/traditional/inferred/symbolic_interpretation/alternatives/evidence/derivation/provenance/authority/status)
- CrossTraditionArchetypePacket.v1 — proposed only; no specialized validated contract shipped
- RitualGrammarPacket.v1 — proposed only; no specialized validated contract shipped
- TemporalSymbolicPacket.v1 — proposed only; no specialized validated contract shipped
- DivinatoryRenderPacket.v1 (explicit auth required)
- SynchronicityAnalysisPacket.v1 — proposed only; no specialized validated contract shipped

Use OPEN/ALIGN/ASCEND/CLEAR/SEAL framing in prose summaries when applicable. Separate OBSERVED / COMPUTED / TRADITION-ATTESTED / ... clearly. Mythic compression after engineering analysis only.

## Authority & Boundaries (OBSERVED)

- SHADOW lane default for motifs/anomalies/interpretations.
- FORECAST authority: false (only calibrated evidence via other subsystems).
- Execution / canon / truth authority: false.
- Divination: explicit only.
- Integrates by adapter: enriches Oracle, SHADOW, Noctis, Neon, AAL-Viz, runes, YGGDRASIL. Does not own or mutate.

See references/integration-map.md for exact handoff rules.

## Failure & NOT_COMPUTABLE (OBSERVED)

See references/not-computable.md.

Returns NOT_COMPUTABLE (or CONFLICTED / INVALID_INPUT) on missing sources, unverifiable attributions, insufficient data for calculation (e.g. astrology without time/place/ephemeris), unspecified systems, unresolved tradition conflicts, insufficient motifs, etc. Never forces an answer.

## Rune Interface

Proposed (documented; register via abx-runes-yggdrasil-manager before use):

RUNE.ESOTERIC.INTAKE, RUNE.ESOTERIC.SOURCE.NORMALIZE, RUNE.SYMBOL.EXTRACT, RUNE.CORRESPONDENCE.MAP, RUNE.ARCHETYPE.BIND, RUNE.RITUAL.GRAMMAR, RUNE.TRANSFORMATION.TRACE, RUNE.TAROT.RENDER, RUNE.ASTROLOGY.ALIGN, RUNE.CHRONOMANCY.ALIGN (sub to temporal), RUNE.GEMATRIA.COMPUTE, RUNE.SYMBOLIC_GEOMETRY.ENCODE, RUNE.SIGIL.CLASSIFY, RUNE.DREAM.MOTIF.TRACE, RUNE.SYNCHRONICITY.ANALYZE, RUNE.OCCULT.ATTRIBUTION, RUNE.ESOTERIC.CONFLICT, RUNE.ESOTERIC.PROVENANCE, RUNE.ESOTERIC.COMPRESS.

All modular, typed, provenance-bearing, deterministic for normalized input, failure-declaring, authority-declaring. No self-granted runtime.

See references/runes-registration.md.

## Activation Triggers (OBSERVED)

Requests involving: occult/esoteric analysis, Hermeticism, alchemy, Qabalah/Kabbalah (symbolic), tarot/oracle cards, astrology/planetary timing/chronomancy, gematria/numerology, sacred geometry, sigils/runes (historical or ABX), Goetia/Enochian, comparative mythology, archetypes, ritual/initiation structure, magical language, dream symbolism, synchronicity, hyperstition/meme magic, symbolic correspondences, occult pattern attribution, esoteric corpus engineering, integration of symbolic traditions into Abraxas.

Also when implementation touches related Abraxas surfaces.

## Non-Triggers (OBSERVED)

Metaphor alone, ordinary technical terms that resemble occult terms, "oracle" as DB, "rune" as unrelated lib, pure religious history without symbolic needs, standard calendar/math geometry without attribution, standard psych without archetypal framing.

## References

- references/corpus-families.md
- references/claim-taxonomy.md
- references/correspondence-law.md (and other laws)
- references/archetype-families.md
- references/divination-modes.md
- references/integration-map.md
- references/not-computable.md
- references/examples.md (golden vectors)
- references/runes-registration.md
- ABX_NEON_GENIE_NOTION... and similar for cross-ref (symbolic opportunity)

## Failure Behavior

- Parse/activation failure → clear error + NOT_COMPUTABLE packet.
- Insufficient data → explicit NOT_COMPUTABLE with reason.
- Conflict → CONFLICTED + alternatives preserved.
- Determinism: identical normalized input → identical packet (hashes, ordering stable).
- No mutation of canon/runtime during analysis.

See references for full contracts and examples.
## ALife Adapter Integration (added per addendum + audit)

See `references/alife_integration_audit.md` (core ALife = MISSING_CREATE in repo; adapter only).

Emits `SymbolicOrganismCandidate.v1` and related packets for handoff to existing ALife runtime.

New runes (to be registered via runes-yggdrasil-manager):
- RUNE.ESOTERIC.ORGANISMIZE
- RUNE.ARCHETYPE.LINEAGE
- RUNE.CORRESPONDENCE.REACT
- RUNE.SIGIL.GENOTYPE
- RUNE.SYMBOLIC.POPULATION / EGREGORE.MODEL / HYPERSTITION.LINEAGE
- RUNE.SYNCHRONICITY.ECOLOGY
- RUNE.DIVINATORY.ECOLOGY (explicit only)

Strict separation: esoteric skill supplies symbolic genotype + interpretation. ALife runtime owns lifecycle, mutation, selection, propagation, extinction.

All governance rules preserved (SHADOW, entity_assertion=false, fitness ≠ truth, recurrence ≠ forecast).

There is no supported general esoteric CLI for these modes. `alife_adapter.py` exposes `build_alife_packet(mode, input_data, request)`; its canned builders are SYNTHETIC fixtures only, requiring `request={"synthetic_fixture": true}`. Without opt-in they raise NOT_COMPUTABLE; never use them as historical or measured evidence.
Fixture packet shape checks are not evidence of a working ALife runtime. Unsupported live modes remain NOT_COMPUTABLE.


See `alife_adapter.py` for the thin pure-function implementation of the ALife packet builders (KISS, reusable, no side effects).


## Offline synthetic validation
```bash
python -m pytest -c /dev/null -p no:cacheprovider skills/tests/test_domain_routes.py tests/test_alife_adapter.py -q
```
These explicitly opt-in fixtures exercise each adapter and its authority labels.
No registered rune, live tradition analysis or forecast is implied. General
esoteric analysis remains a source-grounded procedural lane; do not invent a CLI
or claim unsupported specialized packets have schemas.
