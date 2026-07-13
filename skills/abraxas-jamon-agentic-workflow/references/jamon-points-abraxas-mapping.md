# Jamon 0-18 Points ↔ Abraxas Integration Mapping (v1.0)

This reference provides the explicit cross-mapping used by `abraxas-jamon-agentic-workflow`.

## Core Mappings
- **Point 0 (Router)**: AGENTS.md + mandatory pre-reads (README/PLANS/GOVERNANCE_V3) + abraxas-repo-intel smallest evidence packet.
- **Points 1-2 (Intake + Self-Healing Docs)**: OBSERVED/INFERRED/SPECULATIVE + provenance + first-7-lines rich summaries + exact Obsidian YAML. Update SKILL.md + references/ on every non-trivial task.
- **Point 3 (Implementation)**: Always execute code/tests yourself (scrubbed env). TDD during build. Use rtk/terminal.
- **Points 4-5 (Tests/Linting)**: `abraxas-validation-routing` (narrowest first) + targeted pytest + `scripts/run_fast_ci.py`. Scrubbed verification mandatory.
- **Point 6 (Cross-Review)**: Different persona/model via multi-agent-orchestrator or steer. Checklists include runes/governance, Brier, hyperstition risk, false-confidence.
- **Point 7 (Trace & Commit)**: Worksheets/receipts in out/, conventional commits, change ledgers where applicable.
- **Point 9 (Tools/Scripts)**: Prefer built-ins. Create reusable scripts under skills/.../scripts/ or bin/.
- **Point 10/14 (Sweeps/Audits)**: Periodic commit scans, skill drift via curator, false-confidence audits.
- **Point 12 (Autonomous Loop)**: "continue"/"keep going" = full forward progress on non-dangerous (Layer 0/1 per automated-production-governance). Night-shift handoff via worksheet + receipt. Force comprehensive TODO on continuation cues.
- **Point 18 (End-of-Shift)**: Full validations, feedback, Brier calibration, rune alignment confirmation.

## Abraxas Enhancements Layered On Top
- Ingest-first evidence before claims.
- Rune/YGGDRASIL binding via abx-runes-yggdrasil-manager and abraxas_unbound_rune_analyzer.
- Brier scoring + hyperstition scanning on forecasts/memetic topics.
- Determinism invariants (canonical_hash, no wall-clock/UUID in deterministic surfaces).
- Governance V3 + automated-production-governance (AUTOMATED_PRODUCTION default for routine).
- Structured output + fail-closed on dangerous surfaces (canon, git, canary, runtime authority).
- Class-level umbrellas + references/ for durability (per user preference and hermes-agent-skill-authoring).

## Verification Block Integration
Always close with the 9-item checklist in the main SKILL.md (targeted tests + cross-review + docs update + Brier + rune alignment + provenance + no fabrication + ingest path).

See main SKILL.md for full workflow steps and guardrails.

**Maintenance**: Update this reference when Jamon points evolve or new Abraxas runes/governance surfaces are bound. Patch the parent umbrella on changes.