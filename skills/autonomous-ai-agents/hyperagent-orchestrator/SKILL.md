---
name: hyperagent-orchestrator
description: Use when working with HyperAgent or hyperagent.com to authenticate, author skills, deploy roles, orchestrate fleets, or bridge HyperAgent outputs into Abraxas workflows. Encodes deterministic role configs, safe credential handling, fleet operations, and Abraxas import/export patterns.
version: 1.0.0
author: Hermes Agent
license: Proprietary
metadata:
  hermes:
    tags: [hyperagent, agents, orchestration, skills, fleets, deployment, integrations, abx-bridge]
    related_skills: [abraxas-multi-agent-orchestrator, abraxas-reviewable-capability-layer, hermes-agent, hermes-agent-skill-authoring, skill-maintenance]
---
# hyperagent-orchestrator

## Overview
HyperAgent is the outer command surface; Abraxas is the inner meaning surface. Use this skill when you need to teach a HyperAgent account once, reuse it across runs, and keep the output bridgeable back into Abraxas with provenance, symbolic compression, and Brier-aware telemetry.

This skill is the HyperAgent-specific umbrella under the broader Abraxas multi-agent stack. It is designed to stay deterministic: config in JSON/YAML, secrets in env vars or a secure store, repeatable deployment payloads, and explicit export/import boundaries.

## When to Use
- You mention HyperAgent, hyperagent.com, HyperAgent skills, agent fleets, agent deployment, or long-running hosted agents.
- You need to authenticate to HyperAgent or refresh a session without hard-coding secrets.
- You want to create or version a reusable skill, agent role, or workflow for HyperAgent.
- You want triggers, budgets, tool permissions, evals, observability, or fleet monitoring.
- You want to export Abraxas subsystems into HyperAgent roles or import HyperAgent outputs back into Abraxas.
- You need compliance-aware orchestration for agents that may touch external systems.

## OBSERVED / INFERRED / SPECULATIVE

### OBSERVED
- HyperAgent is an Airtable platform for always-on agents and hosted workflow execution. Public examples show reusable skills stored as JSON files and loaded at runtime rather than re-explained every turn. [provenance: web search results; Airtable article; public HyperAgent skills repo]
- Airtable describes HyperAgent as an agent execution platform tied to structured operational data, connected tools, and governance/human oversight. [provenance: Airtable articles on AI agent skills, agent frameworks, and AI agents]
- Public HyperAgent skill examples cover design systems, content production, and ops workflows, which implies reusable “teach once, apply many times” behavior. [provenance: public skills repo / notes]

### INFERRED
- HyperAgent skill payloads should be versioned, role-scoped, and deterministic enough to diff, review, and deploy repeatedly.
- Auth/session handling should prefer environment variables or a secure secret store and avoid embedding credentials inside skill files.
- Fleets likely need explicit model budgets, tool permissions, triggers, and evaluation hooks to stay predictable at scale.
- Abraxas ↔ HyperAgent bridging should preserve provenance, canonical hashes, and a clean split between operational payloads and interpretation layers.

### SPECULATIVE
- Exact HyperAgent API endpoints, OAuth flow details, and role JSON keys may change; verify against the live platform docs before binding a production integration.
- Browser/shell/code-execution permissions may be configured as platform-level tool grants rather than embedded in every skill file.
- “Skills” may be imported/exported as JSON with platform-specific metadata; treat the templates here as a compatible operating model, not a guaranteed wire format.

## Operating Model

### 1) Authenticate without leaking secrets
- Put tokens in `HYPERAGENT_API_KEY`, `HYPERAGENT_OAUTH_TOKEN`, or your platform’s secure store.
- Prefer one source of truth per environment.
- Keep session state out of skill files; if the platform supports refresh tokens, store them only in the secure store.
- If the account supports SSO/OAuth, keep the refresh path separate from deployment payload generation.

### 2) Author skills once, reuse everywhere
Treat a HyperAgent skill as a stable unit of reusable operational knowledge:
- clear name
- version field
- concise purpose
- explicit input/output contract
- tool permissions
- failure policy
- eval or acceptance criteria

When a workflow changes, update the skill once instead of re-prompting the agent.

### 3) Build deployable roles, not chat prompts
A role should declare:
- trigger(s)
- system prompt / mission text
- allowed tools
- model choice / fallback
- budget or cost guardrails
- memory scope
- eval checks
- delivery destination(s)
- human escalation rule

### 4) Orchestrate fleets deterministically
Use separate agents for planner, navigator, analyst, editor, executor, and reviewer patterns when the task is multi-step.
- Planner: decomposes work and sets success criteria.
- Navigator: gathers source material and routes dependencies.
- Analyst: compresses evidence into actionable conclusions.
- Editor: writes the deliverable.
- Executor: performs bounded external actions.
- Reviewer: checks policy, provenance, and completion.

If one agent needs to hand work to another, make the handoff explicit in a machine-readable payload.

### 5) Bridge to Abraxas cleanly
- Export Abraxas subsystem logic as HyperAgent skills or roles.
- Import HyperAgent outputs back into Abraxas as structured JSON.
- Preserve `canonical_hash`, source URI, timestamps, and a short provenance chain.
- Keep OBSERVED / INFERRED / SPECULATIVE layers separate from raw artifacts.
- Keep Brier scoring telemetry-only; do not use it as an authority escalation mechanism.

