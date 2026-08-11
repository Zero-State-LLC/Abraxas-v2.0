---
name: abraxas-jamon-agentic-workflow
description: Historical Jamon workflow reference for Abraxas. Do not use as the default router. Current routing is AGENTS.md + SKILLS.md; use abraxas-master-loop-workflow only for autonomous multi-cycle loop work.
version: 1.0.0
author: Hermes / Abraxas Governed Operator (appliedalchemylabs)
license: Proprietary
platforms: [macos, linux]
metadata:
  status: SUPERSEDED
  default: false
  superseded_by: [abraxas-master-loop-workflow, AGENTS.md, SKILLS.md]
  hermes:
    tags: [abraxas, agentic, jamon, workflow, self-healing, governance, autonomous, runes, brier, provenance, deterministic, ingest-first]
    related_skills: [abraxas-jamon-agentic-workflow, abraxas_v2_governed_operator_loop, abraxas-repo-intel, abraxas-automated-production-governance, abraxas-validation-routing, hermes-agent-skill-authoring, abraxas-obsidian-distiller, abraxas-multi-agent-orchestrator, hermes-graph-of-loops, hermes-outcome-driven-improver, modular-synth-catalog-research]
---

# ABRAXAS JAMON AGENTIC WORKFLOW v1.0

**Status:** `SUPERSEDED` historical reference. Current default execution doctrine is
[`../../AGENTS.md`](../../AGENTS.md) and [`../../SKILLS.md`](../../SKILLS.md).
Do not route ordinary or non-trivial work through this skill merely because it
exists. Use `abraxas-master-loop-workflow` only for genuine autonomous multi-cycle
work.
**Hermes Operator Mode** – Activated for ALL Abraxas sessions unless explicitly overridden.

Fuses Jamon Holmgren’s 0–18 agentic points with Abraxas-v2.0 conventions: structured outputs, provenance tagging, Brier calibration, rune/governance bindings, symbolic compression, HollerSports determinism, hyperstition scanning, Governance V3, CLI Operator Layer (smallest complete evidence packet), and ingest-first evidence acquisition.

## Overview
This historical class-level umbrella captured an earlier autonomous workflow pattern. It no longer enforces the standard workflow for current tasks; use it only as provenance/reference when maintaining old Jamon-style loop material.

**Current interpretation:** Apply `AGENTS.md` and `SKILLS.md` first. Reuse details below only when they still help a specialist autonomous loop, and discard ceremony that is not required to prove the task contract.

## When to Use
- Do not load this skill at the start of an Abraxas session by default.
- Use only as historical reference for old Jamon workflow details, or use `abraxas-master-loop-workflow` for current autonomous loop work.
- Cross-persona reviews, sweeps, audits, end-of-shift validation.

**Do not use for:**
- Trivial one-off lookups (use direct tools or narrower skills).
- When user explicitly says "override workflow" or "skip agentic mode".
- Pure SHADOW-only analysis without execution intent (use repo-intel + governed loop directly).

## 1. ROUTER (AGENTS.md – Jamon Point 0)
**Historical pattern, not a current mandatory first action.**

1. Load `@/AGENTS.md` (master router).
2. Read (or confirm prior read of) mandatory pre-change docs:
   - `README.md`
   - `PLANS.md`
   - `GOVERNANCE_V3.md`
3. Map:
   - **MODE**: Discover → Plan → Build → Review → Bugfix → Loop → Forecast/Ingest
   - **ARCHITECTURE**: core/, out/audit/, scripts/, skills/, memory/, runes/, holler-sports/, contracts/
   - **PERSONAS**: hermes-cracked-python-engineer, senior-python-architect, abraxas-orchestrator
   - **TRIGGERS**: hyperstition/memetic → abraxas-slang-emulation; forecasting → Brier calibration; code → run + targeted tests (scrubbed env)
4. Use `abraxas-repo-intel` for smallest complete evidence packet before deep work.
5. Emit initial OBSERVED/INFERRED/SPECULATIVE + provenance (sources, git ref, timestamps).

**Completion criterion:** Router state + evidence packet logged. No edits until this is explicit.

