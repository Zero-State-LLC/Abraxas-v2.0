# Golden Test Vectors (ABX.EsotericIntelligence.v0.1)

## Vector 1: Hermetic Alchemical (transformation)
Input: "prima materia calcination dissolution"
Expected: transformation stages with alternatives; claim_class TRADITION_ATTESTED; NOT_COMPUTABLE on medical claims.

## Vector 2: Tree of Life Path
Input: "Netzach to Hod"
Expected: tradition (Qabalah) preserved; comparative functional only; identity false.

## Vector 3: Tarot deterministic
Input: seed=42, 3-card spread
Expected: reproducible draw; upright/reversed; archetype mapping; no forecast.

## Vector 4: Astrology missing time
Input: "Sun in Leo transits" (no birth data)
Expected: NOT_COMPUTABLE with reason "missing birth time/location".

## Vector 5: Gematria Hebrew
Input: "אלהים" explicit Hebrew gematria
Expected: value 86 (or standard); normalization noted; collisions listed.

## Vector 6: Sacred Geometry
Input: "vesica piscis description"
Expected: observed geometry + symbolic attribution separated; no proof claim.

## Vector 7: Hermes/Thoth comparative
Input: "Hermes Trismegistus vs Thoth"
Expected: functional role overlap; identity_equivalence=false; separate tradition candidates.

## Vector 8: Dream motifs
Input: "door water unknown guide"
Expected: threshold motif; personal assoc precedence; cultural alternatives; SHADOW only.

## Vector 9: Numeric synchronicity
Input: "repeated 23s in media"
Expected: recurrence noted + algorithmic exposure alternative + symbolic hypothesis; causal=false.

## Vector 10: Goetic sigil unsourced
Input: "sigil of X" (no source)
Expected: NOT_COMPUTABLE or UNSOURCED.

(Additional vectors for ritual grammar, ABX-Rune vs historical rune distinction, explicit divinatory request vs blocked.)

Store expected as invariant assertions in tests.
## ALife Adapter Vectors (v0.2 per addendum)
## Vector 11: Organismize
Input: --mode organismize "Hermes messenger archetype threshold"
Expected: SymbolicOrganismCandidate.v1 (class ARCHETYPE/SYMBOL), governance.entity_assertion=false, provenance, handoff string to existing RUNE.ORGANISMIZE. Fitness specialized (interpretive_utility etc.).

## Vector 12: Archetype Lineage
Input: --mode archetype_lineage "Hermes"
Expected: ABX.ArchetypeLineage.v1 with branches, stable_motif_genes, current_phenotypes, active_habitats, no entity assertion.

## Vector 13: Sigil Genotype
Input: --mode sigil_genotype "I maintain calm focus while shipping Sigil-Forge"
Expected: ABX.SigilGenotype.v1; construction `spare.letter_monogram`; primitives `mntclfswhpgr` (not hardcoded H,M); intent_digest SHA-256 of normalized intent; plaintext omitted; governance SHADOW / entity_assertion=false / forecast_authority=false; variant_classification `FORGE_CORE` or `LOCAL_SPARE_REDUCTION`. All-vowel input → construction NOT_COMPUTABLE.

## Vector 14: Distributed Population
Input: --mode population_model "hyperstition of the messenger"
Expected: ABX.DistributedSymbolicPopulation.v1, entity_assertion=false, causal_claim=false, propagation channels tracked.

