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
