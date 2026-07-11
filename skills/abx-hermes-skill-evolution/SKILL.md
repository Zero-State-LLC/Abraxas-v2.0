---
name: abx-hermes-skill-evolution
description: "Observes Abraxas operations, aggregates skill-performance evidence, detects recurring failure or inefficiency patterns, and generates versioned candidate skill patches for replay, canary evaluation, and operator-approved promotion. Never mutates active skills directly. Produces SkillEvolutionCandidate and SkillPatchCandidate artifacts only."
version: 0.1.0
author: Abraxas Governed Operator
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [abraxas, hermes, skill-evolution, operation-trace, performance-ledger, replay, canary, promotion-gate, abraxas-ingest]
    related_skills: [abx-familiar-signal-forager, abraxas-repo-intel, abraxas-validation-routing, abraxas-automated-production-governance, abx-runes-yggdrasil-manager]
---
# ABX-HERMES SKILL EVOLUTION

## Purpose
Observe Abraxas operations, normalize to OperationTrace, aggregate into SkillPerformanceLedger, detect evolution signals, propose bounded SkillPatchCandidate artifacts. Route through Abraxas Ingest, replay harness, canary, and promotion gate. Preserve determinism, provenance, and the strict boundary: operations generate candidates; only operator/governance authorizes promotion to active skills.

## Core Boundary
operations may generate skill candidates
operations may not directly rewrite active skills

## OperationTrace (input contract)
See proposal: operation_id, skill_id, task_class, repo_commit, inputs_hash, plan_hash, commands_run, outputs, validation_results, evidence_status, completion_status, operator_interventions, token_usage, elapsed_time, failure_signatures, brier_score.

## Flow
1. Ingest OperationTrace via Abraxas Ingest or direct.
2. Update SkillPerformanceLedger (keyed by skill_id + version + task_class).
3. Run abx-skill-evolution-analyzer: detect recurring patterns (operator corrections, false completions, token spikes, NOT_COMPUTABLE, drift).
4. Emit SkillEvolutionCandidate.
5. Generate SkillPatchCandidate (diff-style, minimal, with rollback_plan).
6. Replay harness: compare old vs candidate on historical set (success/failure/corrected/edge/NOT_COMPUTABLE).
7. Canary: parallel shadow run, advisory only, record deltas.
8. Promotion gate: evidence_count >= threshold, regressions==0, brier_delta <= target, operator_approval==true.

## Rune / YGGDRASIL Routes (planned)
operation_to_skill_evidence
skill_evidence_to_candidate_patch
candidate_patch_to_replay
replay_to_canary
canary_to_operator_review
No direct route from operation trace to active skill mutation.

## Memory Boundary
SkillMemoryCandidate only (durable_write_authorized=false until promotion).

## Completion Rule for Promotion
evidence_count >= minimum_threshold AND replay_regressions == 0 AND brier_delta <= target AND false_completion_delta <= 0 AND token_delta within budget AND authority_scan == PASS AND operator_approval == true

## Status
CANDIDATE / SHADOW. No production mutation authority.

## v2.2 — First Replayable Skill-Evolution Cycle (Implemented)

- Frozen replay corpus (7 cases) with schema + provenance
- Real deterministic replay comparator (no regressions on candidate)
- Isolated candidate patch applier (shadow workspace only, active untouched)
- SHADOW canary comparator (active authoritative, 0 authority violations)
- Promotion eligibility gate (CANARY_ELIGIBLE requires replay=0, canary runs >=5, operator approval)
- Targeted tests (9 tests across replay, canary, promotion, authority, determinism, candidate patch)
- Live runner: scripts/run_abx_hermes_skill_evolution_cycle.py
- Full cycle receipt emitted with invariants: active_skill_modified=false, candidate_promoted=false

