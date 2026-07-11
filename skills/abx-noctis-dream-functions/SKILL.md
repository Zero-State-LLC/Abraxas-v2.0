---
name: abx-noctis-dream-functions
description: "Governed orchestration skill for the Abraxas NOCTIS dream lane (SHADOW_SYMBOLIC). Routes human or system dream material through current NOCTIS functions (or thin adapters), emits typed provenance-complete symbolic artifacts, enforces privacy, memory-candidate-only, SHADOW, and no-forecast/no-medical/no-direct-canon boundaries. Reuses existing surfaces; does not create a parallel dream engine."
version: 0.1.0
author: Abraxas Governed Operator
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [abraxas, noctis, dream, symbolic, shadow-symbolic, continuity, motif, abx-runes, yggdrasil, validation-routing]
    related_skills: [abraxas-repo-intel, abraxas-validation-routing, abraxas-automated-production-governance, abx-runes-yggdrasil-manager, abx-familiar-signal-forager]
    authority: SHADOW_SYMBOLIC_PROCESSING_ONLY
    runtime_authority: false
    canon_authority: false
    promotion_authority: false
    forecast_authority: false
    memory_write_authority: false
---

# ABX-NOCTIS-DREAM-FUNCTIONS

## Purpose

Route human or system dream material through the governed NOCTIS (Narrative Oneiric Compression and Transformation Interpretation System) lane.

**Core contract:**
- Intake and normalize dream material.
- Extract bounded symbols and motifs.
- Produce typed symbolic artifacts (packets, graphs, continuity candidates, artifact intents, projections).
- Preserve privacy tiers and SHADOW authority.
- Emit provenance-complete receipts.
- Never grant medical, diagnostic, predictive, canon, routing, forecast, or direct durable-memory authority.

**Governing law:**
> Dreams inform the system. Dreams do not govern the system.

This is an **orchestration and usage skill**. It reuses existing NOCTIS functions where present. It provides thin adapters, contracts, runners, validators, and receipts for the missing integration surfaces.

## Invocation Conditions

Invoke for:
- Analyze a (human or system) dream
- Normalize dream text
- Extract motifs/symbols
- Produce symbolic continuity candidates
- Generate artifact-intent / probe / projection candidates
- Cross-map motifs against SHADOW evidence
- LUCID-style report or WISP proposal candidate generation
- AAL-Viz dream projection

Do **not** invoke for medical/psychiatric claims, prediction, or direct memory/forecast/canon mutation.

## Input Modes

- **HUMAN_DREAM**: User-reported narrative (raw + normalized, privacy tier preserved).
- **SYSTEM_DREAM**: Synthetic, explicitly labeled `synthetic=true`, with source ledger/state refs and deterministic seed.
- **DREAM_HISTORY_REVIEW**: Explicit prior records only.
- **ARTIFACT_INTENT / PROBE_CANDIDATE / PROJECTION_ONLY**: Candidate-only outputs.

## Dream Input Contract (current repo-standard equivalent)

```yaml
schema_version: "DreamInput.v1"
dream_id: string
source: USER | EXTERNAL | SYSTEM
captured_at: ISO-8601
privacy_tier: PRIVATE | RESEARCH | PUBLIC_SYNTHETIC
narrative_raw: string
narrative_normalized: string
context: object
emotional_vector: object
seed: string
provenance:
  intake_method: ...
  content_sha256: string
authority:
  lane: SHADOW_SYMBOLIC
  medical_claims_allowed: false
  ...
```

Empty narrative → `NOT_COMPUTABLE`.

## Required Functional Route (governed)

Dream input
→ policy/privacy gate
→ normalization (preserve raw, deterministic normalize)
→ motif/symbol extraction (evidence-bound)
→ symbolic analysis / graph assembly
→ compression & continuity (against explicit history only)
→ artifact-intent / probe candidates (candidate_only)
→ YGGDRASIL memory-candidate (via runes-yggdrasil-manager)
→ Oracle SHADOW packet (compressed motifs only)
→ AAL-Viz projection (PROJECTION_ONLY)
→ delivery receipt

