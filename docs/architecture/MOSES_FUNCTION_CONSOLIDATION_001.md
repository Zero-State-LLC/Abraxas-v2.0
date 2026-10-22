# Abraxas Moses Function — Consolidation Contract

**Status:** SHADOW / specification-first  
**Intent:** Extend and fuse existing Abraxas architecture. Do not create a parallel engine.

## Mission

Abraxas is the governed transformation boundary between sufficiently resolved meaning and executable structure.

```text
ZERO → SIGNAL → MEANING → ABRAXAS/MOSES → ARCHITECTURE → INSTITUTION → EVIDENCE → ZERO′
```

The Moses function MUST preserve provenance and declared semantic invariants while lowering meaning through explicit intermediate representations. It MUST NOT silently invent, delete, or materially alter upstream meaning.

## Canonical four-artifact spine

1. **MeaningPacket** — canonical interpretation handoff.
2. **GroundingReceipt** — evidence/anomaly gate over the MeaningPacket.
3. **ArchitecturePacket** — governed lowering into executable structure.
4. **OutcomeReceipt** — observed outcome and settlement evidence returned to ingest.

These are contracts and composition surfaces over existing modules. They are not new intelligence subsystems.

## Functional ownership

### Interpretation
Extend existing **Ingest → Evidence → BeliefGraph → Oracle** spine.

Sibling specialists may contribute through adapters:
- Semion: symbolic/semiotic representation.
- Hyperlex: semantic representation/transformation.
- Noesis: semantic-invariance evidence.

All contributions converge into one MeaningPacket. No sibling becomes a second product kernel.

### Grounding
Fuse outputs, not authority:
- **Trutina/Brier evidence** supplies grounding/calibration evidence.
- **SHADOW** supplies anomaly/drift observations only.

SHADOW MUST NOT gain decision or FORECAST authority.

Grounding states:
- `RESOLVED`
- `PROVISIONAL`
- `CONTRADICTED`
- `NOT_COMPUTABLE`

Only policy-permitted states may enter architectural lowering.

### Formalization / Moses compile
Extend **ABX runes + Yggdrasil topology + existing workflow/spec doctrine**.

Canonical lowering chain:

```text
MeaningPacket
→ DomainIR
→ RequirementsIR
→ JourneyIR
→ WorkflowIR
→ StateTransitionIR
→ ContractIR
→ Data/Governance/ArchitectureIR
→ AcceptanceIR
→ ImplementationIR
→ ArchitecturePacket
```

Behavioral invariant:

```text
Journey → Workflow → State Transition → Contract → Acceptance Test → Implementation Task
```

Every lowering step MUST emit provenance and semantic-preservation evidence or fail closed.

### Verification / settlement
Extend existing **FORECAST + outcome_brier/Trutina + settlement + provenance**.

ArchitecturePacket declares expected observable outcomes before institutional execution. Observed outcomes return as OutcomeReceipt and re-enter ingest as evidence. Technical, empirical, and economic settlement remain independent.

## Core invariants

**MF-INV-001 — Semantic preservation**  
No downstream representation may silently introduce, delete, or materially alter upstream meaning.

**MF-INV-002 — Explicit transformation**  
Every material semantic change is represented in a receipt with source, reason, confidence, and operator/policy authority.

**MF-INV-003 — Fail closed**  
Insufficient or contradictory signal returns `NOT_COMPUTABLE`; architectural specificity MUST NOT exceed evidentiary specificity.

**MF-INV-004 — Provenance continuity**  
Every ArchitecturePacket MUST trace to the MeaningPacket and GroundingReceipt that authorized its derivation.

**MF-INV-005 — Lane isolation**  
SHADOW detects anomaly/drift only. FORECAST performs evidence-based inference only. No implicit escalation is permitted.

**MF-INV-006 — No new kernel**  
Implementation MUST extend existing Oracle, BeliefGraph, Yggdrasil, rune, forecast, settlement, canonical serialization, and artifact-repository surfaces before any new subsystem is considered.

**MF-INV-007 — Evidence recursion**  
OutcomeReceipt is evidence, not automatic truth or canon. It re-enters the existing evidence pipeline.

## Minimal contract shapes

### MeaningPacket
Required semantic fields:
- `meaning_id`
- `observations[]`
- `interpretations[]`
- `semantic_invariants[]`
- `contradictions[]`
- `uncertainty[]`
- `provenance[]`
- `status`
- `canonical_hash`