**Gate Status (v2.2)**
REPLAY_CORPUS: FROZEN (7)
REPLAY_ENGINE: IMPLEMENTED (regressions=0)
CANARY_MODE: SHADOW_ONLY
PROMOTION: OPERATOR_REVIEW_REQUIRED

Last updated: 2026-07-11T07:08:18.568222+00:00


## v2.3 — Live Training Signal Emission & Continuous Evaluation Pipeline (Implemented)

- Live OperationTrace emitter: scripts/abx_hermes_live_operation_trace_emitter.py
- Runner integrated with live emitter + dynamic signal (v2_3)
- Live traces: 6+ from recent audit artifacts
- Operator review simulation layer
- Cycle 003_LIVE with live_traces_count
- Invariants: active untouched, 0 regressions, CANARY_ELIGIBLE

**Gate Status (v2.3)**
LIVE_EMITTER: IMPLEMENTED
DYNAMIC_TRACES: 6
OPERATOR_REVIEW_SIM: IMPLEMENTED
CONTINUOUS: RUNNABLE
PROMOTION: OPERATOR_REVIEW_REQUIRED

Last updated: 2026-07-11T07:30:08.215510+00:00



## v2.3 — Promotion Readiness Assessment (Completed)

- New `abx_skill_promotion_readiness_assessor.py` (advisory only)
- Aggregates replay, canary, cycle, live traces
- Applies local advisory thresholds (min 7 live traces, 1.0 agreement, 0 regressions, active untouched)
- Produces `abx_hermes_skill_evolution_promotion_readiness_v2_3.latest.json`
- Decision on verified run: EXTENDED_CANARY_READY
- Authority: advisory_only, no production activation, no active replacement
- Anomalies logged (e.g. LOW_SAMPLE_SIZE)
- Deterministic hash + stable replay
- Integrated into cycle runner
- 5 new targeted tests + original 9 continue to pass

**Gate Status (v2.3)**
LIVE_TRACES: 7+
AGREEMENT: 1.0
REGRESSIONS: 0
ACTIVE_UNTOUCHED: true
DECISION: EXTENDED_CANARY_READY
OPERATOR_REVIEW: REQUIRED

Last updated: 2026-07-11T07:47:11.842737+00:00

## v2.4 — Extended Shadow Observation & Live Corpus Expansion (5-PHASE COMPLETE)

- Phase 1: Live corpus expander (`abx_skill_live_corpus_expander.py`) — ADDITIVE_LIVE_ONLY, 11 cases
- Phase 2: Deep wiring of readiness + expanded corpus into cycle receipts
- Phase 3: Live Brier/performance ledger (`abx_skill_live_brier_ledger.py`)
- Phase 4: Formal extended canary observer (`abx_skill_extended_canary_observer.py`)
- Phase 5: Full scrubbed verification + SKILL.md + receipts

**Cycle**: ABX_HERMES_EVOLUTION_CYCLE_004_LIVE_V2_4
**Key outputs**:
- abx_hermes_skill_evolution_promotion_readiness_v2_3.latest.json → EXTENDED_CANARY_READY
- abx_hermes_live_expanded_corpus_v2_4.latest.json
- abx_hermes_live_brier_ledger_v2_4.latest.json
- abx_hermes_extended_canary_observation_v2_4.latest.json (EXTENDED_OBSERVATION_READY)
**Invariants**: active_skill_modified=False, candidate_promoted=False, SHADOW_ONLY, refs=3, 0 regressions, agreement 1.0
**Pytest**: 14/14 PASS (scrubbed)

**Gate Status (v2.4 COMPLETE)**
EXPANDED_CORPUS: 11 cases (ADDITIVE)
BRIER_LEDGER: IMPLEMENTED
EXTENDED_CANARY: IMPLEMENTED
PROMOTION: OPERATOR_REVIEW_REQUIRED (unchanged)

Last updated: 2026-07-11T13:38:37.335234+00:00