## Role Lifecycle

1. Define the role in a JSON template.
2. Attach triggers, tools, budgets, and evals.
3. Dry-run locally with the helper script or a fixture file.
4. Deploy or update the role.
5. Observe the first runs for drift, cost spikes, or tool failures.
6. Patch the skill once when the procedure stabilizes.

Completion criterion: the role definition is reproducible from the template and the deployment payload is diffable.

## Compliance and Safety
- Do not encode real-money wagering behavior into HollerSports or any other agent unless the task is explicitly compliance-reviewed and legally allowed.
- Do not grant shell, browser, or integration tools broadly when a narrower capability suffices.
- Do not expose credentials in prompts, logs, or exported skills.
- Treat rate limits as a design constraint: cache, back off, and isolate retries.
- Sandbox risky external actions behind explicit execution roles.

## Common Patterns

| Pattern | Use | Completion criterion |
|---|---|---|
| Planner/Navigator/Executor | Long, multi-step workflows | Each agent has a single job and handoff format |
| Research/Writer/Reviewer | Analysis-to-doc pipelines | Evidence packet and final output differ cleanly |
| Monitor/Filter/Escalate | Long-running watch tasks | Alerts fire only when thresholds are met |
| Batch A/B agents | Comparing prompts or models | Evaluation metric and winner rule are declared up front |

## HyperAgent ↔ Abraxas Bridge

Use HyperAgent when you want hosted execution, enterprise integrations, and durable workflows.
Use Abraxas when you want symbolic compression, governance layers, provenance discipline, and downstream synthesis.

Bridge rule:
- HyperAgent emits structured run output.
- Abraxas compresses, tags, scores, and archives the output.
- Do not let the two layers blur: execution stays operational; interpretation stays governed.

## Support Files
- `references/hyperagent-platform-facts.md` — observed platform summary and caveats.
- `references/hyperagent-abraxas-bridge.md` — export/import rules and mapping notes.
- `references/hyperagent-role-blueprints.md` — reusable planner/navigator/executor blueprints.
- `templates/hyperagent-agent-config.json` — generic role config template.
- `templates/hyperagent-skill.json` — generic skill payload template.
- `assets/hyperagent-agent-config.schema.json` — JSON Schema for local validation.
- `assets/abraxas-hyperagent-mapping.yaml` — Abraxas subsystem ↔ HyperAgent role map.
- `scripts/hyperagent_auth_helper.py` — local credential/session inspector.
- `scripts/hyperagent_deploy_role.py` — deterministic role payload builder.
- `scripts/hyperagent_export_import_bridge.py` — Abraxas ↔ HyperAgent mapping bridge.
- `scripts/validate_skill.py` — lightweight skill-tree validator.

## Common Pitfalls
1. Treating HyperAgent like a generic chat bot. It is a hosted workflow system; define roles, tools, and success criteria.
2. Embedding secrets in skill files. Keep credentials outside the skill tree.
3. Over-granting tools. Narrow permissions beat universal tool access.
4. Failing to version roles. A deployable role must be diffable and reproducible.
5. Collapsing execution and interpretation. Keep HyperAgent outputs raw until Abraxas compresses them.
6. Claiming exact API behavior without checking live docs. Verify the platform before binding production automation.

## Verification Checklist
- [ ] Frontmatter starts at byte 0 and parses cleanly.
- [ ] Skill name is lowercase with hyphens and matches the directory.
- [ ] Support files exist under `references/`, `templates/`, `assets/`, or `scripts/`.
- [ ] Auth helper resolves required env vars and prints a deterministic status object.
- [ ] Deploy helper emits a stable JSON payload for a sample role.
- [ ] Bridge helper round-trips an example Abraxas payload.
- [ ] SKILL.md stays compact enough to load repeatedly without bloat.
- [ ] The skill is folded into the Abraxas umbrella through `related_skills` and bridge references.

## Example Usage
- Deploy a HyperAgent role for daily LA/CA signal foraging:
  - `python skills/autonomous-ai-agents/hyperagent-orchestrator/scripts/hyperagent_deploy_role.py --template skills/autonomous-ai-agents/hyperagent-orchestrator/templates/hyperagent-agent-config.json --name la-signal-forager --mission "Monitor LA/CA developments with compliance filters and daily summaries" --dry-run`
- Migrate Abraxas Codex Slice79 into a HyperAgent fleet role:
  - `python skills/autonomous-ai-agents/hyperagent-orchestrator/scripts/hyperagent_export_import_bridge.py --mode export --input slice79.json --output hyperagent-role.json`
  - `python skills/autonomous-ai-agents/hyperagent-orchestrator/scripts/hyperagent_deploy_role.py --input hyperagent-role.json --dry-run`
- Check auth/session posture:
  - `python skills/autonomous-ai-agents/hyperagent-orchestrator/scripts/hyperagent_auth_helper.py --status`

## Validation
Prefer a small local validation pass before treating the skill as done:
1. Run the bundled validator script.
2. Confirm every support file path exists.
3. Inspect a generated deployment payload.
4. Keep production API calls behind an explicit `--post`/`--deploy` flag.

## Notes for Curators
This skill overlaps with `abraxas-multi-agent-orchestrator` and `abraxas-reviewable-capability-layer`. Keep HyperAgent-specific mechanics here; keep cross-platform orchestration theory in the broader Abraxas umbrellas.