### GroundingReceipt
- `meaning_id`
- `evidence_refs[]`
- `shadow_findings[]`
- `grounding_disposition`
- `unresolved[]`
- `provenance[]`
- `canonical_hash`

### ArchitecturePacket
- `architecture_id`
- `meaning_id`
- `grounding_receipt_id`
- `semantic_invariants[]`
- `lowering_trace[]`
- `domain`
- `requirements[]`
- `journeys[]`
- `workflows[]`
- `state_transitions[]`
- `contracts[]`
- `acceptance_tests[]`
- `implementation_tasks[]`
- `unresolved[]`
- `provenance[]`
- `canonical_hash`

### OutcomeReceipt
- `architecture_id`
- `expected_outcomes[]`
- `observed_outcomes[]`
- `settlements`
- `deviations[]`
- `evidence_refs[]`
- `provenance[]`
- `canonical_hash`

## Workflow

### WF-MF-001 — Meaning to architecture

**Trigger:** a MeaningPacket is submitted for formalization.

**Preconditions:** schema-valid packet; provenance resolvable; activation lane known.

**Deterministic path:**
1. Validate MeaningPacket.
2. Run grounding composition using existing evidence + SHADOW surfaces.
3. If disposition is CONTRADICTED or NOT_COMPUTABLE, stop and emit GroundingReceipt.
4. Preserve declared semantic invariants.
5. Lower through the canonical IR sequence.
6. Validate every generated contract/state transition against upstream requirements.
7. Generate acceptance tests before implementation tasks.
8. Emit ArchitecturePacket and canonical hash.
9. Register expected outcomes for FORECAST/settlement.

**Failure:** any provenance break, unsupported semantic mutation, unresolved contradiction, or invalid lowering fails closed.

**Terminal states:** `ARCHITECTURE_READY`, `PROVISIONAL`, `CONTRADICTED`, `NOT_COMPUTABLE`.

## Acceptance criteria

- Same canonical inputs produce byte-equivalent canonical artifacts.
- Every ArchitecturePacket requirement traces to at least one MeaningPacket interpretation/observation.
- Every implementation task traces backward through acceptance test → contract → state transition → workflow → journey → requirement.
- Removing an upstream semantic invariant causes verification to fail if a downstream artifact still depends on it.
- SHADOW findings cannot independently authorize lowering.
- A NOT_COMPUTABLE GroundingReceipt cannot produce an ArchitecturePacket.
- OutcomeReceipt cannot self-promote evidence to canon.
- Existing product spine remains valid; no parallel runtime kernel is introduced.

## Consolidation map

| Existing surface | Moses role | Action |
|---|---|---|
| Ingest / Evidence / BeliefGraph / Oracle | interpretation substrate | EXTEND |
| Semion / Hyperlex / Noesis | representation + invariance specialists | ADAPT/FUSE AT CONTRACT |
| Trutina / outcome_brier | grounding + calibration | EXTEND |
| SHADOW | anomaly/drift detection | PRESERVE AUTHORITY BOUNDARY |
| ABX runes | deterministic lowering functions | EXTEND |
| Yggdrasil | dependency/topology routing | EXTEND |
| FORECAST | expected-outcome inference | EXTEND |
| Settlement / provenance | observed evidence + receipts | EXTEND |
| Alembic | optional specialist routing | REUSE; DO NOT ELEVATE |
| New Moses/Meaning/Intent engine | duplicate kernel | DO NOT CREATE |

## Implementation sequence

1. Contract-only: add schemas for the four spine artifacts using existing canonical conventions.
2. Adapter-only: map existing Oracle/BeliefGraph output into MeaningPacket without changing Oracle authority.
3. Composition-only: produce GroundingReceipt from existing evidence/Trutina + SHADOW outputs.
4. Extend runes/Yggdrasil for deterministic IR lowering.
5. Add traceability verifier and semantic-invariant verifier.
6. Bind ArchitecturePacket acceptance conditions to FORECAST.
7. Emit OutcomeReceipt through existing settlement/provenance surfaces.
8. Replay/golden tests across the full loop.
9. Only after evidence exists, consider any authority promotion.

## Non-goals

- No autonomous canon promotion.
- No SHADOW→FORECAST escalation.
- No replacement of the existing supported product spine.
- No new model merely to implement this doctrine.
- No direct business/institutional execution authority.
- No claim that representation proves causal instantiation.