## 2. STANDARD WORKFLOW (Jamon Points 1 + Abraxas)
Historical loop pattern; do not apply to every task. Current tasks should use the smallest `AGENTS.md` execution mode that proves the contract.

1. **Intake**
   Parse query. Output explicit:
   - OBSERVED (directly from tools/files)
   - INFERRED (logically derived with evidence)
   - SPECULATIVE (forward projection with Brier)
   Full provenance required.

2. **Research/Plan**
   Use `abraxas-obsidian-distiller`, `firecrawl-*`, arxiv, or repo-intel as needed.
   Surface ≥2 paths: Conventional vs Cracked/Experimental.
   Trade-offs table: maintainability, performance, observability, symbolic coherence, Brier risk, rune alignment.

3. **Implementation (Jamon Point 3)**
   Always run the app/code yourself (terminal, python, pytest, rtk, etc.).
   Write targeted tests **during** build (TDD preferred).
   Fix issues in-loop using `abraxas-validation-routing` (narrowest validation first).
   Use scrubbed env for Python verification:
   `env -i PATH="$PATH" HOME="$HOME" USER="$USER" UV_CACHE_DIR="$HOME/.cache/uv" uv run python -m pytest ...`

4. **Self-Healing Docs (Point 2)**
   Update every touched system doc. Keep first 7 lines as rich summary + YAML frontmatter where applicable (Obsidian style).
   Update SKILL.md (prefer patch on umbrella) and add to references/ for session detail.

5. **Tests & Linting (Points 4–5)**
   Targeted tests + `python scripts/run_fast_ci.py` before PR-related actions.
   Pre-commit linters with `--fix`.
   Visual regression / performance benchmarks when surfaces change.
   E2E where relevant; maintain TESTS.md list for touched areas.

6. **Cross-Review (Point 6)**
   Spawn review via different persona/model (use multi-agent-orchestrator or explicit steer).
   Checklists: security, AI smells, Abraxas runes/governance alignment, maintainability, false-confidence, hyperstition risk.

7. **Trace & Commit (Point 7)**
   Create worksheet in `out/worksheets/` or equivalent (git-tagged).
   Commit with changes + feedback summary. Prefer conventional commits.

8. **Autonomous Loop (Point 12)**
   On "continue", "keep going", "go ahead until complete", or equivalent (user-authorized): continue without further input until validation or hard escalation.
   Use TODO list (force comprehensive phased list on continuation cues).
   Night-shift prep specs during day; handoff via worksheet/receipt.

9. **Sweeps & Audits (Points 10, 14)**
   Periodic commit scans, false-confidence audits, skill drift checks (curator every ~15 tool calls or on signal).

10. **End-of-Shift (Point 18)**
    Full validations (targeted tests, benchmarks, cross-review).
    Agent feedback to FEEDBACK.md or equivalent.
    Brier calibration on any predictions/forecasts.

11. **Learning Close**
    If task ≥5 significant steps or non-trivial technique discovered: "Save this as new skill / patch umbrella" with verification block.
    Update MEMORY via memory tool or skill references/.
    Emit structured receipt (OBSERVED/INFERRED/SPECULATIVE + Brier where applicable).

## 3. ABRAXAS-SPECIFIC GUARDRAILS & ENHANCEMENTS
- **Structured Output**: Every actionable response ends with clear tiers + provenance. Tag Brier scores on forecasts. Use exact Obsidian YAML frontmatter for durable artifacts.
- **Symbolic / Rune Layer**: Bind changes to runes/governance via `abx-runes-yggdrasil-manager`. Flag hyperstition surfaces. Auto-trigger slang-emulation on memetic signals.
- **Determinism & Observability**: Preserve canonical_hash, deterministic serialization. Invariants, structured logging, explicit error handling. Cite tools/docs for every claim. No hallucinations.
- **Tool Use**: Prefer built-ins (bash/rtk, python REPL via execute_code or terminal, file ops, search). Create bin/ or skills/.../scripts/ for reusable reviews/scans/profilers (per Jamon Point 9).
- **Ingest-First Evidence**: Apply Abraxas Ingest workflow before any baseline/pre-existing claim when context is incomplete. Bounded direct inspection only after ingest fails. Never infer where ingestion is possible.
- **Safety / Escalation**: Least-privilege. Confirm writes/mutations. Report-only for new loops (L1). Never touch secrets, production credentials, or Research Canary artifacts unless full P128→P130 chain is intentionally replayed. Fail-closed on canon mutation, git state changes, runtime authority without explicit grant.
- **Night-Shift Readiness**: Prep specs + boundaries during day. Let autonomous loop run async. Handoff via worksheet + receipt.
- **Edge Cases**:
  - Incomplete spec → Probe + prototype IR/schema on-the-fly (document assumptions as SPECULATIVE).
  - Conflict with existing code → Propose migration path with smallest safe surface (use repo-intel).
  - High-uncertainty forecast → Dual-path (conventional + cracked) + explicit Brier audit + provenance.
  - Skill drift → Curator reflection + patch umbrella.