- Phase 1: Live corpus expander (`abx_skill_live_corpus_expander.py`) — 9 cases, ADDITIVE_LIVE_ONLY
- Phase 2: Deep wiring of readiness decision + expanded corpus into cycle receipts
- Phase 3: Live Brier/performance ledger (`abx_skill_live_brier_ledger.py`)
- Phase 4: Formal extended canary observer (`abx_skill_extended_canary_observer.py`)
- Phase 5: Full verification + SKILL.md + receipt

**Cycle 004**: ABX_HERMES_EVOLUTION_CYCLE_004_LIVE_V2_4
**Invariants**: active_skill_modified=False, candidate_promoted=False, SHADOW_ONLY, refs=3

**Gate Status (v2.4)**
EXPANDED_CORPUS: 9 cases (ADDITIVE)
BRIER_LEDGER: IMPLEMENTED (advisory)
EXTENDED_CANARY: IMPLEMENTED
PROMOTION: STILL OPERATOR_REVIEW_REQUIRED

Last updated: 2026-07-11T13:35:41.079507+00:00

## v2.5 — Governance Integration & Recurring Lane Activation (In Progress)

- Phase 1: Governance lane wiring (abx_hermes_extended_shadow_v2_4 in NEXT_RECOMMENDED_LANES)
- Phase 2: Recurring lane recommendation emission
- Phase 3: Cross-surface signal ingestion (holler/oracle/slang) + formal operator review decision record
- Phase 4: SKILL.md v2.5 section
- Phase 5: Full scrubbed verification + V2_5 receipt + continuation-audit close

**Invariants**: active_skill_modified=False, refs=3, SHADOW_ONLY

Last updated: 2026-07-11T13:42:49.737215+00:00

## v2.6 — Formal Operator Review Packet (FORMAL_OPERATOR_REVIEW_PACKET_READY)

- Packet generator: abx_skill_formal_operator_review_packet.py
- Consumes v2.5 formal operator review record (formal-op-review-v2.5-13)
- Reconciles upstream artifacts (cycle, replay, canary, brier, expanded, readiness)
- Cross-surface signals resolved where possible or marked SOURCE_UNRESOLVED
- Explicit states: FORMAL_OPERATOR_REVIEW_PACKET_READY (or BLOCKED_*/MORE_EVIDENCE/NOT_COMPUTABLE)
- Bounded operator decisions only (no APPROVE production, no promote/activate)
- SHADOW anomalies only; FORECAST = packet ready for human review
- Deterministic hash; no operator decision synthesized
- No active skill mutation, refs stable at 3

**Key invariants preserved**: active_modified=false, operator_decision_present=false, promotion_authorized=false, production_activation_allowed=false

Last updated: 2026-07-11T13:48:11.874893+00:00

## v2.7 — Interactive Formal Operator Decision Intake Builder

- New module: `abx_skill_formal_operator_decision_builder.py`
- Two-stage: INTERACTIVE HUMAN PACKET BUILDER → INDEPENDENT INTAKE VALIDATOR
- Loads v2.6 review packet, derives machine fields automatically
- Collects 10 human-required fields **one at a time** with immediate validation
- Normalization for natural language decisions
- Working state: `out/operator_input/.working/abx_hermes_formal_operator_decision_v2_7.working.json` (INCOMPLETE_OPERATOR_INPUT)
- Completed only on explicit CONFIRM: `out/operator_input/abx_hermes_formal_operator_decision_v2_7.input.json`
- Non-interactive mode (cycle default): emits OPERATOR_INPUT_INCOMPLETE + next field, rc=0, no hang
- Interactive: `uv run python skills/abx-hermes-skill-evolution/abx_skill_formal_operator_decision_builder.py --interactive`
- Preserves original + normalized responses + provenance
- Explicit states: FORMAL_OPERATOR_DECISION_INTAKE_READY, COLLECTING..., OPERATOR_CONFIRMATION_REQUIRED, OPERATOR_DECISION_RECORD_BUILT, BLOCKED_BY_PACKET_DRIFT, etc.
- No promotion/activation/mutation ever

