# ADR-0019: Agent Doctrine and Skill Routing Consolidation

## Status

Accepted

## Context

Abraxas agent guidance had accumulated router logic, historical governance procedures, multi-agent handoff details, skill loading assumptions, and operational troubleshooting in the default `AGENTS.md` path. Skills also contained overlapping universal-router claims that made ordinary engineering look like it required autonomous loop orchestration.

Governance V3 now makes routine engineering implementation-first at Layer 0, while preserving deterministic validation and operator gates for external production, canon, runtime, and semantic conflicts.

## Decision

1. `AGENTS.md` is the concise constitutional router for authority, startup, MSW execution, evidence states, execution modes, activation boundaries, deterministic invariants, SHADOW/FORECAST separation, RDI invariants, multi-agent routing, skill routing, validation, and historical material.
2. `SKILLS.md` is the canonical skill registry/router. It classifies each repository skill and makes skill loading task-specific rather than default.
3. `abraxas-master-loop-workflow` is specialist-only for autonomous multi-cycle loops, recursive improvement, scheduled campaigns, and durable loop state.
4. `abraxas-jamon-agentic-workflow` is preserved as superseded historical reference.
5. WorkPacket/HandoffEnvelope workflows are required only for real delegated or peer multi-agent work, not ordinary single-agent code changes.
6. Brier scoring is reserved for genuine probabilistic forecasts with settlement semantics.
7. Doctrine drift is validated by a lightweight deterministic script and tests rather than a new orchestration database.

## Consequences

- Agents can determine default authority and execution mode with a small startup read set.
- Historical governance artifacts remain preserved but no longer pollute ordinary execution.
- Skills cannot silently override `AGENTS.md` or Governance V3.
- Master-loop capability remains available without becoming the default route.
- Future drift in skill registry paths, authority language, required references, and master-loop defaults can be caught automatically.

## Validation

- `python -m scripts.governance.validate_agent_doctrine`
- `python -m pytest tests/test_agent_doctrine_validation.py -q`
- `python scripts/run_fast_ci.py`