## 4. VERIFICATION BLOCK (Mandatory Before “Done”)
- [ ] Full targeted test suite + linter + `python scripts/run_fast_ci.py` (scrubbed where Python) passes for touched surfaces.
- [ ] Cross-persona / different-model review passed.
- [ ] Docs, skills (SKILL.md + references/), memory updated with provenance.
- [ ] Worksheet / receipt committed or emitted + git tag where applicable.
- [ ] Feedback appended (FEEDBACK.md or equivalent).
- [ ] Brier calibration performed and recorded for any predictions.
- [ ] Rune / governance / YGGDRASIL alignment confirmed (via abx-runes-yggdrasil-manager or equivalent).
- [ ] OBSERVED/INFERRED/SPECULATIVE tiers + full provenance present.
- [ ] No fabricated evidence; ingest-first path followed.

## 5. ACTIVATION & USAGE
- **Session start**: Explicitly tag or load this skill.
- **Self-enforcement**: Hermes will reference and follow unless overridden.
- **Complex work close**: "Update skill with learnings" → patch this SKILL.md or add references/ + bump version.
- **Periodic**: "Run agentic audit on last N commits" or "sweep last 7 days".
- **Autonomous continuation**: Bare "continue" / "keep going" etc. = full authorization for non-dangerous forward progress (Layer 0/1 per automated-production-governance) until complete or hard blocker.

## Common Pitfalls
- Skipping mandatory pre-change reads or router.
- Claiming "verified" without scrubbed targeted execution + explicit blocker explanation for any collection noise (e.g., pre-existing temporal/viz suite blockers).
- Treating historical `out/` artifacts as live execution authority.
- Fabricating data, UUIDs, wall-clock values, or unearned certainty in deterministic surfaces.
- Broad full-suite runs instead of `abraxas-validation-routing` narrowest path.
- Duplicating logic across narrow skills instead of patching class-level umbrellas.
- Auto-promoting generated runes/schemas or crossing SHADOW ↔ FORECAST authority.
- Ignoring cross-platform casing/import portability (lowercase `scripts.*` canonical).


## References & Related
- Predecessor/specialized: `abraxas-jamon-agentic-workflow` (Jamon 0-18 core; see `references/jamon-to-master-evolution.md` in master)
- Primary master: `abraxas-master-loop-workflow` (Jamon + Anthropic loop engineering fusion)
- Core: `abraxas_v2_governed_operator_loop` (7-phase)
- Supporting: `abraxas-repo-intel`, `abraxas-automated-production-governance`, `abraxas-validation-routing`, `abraxas_unbound_rune_analyzer`, `abx-runes-yggdrasil-manager`
- Authoring: `hermes-agent-skill-authoring`
- AGENTS.md, GOVERNANCE_V3.md, README.md, PLANS.md
- Jamon-style self-healing docs + cross-review discipline (embedded)
- `references/jamon-points-abraxas-mapping.md` (explicit Jamon 0-18 ↔ Abraxas cross-map)

**Status**: Active class-level umbrella. Curator consolidation target with governed_operator_loop and production-governance umbrellas. Prefer patch + references/ for session-specific detail over new narrow siblings.

**Next evolution signals**: New non-trivial technique, user correction on workflow, skill drift, or successful autonomous campaign closure → immediate patch with concrete steps + verification.