**Entry for humans (interactive):**
uv run python skills/abx-hermes-skill-evolution/abx_skill_formal_operator_decision_builder.py --interactive

Last updated: 2026-07-11T14:06:21.333993+00:00

## v2.8 — Independent Decision Intake Validator (End-to-End Closure)

- New module: abx_skill_formal_operator_decision_validator.py
- Independent validation of builder output (no trust)
- Checks: review binding (id + hash), decision in allowed set, all 6 acks explicitly true, operator identity present, authority boundaries all false
- Emits: abx_hermes_formal_operator_decision_validation_v2_8.latest.json
- States: VALIDATED | BLOCKED_BY_VALIDATION_ERRORS | NOT_COMPUTABLE
- Wired into cycle after builder
- Non-interactive safe, advisory only
- Existing 34 targeted tests pass

Cycle now runs: emitter → replay/canary/... → builder (non-int) → validator

Last updated: 2026-07-11T14:11:50.207953+00:00

## v2.9 — Decision-Aware Promotion Eligibility + Traceable Decision Ledger (in progress)

- New module: abx_skill_formal_operator_decision_ledger.py
- Consumes validated decision + review packet → emits traceable ledger
- Readiness assessor updated to load ledger and record operator_decision_* evidence
- Cycle wired: ... → validator → ledger
- Decision now flows into promotion surfaces (advisory only)
- Current run: VALIDATED + ledger emitted + EXTENDED_CANARY_READY preserved

Last updated: 2026-07-11T14:16:40.131927+00:00

## Unattended Continuation (v2.9 morning errands window)

See: `out/UNATTENDED_CONTINUATION_PLAN_v2.9.md`

Runner: `scripts/run_unattended_abx_continuation.py`
- 8 cycles, 20 min sleep
- Fully scrubbed env
- Emits unattended_cycle_*.json receipts
- Stops on refs != 3 or active_modified == True

Launch before leaving:
nohup env -i PATH="$PATH" HOME="$HOME" USER="$USER" UV_CACHE_DIR="$HOME/.cache/uv" \
  uv run python scripts/run_unattended_abx_continuation.py \
  > logs/unattended_$(date +%Y%m%d_%H%M).log 2>&1 &

Monitor: tail -f logs/unattended_*.log

Handoff receipt: out/audit/UNATTENDED_HANDOFF_v2.9.json

## v2.9 Update (continuation)
- Ledger consumption wired into promotion readiness assessor (positive decision flag for APPROVE)
- Dedicated tests added (test_abx_skill_evolution_decision_ledger.py: 3 tests, all pass)
- Unattended runner active (8-cycle plan, 20min interval)
- All cycles preserve refs=3, active_modified=False
- Receipts: V2_9_PROGRESS.json, UNATTENDED_HANDOFF, PRE_UNATTENDED_AUDIT
Last: 2026-07-11T18:24:30.534752+00:00

## v2.9 5-PHASE WORKSTREAM COMPLETE + UNATTENDED HANDOFF (2026-07-11)
- Decision ledger fully consumed in readiness assessor and promotion gate
- Operator decision (APPROVE_EXTENDED_OBSERVATION + VALIDATED) reinforces CANARY_ELIGIBLE (advisory only)
- New tests: tests/test_abx_skill_evolution_decision_ledger.py (3 tests, happy path + invariants)
- Full suite: 35/35 PASS under scrubbed env
- Unattended runner + plan delivered and verified
- All invariants held: Refs=3, active_modified=False, rc=0
- Next: v2.10 Operator Decision Brier Integration + Cross-Surface + Promotion Simulation
Receipts: V2_9_5_PHASE_COMPLETE.json, NEXT_CONTINUATION_AUDIT_V2_9_COMPLETE.json
TODO LIST FULLY COMPLETE for this segment.