## Rune / YGGDRASIL Integration

**Before registering or using dream runes, invoke the sibling skill:**

`abx-runes-yggdrasil-manager`

Expected conceptual runes (to be registered via the manager after discovery):
- RUNE.NOCTIS.DREAM.NORMALIZE
- RUNE.NOCTIS.MOTIF.EXTRACT
- RUNE.NOCTIS.CONTINUITY.LINK
- RUNE.NOCTIS.ARTIFACT_INTENT
- RUNE.NOCTIS.YGGDRASIL.BRIDGE
- RUNE.NOCTIS.PROJECTION

This skill uses registered runes. It does not manage the registry.

## Boundaries (Hard)

- **Privacy**: Raw private text stays isolated; prefer compressed motif packets.
- **Medical/Therapy**: Explicitly disabled. Output framing is symbolic/reflective only.
- **Memory**: MemoryWriteCandidate only. `direct_write_allowed=false`, operator_review_required.
- **Oracle**: SHADOW annotations only (no raw private narrative, no forecast weights).
- **Forecast**: Never. Outputs limited to PROBE_READY / CANDIDATE_ONLY / OBSERVE_ONLY.
- **YGGDRASIL / Canon**: Candidate-only. No direct mutation.

## Core Stages (thin adapters over current surfaces)

1. Normalization — preserve raw exactly + deterministic whitespace/ID/seed.
2. Motif Extraction — evidence from text; stable IDs via sha256(dream_id + type + label).
3. Continuity — explicit prior records only.
4. Artifact Intent — candidate_only, operator_review_required.
5. Projection — display-only controls.

## Validation Routing

Primary: CLASS.REGISTRY_OR_MANIFEST, CLASS.JSON_SCHEMA, CLASS.PYTHON_LIBRARY, CLASS.RUNNER_OR_CLI, CLASS.ADVISORY_JSON_GENERATOR.

Targeted only:
- py_compile
- direct runner on synthetic fixtures
- JSON parse + schema validation
- authority/privacy/forecast boundary scans
- targeted pytest

Full-suite: NOT_RUN_NOT_REQUIRED (BLOCKED_BY_PRE_EXISTING_BASELINE).

## Prohibited

- Inventing dream content or history
- Medical/diagnostic/predictive claims
- Direct YGGDRASIL/durable memory writes
- Routing raw private dreams to public/forecast surfaces
- Creating a parallel dream engine
- Claiming validation without executing paths
- Weakening boundaries for green receipts

## Output Contract (Delivery)

```yaml
mode: ...
dream_id: ...
source: ...
privacy_tier: ...
artifacts:
  dream_packet_ref: ...
  analysis_ref: ...
  ...
registers:
  observed: []
  inferred: []
  speculative: []
  not_computable: []
authority:
  lane: SHADOW_SYMBOLIC
  non_governing: true
  memory_candidate_only: true
  forecast_authority: false
  ...
provenance: ...
status:
  analysis_status: ...
  validation_status: ...
```

## References

- `references/dream_input_contract.md`
- `references/noctis_boundaries.md`
- `references/runes_integration.md`
- `references/pipeline_contract.md`
- `references/validation_receipt_template.md`
- `abx-runes-yggdrasil-manager` (for rune/route governance)
- `abx-familiar-signal-forager` + `abraxas-ingest` (for source acquisition/normalization)
- `abraxas-validation-routing` (full appendix + Ingest amendment)

---

**Integration note (per larger flows):**

After repo-intel and before heavy Signal Forager or new capability work on dream material:
1. Apply `abx-runes-yggdrasil-manager` to resolve dream runes/routes.
2. Use this skill for governed NOCTIS processing.
3. Route external/legacy dream sources through Abraxas Ingest + FAMILIAR first.
4. Emit full receipts and respect all boundaries.

This is a sibling skill in the governed SHADOW symbolic stack.