# Generator / Evaluator Split

**Rule**: Never self-grade. Always separate roles.

- **Generator** (hermes-cracked-python-engineer persona):
  - Visionary/DMT-edge creativity.
  - Proposes implementation, runs code, writes tests.
  - Produces initial artifacts + OBSERVED/INFERRED/SPECULATIVE.

- **Evaluator** (senior-python-architect or "Doubt-First Auditor"):
  - Balanced, production-minded, skeptical.
  - Assumes failure until proven by machine checks.
  - Runs checklists: security, AI smells, runes/governance, maintainability, false-confidence, hyperstition risk.
  - Signs off only on verifiable evidence.

Use multi-agent-orchestrator or explicit steer for different models/personas when possible.

This split is non-negotiable for high-stakes or long-running loops.