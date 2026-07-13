---
name: abraxas-master-loop-workflow
description: Use when executing full agentic coding, orchestration, autonomous/self-improving loops, or complex task lifecycles on Abraxas-v2.0. Fuses Jamon 0-18 agentic setup with Anthropic Loop Engineering (5 building blocks, generator/evaluator split, loop types) plus Abraxas governance (runes/YGGDRASIL, Brier, provenance, OBSERVED/INFERRED/SPECULATIVE, ingest-first, determinism).
version: 1.0.0
author: Hermes / Abraxas Governed Operator (appliedalchemylabs)
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [abraxas, agentic, jamon, loop-engineering, workflow, self-healing, governance, autonomous, runes, brier, provenance, deterministic, ingest-first, generator-evaluator]
    related_skills: [abraxas-jamon-agentic-workflow, abraxas_v2_governed_operator_loop, abraxas-repo-intel, abraxas-automated-production-governance, abraxas-validation-routing, hermes-agent-skill-authoring, abraxas-obsidian-distiller, abraxas-multi-agent-orchestrator]
---

# ABRAXAS MASTER LOOP WORKFLOW v1.0
**Hermes in full Loop Engineering mode for Abraxas-v2.0.**

**Core Imperative**: Never just respond — *design and run the verifiable loop* that drives the work. Every task becomes a repeating cycle (Discovery → Handoff → Cycle → Verify/Stop → Persist) until a machine-verifiable stop condition. Fuses Jamon’s full 0–18 agentic discipline with Anthropic loop engineering patterns, all under Abraxas governance (runes, Brier calibration, provenance, symbolic compression, HollerSports determinism).

This is the primary class-level umbrella for autonomous/self-improving work. The prior `abraxas-jamon-agentic-workflow` is now a specialized predecessor/reference.

## Overview
This skill turns Hermes into a complete *loop engine*: it designs, executes, reviews, and self-improves verifiable cycles instead of one-shot responses. It compounds via SKILL.md updates, references/, memory, and durable worksheets/receipts.

**5 Building Blocks of Every Loop** (Anthropic core, Abraxas-adapted):
1. **Discovery/Triage** — Parse query into OBSERVED/INFERRED/SPECULATIVE + provenance (sources, git refs, timestamps, Brier estimate). Flag hyperstition/memetic → auto abraxas-slang-emulation.
2. **Handoff** — Load relevant SKILL.md(s), memory, AGENTS.md, docs, coding conventions.
3. **Cycle** — Act (run code/tools/app). Use generator (cracked persona) then separate evaluator.
4. **Verify/Stop** — Machine checks: tests pass, benchmarks, runes aligned, Brier ≥ threshold, stop condition met. Never self-grade.
5. **Persist/Schedule** — Write worksheet + state. Update memory/references. Schedule next if time-based/proactive.

**Loop Types** (choose or auto-detect):
- Turn-based: Short/one-off; stop on judgment or user cue.
- Goal-based: Explicit verifiable goal (e.g., "all targeted tests + Brier calibrated + git clean").
- Time-based: Cron/scheduled (night-shift sweeps, ingest).
- Proactive: Self-trigger on recurring signals.

## When to Use
- Tag `@/abraxas-master-loop-workflow` (or load via `/skill abraxas-master-loop-workflow`) at session start for any non-trivial Abraxas work.
- Full lifecycles: features, autonomous campaigns, skill evolution, forecasting, night-shift, complex orchestration.
- When the task benefits from repeatable, verifiable cycles rather than one-shot execution.
- Cross-persona reviews, sweeps, meta-audits.

**Do not use for**:
- Trivial lookups (use direct tools or narrower skills).
- Pure SHADOW analysis without execution intent (use repo-intel + governed loop).
- When user explicitly says "override workflow" or "one-shot only".

## 1. Router & Foundations (Jamon Point 0 + Loop Discovery)
**Mandatory first action on every task.**

1. Load `@/AGENTS.md` (master router). Read mandatory pre-change docs (README.md, PLANS.md, GOVERNANCE_V3.md).
2. Map MODE (Discover → Plan → Build → Review → Loop → Forecast/Ingest), architecture, personas (hermes-cracked-python-engineer for generation, senior-python-architect for evaluation/orchestration).
3. Emit initial OBSERVED/INFERRED/SPECULATIVE + provenance + Brier estimate.
4. Choose/detect loop type and building-block sequence.
5. Load this skill + related (jamon predecessor, governed loop, etc.).

**Completion criterion**: Router state + evidence packet logged. No edits until explicit.

## 2. Full Agentic Execution (Jamon 1–18 + Loop Enhancements)
Execute per cycle:

1. **Intake + Discovery** — OBSERVED/INFERRED/SPECULATIVE with full provenance.
2. **Research/Plan** — Use repo-intel, obsidian-distiller, etc. Surface ≥2 paths (conventional vs cracked). Trade-offs table (maintainability, performance, observability, symbolic coherence, Brier risk, rune alignment).
3. **Implementation (Cycle block)** — Always run app/code yourself (terminal, python, pytest, rtk). Write targeted tests during build. Use `abraxas-validation-routing` (narrowest first). Scrubbed env for Python: `env -i PATH="$PATH" ... uv run python -m pytest ...`.
4. **Self-Healing Docs** — Update every touched file; keep first 7 lines rich. Prefer patch on umbrellas + references/ for detail.
5. **Tests, Linting, Benchmarks** — Targeted + `python scripts/run_fast_ci.py` before PR actions. Pre-commit with --fix. Visual regression/performance when surfaces change.
6. **Cross-Review (Generator → Evaluator)** — Cracked (visionary) generation then senior/Doubt-First Auditor evaluation. Checklists: security, AI smells, runes/governance, maintainability, false-confidence, hyperstition risk. Never self-grade.
7. **Trace & Commit** — Worksheet in out/ (git-tagged). Conventional commits.
8. **Autonomous Loop** — On "continue", "keep going", etc.: continue without further input until stop condition or hard escalation. Force comprehensive phased TODO on continuation cues. Night-shift prep during day.
9. **Sweeps & Audits** — Periodic commit scans, false-confidence audits, skill drift checks.
10. **Feedback & Persist** — Append to FEEDBACK.md or equivalent. Update memory/references. Schedule next cycle if applicable.
11. **End-of-Shift / Stop** — Full validations, Brier calibration, rune alignment. Emit structured JSON receipt.

**Loop Controls**:
- Iteration caps + no-progress detection.
- Generator/Evaluator split.
- Token management: choose model/effort; reduce via strong verification.
- Failure modes: infinite loop → caps; hallucination → separate eval + tests; cost overrun → partial outputs + escalate.

## 3. Abraxas-Specific Layers (Non-Negotiable)
- **Structured Output** (end of every cycle or major step):
  ```json
  {
    "OBSERVED": [...],
    "INFERRED": [...],
    "SPECULATIVE": [...],
    "PROVENANCE": { "sources": [], "brier": 0.XX, "git_ref": "" },
    "LOOP_STATE": { "cycles": N, "stop_condition_met": true/false, "loop_type": "goal-based" },
    "NEXT_ACTION": "persist | schedule | escalate"
  }
  ```
- **Verification Block** (mandatory before "DONE"):
  - [ ] Targeted tests + linter + fast CI (scrubbed) pass for touched surfaces.
  - [ ] Evaluator (different persona) approved.
  - [ ] Docs/skills/memory/references updated with provenance.
  - [ ] Worksheet/receipt emitted + git tag.
  - [ ] Brier calibration recorded.
  - [ ] Rune/governance/YGGDRASIL alignment confirmed.
  - [ ] OBSERVED/INFERRED/SPECULATIVE + full provenance present.
  - [ ] No fabricated evidence; ingest-first followed.
- **Symbolic/Rune Layer**: Bind via abx-runes-yggdrasil-manager / unbound-rune-analyzer. Flag hyperstition.
- **Determinism & Observability**: Preserve canonical_hash, deterministic serialization. Cite tools/docs. No hallucinations.
- **Ingest-First Evidence**: Apply before baseline claims when context incomplete.
- **Safety/Escalation**: Least-privilege. Confirm mutations. Fail-closed on canon/git/canary/runtime authority. Never touch secrets.
- **Edge Cases**:
  - Underspecified → Probe + prototype IR/schema (document as SPECULATIVE).
  - High-uncertainty → Dual paths + Brier audit.
  - Loop drift → Evaluator forces reset + skill patch.

## 4. Activation & Autonomy Rules
- **Session start**: "Activate abraxas-master-loop-workflow. Task: [input]."
- **Autonomous**: Continue cycles on "continue"/"keep going" until verifiable stop or escalation (worksheet handoff).
- **Periodic Meta-Loop**: Every 7 days or major batch → full agentic audit/sweep.
- **Learning Close**: If cycle ≥5 steps or novel technique: "Save/update skill" with verification block. Patch umbrellas + references/.

**Verification Receipt Template** (append to every cycle close):
- Tests run & passed?
- Evaluator approved?
- Docs/memory updated?
- Worksheet committed + tag?
- Brier/rune alignment?
- New skill/ref saved?

## Common Pitfalls
- Skipping AGENTS.md router or mandatory pre-change reads.
- Claiming "verified" without scrubbed checks + explicit blocker explanation for collection noise.
- Self-grading (no generator/evaluator split).
- Treating historical out/ as live authority.
- Broad full-suite runs instead of narrowest validation.
- Duplicating logic instead of patching class-level umbrellas.
- Ignoring cross-platform casing (prefer lowercase `scripts.*`).
- Infinite loops without caps or no-progress detection.
- Fabricating data, wall-clock, UUIDs in deterministic surfaces.

## References & Related
- Predecessor: `abraxas-jamon-agentic-workflow` (Jamon 0-18 core; now specialized)
- Core: `abraxas_v2_governed_operator_loop` (7-phase)
- Supporting: `abraxas-repo-intel`, `abraxas-automated-production-governance`, `abraxas-validation-routing`, `abraxas_unbound_rune_analyzer`, `abx-runes-yggdrasil-manager`
- Authoring: `hermes-agent-skill-authoring`
- AGENTS.md, GOVERNANCE_V3.md, README.md, PLANS.md
- `references/loop-building-blocks.md` (detailed 5 blocks + Anthropic patterns)
- `references/loop-types-and-controls.md`
- `references/generator-evaluator-split.md`

**Status**: Active primary class-level umbrella. Prefer this for new autonomous work. Curator target for consolidation with governed loop.

**Next evolution signals**: New non-trivial loop pattern, user correction, successful long-running campaign closure → immediate patch + verification.

See `references/jamon-to-master-evolution.md` for migration notes from the predecessor skill.