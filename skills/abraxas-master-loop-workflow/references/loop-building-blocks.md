# 5 Building Blocks of Every Loop (Abraxas-Adapted)

## 1. Discovery/Triage
- Parse user query.
- Emit OBSERVED (direct from tools/files), INFERRED (logically derived), SPECULATIVE (forward projection with Brier).
- Full provenance: sources, git refs, timestamps.
- Flag hyperstition/memetic signals → trigger abraxas-slang-emulation.
- Choose/detect loop type.

**Completion**: Structured packet logged. No action until complete.

## 2. Handoff
- Load this skill + predecessor (jamon), AGENTS.md, mandatory docs, relevant SKILL.md(s), memory, conventions.
- Use smallest complete evidence packet (repo-intel).

**Completion**: All required context loaded and cited.

## 3. Cycle (Act)
- Generator phase (hermes-cracked-python-engineer persona): implement, run code/tools.
- Always execute yourself (terminal, pytest scrubbed, rtk).
- Write targeted tests during build.
- Use narrowest validation (`abraxas-validation-routing`).

**Completion**: Action performed + immediate results captured.

## 4. Verify/Stop
- Separate Evaluator phase (senior-python-architect or "Doubt-First Auditor" — assume failure until proven).
- Machine-verifiable checks:
  - Targeted tests + linter + fast CI pass (scrubbed).
  - Benchmarks stable.
  - Rune/governance alignment.
  - Brier ≥ threshold (where applicable).
  - Stop condition explicitly met.
- Never self-grade.

**Completion**: Evaluator sign-off or explicit failure + next action.

## 5. Persist/Schedule
- Write worksheet/receipt in out/ (git-tagged).
- Update SKILL.md/references/memory.
- Schedule next cycle if time-based or proactive.
- Emit structured JSON (OBSERVED/INFERRED/SPECULATIVE + LOOP_STATE + NEXT_ACTION).

**Completion**: Durable artifacts written + state persisted.